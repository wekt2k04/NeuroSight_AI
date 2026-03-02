# data_loader.py
"""
Raw data ingestion module.

Handles file discovery and organization from raw dataset structure.
Traverses class folders, validates file formats, and returns structured dataframes.
This is the first step in the data pipeline before any preprocessing or splitting.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union
import logging
from collections import defaultdict
import argparse

# Import configuration
import config as cfg

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(cfg.LOGS_DIR / 'data_loader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Supported image file extensions
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}


def validate_file_format(file_path: Path) -> bool:
    """
    Validate that file has a supported image format.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file format is supported, False otherwise
    """
    return file_path.suffix.lower() in SUPPORTED_EXTENSIONS


def get_class_directories(data_dir: Path) -> List[Path]:
    """
    Get all class directories in the data directory.
    
    Args:
        data_dir: Root data directory
        
    Returns:
        List of paths to class directories
    """
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    class_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
    
    if not class_dirs:
        logger.warning(f"No class directories found in {data_dir}")
    
    return class_dirs


def scan_directory(
    data_dir: Path,
    class_names: Optional[List[str]] = None,
    recursive: bool = True,
    validate_images: bool = True
) -> pd.DataFrame:
    """
    Scan directory and collect all image files with their class labels.
    
    Args:
        data_dir: Root data directory containing class subdirectories
        class_names: Optional list of class names to include (None = all)
        recursive: Whether to search recursively within class directories
        validate_images: Whether to validate file formats
        
    Returns:
        DataFrame with columns: 'filename', 'label', 'class_name', 'file_path', 'split'
    """
    data_dir = Path(data_dir)
    logger.info(f"Scanning directory: {data_dir}")
    
    # Get class directories
    class_dirs = get_class_directories(data_dir)
    
    # Filter by class names if provided
    if class_names:
        class_dirs = [d for d in class_dirs if d.name in class_names]
        logger.info(f"Filtered to {len(class_dirs)} specified classes: {class_names}")
    
    # Create class to label mapping using cfg.CLASS_MAPPING for consistency
    # STRICT: Only accept classes defined in cfg.CLASS_MAPPING
    class_to_label = {}
    unknown_classes = []
    
    for class_dir in class_dirs:
        class_name = class_dir.name
        if class_name in cfg.CLASS_MAPPING:
            class_to_label[class_name] = cfg.CLASS_MAPPING[class_name]
        else:
            # Collect unknown classes for error reporting
            unknown_classes.append(class_name)
    
    # If there are unknown classes, raise an error to prevent silent mislabeling
    if unknown_classes:
        logger.error(f"Unknown class directories found: {unknown_classes}")
        logger.error(f"Expected classes from config: {list(cfg.CLASS_MAPPING.keys())}")
        raise ValueError(
            f"Classes {unknown_classes} found in data directory but not defined in "
            f"cfg.CLASS_MAPPING. Please update config.py or remove unknown directories."
        )
    
    logger.info(f"Class to label mapping: {class_to_label}")
    
    # Collect all image files
    data_records = []
    skipped_files = 0
    
    for class_dir in class_dirs:
        class_name = class_dir.name
        label = class_to_label[class_name]
        
        # Get all image files in class directory
        if recursive:
            # Recursive search
            image_files = []
            for ext in SUPPORTED_EXTENSIONS:
                image_files.extend(class_dir.rglob(f"*{ext}"))
                image_files.extend(class_dir.rglob(f"*{ext.upper()}"))
        else:
            # Non-recursive search (only direct children)
            image_files = []
            for ext in SUPPORTED_EXTENSIONS:
                image_files.extend(class_dir.glob(f"*{ext}"))
                image_files.extend(class_dir.glob(f"*{ext.upper()}"))
        
        # Remove duplicates (if any)
        image_files = list(set(image_files))
        
        logger.info(f"Found {len(image_files)} files in {class_name}")
        
        # Process each file
        for file_path in image_files:
            # Validate file format
            if validate_images and not validate_file_format(file_path):
                logger.debug(f"Skipping unsupported file: {file_path}")
                skipped_files += 1
                continue
            
            # Create relative path from project root (for cross-platform compatibility)
            rel_path = file_path.relative_to(cfg.PROJECT_ROOT)
            
            data_records.append({
                'filename': str(rel_path),
                'label': label,
                'class_name': class_name,
                'file_path': str(file_path),
                'split': 'unknown'  # Will be set during stratification
            })
    
    df = pd.DataFrame(data_records)
    
    # Log summary
    logger.info(f"\n{'='*50}")
    logger.info(f"SCAN COMPLETE: {data_dir}")
    logger.info(f"{'='*50}")
    logger.info(f"Total files collected: {len(df)}")
    logger.info(f"Skipped files: {skipped_files}")
    logger.info(f"Classes found: {sorted(df['class_name'].unique())}")
    
    # Log per-class distribution
    class_counts = df['class_name'].value_counts()
    for class_name, count in class_counts.items():
        percentage = (count / len(df)) * 100
        logger.info(f"  {class_name}: {count} ({percentage:.2f}%)")
    
    logger.info(f"{'='*50}\n")
    
    return df


def load_train_test_split(
    train_dir: Path = cfg.RAW_DATA_DIR / 'train',
    test_dir: Path = cfg.RAW_DATA_DIR / 'test',
    class_names: Optional[List[str]] = None,
    validate_images: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load train and test splits from separate directories.
    
    Args:
        train_dir: Path to training data directory
        test_dir: Path to test data directory
        class_names: Optional list of class names to include
        validate_images: Whether to validate file formats
        
    Returns:
        Tuple of (train_df, test_df)
    """
    logger.info("="*60)
    logger.info("LOADING TRAIN/TEST SPLITS")
    logger.info("="*60)
    
    # Scan train directory
    train_df = scan_directory(
        train_dir,
        class_names=class_names,
        validate_images=validate_images
    )
    train_df['split'] = 'train_original'
    
    # Scan test directory
    test_df = scan_directory(
        test_dir,
        class_names=class_names,
        validate_images=validate_images
    )
    test_df['split'] = 'test'
    
    # Verify class consistency
    train_classes = set(train_df['class_name'].unique())
    test_classes = set(test_df['class_name'].unique())
    
    if train_classes != test_classes:
        logger.warning(f"Class mismatch: Train {train_classes} vs Test {test_classes}")
    
    logger.info(f"\nTrain set: {len(train_df)} images")
    logger.info(f"Test set: {len(test_df)} images")
    logger.info(f"Total: {len(train_df) + len(test_df)} images")
    
    return train_df, test_df


def save_raw_dataframe(
    df: pd.DataFrame,
    output_path: Path = cfg.INTERIM_DATA_DIR / 'raw_file_list.csv'
):
    """
    Save raw dataframe to CSV.
    
    Args:
        df: DataFrame to save
        output_path: Path to save CSV file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Saved raw file list to {output_path}")


def load_raw_dataframe(
    file_path: Path = cfg.INTERIM_DATA_DIR / 'raw_file_list.csv'
) -> pd.DataFrame:
    """
    Load previously saved raw dataframe.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        Loaded DataFrame
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    logger.info(f"Loaded raw file list from {file_path}: {len(df)} files")
    return df


def get_class_statistics(df: pd.DataFrame) -> Dict:
    """
    Calculate class statistics from dataframe.
    
    Args:
        df: DataFrame with 'class_name' and 'split' columns
        
    Returns:
        Dictionary with class statistics
    """
    stats = {}
    
    # Overall statistics
    stats['total_samples'] = len(df)
    stats['class_distribution'] = df['class_name'].value_counts().to_dict()
    
    # Split statistics if available
    if 'split' in df.columns:
        stats['split_distribution'] = df['split'].value_counts().to_dict()
        
        # Per-split class distribution
        stats['per_split_distribution'] = {}
        for split in df['split'].unique():
            split_df = df[df['split'] == split]
            stats['per_split_distribution'][split] = split_df['class_name'].value_counts().to_dict()
    
    return stats


def main(args=None):
    """
    Main function to run data loading.
    """
    if args is None:
        parser = argparse.ArgumentParser(description='Load and organize raw data')
        parser.add_argument('--train_dir', type=str, default=str(cfg.RAW_DATA_DIR / 'train'),
                          help='Training data directory')
        parser.add_argument('--test_dir', type=str, default=str(cfg.RAW_DATA_DIR / 'test'),
                          help='Test data directory')
        parser.add_argument('--output_dir', type=str, default=str(cfg.INTERIM_DATA_DIR),
                          help='Output directory for CSV files')
        parser.add_argument('--no_validate', action='store_true',
                          help='Skip image format validation')
        args = parser.parse_args()
    
    # Convert to Path objects
    train_dir = Path(args.train_dir)
    test_dir = Path(args.test_dir)
    output_dir = Path(args.output_dir)
    
    # Load train and test splits
    train_df, test_df = load_train_test_split(
        train_dir=train_dir,
        test_dir=test_dir,
        class_names=cfg.CLASS_NAMES,
        validate_images=not args.no_validate
    )
    
    # Save raw dataframes
    output_dir.mkdir(parents=True, exist_ok=True)
    
    train_df.to_csv(output_dir / 'raw_train.csv', index=False)
    test_df.to_csv(output_dir / 'raw_test.csv', index=False)
    
    # Save combined dataframe
    combined_df = pd.concat([train_df, test_df], ignore_index=True)
    combined_df.to_csv(output_dir / 'raw_all.csv', index=False)
    
    # Log statistics
    stats = get_class_statistics(combined_df)
    logger.info(f"\n{'='*50}")
    logger.info("DATASET STATISTICS")
    logger.info(f"{'='*50}")
    logger.info(f"Total samples: {stats['total_samples']}")
    logger.info("\nClass distribution:")
    for class_name, count in stats['class_distribution'].items():
        logger.info(f"  {class_name}: {count}")
    logger.info(f"{'='*50}")
    
    logger.info(f"\nRaw data files saved to {output_dir}")
    
    return train_df, test_df


if __name__ == "__main__":
    train_df, test_df = main()