#!/usr/bin/env python3
"""Generate a placeholder `best_model.pt` matching the production architecture.

This script builds an EfficientNet-B0 model with a final linear layer sized for
4 classes and saves its `state_dict` to `models/weights/best_model.pt`.

Note: this produces randomly-initialized weights (placeholder). Replace with
trained weights for real inference accuracy.
"""
import os
import sys

try:
    import torch
    from torchvision.models import efficientnet_b0
except Exception as exc:  # pragma: no cover - environment dependent
    print("ERROR: torch or torchvision not available in this environment:", exc, file=sys.stderr)
    raise


def build_model(num_classes: int = 4) -> torch.nn.Module:
    model = efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(in_features, num_classes)
    return model


def main() -> int:
    out_dir = os.path.join("models", "weights")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "best_model.pt")

    model = build_model(num_classes=4)
    # Save only the state_dict to match inference loader expectations
    torch.save(model.state_dict(), out_path)
    print(f"Saved placeholder weights to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
