import gc

import numpy as np
import torch
from core.inference.predictors.mask_based_image_inpainter import MaskBasedImageInpainter
from PIL import Image
from simple_lama_inpainting.utils.util import prepare_img_and_mask
from typing_extensions import override


class LamaImageInpainter(MaskBasedImageInpainter):
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.device = None

    @override
    def load(self, device: str) -> None:
        self.model = (
            torch.jit.load(self.model_path, map_location=device)
            if self.model is None
            else self.model.to(device)
        )
        self.device = device

    @override
    def unload(self) -> None:
        if self.model is not None:
            try:
                self.model.to("cpu")
            except Exception:
                pass

        self.model = None
        self.device = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.ipc_collect()
            torch.cuda.empty_cache()

    @override
    def inpaint_with_mask(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() before inpainting.")

        image, mask = prepare_img_and_mask(image, mask, self.device)
        with torch.inference_mode():
            result = self.model(image, mask)
            result = result[0].permute(1, 2, 0).detach().cpu().numpy()
            result = np.clip(result * 255, 0, 255).astype(np.uint8)
            return Image.fromarray(result)
