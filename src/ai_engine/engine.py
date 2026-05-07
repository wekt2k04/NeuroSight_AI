from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy as np
from PIL import Image

from .domain import PredictionResult


class InferenceEngine(Protocol):
    def predict(self, image_path: str) -> PredictionResult:
        ...


class OnnxInferenceEngine:
    def __init__(self, session, classes=None):
        self.session = session
        self.classes = classes or ["Normal", "Mild", "Moderate", "Severe"]

    def preprocess(self, image_path: str):
        image = Image.open(image_path).convert("RGB")
        image = image.resize((224, 224), Image.Resampling.BILINEAR)
        image_np = np.asarray(image, dtype=np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        image_np = (image_np - mean) / std
        image_np = np.transpose(image_np, (2, 0, 1))
        return np.expand_dims(image_np, axis=0).astype(np.float32)

    def predict(self, image_path: str) -> PredictionResult:
        input_arr = self.preprocess(image_path)
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: input_arr})

        logits = np.squeeze(np.array(outputs[0], dtype=np.float32))
        if logits.ndim != 1:
            raise RuntimeError(f"Unexpected ONNX output shape: {logits.shape}")
        if logits.shape[0] != len(self.classes):
            raise RuntimeError(f"Expected {len(self.classes)} classes, got {logits.shape[0]}")

        exp = np.exp(logits - np.max(logits))
        probabilities = exp / np.sum(exp)
        idx = int(np.argmax(probabilities))
        return PredictionResult(
            diagnosis=self.classes[idx],
            confidence=float(probabilities[idx]),
            heatmap_path=None,
        )


class FileSystemModelLocator:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)

    def resolve(self, model_name: str) -> Path:
        candidate = self.base_dir / model_name
        if not candidate.exists():
            raise FileNotFoundError(f"Model file not found: {candidate}")
        return candidate
