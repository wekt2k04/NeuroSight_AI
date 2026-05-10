#!/usr/bin/env python3
import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path
from PIL import Image
import numpy as np
from torchvision.models import efficientnet_b0

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEIGHTS_PATH = PROJECT_ROOT / "models" / "weights" / "best_model.pt"
ONNX_PATH    = PROJECT_ROOT / "best_model.onnx"
CLASS_LABELS = ["NonDemented", "VeryMildDemented", "MildDemented", "ModerateDemented"]

IMG_CANDIDATES = [
    PROJECT_ROOT / "data" / "samples" / "OAS1_0001_MR1_mpr-1_100.jpg",
    Path(r"C:/Users/Wilfried/OneDrive/Bureau/Wilfried/professionnel/Ecole/2e GIIA/S4/NeuroSight_AI/data/samples/OAS1_0001_MR1_mpr-1_100.jpg"),
]

def build_model(num_classes=4):
    model = efficientnet_b0(weights=None)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    return model

def load_real_input():
    for p in IMG_CANDIDATES:
        if Path(p).exists():
            print(f"Image : {p}")
            img = Image.open(p).convert("RGB").resize((224, 224))
            arr = (np.array(img, dtype=np.float32) / 255.0 - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
            t = torch.from_numpy(arr.transpose(2, 0, 1)[np.newaxis]).float()  # ✅ explicitement float32
            return t
    print("⚠️  Image introuvable, dummy float32")
    return torch.randn(1, 3, 224, 224, dtype=torch.float32)

class NeuroSightCAMWrapper(nn.Module):
    def __init__(self, base_model, use_relu=True):
        super().__init__()
        self.features   = base_model.features
        self.avgpool    = base_model.avgpool
        self.classifier = base_model.classifier
        self.fc_weights = base_model.classifier[1].weight  # (4, 1280)
        self.use_relu   = use_relu

    def forward(self, x):
        feat   = self.features(x)
        pooled = self.avgpool(feat)
        flat   = torch.flatten(pooled, 1)
        logits = self.classifier(flat)
        w      = self.fc_weights.unsqueeze(-1).unsqueeze(-1)
        cam    = F.conv2d(feat, w)
        if self.use_relu:
            cam = F.relu(cam)
        return logits, cam

def diagnose(base_model, inp):
    print("\n--- DIAGNOSTIC CAM ---")
    base_model.eval()
    with torch.no_grad():
        feat = base_model.features(inp.float())
        print(f"features  dtype    : {feat.dtype}")
        print(f"features  min/max  : {feat.min():.4f} / {feat.max():.4f}")
        w = base_model.classifier[1].weight.unsqueeze(-1).unsqueeze(-1)
        cam_raw = F.conv2d(feat, w)
        print(f"cam brut  min/max  : {cam_raw.min():.4f} / {cam_raw.max():.4f}")
        cam_relu = F.relu(cam_raw)
        print(f"cam relu  min/max  : {cam_relu.min():.4f} / {cam_relu.max():.4f}")
        use_relu = cam_relu.max().item() > 1e-6
        print(f"→ ReLU conservé : {use_relu}")
    return use_relu

def export():
    print(f"Chargement : {WEIGHTS_PATH}")
    if not WEIGHTS_PATH.exists():
        raise FileNotFoundError(f"Introuvable : {WEIGHTS_PATH}")

    base_model = build_model()
    checkpoint = torch.load(WEIGHTS_PATH, map_location="cpu")
    sd = checkpoint.get("state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
    base_model.load_state_dict(sd, strict=True)
    base_model.eval()

    print("\nPoids classifier :")
    for k, v in sd.items():
        if "classifier" in k:
            print(f"  {k} : {v.shape}  min={v.min():.4f} max={v.max():.4f}")

    inp = load_real_input()
    print(f"Input dtype : {inp.dtype}  shape : {inp.shape}")

    use_relu = diagnose(base_model, inp)

    cam_model = NeuroSightCAMWrapper(base_model, use_relu=use_relu)
    cam_model.eval()

    print(f"\nExport ONNX → {ONNX_PATH}")
    with torch.no_grad():
        torch.onnx.export(
            cam_model,
            inp,
            str(ONNX_PATH),
            export_params=True,
            opset_version=18,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["logits", "cam_heatmaps"],
        )
    print("✅ Export ONNX terminé")

    import onnxruntime as ort
    sess = ort.InferenceSession(str(ONNX_PATH), providers=["CPUExecutionProvider"])
    logits, cam = sess.run(None, {"input": inp.numpy()})
    print(f"\n--- VALIDATION ONNX ---")
    print(f"logits : {logits.shape}  → {logits[0]}")
    print(f"cam    : {cam.shape}  min={cam.min():.6f} max={cam.max():.6f}")
    if cam.max() > 1e-6:
        print("✅ CAM non-nulle → heatmap fonctionnelle")
    else:
        print("❌ CAM nulle → le modèle n'a pas de features discriminantes exploitables")
        print("   Cause probable : modèle peu entraîné ou poids FC trop petits")
        print(f"   FC weight range: {sd['classifier.1.weight'].abs().max():.4f}")

if __name__ == "__main__":
    export()