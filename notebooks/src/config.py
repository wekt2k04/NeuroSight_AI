"""
Configuration control for the NeuroSight AI project.
This module defines the Config class, which manages the configuration settings for the project.
The Config class provides methods to load, save, and access configuration settings, allowing for easy management of project parameters and settings.
"""

import os 
import json
from pathlib import Path


# =============================================================================
# PROJECT PATHS
# =============================================================================

# Project root directory (3 levels up from this file: notebooks/src/config.py -> NeuroSight_AI)
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()

# Data directories
RAW_DATA_DIR = PROJECT_ROOT / 'notebooks' / 'data' / 'raw'  # Base raw data dir (contains train/ and test/)
INTERIM_DATA_DIR = PROJECT_ROOT / 'data' / 'interim'
PROCESSED_DATA_DIR = PROJECT_ROOT / 'data' / 'processed'

# Reports and outputs directories
REPORTS_DIR = PROJECT_ROOT / 'notebooks' / 'notebook' / 'reports'
FIGURES_DIR = REPORTS_DIR / 'figures'
MODELS_DIR = PROJECT_ROOT / 'models'
LOGS_DIR = PROJECT_ROOT / 'logs'

# Ensure critical directories exist (logs, interim, processed)
for directory in [LOGS_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# =============================================================================
# DATA CONFIGURATION
# =============================================================================

# Dataset structure
CLASS_NAMES = ['MildDemented', 'ModerateDemented', 'NonDemented', 'VeryMildDemented']
CLASS_MAPPING = {name: idx for idx, name in enumerate(CLASS_NAMES)}



# =============================================================================
# IMAGE PROCESSING CONFIGURATION
# =============================================================================

# Image dimensions
IMG_SIZE = 224  # Standard for transfer learning (ImageNet models)
# Note: Original images are grayscale (1 channel), stacked to 3 channels for transfer learning models
IMG_CHANNELS = 3  # Stack grayscale to 3 channels for compatibility with ImageNet-pretrained backbones

# Normalization parameters (ImageNet stats for transfer learning)
# Mean and std for each channel (RGB order)
NORMALIZE_MEAN = [0.485, 0.456, 0.406]  # ImageNet mean
NORMALIZE_STD = [0.229, 0.224, 0.225]   # ImageNet std

# Alternative: Dataset-specific normalization (uncomment to use)
# These would need to be calculated from the actual dataset
# NORMALIZE_MEAN_DATASET = None  # To be calculated
# NORMALIZE_STD_DATASET = None   # To be calculated

# Skull stripping option (from experiments)
APPLY_SKULL_STRIP = False  # Based on preprocessing experiments

# Grayscale conversion (notebook final decision: convert to grayscale then stack 3 channels)
TO_GRAYSCALE = True  # Converts to grayscale for better brain region focus
STACK_GRAYSCALE_CHANNELS = True  # Stack grayscale to 3 channels for transfer learning models


# =============================================================================
# AUGMENTATION CONFIGURATION
# =============================================================================

# Augmentation intensity levels
USE_STRONG_AUGMENTATION = False  # Set to True for stronger augmentation

# Basic augmentations (always applied during training)
AUGMENTATION_CONFIG = {
    'horizontal_flip_prob': 0.5,
    'rotation_limit': 10,  # degrees
    'rotation_prob': 0.3,
}

# Strong augmentations (additional transformations)
STRONG_AUGMENTATION_CONFIG = {
    'brightness_contrast_range': 0.15,  # 15% range
    'brightness_contrast_prob': 0.3,
    'gaussian_noise_var_range': (10, 20),
    'gaussian_noise_prob': 0.2,
    'clahe_prob': 0.2,  # Contrast Limited Adaptive Histogram Equalization
}

# Per-class augmentation intensity (if needed)
# Values > 1.0 increase augmentation for specific classes
CLASS_AUGMENTATION_FACTORS = {
    'MildDemented': 1.0,
    'ModerateDemented': 1.2,  # Slightly more augmentation for minority classes
    'NonDemented': 1.0,
    'VeryMildDemented': 1.1,
}


# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Model architecture
BACKBONE = 'efficientnet-b0'  # Options: 'resnet50', 'efficientnet-b0', 'densenet121'
PRETRAINED = True  # Use efficientNet pretrained weights

# Training parameters
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001
WEIGHT_DECAY = 1e-4

# Learning rate scheduling
LR_SCHEDULER = 'cosine'  # Options: 'step', 'cosine', 'plateau'
LR_STEP_SIZE = 10  # For step scheduler
LR_GAMMA = 0.1     # For step scheduler

# Early stopping
EARLY_STOPPING_PATIENCE = 10
EARLY_STOPPING_MIN_DELTA = 0.001

# Loss function
LOSS_FUNCTION = 'cross_entropy'  # Options: 'cross_entropy', 'focal_loss'

# Class weights (for imbalanced datasets)
USE_CLASS_WEIGHTS = True
CLASS_WEIGHTS = 'balanced'  # 'balanced' or custom dict


# =============================================================================
# EVALUATION CONFIGURATION
# =============================================================================

# Metrics to track during training
METRICS = ['accuracy', 'precision', 'recall', 'f1_score', 'auc']

# Confusion matrix normalization
CONFUSION_MATRIX_NORMALIZE = 'true'  # Options: 'true', 'pred', 'all', None

# Number of top predictions to show in classification report
TOP_K_PREDICTIONS = 3


# =============================================================================
# RANDOM SEED FOR REPRODUCIBILITY
# =============================================================================

RANDOM_SEED = 42


# =============================================================================
# LOGGING AND CHECKPOINTING
# =============================================================================

# Checkpoint settings
SAVE_BEST_ONLY = True
SAVE_WEIGHTS_ONLY = True  # Save only model weights, not entire model
CHECKPOINT_MONITOR = 'val_accuracy'
CHECKPOINT_MODE = 'max'  # 'max' or 'min'

# Logging
LOG_EVERY_N_STEPS = 10
USE_TENSORBOARD = True
TENSORBOARD_LOG_DIR = LOGS_DIR / 'tensorboard'

# Experiment tracking
EXPERIMENT_NAME = None  # Will be auto-generated if None
EXPERIMENT_TAGS = ['baseline', 'resnet50', 'augmentation']


# =============================================================================
# INFERENCE CONFIGURATION
# =============================================================================

# Inference settings
INFERENCE_BATCH_SIZE = 64
INFERENCE_NUM_WORKERS = 4

# Prediction thresholds (for binary classification)
PREDICTION_THRESHOLD = 0.5

# Output format for predictions
PREDICTION_OUTPUT_COLUMNS = ['filename', 'predicted_class', 'confidence', 'probabilities']


# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================

# Device configuration
DEVICE = 'cuda'  # Options: 'cuda', 'cpu', 'mps' (for Apple Silicon)
NUM_WORKERS = 4  # DataLoader workers
PIN_MEMORY = True  # For faster GPU transfer

# Mixed precision training
USE_AMP = True  # Automatic Mixed Precision

# Gradient accumulation steps (for larger effective batch size)
GRADIENT_ACCUMULATION_STEPS = 1

# Debug mode (limits data for quick testing)
DEBUG_MODE = False
DEBUG_SAMPLE_SIZE = 100  # Number of samples to use in debug mode


VAL_RATIO = 0.2
RANDOM_SEED = 42