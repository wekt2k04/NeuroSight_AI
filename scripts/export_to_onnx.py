#!/usr/bin/env python3
import torch
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path
from torchvision.models import efficientnet_b0

# Chemins basés sur la structure de ton projet
PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEIGHTS_PATH = PROJECT_ROOT / "models" / "weights" / "best_model.pt"
ONNX_PATH = PROJECT_ROOT / "models" / "weights" / "best_model.onnx"
CLASS_LABELS = ["NonDemented", "VeryMildDemented", "MildDemented", "ModerateDemented"]

def build_model(num_classes: int) -> torch.nn.Module:
    model = efficientnet_b0(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(in_features, num_classes)
    return model

class NeuroSightCAMWrapper(nn.Module):
    """Génère les prédictions ET les cartes d'activation (CAM) pour ONNX."""
    def __init__(self, base_model):
        super().__init__()
        self.base_model = base_model
        self.fc_weights = base_model.classifier[1].weight

    def forward(self, x):
        features = self.base_model.features(x)
        x_pool = self.base_model.avgpool(features)
        x_flat = torch.flatten(x_pool, 1)
        logits = self.base_model.classifier(x_flat) 
        
        # Génération de la Heatmap
        cam = F.conv2d(features, self.fc_weights.unsqueeze(-1).unsqueeze(-1))
        cam = F.relu(cam) 
        return logits, cam

def export():
    print(f"Chargement des poids depuis : {WEIGHTS_PATH}")
    if not WEIGHTS_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable: {WEIGHTS_PATH}")

    base_model = build_model(len(CLASS_LABELS))
    checkpoint = torch.load(WEIGHTS_PATH, map_location="cpu")
    state_dict = checkpoint.get("state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint
    base_model.load_state_dict(state_dict, strict=True)
    
    cam_model = NeuroSightCAMWrapper(base_model)
    cam_model.eval() 

    dummy_input = torch.randn(1, 3, 224, 224)

    print(f"Exportation 'Double Sortie' en cours vers : {ONNX_PATH} ...")
    torch.onnx.export(
        cam_model, 
        dummy_input, 
        ONNX_PATH, 
        export_params=True,
        opset_version=18,          
        do_constant_folding=False, 
        input_names=['input'],     
        output_names=['logits', 'cam_heatmaps']
    )
    print("Exportation réussie ! ✅")

if __name__ == "__main__":
    export()