"""
NeuroSight AI - Data Pipeline Module (Engineered Version)
=========================================================

Ce module centralise la logique avancée de préparation des données :
- Reproductibilité (Seeds fixes)
- Séparation stricte des augmentations (Train vs Validation)
- Interception dynamique (TransformedSubset)
- Équilibrage robuste (WeightedRandomSampler avec np.bincount)
- Optimisation GPU (pin_memory, num_workers)
- Fonctions d'audit et de visualisation visuelle
"""

import os
import torch
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from typing import Tuple, Dict, List

from torch.utils.data import DataLoader, random_split, WeightedRandomSampler, Subset, Dataset
from torchvision import datasets, transforms

# ==========================================================
# 1. CONFIGURATION & REPRODUCTIBILITÉ
# ==========================================================
SEED = 42

# On force la reproductibilité pour que l'IA ait les mêmes données à chaque exécution
torch.manual_seed(SEED)
np.random.seed(SEED)
fixed_generator = torch.Generator().manual_seed(SEED)


# ==========================================================
# 2. TRANSFORMS (LES DEUX CUISINES)
# ==========================================================
def get_transforms(img_size: int = 224) -> Tuple[transforms.Compose, transforms.Compose]:
    """
    Crée les pipelines de transformation pour l'entraînement et la validation.
    """
    #---- changes applied in order to improve the performance of the model
    # Pipeline d'entraînement : On "muscle" l'IA (Augmentation de données)
    train_transform = transforms.Compose([
        # transforms.Resize((img_size, img_size)),
        # transforms.RandomHorizontalFlip(p=0.5),      # Symétrie
        # transforms.RandomRotation(degrees=15),       # Légères rotations
        # transforms.ColorJitter(brightness=0.1, contrast=0.1), # Variations scanner
        # transforms.ToTensor(),
        # # Normalisation ImageNet requise pour EfficientNet
        # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        transforms.RandomResizedCrop(224, scale=(0.85, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),   # OK for brain symmetry
        transforms.RandomRotation(10),            # reduced (safer)
        transforms.RandomAffine(
            degrees=0,
            translate=(0.02, 0.02),               # small shifts only
            scale=(0.98, 1.02)
        ),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.1, scale=(0.02, 0.05)),  # reduced

    ])

    # Pipeline de validation : Stérile et clinique
    val_transform = transforms.Compose([
        # transforms.Resize((img_size, img_size)),
        # transforms.ToTensor(),
        # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225]),

    ])

    return train_transform, val_transform


# ==========================================================
# 3. L'INTERCEPTEUR (ÉVITER LA FUITE DE DONNÉES)
# ==========================================================
class TransformedSubset(Dataset):
    """
    Classe wrapper pour appliquer dynamiquement une transformation
    spécifique (train ou val) après avoir coupé le dataset.
    """
    def __init__(self, subset, transform=None):
        self.subset = subset
        self.transform = transform
        
    def __getitem__(self, index):
        x, y = self.subset[index]
        if self.transform:
            x = self.transform(x)
        return x, y
        
    def __len__(self):
        return len(self.subset)


# ==========================================================
# 4. ORCHESTRATION (DATALOADERS & SAMPLER)
# ==========================================================
def get_dataloaders(data_dir: str, 
                    batch_size: int = 32, 
                    val_split: float = 0.2) -> Tuple[DataLoader, DataLoader, List[str]]:
    """
    Fonction principale pour charger, équilibrer et optimiser les données.
    """
    
    # 1. Chargement brut (SANS transformation pour le moment)
    full_dataset = datasets.ImageFolder(root=data_dir)
    classes = full_dataset.classes
    
    # 2. Découpage (Split) avec graine fixe
    train_size = int((1.0 - val_split) * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_indices, val_indices = random_split(
        full_dataset, [train_size, val_size], generator=fixed_generator
    )

    # 3. Équilibrage des classes (WeightedRandomSampler)
    # Extraction sécurisée des étiquettes (targets) du sous-ensemble d'entraînement
    train_targets = np.array([full_dataset.targets[i] for i in train_indices.indices])
    
    # Comptage via numpy (rapide et robuste)
    class_sample_count = np.bincount(train_targets, minlength=len(classes))
    
    # Calcul des poids (1 / fréquence) avec protection division par zéro
    weight = np.divide(1., class_sample_count, 
                       out=np.zeros_like(class_sample_count, dtype=float), 
                       where=class_sample_count != 0)
    
    # Attribution du poids à chaque image d'entraînement
    samples_weight = torch.from_numpy(np.array([weight[t] for t in train_targets]))
    
    # Le Croupier (Sampler)
    sampler = WeightedRandomSampler(
        weights=samples_weight, 
        num_samples=len(samples_weight), 
        replacement=True
    )

    # 4. Application des transformations via l'Intercepteur
    train_transform, val_transform = get_transforms()
    train_data = TransformedSubset(train_indices, transform=train_transform)
    val_data = TransformedSubset(val_indices, transform=val_transform)

    # 5. Création des usines (DataLoaders) optimisées
    train_loader = DataLoader(
        train_data, 
        batch_size=batch_size, 
        sampler=sampler,        # Utilise le sampler (donc shuffle=False implicite)
        num_workers=2,          # Parallélisation CPU
        pin_memory=True,        # Voie express vers le GPU
        drop_last=True          # Stabilité mathématique
    )

    test_loader = DataLoader(
        val_data, 
        batch_size=batch_size, 
        shuffle=False,          # Pas de mélange pour la validation
        num_workers=2,
        pin_memory=True
    )

    return train_loader, test_loader, classes


# ==========================================================
# 5. FONCTIONS D'AUDIT ET VISUALISATION (Leila & Wilfried)
# ==========================================================
def plot_class_distribution(dataset: Dataset) -> None:
    """
    Affiche la distribution brute des classes pour l'audit.
    """
    # Si c'est un TransformedSubset, on doit remonter à l'ImageFolder d'origine
    if isinstance(dataset, TransformedSubset):
        real_dataset = dataset.subset.dataset
        indices = dataset.subset.indices
        labels = [real_dataset.targets[i] for i in indices]
        classes = real_dataset.classes
    else:
        labels = dataset.targets
        classes = dataset.classes

    counts = Counter(labels)
    class_counts = {classes[idx]: count for idx, count in counts.items()}

    plt.figure(figsize=(10, 5))
    plt.bar(class_counts.keys(), class_counts.values(), color=['#4C72B0', '#55A868', '#C44E52', '#8172B2'])
    plt.title("Distribution des Classes dans le Dataset")
    plt.ylabel("Nombre d'images")
    plt.xticks(rotation=15)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()


def show_sample_batch(dataloader: DataLoader, classes: List[str], num_samples: int = 8) -> None:
    """
    Récupère un lot, inverse la normalisation mathématique et l'affiche.
    """
    images, labels = next(iter(dataloader))

    # Dénormalisation pour affichage humain
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)

    images = images * std + mean
    images = torch.clamp(images, 0, 1) # Assure que les pixels restent entre 0 et 1

    num_samples = min(num_samples, len(images))
    cols = 4
    rows = (num_samples + cols - 1) // cols

    plt.figure(figsize=(15, 3 * rows))
    for i in range(num_samples):
        plt.subplot(rows, cols, i+1)
        # Transformation CHW -> HWC pour l'écran
        img = images[i].permute(1, 2, 0).numpy()
        plt.imshow(img)
        plt.title(classes[labels[i]])
        plt.axis("off")

    plt.tight_layout()
    plt.show()
