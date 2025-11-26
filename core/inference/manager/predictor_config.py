from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from core.inference.predictors.predictor import Predictor


@dataclass
class PredictorConfig:
    """Configuration for a predictor instance pool."""

    predictor_class: Type[Predictor]
    init_args: Dict[str, Any]
    pool_size: int = 1
    device: str = "cuda"
    preload: bool = False
    # Optional pre-created instance to allow sharing between configs/usages
    instance: Optional[Predictor] = None

    def create_instance(self) -> Predictor:
        """Create a new predictor instance with the configured arguments."""
        if self.instance is not None:
            return self.instance
        return self.predictor_class(**self.init_args)
