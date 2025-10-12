import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Type, TypeVar

from core.inference.manager.predictor_config import PredictorConfig
from core.inference.manager.predictor_pool import PredictorPool
from core.inference.predictors.predictor import Predictor

T = TypeVar("T", bound=Predictor)


class PredictorManager:
    """
    Manages predictor instances with pooling and async support.

    Usage:
        # Setup
        manager = PredictorManager()
        manager.register(PredictorConfig(
            predictor_class=GroundingDinoObjectDetector,
            init_args={"checkpoint_path": "...", "config_path": "..."},
            pool_size=2,
            device="cuda",
            preload=True
        ))

        # Use
        async with manager.get_predictor(LabelBasedObjectDetector) as predictor:
            results = predictor.detect_with_label(image, "person")

        # Cleanup
        await manager.shutdown()
    """

    def __init__(self):
        self._configs: List[PredictorConfig] = []
        self._pools: Dict[Type[Predictor], List[PredictorPool]] = {}
        self._initialized = False
        self._lock = asyncio.Lock()

    def register(self, config: PredictorConfig) -> None:
        """Register a predictor configuration."""
        if self._initialized:
            raise RuntimeError("Cannot register predictors after initialization")
        self._configs.append(config)

    async def initialize(self):
        """Initialize all registered predictor pools."""
        async with self._lock:
            if self._initialized:
                return

            for config in self._configs:
                pool = PredictorPool(config)

                # Map the predictor to all its base classes
                for base_class in config.predictor_class.__mro__:
                    if base_class is Predictor or issubclass(base_class, Predictor):
                        if base_class not in self._pools:
                            self._pools[base_class] = []
                        self._pools[base_class].append(pool)

            self._initialized = True

    async def shutdown(self):
        """Shutdown all predictor pools."""
        async with self._lock:
            if not self._initialized:
                return

            # Shutdown all pools
            shutdown_tasks = []
            seen_pools = set()

            for pools in self._pools.values():
                for pool in pools:
                    if id(pool) not in seen_pools:
                        seen_pools.add(id(pool))
                        shutdown_tasks.append(pool.shutdown())

            await asyncio.gather(*shutdown_tasks)

            self._pools.clear()
            self._configs.clear()
            self._initialized = False

    @asynccontextmanager
    async def get_predictor(self, predictor_type: Type[T]) -> T:
        """
        Get a predictor instance by base class type.

        Args:
            predictor_type: The base class type to request (e.g., LabelBasedObjectDetector)

        Returns:
            A predictor instance that implements the requested type

        Raises:
            ValueError: If no predictor is registered for the requested type
        """
        if not self._initialized:
            await self.initialize()

        if predictor_type not in self._pools:
            raise ValueError(
                f"No predictor registered for type {predictor_type.__name__}"
            )

        # Get pools that can provide this predictor type
        pools = self._pools[predictor_type]

        # Try to acquire from the first available pool with shortest queue
        # This provides simple load balancing
        pool = min(pools, key=lambda p: p.available.qsize())

        async with pool.acquire() as predictor:
            yield predictor
