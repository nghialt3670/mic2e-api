import asyncio
from contextlib import asynccontextmanager
from typing import List

from core.inference.manager.predictor_config import PredictorConfig
from core.inference.predictors.predictor import Predictor


class PredictorPool:
    """Manages a pool of predictor instances for a specific predictor type."""

    def __init__(self, config: PredictorConfig):
        self.config = config
        self.available: asyncio.Queue[Predictor] = asyncio.Queue()
        self.all_instances: List[Predictor] = []
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self):
        """Initialize the pool by creating instances."""
        async with self._lock:
            if self._initialized:
                return

            for _ in range(self.config.pool_size):
                instance = self.config.create_instance()
                self.all_instances.append(instance)

                if self.config.preload:
                    await asyncio.to_thread(instance.load, self.config.device)

                await self.available.put(instance)

            self._initialized = True

    async def shutdown(self):
        """Shutdown the pool by unloading all instances."""
        async with self._lock:
            if not self._initialized:
                return

            # Drain the queue
            instances_to_unload = []
            while not self.available.empty():
                try:
                    instance = self.available.get_nowait()
                    instances_to_unload.append(instance)
                except asyncio.QueueEmpty:
                    break

            # Unload all instances
            for instance in self.all_instances:
                await asyncio.to_thread(instance.unload)

            self.all_instances.clear()
            self._initialized = False

    @asynccontextmanager
    async def acquire(self):
        """Acquire a predictor instance from the pool."""
        if not self._initialized:
            await self.initialize()

        # Get an available instance
        instance = await self.available.get()

        try:
            # Ensure it's loaded on the correct device
            if not self.config.preload:
                await asyncio.to_thread(instance.load, self.config.device)

            yield instance
        finally:
            # Return instance to pool
            await self.available.put(instance)
