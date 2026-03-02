# dataset.py
"""
PyTorch Dataset implementation for medical image classification.

Bridges preprocessing, augmentation, and PyTorch data loading.
Accepts CSV files with image paths and labels, applies preprocessing,
and returns image and label tensors ready for model consumption.
"""

import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Callable, Union, Dict
import logging

# Import project modules
import config as cfg
from preprocessing import PreprocessingPipeline, default_pipeline, imagenet_pipeline
from augmentation import AugmentationPipeline, WeakAugmentation, StrongAugmentation

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalImageDataset(Dataset):
    """
    PyTorch Dataset for medical image classification.
    
    Handles:
    - Loading image paths from CSV
    - Applying preprocessing (resize, normalization)
    - Applying augmentation during training
    - Converting to tensors
    """
    
    def __init__(
        self,
        csv_file: Union[str, Path],
        root_dir: Optional[Union[str, Path]] = None,
        transform: str = 'train',  # 'train', 'val', 'test'
        preprocessing_pipeline: Optional[PreprocessingPipeline] = None,
        augmentation_pipeline: Optional[AugmentationPipeline] = None,
        img_size: int = cfg.IMG_SIZE,
        use_imagenet_stats: bool = False,
        return_path: bool = False,
        class_mapping: Dict[str, int] = cfg.CLASS_MAPPING,
        debug_mode: bool = cfg.DEBUG_MODE,
        debug_samples: int = cfg.DEBUG_SAMPLE_SIZE
    ):
        """
        Initialize the dataset.
        
        Args:
            csv_file: Path to CSV file with image paths and labels
            root_dir: Root directory to prepend to image paths (if paths are relative)
            transform: Type of transform to apply ('train', 'val', 'test')
            preprocessing_pipeline: Custom preprocessing pipeline (uses default if None)
            augmentation_pipeline: Custom augmentation pipeline (creates based on transform if None)
            img_size: Target image size (used if pipelines not provided)
            use_imagenet_stats: Use ImageNet stats for normalization
            return_path: Whether to return image path (for debugging)
            class_mapping: Dictionary mapping class names to integer labels
            debug_mode: If True, limit dataset size for debugging
            debug_samples: Number of samples to use in debug mode
        """
        self.csv_file = Path(csv_file)
        self.root_dir = Path(root_dir) if root_dir else None
        self.transform_type = transform
        self.return_path = return_path
        self.class_mapping = class_mapping
        
        # Load and validate CSV
        self.data = self._load_csv()
        
        # Apply debug mode if enabled
        if debug_mode:
            self.data = self.data.head(debug_samples)
            logger.info(f"DEBUG MODE: Using {len(self.data)} samples")
        
        # Setup preprocessing pipeline
        if preprocessing_pipeline is None:
            if use_imagenet_stats:
                self.preprocessing = imagenet_pipeline
            else:
                self.preprocessing = default_pipeline
        else:
            self.preprocessing = preprocessing_pipeline
        
        # Setup augmentation pipeline (only for training)
        self.augmentation = None
        if transform == 'train':
            if augmentation_pipeline is None:
                # Create augmentation based on config
                use_strong = cfg.USE_STRONG_AUGMENTATION
                self.augmentation = AugmentationPipeline(
                    img_size=img_size,
                    use_strong=use_strong
                )
            else:
                self.augmentation = augmentation_pipeline
            
            logger.info(f"Dataset initialized in TRAIN mode with augmentation")
        else:
            logger.info(f"Dataset initialized in {transform.upper()} mode (no augmentation)")
        
        # Log dataset info
        self._log_dataset_info()
    
    def _load_csv(self) -> pd.DataFrame:
        """
        Load and validate CSV file.
        
        Returns:
            DataFrame with image paths and labels
        
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If required columns are missing
        """
        if not self.csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_file}")
        
        df = pd.read_csv(self.csv_file)
        
        # Check required columns
        required_cols = ['filename', 'label', 'class_name']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"CSV missing required columns: {missing_cols}")
        
        # Ensure label column is integer type
        df['label'] = df['label'].astype(int)
        
        return df
    
    def _log_dataset_info(self):
        """Log dataset statistics."""
        logger.info(f"Dataset loaded from: {self.csv_file.name}")
        logger.info(f"Total samples: {len(self.data)}")
        logger.info(f"Transform mode: {self.transform_type}")
        
        # Log class distribution
        class_counts = self.data['class_name'].value_counts()
        for class_name, count in class_counts.items():
            logger.info(f"  {class_name}: {count} samples")
    
    def __len__(self) -> int:
        """Return total number of samples."""
        return len(self.data)
    
    def _get_image_path(self, idx: int) -> Path:
        """
        Get full image path for given index.
        
        Args:
            idx: Sample index
            
        Returns:
            Full path to image file
        """
        rel_path = self.data.iloc[idx]['filename']
        
        if self.root_dir:
            return self.root_dir / rel_path
        else:
            return cfg.PROJECT_ROOT / rel_path
    
    def __getitem__(self, idx: int) -> Union[
        Tuple[torch.Tensor, torch.Tensor],
        Tuple[torch.Tensor, torch.Tensor, str]
    ]:
        """
        Get item by index.
        
        Args:
            idx: Sample index
            
        Returns:
            If return_path=False: (image_tensor, label_tensor)
            If return_path=True: (image_tensor, label_tensor, image_path)
        """
        # Get image path and label
        img_path = self._get_image_path(idx)
        label = self.data.iloc[idx]['label']
        class_name = self.data.iloc[idx]['class_name']
        
        try:
            # Step 1: Apply preprocessing (without normalization to preserve uint8 for augmentation)
            image = self.preprocessing(img_path, skip_normalization=(self.augmentation is not None))
            
            # Step 2: Apply augmentation if in training mode (works on uint8)
            if self.augmentation is not None:
                image = self.augmentation(image, class_name=class_name)
                # Step 3: Normalize after augmentation
                image = self.preprocessing.normalize(image)
            
            # Convert to tensor
            # Handle different image formats
            if len(image.shape) == 3:
                # RGB image: (H, W, C) -> (C, H, W)
                image_tensor = torch.from_numpy(image).permute(2, 0, 1).float()
            elif len(image.shape) == 2:
                # Grayscale: (H, W) -> (1, H, W)
                image_tensor = torch.from_numpy(image).unsqueeze(0).float()
            else:
                raise ValueError(f"Unexpected image shape: {image.shape}")
            
            # Convert label to tensor
            label_tensor = torch.tensor(label, dtype=torch.long)
            
            # Return with or without path
            if self.return_path:
                return image_tensor, label_tensor, str(img_path)
            else:
                return image_tensor, label_tensor
                
        except Exception as e:
            logger.error(f"Error processing {img_path}: {e}")
            # Return a zero tensor and the label as fallback
            # This should ideally not happen with proper data validation
            dummy_image = torch.zeros((3, cfg.IMG_SIZE, cfg.IMG_SIZE))
            label_tensor = torch.tensor(label, dtype=torch.long)
            
            if self.return_path:
                return dummy_image, label_tensor, str(img_path)
            else:
                return dummy_image, label_tensor


class TrainDataset(MedicalImageDataset):
    """Convenience class for training dataset with augmentation."""
    
    def __init__(self, csv_file: Union[str, Path], **kwargs):
        """Initialize training dataset."""
        kwargs['transform'] = 'train'
        super().__init__(csv_file, **kwargs)


class ValDataset(MedicalImageDataset):
    """Convenience class for validation dataset without augmentation."""
    
    def __init__(self, csv_file: Union[str, Path], **kwargs):
        """Initialize validation dataset."""
        kwargs['transform'] = 'val'
        super().__init__(csv_file, **kwargs)


class TestDataset(MedicalImageDataset):
    """Convenience class for test dataset without augmentation."""
    
    def __init__(self, csv_file: Union[str, Path], **kwargs):
        """Initialize test dataset."""
        kwargs['transform'] = 'test'
        super().__init__(csv_file, **kwargs)


def create_datasets(
    train_csv: Union[str, Path] = cfg.PROCESSED_DATA_DIR / 'train_split.csv',
    val_csv: Union[str, Path] = cfg.PROCESSED_DATA_DIR / 'val_split.csv',
    test_csv: Union[str, Path] = cfg.PROCESSED_DATA_DIR / 'test_split.csv',
    root_dir: Optional[Union[str, Path]] = cfg.PROJECT_ROOT,
    img_size: int = cfg.IMG_SIZE,
    use_imagenet_stats: bool = False,
    return_path: bool = False,
    debug_mode: bool = cfg.DEBUG_MODE
) -> Tuple[MedicalImageDataset, MedicalImageDataset, MedicalImageDataset]:
    """
    Create train, validation, and test datasets.
    
    Args:
        train_csv: Path to training split CSV
        val_csv: Path to validation split CSV
        test_csv: Path to test split CSV
        root_dir: Root directory for image paths
        img_size: Target image size
        use_imagenet_stats: Use ImageNet stats for normalization
        return_path: Whether to return image paths
        debug_mode: If True, limit dataset size for debugging
        
    Returns:
        Tuple of (train_dataset, val_dataset, test_dataset)
    """
    # Common kwargs
    common_kwargs = {
        'root_dir': root_dir,
        'img_size': img_size,
        'use_imagenet_stats': use_imagenet_stats,
        'return_path': return_path,
        'debug_mode': debug_mode
    }
    
    # Create datasets
    train_dataset = TrainDataset(train_csv, **common_kwargs)
    val_dataset = ValDataset(val_csv, **common_kwargs)
    test_dataset = TestDataset(test_csv, **common_kwargs)
    
    logger.info(f"Created datasets: Train={len(train_dataset)}, "
                f"Val={len(val_dataset)}, Test={len(test_dataset)}")
    
    return train_dataset, val_dataset, test_dataset


if __name__ == "__main__":
    # Test code
    import torch
    from torch.utils.data import DataLoader
    
    # Test dataset creation
    try:
        train_ds, val_ds, test_ds = create_datasets(debug_mode=True)
        
        # Test single item
        img, label = train_ds[0]
        print(f"Sample image shape: {img.shape}")
        print(f"Sample label: {label}")
        print(f"Image dtype: {img.dtype}")
        print(f"Image stats - mean: {img.mean():.4f}, std: {img.std():.4f}")
        
        # Test dataloader
        train_loader = DataLoader(
            train_ds,
            batch_size=cfg.BATCH_SIZE,
            shuffle=True,
            num_workers=cfg.NUM_WORKERS,
            pin_memory=cfg.PIN_MEMORY
        )
        
        # Test a batch
        batch_images, batch_labels = next(iter(train_loader))
        print(f"\nBatch shape: {batch_images.shape}")
        print(f"Batch labels shape: {batch_labels.shape}")
        print(f"Batch labels: {batch_labels}")
        
    except FileNotFoundError as e:
        print(f"Test files not found: {e}")
        print("Run stratification.py first to generate split files.")