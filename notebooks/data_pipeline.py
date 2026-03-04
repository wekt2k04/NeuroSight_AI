"""
NeuroSight AI - Data Pipeline Module
====================================

This module centralizes all dataset preparation logic:
- Data augmentation
- Dataset splitting
- Weighted sampling for class imbalance
- DataLoader orchestration
- Dataset auditing utilities
- Visualization helpers

This file is designed to be IMPORTED.
It does NOT execute anything on import.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from typing import Tuple, Dict, List

import torch
from torch.utils.data import DataLoader, Subset, WeightedRandomSampler
from torchvision import datasets, transforms


# ==========================================================
# TRANSFORMS
# ==========================================================

def get_transforms(img_size: int = 224) -> Tuple[transforms.Compose, transforms.Compose]:
    """
    Create training and validation transforms.

    Parameters
    ----------
    img_size : int
        Target image size.

    Returns
    -------
    train_transform : torchvision.transforms.Compose
        Data augmentation + normalization for training.
    val_transform : torchvision.transforms.Compose
        Only resizing + normalization for validation.
    """

    train_transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    return train_transform, val_transform


# ==========================================================
# CLASS DISTRIBUTION (AUDIT LOGIC)
# ==========================================================

def plot_class_distribution(dataset: datasets.ImageFolder) -> Tuple[Dict[str, int], plt.Figure]:
    """
    Compute and prepare class distribution.

    This function DOES NOT call plt.show().
    It returns the computed distribution and figure so it can be used externally.

    Parameters
    ----------
    dataset : torchvision.datasets.ImageFolder
        Loaded dataset.

    Returns
    -------
    class_counts : dict
        Dictionary mapping class name -> number of samples.
    fig : matplotlib.figure.Figure
        The prepared figure (caller must call plt.show()).
    """

    labels = [sample[1] for sample in dataset.samples]
    counts = Counter(labels)

    class_counts = {
        dataset.classes[class_idx]: count
        for class_idx, count in counts.items()
    }

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(class_counts.keys(), class_counts.values())
    ax.set_title("Class Distribution")
    ax.set_xlabel("Classes")
    ax.set_ylabel("Number of Images")
    plt.xticks(rotation=45)
    plt.tight_layout()

    return class_counts, fig


# ==========================================================
# WEIGHTED SAMPLER (IMBALANCE HANDLING)
# ==========================================================

def create_weighted_sampler(dataset: datasets.ImageFolder,
                            indices: List[int]) -> WeightedRandomSampler:
    """
    Create a WeightedRandomSampler to handle class imbalance.

    Uses np.bincount to compute class frequencies.

    Parameters
    ----------
    dataset : ImageFolder
        Full dataset.
    indices : list
        Indices corresponding to training subset.

    Returns
    -------
    sampler : WeightedRandomSampler
        Sampler that balances minority classes.
    """

    # Extract labels for subset
    subset_labels = [dataset.samples[i][1] for i in indices]

    # Count occurrences per class
    class_counts = np.bincount(subset_labels)

    # Avoid division by zero
    class_weights = 1. / (class_counts + 1e-6)

    # Assign weight to each sample
    sample_weights = [class_weights[label] for label in subset_labels]

    sampler = WeightedRandomSampler(
        weights=torch.DoubleTensor(sample_weights),
        num_samples=len(sample_weights),
        replacement=True
    )

    return sampler


# ==========================================================
# DATALOADER ORCHESTRATION
# ==========================================================

def get_dataloaders(data_dir: str,
                    batch_size: int = 32,
                    test_split: float = 0.2,
                    use_weighted_sampler: bool = True
                    ) -> Tuple[DataLoader, DataLoader, List[str]]:
    """
    Main orchestration function.

    Steps:
    1. Load dataset
    2. Split train/test
    3. Create weighted sampler if needed
    4. Return DataLoaders

    Parameters
    ----------
    data_dir : str
        Path to dataset root directory.
    batch_size : int
        Batch size.
    test_split : float
        Percentage of test data.
    use_weighted_sampler : bool
        Whether to apply imbalance correction.

    Returns
    -------
    train_loader : DataLoader
    test_loader : DataLoader
    classes : list
        List of class names.
    """

    train_transform, test_transform = get_transforms()

    full_dataset = datasets.ImageFolder(
        root=data_dir,
        transform=train_transform
    )

    dataset_size = len(full_dataset)
    indices = list(range(dataset_size))
    split = int(np.floor(test_split * dataset_size))

    np.random.shuffle(indices)

    test_indices = indices[:split]
    train_indices = indices[split:]

    train_subset = Subset(full_dataset, train_indices)

    # Test dataset with different transform
    test_dataset = datasets.ImageFolder(
        root=data_dir,
        transform=test_transform
    )
    test_subset = Subset(test_dataset, test_indices)

    if use_weighted_sampler:
        sampler = create_weighted_sampler(full_dataset, train_indices)
        train_loader = DataLoader(
            train_subset,
            batch_size=batch_size,
            sampler=sampler
        )
    else:
        train_loader = DataLoader(
            train_subset,
            batch_size=batch_size,
            shuffle=True
        )

    test_loader = DataLoader(
        test_subset,
        batch_size=batch_size,
        shuffle=False
    )

    return train_loader, test_loader, full_dataset.classes


# ==========================================================
# VISUALIZATION UTILS
# ==========================================================

def show_sample_batch(dataloader: DataLoader,
                      classes: List[str],
                      num_samples: int = 8) -> plt.Figure:
    """
    Prepare a denormalized batch visualization.

    DOES NOT call plt.show().

    Parameters
    ----------
    dataloader : DataLoader
    classes : list
        Class names.
    num_samples : int
        Number of samples to display (default 8).

    Returns
    -------
    fig : matplotlib.figure.Figure
        Prepared matplotlib figure.
    """

    images, labels = next(iter(dataloader))

    # Denormalize
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)

    images = images * std + mean
    images = torch.clamp(images, 0, 1)

    # Create grid layout (2 rows x 4 cols for 8 images)
    num_samples = min(num_samples, len(images))
    cols = 4
    rows = (num_samples + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(12, 6))
    axes = axes.flatten() if num_samples > 1 else [axes]

    for i in range(num_samples):
        img = images[i].permute(1, 2, 0).numpy()
        axes[i].imshow(img)
        axes[i].set_title(classes[labels[i]])
        axes[i].axis("off")

    # Hide unused subplots
    for i in range(num_samples, len(axes)):
        axes[i].axis("off")

    plt.tight_layout()
    return fig