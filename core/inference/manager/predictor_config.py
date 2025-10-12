from dataclasses import dataclass
from typing import Any, Dict, Type

from core.inference.predictors.predictor import Predictor


@dataclass
class PredictorConfig:
    """Configuration for a predictor instance pool."""

    predictor_class: Type[Predictor]
    init_args: Dict[str, Any]
    pool_size: int = 1
    device: str = "cuda"
    preload: bool = False

    def create_instance(self) -> Predictor:
        """Create a new predictor instance with the configured arguments."""
        return self.predictor_class(**self.init_args)
