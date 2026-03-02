# stratification.py
"""
Perform balanced stratified splitting for medical imaging datasets.

This module ensures fair class distribution across train, validation, and test sets,
which is critical for medical AI fairness and reliable model evaluation.

Note: The original dataset is already split into train/test.
This script further splits the training data into train/validation while maintaining
stratification.
✅ Split ONLY train → train + validation

❌ NOT recompute global train/test ratios

❌ NOT verify against TRAIN_RATIO / TEST_RATIO

✅ Keep test untouched
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import logging
from typing import Tuple, Dict, List, Optional
import argparse

# Import configuration
import config as cfg

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(cfg.LOGS_DIR / 'stratification.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_file_list_and_labels(data_dir: Path, class_names: List[str]) -> pd.DataFrame:
    """
    Load all image files and their corresponding labels from directory structure.
    
    Args:
        data_dir: Path to data directory (should contain class subdirectories)
        class_names: List of class names
        
    Returns:
        DataFrame with columns: 'filename', 'label', 'class_name', 'split'
    """
    logger.info(f"Loading files from {data_dir}")
    
    file_list = []
    
    for class_name in class_names:
        class_dir = data_dir / class_name
        if not class_dir.exists():
            logger.warning(f"Directory {class_dir} does not exist. Skipping.")
            continue
            
        # Get all image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.tif']:
            image_files.extend(class_dir.glob(ext))
        
        logger.info(f"Found {len(image_files)} files in {class_name}")
        
        for img_path in image_files:
            file_list.append({
                'filename': str(img_path.relative_to(cfg.PROJECT_ROOT)),
                'label': cfg.CLASS_MAPPING[class_name],
                'class_name': class_name,
                'split': 'unknown'  # Will be set later
            })
    
    df = pd.DataFrame(file_list)
    logger.info(f"Total files loaded: {len(df)}")
    
    return df


def compute_class_distribution(df: pd.DataFrame, split: Optional[str] = None) -> Dict:
    """
    Compute class distribution in the dataset.
    
    Args:
        df: DataFrame with 'class_name' column
        split: Optional split name to filter by
        
    Returns:
        Dictionary with class names as keys and counts as values
    """
    if split:
        subset = df[df['split'] == split]
    else:
        subset = df
    
    distribution = subset['class_name'].value_counts().to_dict()
    return distribution


def log_distribution(df: pd.DataFrame, title: str = "Class Distribution"):
    """
    Log the class distribution with percentages.
    
    Args:
        df: DataFrame with 'class_name' column
        title: Title for the log entry
    """
    total = len(df)
    distribution = compute_class_distribution(df)
    
    logger.info(f"\n{'='*50}")
    logger.info(f"{title}: {total} total samples")
    logger.info(f"{'='*50}")
    
    for class_name, count in distribution.items():
        percentage = (count / total) * 100
        logger.info(f"  {class_name}: {count} ({percentage:.2f}%)")
    
    logger.info(f"{'='*50}\n")





def verify_stratification(train_df: pd.DataFrame,
                          val_df: pd.DataFrame) -> bool:

    train_dist = compute_class_distribution(train_df)
    val_dist = compute_class_distribution(val_df)

    train_pct = {k: v/len(train_df)*100 for k, v in train_dist.items()}
    val_pct = {k: v/len(val_df)*100 for k, v in val_dist.items()}

    logger.info("\nStratification Check (Train vs Validation)")
    logger.info(f"{'Class':<20} {'Train %':<10} {'Val %':<10}")

    stratified_ok = True

    for class_name in sorted(train_pct.keys()):
        t = train_pct.get(class_name, 0)
        v = val_pct.get(class_name, 0)

        logger.info(f"{class_name:<20} {t:<10.2f} {v:<10.2f}")

        if abs(t - v) > 3:   # tighter tolerance
            stratified_ok = False

    if stratified_ok:
        logger.info("✓ Stratification OK")
    else:
        logger.warning("⚠ Train/Val distributions differ")

    return stratified_ok


def perform_stratified_split(
    train_df: pd.DataFrame,
    val_size: float,
    random_state: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:

    logger.info(f"Splitting TRAIN data into Train/Validation (val_size={val_size:.2f})")

    X_train, X_val, y_train, y_val = train_test_split(
        train_df['filename'],
        train_df['label'],
        test_size=val_size,
        stratify=train_df['label'],
        random_state=random_state,
        shuffle=True
    )

    train_split = train_df[train_df['filename'].isin(X_train)].copy()
    val_split = train_df[train_df['filename'].isin(X_val)].copy()

    train_split['split'] = 'train'
    val_split['split'] = 'validation'

    logger.info(f"Final counts → Train: {len(train_split)}, Val: {len(val_split)}")

    return train_split, val_split


def save_split_files(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    output_dir: Path = cfg.PROCESSED_DATA_DIR
):
    """
    Save split DataFrames to CSV files.
    
    Args:
        train_df, val_df, test_df: DataFrames for each split
        output_dir: Directory to save CSV files
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save full split information
    all_splits = pd.concat([train_df, val_df, test_df], ignore_index=True)
    all_splits.to_csv(output_dir / 'all_splits.csv', index=False)
    
    # Save individual split files
    train_df.to_csv(output_dir / 'train_split.csv', index=False)
    val_df.to_csv(output_dir / 'val_split.csv', index=False)
    test_df.to_csv(output_dir / 'test_split.csv', index=False)
    
    # Save summary statistics
    summary = {
        'split': ['train', 'validation', 'test', 'total'],
        'count': [
            len(train_df), 
            len(val_df), 
            len(test_df), 
            len(train_df) + len(val_df) + len(test_df)
        ]
    }
    
    # Add class counts
    for class_name in cfg.CLASS_NAMES:
        summary[f'{class_name}_count'] = [
            len(train_df[train_df['class_name'] == class_name]),
            len(val_df[val_df['class_name'] == class_name]),
            len(test_df[test_df['class_name'] == class_name]),
            len(train_df[train_df['class_name'] == class_name]) + 
            len(val_df[val_df['class_name'] == class_name]) + 
            len(test_df[test_df['class_name'] == class_name])
        ]
    
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(output_dir / 'split_summary.csv', index=False)
    
    logger.info(f"Split files saved to {output_dir}")


def main(args=None):
    """
    Main function to perform stratified splitting.
    """
    logger.info("="*60)
    logger.info("STRATIFIED SPLITTING FOR MEDICAL IMAGING DATASET")
    logger.info("="*60)
    
    # Parse command line arguments if provided
    if args is None:
        parser = argparse.ArgumentParser(description='Perform stratified splitting')
        parser.add_argument('--train_dir', type=str, default=None,
                          help='Path to training data directory (overrides config)')
        parser.add_argument('--test_dir', type=str, default=None,
                          help='Path to test data directory (overrides config)')
        parser.add_argument('--val_size', type=float, default=cfg.VAL_RATIO,
                          help='Validation set proportion')
        parser.add_argument('--random_seed', type=int, default=cfg.RANDOM_SEED,
                          help='Random seed for reproducibility')
        args = parser.parse_args()
    
    # Set random seed for reproducibility
    np.random.seed(args.random_seed if hasattr(args, 'random_seed') else cfg.RANDOM_SEED)
    
    # Define data directories
    train_dir = Path(args.train_dir) if hasattr(args, 'train_dir') and args.train_dir else cfg.RAW_DATA_DIR / 'train'
    test_dir = Path(args.test_dir) if hasattr(args, 'test_dir') and args.test_dir else cfg.RAW_DATA_DIR / 'test'
    
    # Load training data (to be split into train/validation)
    logger.info(f"Loading training data from: {train_dir}")
    train_full_df = load_file_list_and_labels(train_dir, cfg.CLASS_NAMES)
    
    # Load test data (already separate)
    logger.info(f"Loading test data from: {test_dir}")
    test_df = load_file_list_and_labels(test_dir, cfg.CLASS_NAMES)
    test_df['split'] = 'test'
    
    # Log initial distributions
    log_distribution(train_full_df, "Initial Training Data Distribution")
    log_distribution(test_df, "Test Data Distribution")
    
    # Perform stratified split of training data
    val_size = args.val_size if hasattr(args, 'val_size') else cfg.VAL_RATIO
    train_df, val_df = perform_stratified_split(
        train_full_df, 
        val_size=val_size,
        random_state=args.random_seed if hasattr(args, 'random_seed') else cfg.RANDOM_SEED
    )
    
    # Log final distributions
    logger.info("\n" + "="*60)
    logger.info("FINAL SPLIT DISTRIBUTIONS")
    logger.info("="*60)
    
    log_distribution(train_df, "Training Set Distribution")
    log_distribution(val_df, "Validation Set Distribution")
    log_distribution(test_df, "Test Set Distribution")
    
    
    # Verify stratification quality
    verify_stratification(train_df, val_df)
    
    # Save split files
    save_split_files(train_df, val_df, test_df)
    
    logger.info("="*60)
    logger.info("STRATIFIED SPLITTING COMPLETED SUCCESSFULLY")
    logger.info("="*60)
    
    return train_df, val_df, test_df


if __name__ == "__main__":
    train_df, val_df, test_df = main()