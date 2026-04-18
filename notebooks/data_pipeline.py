"""
NeuroSight AI - Data Pipeline Module (v3 - Corrected)
======================================================

Corrections appliquées (v3) :
- [BUG FIX] Split en 3 étapes : patients ModerateDemented forcés dans le val set
            pour garantir leur présence même avec très peu de patients uniques.
- [AMÉLIORATION] Augmentation data enrichie pour IRM cérébrales (RandomErasing,
            RandomAffine, RandomVerticalFlip).
- Conservation de toutes les garanties v2 : MICE, zéro leakage, WeightedRandomSampler.
"""

import os
import re
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from typing import Tuple, List
from PIL import Image

from torch.utils.data import DataLoader, WeightedRandomSampler, Dataset
from torchvision import transforms

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.model_selection import GroupShuffleSplit

# ==========================================================
# 1. CONFIGURATION & REPRODUCTIBILITÉ
# ==========================================================
SEED = 42

torch.manual_seed(SEED)
np.random.seed(SEED)
fixed_generator = torch.Generator().manual_seed(SEED)

CDR_TO_CLASS = {
    0.0: 0,  # NonDemented
    0.5: 1,  # VeryMildDemented
    1.0: 2,  # MildDemented
    2.0: 3   # ModerateDemented
}
CLASS_NAMES = ['NonDemented', 'VeryMildDemented', 'MildDemented', 'ModerateDemented']


# ==========================================================
# 2. CLASSE DATASET PERSONNALISÉE
# ==========================================================
class OASISDataset(Dataset):
    """Dataset PyTorch qui charge les images 2D et les associe aux étiquettes."""
    def __init__(self, df: pd.DataFrame, transform=None):
        self.df = df.reset_index(drop=True)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        img_path = self.df.iloc[idx]['path']
        label = self.df.iloc[idx]['label']
        image = Image.open(img_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return image, label


# ==========================================================
# 3. FONCTION PRINCIPALE DE PIPELINE (v3 - CORRECTED)
# ==========================================================
def prepare_data(
    csv_path: str,
    images_dir: str,
    batch_size: int = 32,
    val_split: float = 0.2
) -> Tuple[DataLoader, DataLoader, List[str]]:
    """
    Prépare les DataLoaders avec :
    - Imputation MICE
    - Split 3 étapes (garantie Moderate dans val)
    - WeightedRandomSampler (équilibrage train)
    - Augmentation IRM enrichie
    Renvoie : (train_loader, val_loader, class_names)
    """

    # ----------------------------------------------------------
    # ÉTAPE 1 : Chargement CSV + Imputation MICE
    # ----------------------------------------------------------
    print("📖 1. Chargement des données cliniques et Imputation MICE...")
    try:
        df_clinical = pd.read_csv(csv_path)
    except Exception:
        df_clinical = pd.read_excel(csv_path)

    cols_to_impute = ['Age', 'Educ', 'SES', 'MMSE']
    imputer = IterativeImputer(random_state=SEED, max_iter=10)
    df_clinical[cols_to_impute] = imputer.fit_transform(df_clinical[cols_to_impute])
    print("   ✅ Imputation MICE terminée.")

    # ----------------------------------------------------------
    # ÉTAPE 2 : Association images ↔ CSV
    # ----------------------------------------------------------
    print(f"🔍 2. Scan du dossier d'images : {images_dir}")
    valid_files = []
    for root, _, files in os.walk(images_dir):
        for file in files:
            if file.endswith(('.jpg', '.png')):
                match = re.search(r'(OAS1_\d+)', file)
                if match:
                    patient_id = match.group(1) + "_MR1"
                    if patient_id in df_clinical['ID'].values:
                        cdr_score = df_clinical.loc[
                            df_clinical['ID'] == patient_id, 'CDR'
                        ].values[0]
                        if pd.notna(cdr_score) and cdr_score in CDR_TO_CLASS:
                            valid_files.append({
                                'path': os.path.join(root, file),
                                'patient_id': patient_id,
                                'label': CDR_TO_CLASS[cdr_score]
                            })

    files_df = pd.DataFrame(valid_files)
    if len(files_df) == 0:
        raise ValueError("❌ Aucune image valide trouvée. Vérifiez les chemins.")
    print(f"   ✅ {len(files_df)} images valides associées avec succès.")

    # Audit de distribution brute
    label_counts = files_df['label'].value_counts().sort_index()
    for lbl, cnt in label_counts.items():
        print(f"   📊 Classe {CLASS_NAMES[lbl]:>20s} : {cnt:>6d} images")

    # ----------------------------------------------------------
    # ÉTAPE 3 : SPLIT EN 3 PHASES — Zéro Leakage + Moderate Garanti
    # ----------------------------------------------------------
    print(f"\n🛡️  3. Application du Split 3 étapes (Validation: {val_split*100:.0f}%)...")

    # Phase A : Isoler tous les patients ModerateDemented (CDR=2.0)
    # Leur nombre est trop faible pour StratifiedGroupKFold → on les force dans val
    moderate_patient_ids = set(files_df[files_df['label'] == 3]['patient_id'].unique())
    mask_moderate = files_df['patient_id'].isin(moderate_patient_ids)
    moderate_df = files_df[mask_moderate].copy()
    other_df    = files_df[~mask_moderate].copy()

    n_moderate_patients = len(moderate_patient_ids)
    n_moderate_images   = len(moderate_df)
    print(f"   🔴 ModerateDemented : {n_moderate_patients} patient(s) unique(s) | "
          f"{n_moderate_images} images → forcé(s) dans VAL")

    # Phase B : Splitter les 3 autres classes avec GroupShuffleSplit (zéro leakage garanti)
    gss = GroupShuffleSplit(n_splits=1, test_size=val_split, random_state=SEED)
    train_idx, val_idx = next(
        gss.split(X=other_df, y=other_df['label'], groups=other_df['patient_id'])
    )
    train_df = other_df.iloc[train_idx].copy()
    val_base_df = other_df.iloc[val_idx].copy()

    # Phase C : Fusionner les patients Moderate dans le val set
    val_df = pd.concat([val_base_df, moderate_df], ignore_index=True)

    # ----------------------------------------------------------
    # AUDIT DE QUALITÉ
    # ----------------------------------------------------------
    overlap = set(train_df['patient_id']).intersection(set(val_df['patient_id']))
    print(f"   📊 Patients uniques Train : {len(set(train_df['patient_id']))}")
    print(f"   📊 Patients uniques Val   : {len(set(val_df['patient_id']))}")
    print(f"   🚨 Chevauchement (Leakage): {len(overlap)} patient(s) — Doit être 0.")

    val_classes = val_df['label'].unique()
    if 3 in val_classes:
        n_val_moderate = len(val_df[val_df['label'] == 3])
        print(f"   ✅ ModerateDemented présent dans VAL : {n_val_moderate} images.")
    else:
        print("   ⚠️  ATTENTION : ModerateDemented toujours absent du val (aucun patient CDR=2.0 dans le CSV).")

    # ----------------------------------------------------------
    # ÉTAPE 4 : TRANSFORMATIONS (augmentation enrichie pour IRM)
    # ----------------------------------------------------------
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomRotation(20),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.RandomAffine(degrees=0, translate=(0.05, 0.05)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.25, scale=(0.02, 0.1)),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    train_dataset = OASISDataset(train_df, transform=train_transform)
    val_dataset   = OASISDataset(val_df,   transform=val_transform)

    # ----------------------------------------------------------
    # ÉTAPE 5 : ÉQUILIBRAGE DES BATCHS (WeightedRandomSampler)
    # ----------------------------------------------------------
    print("\n⚖️  4. Calcul des poids de rééquilibrage pour le train...")
    n_classes = len(CLASS_NAMES)
    class_sample_count = np.bincount(train_df['label'].values, minlength=n_classes)
    # Sécurité : éviter division par zéro si une classe est absente du train
    class_sample_count = np.where(class_sample_count == 0, 1, class_sample_count)
    weights = 1.0 / torch.tensor(class_sample_count, dtype=torch.float)
    samples_weights = weights[train_df['label'].values]
    sampler = WeightedRandomSampler(samples_weights, len(samples_weights), replacement=True)

    cores = os.cpu_count()

    # ----------------------------------------------------------
    # ÉTAPE 6 : DATALOADERS
    # ----------------------------------------------------------
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, sampler=sampler,
        num_workers=cores, pin_memory=True, persistent_workers=True
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False,
        num_workers=cores, pin_memory=True, persistent_workers=True
    )

    print("🚀 Pipeline prêt ! DataLoaders générés avec zéro leakage et ModerateDemented garanti dans VAL.")
    return train_loader, val_loader, CLASS_NAMES


# ==========================================================
# 4. FONCTIONS UTILITAIRES (EDA & AUDIT)
# ==========================================================
def plot_class_distribution(dataloader: DataLoader, classes: List[str]) -> None:
    """Affiche la distribution des classes dans un DataLoader."""
    all_labels = []
    for _, labels in dataloader:
        all_labels.extend(labels.numpy())

    counts = Counter(all_labels)
    class_counts = {classes[k]: counts.get(k, 0) for k in range(len(classes))}

    plt.figure(figsize=(10, 5))
    colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B2']
    plt.bar(class_counts.keys(), class_counts.values(), color=colors)
    plt.title("Distribution des Classes dans le DataLoader")
    plt.ylabel("Nombre d'images")
    plt.xticks(rotation=15)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


def show_sample_batch(dataloader: DataLoader, classes: List[str], num_samples: int = 8) -> None:
    """Récupère un lot, inverse la normalisation et l'affiche."""
    images, labels = next(iter(dataloader))

    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std  = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    images = torch.clamp(images * std + mean, 0, 1)

    fig, axes = plt.subplots(1, min(num_samples, len(images)), figsize=(15, 3))
    if num_samples == 1:
        axes = [axes]
    for i, ax in enumerate(axes):
        img = images[i].numpy().transpose(1, 2, 0)
        ax.imshow(img)
        ax.set_title(classes[labels[i].item()], fontsize=9)
        ax.axis("off")
    plt.tight_layout()
    plt.show()
