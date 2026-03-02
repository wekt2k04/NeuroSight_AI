# preprocessing.py
"""
Medical image preprocessing pipeline.

This module handles all image preprocessing operations including:
- Loading images into NumPy arrays
- Resizing to target dimensions
- Z-score normalization
- Optional grayscale conversion
- Optional skull stripping

The pipeline is designed to be used by data loaders and does not save files directly.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Union
import logging

# Import configuration
import config as cfg

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_image(image_path: Union[str, Path], as_grayscale: bool = False) -> np.ndarray:
    """
    Load image from file path into NumPy array.
    
    Args:
        image_path: Path to image file
        as_grayscale: If True, load as grayscale (recommended for MRI)
        
    Returns:
        Image as NumPy array. Grayscale: (H, W), RGB: (H, W, C)
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image cannot be loaded
    """
    image_path = Path(image_path)
    
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Load image - grayscale if requested (efficient for MRI)
    if as_grayscale:
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    else:
        # Read image using OpenCV (BGR format by default)
        img = cv2.imread(str(image_path))
    
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    if as_grayscale:
        return img
    else:
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img_rgb


def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Convert RGB image to grayscale.
    
    Args:
        image: RGB image as NumPy array
        
    Returns:
        Grayscale image with shape (H, W) or (H, W, 1)
    """
    if len(image.shape) == 3 and image.shape[2] == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return gray
    elif len(image.shape) == 2:
        # Already grayscale
        return image
    else:
        raise ValueError(f"Unexpected image shape: {image.shape}")


def resize_image(
    image: np.ndarray, 
    target_size: Tuple[int, int] = (cfg.IMG_SIZE, cfg.IMG_SIZE),
    interpolation: int = cv2.INTER_LINEAR
) -> np.ndarray:
    """
    Resize image to target dimensions.
    
    Args:
        image: Input image as NumPy array
        target_size: Target (height, width) tuple
        interpolation: OpenCV interpolation method
        
    Returns:
        Resized image
    """
    if image.shape[:2] == target_size:
        return image
    
    resized = cv2.resize(image, target_size[::-1], interpolation=interpolation)
    return resized


def skull_stripping(image: np.ndarray) -> np.ndarray:
    """
    Simple skull stripping using thresholding and morphological operations.
    
    Note: Based on experiments, this may be excluded from the final pipeline.
    
    Args:
        image: Input image (any shape)
        
    Returns:
        Image with skull stripped (background removed)
    """
    # Convert to grayscale if needed - handle all possible input formats safely
    if len(image.shape) == 3:
        if image.shape[2] == 3:
            # RGB image - safe to convert
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        elif image.shape[2] == 1:
            # Single channel stored as (H, W, 1) - squeeze and use directly
            gray = np.squeeze(image, axis=-1)
        elif image.shape[2] == 4:
            # RGBA image - convert to RGB first then to grayscale
            rgb = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        else:
            logger.warning(f"Unexpected number of channels {image.shape[2]} in skull_stripping, skipping")
            return image
    elif len(image.shape) == 2:
        # Already grayscale (H, W)
        gray = image.copy()
    else:
        logger.warning(f"Unexpected image shape {image.shape} in skull_stripping, skipping")
        return image
    
    # Apply Otsu's thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Morphological operations to clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Find largest connected component (assumed to be brain)
    num_labels, labels = cv2.connectedComponents(closed)
    
    if num_labels > 1:
        # Get the largest component (excluding background)
        largest_label = 1 + np.argmax([np.sum(labels == i) for i in range(1, num_labels)])
        brain_mask = (labels == largest_label).astype(np.uint8) * 255
    else:
        brain_mask = closed
    
    # Apply mask to original image
    if len(image.shape) == 3:
        # For RGB, apply mask to each channel
        brain_masked = np.zeros_like(image)
        for i in range(3):
            brain_masked[:, :, i] = cv2.bitwise_and(image[:, :, i], image[:, :, i], mask=brain_mask)
    else:
        brain_masked = cv2.bitwise_and(image, image, mask=brain_mask)
    
    return brain_masked


def z_score_normalize(image: np.ndarray, per_channel: bool = True) -> np.ndarray:
    """
    Apply Z-score normalization to image.
    
    For each channel: (x - μ) / σ
    
    Args:
        image: Input image as NumPy array
        per_channel: If True, normalize each channel independently
        
    Returns:
        Normalized image as float32 array
    """
    image = image.astype(np.float32)
    
    if per_channel and len(image.shape) == 3:
        # Normalize each channel independently
        normalized = np.zeros_like(image)
        for c in range(image.shape[2]):
            channel = image[:, :, c]
            mean = np.mean(channel)
            std = np.std(channel)
            
            # Avoid division by zero
            if std > 0:
                normalized[:, :, c] = (channel - mean) / std
            else:
                normalized[:, :, c] = channel - mean
    else:
        # Normalize entire image
        mean = np.mean(image)
        std = np.std(image)
        
        if std > 0:
            normalized = (image - mean) / std
        else:
            normalized = image - mean
    
    return normalized


def normalize_with_stats(
    image: np.ndarray,
    mean: Union[float, list] = cfg.NORMALIZE_MEAN,
    std: Union[float, list] = cfg.NORMALIZE_STD,
    per_channel: bool = True
) -> np.ndarray:
    """
    Normalize image using pre-computed statistics (e.g., ImageNet stats).
    
    Args:
        image: Input image as NumPy array (values typically 0-255)
        mean: Mean value(s) for normalization
        std: Standard deviation value(s) for normalization
        per_channel: If True, use per-channel statistics
        
    Returns:
        Normalized image
    """
    image = image.astype(np.float32)
    
    # Scale from 0-255 to 0-1
    image = image / 255.0
    
    if per_channel and len(image.shape) == 3:
        # Per-channel normalization using provided stats
        normalized = np.zeros_like(image)
        for c in range(image.shape[2]):
            normalized[:, :, c] = (image[:, :, c] - mean[c]) / std[c]
    else:
        # Global normalization
        if isinstance(mean, list):
            mean_val = np.mean(mean)
        else:
            mean_val = mean
        
        if isinstance(std, list):
            std_val = np.mean(std)
        else:
            std_val = std
            
        normalized = (image - mean_val) / std_val
    
    return normalized


def verify_output_shape(
    image: np.ndarray,
    expected_shape: Optional[Tuple[int, ...]] = None
) -> bool:
    """
    Verify that image has expected shape and values are within reasonable range.
    
    Args:
        image: Processed image
        expected_shape: Expected shape tuple (optional)
        
    Returns:
        True if verification passes, False otherwise
    """
    if expected_shape and image.shape != expected_shape:
        logger.error(f"Shape mismatch: expected {expected_shape}, got {image.shape}")
        return False
    
    # Check for NaN or Inf values
    if np.any(np.isnan(image)) or np.any(np.isinf(image)):
        logger.error("Image contains NaN or Inf values")
        return False
    
    # Check value range (after normalization, values should be around 0 with std 1)
    mean_val = np.mean(image)
    std_val = np.std(image)
    
    if abs(mean_val) > 5:
        logger.warning(f"Mean value is unusually high: {mean_val:.2f}")
    
    if std_val < 0.1 or std_val > 5:
        logger.warning(f"Std deviation is unusual: {std_val:.2f}")
    
    return True


class PreprocessingPipeline:
    """
    Main preprocessing pipeline for medical images.
    
    Combines all preprocessing steps into a configurable pipeline.
    """
    
    def __init__(
        self,
        target_size: Tuple[int, int] = (cfg.IMG_SIZE, cfg.IMG_SIZE),
        apply_skull_strip: bool = cfg.APPLY_SKULL_STRIP,
        use_z_score: bool = True,
        use_imagenet_stats: bool = False,
        to_grayscale: bool = False,
        per_channel_norm: bool = True,
        verify_output: bool = True
    ):
        """
        Initialize preprocessing pipeline.
        
        Args:
            target_size: Target (height, width) for resizing
            apply_skull_strip: Whether to apply skull stripping
            use_z_score: Use Z-score normalization (vs. pre-computed stats)
            use_imagenet_stats: Use ImageNet stats for normalization
            to_grayscale: Convert to grayscale
            per_channel_norm: Normalize each channel independently
            verify_output: Verify output shape and values
        """
        self.target_size = target_size
        self.apply_skull_strip = apply_skull_strip
        self.use_z_score = use_z_score
        self.use_imagenet_stats = use_imagenet_stats
        self.to_grayscale = to_grayscale
        self.per_channel_norm = per_channel_norm
        self.verify_output = verify_output
        
        # Validate configuration
        if use_z_score and use_imagenet_stats:
            raise ValueError("Cannot use both Z-score and ImageNet normalization")
    
    def __call__(self, image_path: Union[str, Path], skip_normalization: bool = False) -> np.ndarray:
        """
        Run full preprocessing pipeline on an image.
        
        Args:
            image_path: Path to image file
            skip_normalization: If True, skip normalization step (useful when augmentation comes after)
            
        Returns:
            Preprocessed image as NumPy array
        """
        # Step 1: Load image - use grayscale loading directly when to_grayscale is enabled
        # This is more efficient than loading RGB then converting
        image = load_image(image_path, as_grayscale=self.to_grayscale)
        
        # Step 2: If loaded as grayscale (when to_grayscale=True), ensure consistent shape
        # When to_grayscale=True, image is already grayscale (H, W) from load_image
        if self.to_grayscale:
            # Image is already grayscale (H, W) from load_image
            # Add channel dimension for consistent processing
            if len(image.shape) == 2:
                image = np.expand_dims(image, axis=-1)
            # Don't stack to 3 channels here - wait until after normalization
        
        # Step 3: Optional skull stripping
        if self.apply_skull_strip:
            image = skull_stripping(image)
        
        # Step 4: Resize
        image = resize_image(image, self.target_size)
        
        # Step 5: Normalize (unless skipped for augmentation)
        if not skip_normalization:
            if self.use_z_score:
                image = z_score_normalize(image, per_channel=self.per_channel_norm)
            elif self.use_imagenet_stats:
                image = normalize_with_stats(
                    image, 
                    mean=cfg.NORMALIZE_MEAN,
                    std=cfg.NORMALIZE_STD,
                    per_channel=self.per_channel_norm
                )
            else:
                # Simple scaling to [0, 1]
                image = image.astype(np.float32) / 255.0
            
            # Stack grayscale to 3 channels AFTER normalization for transfer learning models
            if self.to_grayscale and cfg.STACK_GRAYSCALE_CHANNELS and len(image.shape) == 2:
                image = np.expand_dims(image, axis=-1)
            if self.to_grayscale and cfg.STACK_GRAYSCALE_CHANNELS and len(image.shape) == 3 and image.shape[2] == 1:
                image = np.repeat(image, 3, axis=2)
        
        # Step 6: Verify output
        if self.verify_output:
            expected_shape = (*self.target_size, image.shape[2] if len(image.shape) == 3 else 1)
            if not verify_output_shape(image, expected_shape):
                logger.warning(f"Output verification failed for {image_path}")
        
        return image
    
    def normalize(self, image: np.ndarray) -> np.ndarray:
        """
        Apply normalization to an already preprocessed image.
        Useful for normalizing after augmentation.
        
        Args:
            image: Image array (should be uint8 0-255)
            
        Returns:
            Normalized image
        """
        if self.use_z_score:
            image = z_score_normalize(image, per_channel=self.per_channel_norm)
        elif self.use_imagenet_stats:
            image = normalize_with_stats(
                image, 
                mean=cfg.NORMALIZE_MEAN,
                std=cfg.NORMALIZE_STD,
                per_channel=self.per_channel_norm
            )
        else:
            # Simple scaling to [0, 1]
            image = image.astype(np.float32) / 255.0
        
        # Stack grayscale to 3 channels AFTER normalization for transfer learning models
        if self.to_grayscale and cfg.STACK_GRAYSCALE_CHANNELS and len(image.shape) == 2:
            image = np.expand_dims(image, axis=-1)
        if self.to_grayscale and cfg.STACK_GRAYSCALE_CHANNELS and len(image.shape) == 3 and image.shape[2] == 1:
            image = np.repeat(image, 3, axis=2)
        
        return image
    
    def __repr__(self) -> str:
        """String representation of the pipeline."""
        steps = []
        if self.to_grayscale:
            steps.append("Grayscale conversion")
        if self.apply_skull_strip:
            steps.append("Skull stripping")
        steps.append(f"Resize to {self.target_size}")
        if self.use_z_score:
            steps.append("Z-score normalization")
        elif self.use_imagenet_stats:
            steps.append("ImageNet normalization")
        else:
            steps.append("Scale to [0, 1]")
        
        return f"PreprocessingPipeline(steps={steps})"


# Create default pipeline instances based on config
default_pipeline = PreprocessingPipeline(
    target_size=(cfg.IMG_SIZE, cfg.IMG_SIZE),
    apply_skull_strip=cfg.APPLY_SKULL_STRIP,
    use_z_score=True,
    use_imagenet_stats=False,
    to_grayscale=cfg.TO_GRAYSCALE,  # Match notebook decision
    per_channel_norm=True
)

# Pipeline using ImageNet stats (for transfer learning)
imagenet_pipeline = PreprocessingPipeline(
    target_size=(cfg.IMG_SIZE, cfg.IMG_SIZE),
    apply_skull_strip=cfg.APPLY_SKULL_STRIP,
    use_z_score=False,
    use_imagenet_stats=True,
    to_grayscale=cfg.TO_GRAYSCALE,  # Match notebook decision
    per_channel_norm=True
)


if __name__ == "__main__":
    # Simple test code
    test_image_path = cfg.RAW_DATA_DIR / 'train' / 'NonDemented' / 'nonDem0.jpg'
    
    if test_image_path.exists():
        # Test default pipeline
        pipeline = default_pipeline
        print(f"Testing pipeline: {pipeline}")
        
        processed = pipeline(test_image_path)
        print(f"Output shape: {processed.shape}")
        print(f"Output dtype: {processed.dtype}")
        print(f"Output mean: {np.mean(processed):.4f}")
        print(f"Output std: {np.std(processed):.4f}")
        print(f"Output min: {np.min(processed):.4f}")
        print(f"Output max: {np.max(processed):.4f}")
    else:
        print(f"Test image not found: {test_image_path}")