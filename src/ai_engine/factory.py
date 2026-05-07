from __future__ import annotations

from pathlib import Path

import onnxruntime as ort

from .engine import OnnxInferenceEngine


class InferenceEngineFactory:
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)

    def create(self) -> OnnxInferenceEngine:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        providers = ["CPUExecutionProvider"]
        available = ort.get_available_providers()
        if "CUDAExecutionProvider" in available:
            providers.insert(0, "CUDAExecutionProvider")

        session = ort.InferenceSession(str(self.model_path), providers=providers)
        return OnnxInferenceEngine(session)


def create_inference_engine(model_path: str) -> OnnxInferenceEngine:
    return InferenceEngineFactory(model_path).create()
