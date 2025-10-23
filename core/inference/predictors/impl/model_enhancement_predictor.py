# core/predictors/impl/model_enhancing_predictor.py
import gc
from typing import Any, Dict

import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from typing_extensions import override

from core.inference.predictors.impl.img_enhancing_model.aesthetic_regressor import (
    AestheticRegressor,
)
from core.inference.predictors.parameter_enhancement_predictor import (
    ParameterEnhancementPredictor,
)


class ModelEnhancingPredictor(ParameterEnhancementPredictor):
    def __init__(
        self,
        checkpoint_path: str,
        factors: list = ["saturation", "brightness", "tint", "temperature", "contrast"],
        factors_coefs: dict = {
            "saturation": 43,
            "brightness": 43,
            "tint": 30,
            "temperature": 30,
            "contrast": 43,
        },
        n_factors: int = 5,
        activation: str = "tanh",
        backbone: str = "resnet18",
        device: str = "cpu",
    ):
        self.checkpoint_path = checkpoint_path
        self.factors = factors
        self.factors_coefs = factors_coefs
        self.n_factors = n_factors
        self.activation = activation
        self.backbone = backbone
        self.device = device
        self.model: Any = None

    def _build_transform(self):
        return transforms.Compose(
            [
                transforms.Resize((640, 640)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

    @override
    def load(self) -> None:
        self.model = AestheticRegressor(activation=self.activation).to(self.device)
        state_dict = torch.load(self.checkpoint_path, map_location=self.device)
        self.model.load_state_dict(state_dict, strict=False)
        self.model.eval()

    @override
    def unload(self) -> None:
        if self.model is not None:
            try:
                self.model.to("cpu")
            except Exception:
                pass
        self.model = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    @override
    def predict_enhancement(self, image: Image.Image) -> Dict[str, float]:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() before predict.")

        transform = self._build_transform()

        class Normalizer:
            def __init__(self, coefs):
                self.coefs = np.array(list(coefs.values()), dtype=np.float32)

            def transform(self, labels):
                return labels / self.coefs

            def inverse_transform(self, norm_labels):
                return norm_labels * self.coefs

        label_normalizer = Normalizer(self.factors_coefs)
        image_tensor = transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            preds = self.model(image_tensor).cpu().numpy().flatten()

        preds_denorm = label_normalizer.inverse_transform(preds)

        return {
            self.factors[i]: float(preds_denorm[i]) for i in range(len(self.factors))
        }
