#!/usr/bin/env python3
"""NeuroSight AI inference entrypoint.

This script is designed to be launched by the Qt desktop client through QProcess.
It writes a single JSON object to stdout on every exit path and sends all
diagnostic output to stderr so the caller can parse stdout safely.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms
from torchvision.models import efficientnet_b0


LOGGER = logging.getLogger("neurosight.inference")
CLASS_LABELS = ["NonDemented", "VeryMildDemented", "MildDemented", "ModerateDemented"]
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


@dataclass
class InferenceResult:
    prediction: str | None
    diagnosis: str | None
    confidence: float | None
    error: str | None
    heatmap_path: str = ""


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    LOGGER.setLevel(logging.INFO)
    LOGGER.handlers.clear()
    LOGGER.addHandler(handler)
    LOGGER.propagate = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run NeuroSight AI MRI inference")
    parser.add_argument("--image_path", required=True, help="Path to the MRI image to analyze")
    return parser.parse_args()


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def weights_path() -> Path:
    return project_root() / "models" / "weights" / "best_model.pt"


def build_model(num_classes: int) -> torch.nn.Module:
    model = efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(in_features, num_classes)
    return model


def load_model(device: torch.device) -> torch.nn.Module:
    model = build_model(len(CLASS_LABELS))
    weights_file = weights_path()

    if not weights_file.exists():
        raise FileNotFoundError(f"Model weights not found: {weights_file}")

    checkpoint = torch.load(weights_file, map_location=device)
    state_dict = checkpoint.get("state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
    if not isinstance(state_dict, dict):
        raise ValueError("Unsupported checkpoint format. Expected a state dict or a checkpoint dictionary.")

    model.load_state_dict(state_dict, strict=True)
    model.to(device)
    model.eval()
    return model


def preprocess_image(image_path: Path) -> torch.Tensor:
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    image = Image.open(image_path).convert("RGB")
    return transform(image).unsqueeze(0)


def run_inference(image_path: Path) -> InferenceResult:
    if not image_path.exists():
        return InferenceResult(prediction=None, diagnosis=None, confidence=None, error=f"Image not found: {image_path}")
    if image_path.suffix.lower() not in VALID_EXTENSIONS:
        return InferenceResult(
            prediction=None,
            diagnosis=None,
            confidence=None,
            error=f"Unsupported image extension '{image_path.suffix}'.",
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(device)
    input_tensor = preprocess_image(image_path).to(device)

    with torch.inference_mode():
        logits = model(input_tensor)
        probabilities = torch.softmax(logits, dim=1)
        confidence, class_index = torch.max(probabilities, dim=1)

    predicted_index = int(class_index.item())
    if predicted_index < 0 or predicted_index >= len(CLASS_LABELS):
        return InferenceResult(
            prediction=None,
            diagnosis=None,
            confidence=None,
            error=f"Predicted class index out of range: {predicted_index}",
        )

    prediction = CLASS_LABELS[predicted_index]
    confidence_value = float(confidence.item())
    return InferenceResult(
        prediction=prediction,
        diagnosis=prediction,
        confidence=confidence_value,
        error=None,
        heatmap_path="",
    )


def emit_result(result: InferenceResult) -> int:
    payload = {
        "prediction": result.prediction,
        "diagnosis": result.diagnosis,
        "confidence": result.confidence,
        "error": result.error,
        "heatmap_path": result.heatmap_path,
    }
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.flush()
    return 0 if result.error is None else 1


def main() -> int:
    configure_logging()

    try:
        args = parse_args()
        LOGGER.info("Starting inference for %s", args.image_path)
        result = run_inference(Path(args.image_path))
        if result.error:
            LOGGER.error(result.error)
        else:
            LOGGER.info("Inference complete: %s (confidence %.4f)", result.prediction, result.confidence or 0.0)
        return emit_result(result)
    except Exception as exc:  # pragma: no cover - defensive bridge entrypoint
        LOGGER.exception("Unhandled inference failure")
        return emit_result(
            InferenceResult(
                prediction=None,
                diagnosis=None,
                confidence=None,
                error=str(exc),
                heatmap_path="",
            )
        )


if __name__ == "__main__":
    raise SystemExit(main())