"""
NeuroSight AI - Data Pipeline Module (Fixed Two-Stage Sampling with Balanced Test Set)
=====================================================================================

Fixes applied:
- Three-way stratified split (train/val/test) with class balancing
- Guarantees all classes appear in test set
- Handles small patient counts gracefully
- Two-stage sampling: oversample training set, keep val/test realistic
"""

import os
import re
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from typing import Tuple, List, Optional
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
# 3. STRATIFIED GROUP SPLIT (FIXED - GUARANTEES ALL CLASSES IN TEST)
# ==========================================================
def stratified_group_split(df, val_split=0.15, test_split=0.15, seed=42):
    """
    Patient-level split with STRICT class balancing.
    Ensures every class appears in train, val, AND test sets.
    """
    random.seed(seed)
    
    # Get majority label per patient
    patient_label = df.groupby('patient_id')['label'].agg(lambda x: x.mode()[0]).to_dict()
    
    # Group patients by class
    class_patients = defaultdict(list)
    for pid, lbl in patient_label.items():
        class_patients[lbl].append(pid)
    
    train_patients = set()
    val_patients = set()
    test_patients = set()
    
    for lbl, patients in class_patients.items():
        random.shuffle(patients)
        n_total = len(patients)
        
        # If only 1 patient in class, put in training (not val/test)
        if n_total == 1:
            train_patients.update(patients)
            continue
        
        # If only 2 patients, put 1 in train, 1 in val
        if n_total == 2:
            train_patients.update([patients[0]])
            val_patients.update([patients[1]])
            continue
        
        # If only 3 patients, put 1 in train, 1 in val, 1 in test
        if n_total == 3:
            train_patients.update([patients[0]])
            val_patients.update([patients[1]])
            test_patients.update([patients[2]])
            continue
        
        # Normal case: enough patients for proper split
        n_val = max(1, int(n_total * val_split))
        n_test = max(1, int(n_total * test_split))
        n_train = n_total - n_val - n_test
        
        # Ensure training has at least 1 sample
        if n_train < 1:
            # Take 1 from val if possible
            if n_val > 1:
                n_val -= 1
                n_train = 1
            elif n_test > 1:
                n_test -= 1
                n_train = 1
        
        # Ensure test has at least 1 sample for rare classes
        if n_test < 1 and n_total > 2:
            n_test = 1
            n_train = n_total - n_val - n_test
            if n_train < 0:
                n_train = 0
        
        val_patients.update(patients[:n_val])
        test_patients.update(patients[n_val:n_val + n_test])
        train_patients.update(patients[n_val + n_test:])
    
    train_mask = df['patient_id'].isin(train_patients)
    val_mask = df['patient_id'].isin(val_patients)
    test_mask = df['patient_id'].isin(test_patients)
    
    return (
        df[train_mask].reset_index(drop=True),
        df[val_mask].reset_index(drop=True),
        df[test_mask].reset_index(drop=True)
    )


# ==========================================================
# 4. ENSURE TEST SET HAS ALL CLASSES
# ==========================================================
def ensure_test_has_all_classes(train_df, val_df, test_df, target_test_per_class=50):
    """
    Ensures test set has at least target_test_per_class samples per class.
    Borrows from train or val if needed.
    """
    original_test_counts = test_df['label'].value_counts().sort_index()
    print(f"\n   Original test counts: {dict(original_test_counts)}")
    
    for class_label in range(4):
        current_test_count = len(test_df[test_df['label'] == class_label])
        
        if current_test_count < target_test_per_class:
            # Need more samples in test set
            needed = target_test_per_class - current_test_count
            
            # Borrow from training set first
            train_class_df = train_df[train_df['label'] == class_label]
            if len(train_class_df) >= needed:
                moved = train_class_df.sample(n=needed, random_state=SEED)
                test_df = pd.concat([test_df, moved], ignore_index=True)
                train_df = train_df.drop(moved.index).reset_index(drop=True)
                print(f"   Moved {needed} samples of class {class_label} from train to test")
            else:
                # Borrow from validation set
                val_class_df = val_df[val_df['label'] == class_label]
                if len(val_class_df) >= needed:
                    moved = val_class_df.sample(n=needed, random_state=SEED)
                    test_df = pd.concat([test_df, moved], ignore_index=True)
                    val_df = val_df.drop(moved.index).reset_index(drop=True)
                    print(f"   Moved {needed} samples of class {class_label} from val to test")
                else:
                    # Take what we can from both
                    moved_train = train_class_df.sample(n=min(len(train_class_df), needed), random_state=SEED)
                    test_df = pd.concat([test_df, moved_train], ignore_index=True)
                    train_df = train_df.drop(moved_train.index).reset_index(drop=True)
                    needed -= len(moved_train)
                    
                    if needed > 0:
                        moved_val = val_class_df.sample(n=min(len(val_class_df), needed), random_state=SEED)
                        test_df = pd.concat([test_df, moved_val], ignore_index=True)
                        val_df = val_df.drop(moved_val.index).reset_index(drop=True)
                        print(f"   Moved {len(moved_train) + len(moved_val)} samples of class {class_label} to test")
    
    new_test_counts = test_df['label'].value_counts().sort_index()
    print(f"   New test counts: {dict(new_test_counts)}")
    
    return train_df, val_df, test_df


# ==========================================================
# 5. MAIN PIPELINE
# ==========================================================
def prepare_data(csv_path: str, images_dir: str,
                 batch_size: int = 32,
                 val_split: float = 0.15,
                 test_split: float = 0.15,
                 target_train_per_class: int = 5000,
                 target_test_per_class: int = 50) -> Tuple[DataLoader, DataLoader, DataLoader, List[str]]:
    """
    Returns train_loader, val_loader, test_loader, class_names
    
    Args:
        csv_path: Path to clinical data CSV/Excel file
        images_dir: Path to directory containing images
        batch_size: Batch size for DataLoaders
        val_split: Fraction of patients to use for validation
        test_split: Fraction of patients to use for test
        target_train_per_class: Target samples per class in training (after balancing)
        target_test_per_class: Minimum samples per class in test set
    """
    print("📖 Loading clinical data + MICE imputation...")

    try:
        df_clinical = pd.read_csv(csv_path)
    except Exception:
        df_clinical = pd.read_excel(csv_path)

    # MICE Imputation
    cols_to_impute = ['Age', 'Educ', 'SES', 'MMSE']
    imputer = IterativeImputer(random_state=SEED, max_iter=10)
    df_clinical[cols_to_impute] = imputer.fit_transform(df_clinical[cols_to_impute])
    print("   ✅ MICE imputation done.")

    # Image Linking
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

    # STRATIFIED 3-WAY SPLIT (train/val/test)
    print("\n🛡️ Stratified Group Split (patient-level, class-balanced)...")
    train_df, val_df, test_df = stratified_group_split(
        files_df,
        val_split=val_split,
        test_split=test_split,
        seed=SEED
    )
    
    # Print split statistics
    print(f"\n📊 INITIAL SPLIT STATISTICS:")
    for name, df in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
        counts = df['label'].value_counts().sort_index()
        print(f"   {name}: {dict(counts)}")
    
    # Ensure test set has all classes
    print(f"\n🔄 Ensuring test set has all classes...")
    train_df, val_df, test_df = ensure_test_has_all_classes(
        train_df, val_df, test_df, target_test_per_class=target_test_per_class
    )
    
    # ========== STAGE 1: TRAIN SET BALANCING (OVERSAMPLING) ==========
    print(f"\n⚖️ STAGE 1: Balancing TRAIN set to {target_train_per_class} samples per class...")
    
    balanced_train_dfs = []
    for class_label in range(4):
        class_df = train_df[train_df['label'] == class_label]
        n_current = len(class_df)
        
        if n_current == 0:
            print(f"   ⚠️ WARNING: Class {class_label} has 0 samples in training!")
            # This shouldn't happen with proper splitting
            continue
        
        if n_current < target_train_per_class:
            # Oversample with replacement
            indices = np.random.choice(class_df.index, size=target_train_per_class, replace=True)
            balanced_train_dfs.append(class_df.loc[indices])
            print(f"   Class {class_label}: oversampled from {n_current} to {target_train_per_class}")
        elif n_current > target_train_per_class:
            # Undersample
            balanced_train_dfs.append(class_df.sample(n=target_train_per_class, random_state=SEED))
            print(f"   Class {class_label}: undersampled from {n_current} to {target_train_per_class}")
        else:
            balanced_train_dfs.append(class_df)
            print(f"   Class {class_label}: already at {n_current}")
    
    train_df_balanced = pd.concat(balanced_train_dfs, ignore_index=True)
    print(f"\n   ✅ Train set balanced: {dict(train_df_balanced['label'].value_counts().sort_index())}")
    
    # ========== STAGE 2: Keep VAL and TEST as is ==========
    # (no oversampling for realistic evaluation)
    for name, df in [("Val", val_df), ("Test", test_df)]:
        counts = df['label'].value_counts().sort_index()
        print(f"   {name} set (natural distribution): {dict(counts)}")
    
    # ========== AUGMENTATION ==========
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(260, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
        transforms.RandomAdjustSharpness(sharpness_factor=2.0, p=0.5),
        transforms.RandomSolarize(threshold=190, p=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.2, scale=(0.02, 0.15))
    ])

    val_transform = transforms.Compose([
        transforms.Resize((260, 260)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    train_dataset = OASISDataset(train_df_balanced, transform=train_transform)
    val_dataset = OASISDataset(val_df, transform=val_transform)
    test_dataset = OASISDataset(test_df, transform=val_transform)

    # ========== SAMPLER (for training only) ==========
    class_sample_count = np.bincount(train_df_balanced['label'])
    class_weights = 1. / torch.tensor(class_sample_count, dtype=torch.float32)
    samples_weights = class_weights[train_df_balanced['label'].values]
    
    sampler = WeightedRandomSampler(
        weights=samples_weights,
        num_samples=len(samples_weights),
        replacement=True
    )

    # DataLoaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        sampler=sampler,
        num_workers=4,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )

    print("\n🚀 Pipeline ready.")
    print(f"   Train batches: {len(train_loader)}")
    print(f"   Val batches: {len(val_loader)}")
    print(f"   Test batches: {len(test_loader)}")
    
    return train_loader, val_loader, test_loader, CLASS_NAMES


# ==========================================================
# 6. VISUALIZATION UTILITIES
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
