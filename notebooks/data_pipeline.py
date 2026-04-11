"""
NeuroSight AI - Data Pipeline Module (Engineered Version)
=========================================================

Ce module centralise la logique avancée de préparation des données :
- Reproductibilité (Seeds fixes)
- Imputation MICE (IterativeImputer) pour les données cliniques manquantes
- Zéro Data Leakage (StratifiedGroupKFold par ID Patient)
- Équilibrage robuste des classes rares (WeightedRandomSampler)
- Sortie Pure CNN : (Image, Label) pour compatibilité directe avec EfficientNet.
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

# Activation expérimentale requise par scikit-learn pour IterativeImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.model_selection import StratifiedGroupKFold # <-- CORRECTION MAJEURE ICI

# ==========================================================
# 1. CONFIGURATION & REPRODUCTIBILITÉ
# ==========================================================
SEED = 42

# On force la reproductibilité pour que l'IA ait les mêmes données à chaque exécution
torch.manual_seed(SEED)
np.random.seed(SEED)
fixed_generator = torch.Generator().manual_seed(SEED)

CDR_TO_CLASS = {
    0.0: 0, # NonDemented
    0.5: 1, # VeryMildDemented
    1.0: 2, # MildDemented
    2.0: 3  # ModerateDemented
}
CLASS_NAMES = ['NonDemented', 'VeryMildDemented', 'MildDemented', 'ModerateDemented']

# ==========================================================
# 2. CLASSE DATASET PERSONNALISÉE
# ==========================================================
class OASISDataset(Dataset):
    """Dataset PyTorch qui charge les images 2D et les associe aux étiquettes."""
    def __init__(self, df: pd.DataFrame, transform=None):
        self.df = df
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        img_path = self.df.iloc[idx]['path']
        label = self.df.iloc[idx]['label']
        
        # Conversion RGB pour compatibilité avec EfficientNet
        image = Image.open(img_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
            
        return image, label

# ==========================================================
# 3. FONCTION PRINCIPALE DE PIPELINE (FEATURE ENGINEERED)
# ==========================================================
def prepare_data(csv_path: str, images_dir: str, batch_size: int = 32, val_split: float = 0.2) -> Tuple[DataLoader, DataLoader, List[str]]:
    """
    Prépare les DataLoaders avec Imputation MICE et StratifiedGroupKFold.
    Signature adaptée pour Leila : renvoie (train_loader, val_loader, class_names).
    """
    print("📖 1. Chargement des données cliniques et Imputation MICE...")
    try:
        df_clinical = pd.read_csv(csv_path)
    except Exception:
        df_clinical = pd.read_excel(csv_path)
        
    # --- FEATURE ENGINEERING : Imputation MICE ---
    cols_to_impute = ['Age', 'Educ', 'SES', 'MMSE']
    imputer = IterativeImputer(random_state=SEED, max_iter=10)
    df_clinical[cols_to_impute] = imputer.fit_transform(df_clinical[cols_to_impute])
    print("   ✅ Imputation des valeurs manquantes terminée (MICE).")

    # --- ASSOCIATION IMAGES / CSV ---
    print(f"🔍 2. Scan du dossier d'images : {images_dir}")
    valid_files = []
    for root, _, files in os.walk(images_dir):
        for file in files:
            if file.endswith(('.jpg', '.png')):
                match = re.search(r'(OAS1_\d+)', file)
                if match:
                    patient_id = match.group(1) + "_MR1"
                    if patient_id in df_clinical['ID'].values:
                        cdr_score = df_clinical.loc[df_clinical['ID'] == patient_id, 'CDR'].values[0]
                        if pd.notna(cdr_score) and cdr_score in CDR_TO_CLASS:
                            valid_files.append({
                                'path': os.path.join(root, file),
                                'patient_id': patient_id, # L'ID Patient servira de Groupe
                                'label': CDR_TO_CLASS[cdr_score] # Le Label servira pour la Stratification
                            })
                            
    files_df = pd.DataFrame(valid_files)
    if len(files_df) == 0:
        raise ValueError("❌ Aucune image valide trouvée. Vérifiez les chemins.")
    print(f"   ✅ {len(files_df)} images valides associées avec succès.")

    # --- DATA LEAKAGE PREVENTION & ÉQUILIBRAGE RARE : Stratified Group Split ---
    print(f"\n🛡️ 3. Application du Stratified Group Split (Validation: {val_split*100}%)...")
    
    # On calcule le nombre de splits nécessaires pour atteindre le val_split souhaité (ex: 0.2 -> 5 splits)
    n_splits = max(2, int(1.0 / val_split)) 
    
    # Le StratifiedGroupKFold force les classes rares (comme Moderate) à être réparties dans les deux sets,
    # TOUT en empêchant qu'un patient se retrouve à la fois dans le Train et le Val.
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=SEED)
    
    # On génère la séparation en donnant : X (les données), y (les labels pour stratifier), groups (les patients)
    train_idx, val_idx = next(sgkf.split(X=files_df, y=files_df['label'], groups=files_df['patient_id']))
    
    train_df = files_df.iloc[train_idx].reset_index(drop=True)
    val_df = files_df.iloc[val_idx].reset_index(drop=True)
    
    # Audit visuel interne
    overlap = set(train_df['patient_id']).intersection(set(val_df['patient_id']))
    print(f"   📊 Patients uniques Train : {len(set(train_df['patient_id']))}")
    print(f"   📊 Patients uniques Val   : {len(set(val_df['patient_id']))}")
    print(f"   🚨 Chevauchement (Leakage): {len(overlap)} patients (Doit être 0).")
    
    # Vérification d'assurance sur les classes rares
    val_classes = val_df['label'].unique()
    if 3 not in val_classes:
        print("   ⚠️ ATTENTION : La classe 'Moderate' n'a pas pu être placée dans la validation (trop peu de patients).")
    else:
        print("   ✅ EXCELLENT : La classe 'Moderate' est bien représentée dans l'examen de validation !")

    # --- TRANSFORMATIONS ---
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomRotation(15),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    train_dataset = OASISDataset(train_df, transform=train_transform)
    val_dataset = OASISDataset(val_df, transform=val_transform)

    # --- ÉQUILIBRAGE DES BATCHS ---
    print("\n⚖️ 4. Calcul des poids pour l'équilibrage des classes dans les batchs...")
    class_sample_count = np.bincount(train_df['label'])
    weights = 1. / torch.tensor(class_sample_count, dtype=torch.float)
    samples_weights = weights[train_df['label'].values]
    sampler = WeightedRandomSampler(samples_weights, len(samples_weights))

    # --- DATALOADERS ---
    train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=sampler, num_workers=2, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)
    
    print("🚀 Pipeline prêt ! Les DataLoaders vont générer des lots sécurisés et stratifiés.")
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
    class_counts = {classes[k]: v for k, v in counts.items()}

    plt.figure(figsize=(10, 5))
    plt.bar(class_counts.keys(), class_counts.values(), color=['#4C72B0', '#55A868', '#C44E52', '#8172B2'])
    plt.title("Distribution des Classes dans le Lot / DataLoader")
    plt.ylabel("Nombre d'images")
    plt.xticks(rotation=15)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

def show_sample_batch(dataloader: DataLoader, classes: List[str], num_samples: int = 8) -> None:
    """Récupère un lot, inverse la normalisation mathématique et l'affiche."""
    images, labels = next(iter(dataloader))
    
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    images = images * std + mean
    images = torch.clamp(images, 0, 1)

    fig, axes = plt.subplots(1, min(num_samples, len(images)), figsize=(15, 3))
    if num_samples == 1: axes = [axes]
    
    for i, ax in enumerate(axes):
        img = images[i].numpy().transpose(1, 2, 0)
        ax.imshow(img)
        ax.set_title(classes[labels[i].item()])
        ax.axis("off")
    plt.tight_layout()
    plt.show()