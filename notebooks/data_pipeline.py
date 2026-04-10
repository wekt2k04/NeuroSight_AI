"""
NeuroSight AI - Data Pipeline Module (Engineered + Fixed Version)
=================================================================

Fixes applied:
- Stratified Group Split (ensures all classes appear in validation set)
- Stronger medical-grade augmentation
- Safer WeightedRandomSampler implementation
- Leakage audit included
- Fully reproducible pipeline
"""

import os
import re
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from typing import Tuple, List
from PIL import Image
import random

from torch.utils.data import DataLoader, WeightedRandomSampler, Dataset
from torchvision import transforms

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

# ==========================================================
# 1. CONFIGURATION & REPRODUCIBILITY
# ==========================================================
SEED = 42

torch.manual_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)

CDR_TO_CLASS = {
    0.0: 0,  # NonDemented
    0.5: 1,  # VeryMildDemented
    1.0: 2,  # MildDemented
    2.0: 3   # ModerateDemented
}

CLASS_NAMES = ['NonDemented', 'VeryMildDemented', 'MildDemented', 'ModerateDemented']


# ==========================================================
# 2. DATASET CLASS
# ==========================================================
class OASISDataset(Dataset):
    def __init__(self, df: pd.DataFrame, transform=None):
        self.df = df
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
# 3. STRATIFIED GROUP SPLIT (CRITICAL FIX)
# ==========================================================
def stratified_group_split(df, val_split=0.2, seed=42):
    """
    Patient-level split that guarantees all classes appear in validation set.
    """
    random.seed(seed)

    # Majority label per patient
    patient_label = df.groupby('patient_id')['label'].agg(lambda x: x.mode()[0]).to_dict()

    # Group patients by class
    class_patients = defaultdict(list)
    for pid, lbl in patient_label.items():
        class_patients[lbl].append(pid)

    val_patients = set()

    for lbl, patients in class_patients.items():
        random.shuffle(patients)
        n_val = max(1, int(len(patients) * val_split))
        val_patients.update(patients[:n_val])

    mask = df['patient_id'].isin(val_patients)

    return (
        df[~mask].reset_index(drop=True),
        df[mask].reset_index(drop=True)
    )


# ==========================================================
# 4. MAIN PIPELINE
# ==========================================================
def prepare_data(csv_path: str, images_dir: str,
                 batch_size: int = 32,
                 val_split: float = 0.2) -> Tuple[DataLoader, DataLoader, List[str]]:

    print("📖 Loading clinical data + MICE imputation...")

    try:
        df_clinical = pd.read_csv(csv_path)
    except Exception:
        df_clinical = pd.read_excel(csv_path)

    # ---------------- MICE IMPUTATION ----------------
    cols_to_impute = ['Age', 'Educ', 'SES', 'MMSE']
    imputer = IterativeImputer(random_state=SEED, max_iter=10)
    df_clinical[cols_to_impute] = imputer.fit_transform(df_clinical[cols_to_impute])
    print("   ✅ MICE imputation done.")

    # ---------------- IMAGE LINKING ----------------
    print(f"🔍 Scanning images: {images_dir}")

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
        raise ValueError("❌ No valid images found.")

    print(f"   ✅ {len(files_df)} images linked.")

    # ---------------- STRATIFIED GROUP SPLIT ----------------
    print("\n🛡️ Stratified Group Split (patient-level + class-balanced)...")

    train_df, val_df = stratified_group_split(
        files_df,
        val_split=val_split,
        seed=SEED
    )

    overlap = set(train_df['patient_id']).intersection(set(val_df['patient_id']))

    print(f"   📊 Train patients: {len(set(train_df['patient_id']))}")
    print(f"   📊 Val patients  : {len(set(val_df['patient_id']))}")
    print(f"   🚨 Leakage check : {len(overlap)} (must be 0)")

    # ---------------- AUGMENTATION ----------------
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomRotation(20),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.1),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
        transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 1.5)),
        transforms.RandomAffine(degrees=0, translate=(0.05, 0.05), scale=(0.95, 1.05)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.15, scale=(0.02, 0.1))
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    train_dataset = OASISDataset(train_df, transform=train_transform)
    val_dataset = OASISDataset(val_df, transform=val_transform)

    # ---------------- SAMPLER ----------------
    print("\n⚖️ Building WeightedRandomSampler...")

    class_sample_count = np.bincount(train_df['label'])
    class_weights = 1. / torch.tensor(class_sample_count, dtype=torch.float32)

    samples_weights = class_weights[train_df['label'].values]

    sampler = WeightedRandomSampler(
        weights=samples_weights,
        num_samples=len(samples_weights),
        replacement=True
    )

    # ---------------- DATALOADERS ----------------
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        sampler=sampler,
        num_workers=2,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=2,
        pin_memory=True
    )

    print("🚀 Pipeline ready.")

    return train_loader, val_loader, CLASS_NAMES


# ==========================================================
# 5. VISUALIZATION UTILITIES
# ==========================================================
def plot_class_distribution(dataloader: DataLoader, classes: List[str]) -> None:
    labels = []

    for _, y in dataloader:
        labels.extend(y.numpy())

    counts = Counter(labels)

    plt.figure(figsize=(10, 5))
    plt.bar(
        [classes[k] for k in counts.keys()],
        counts.values()
    )
    plt.title("Class Distribution")
    plt.xticks(rotation=15)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()


def show_sample_batch(dataloader: DataLoader, classes: List[str], num_samples: int = 8) -> None:
    images, labels = next(iter(dataloader))

    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)

    images = images * std + mean
    images = torch.clamp(images, 0, 1)

    fig, axes = plt.subplots(1, min(num_samples, len(images)), figsize=(15, 3))

    if num_samples == 1:
        axes = [axes]

    for i, ax in enumerate(axes):
        img = images[i].numpy().transpose(1, 2, 0)
        ax.imshow(img)
        ax.set_title(classes[labels[i].item()])
        ax.axis("off")

    plt.tight_layout()
    plt.show()
