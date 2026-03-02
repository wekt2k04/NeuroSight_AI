# augmentation.py
"""
Medical image augmentation module.

Handles augmentation logic with separate strategies for majority and minority classes.
Augmentations are applied only during training and preserve labels.

Features:
- Rotation
- Zoom
- Horizontal flip
- Brightness/contrast variation
- Stronger augmentation for minority classes
"""

import numpy as np
import albumentations as A
from albumentations import DualTransform, BasicTransform
from typing import Dict, Optional, Union, List, Callable
import copy
import logging

# Import configuration
import config as cfg

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AugmentationPipeline:
    """
    Augmentation pipeline with class-specific augmentation strategies.
    
    Provides weaker augmentation for majority classes and stronger augmentation
    for minority classes to balance representation during training.
    """
    
    def __init__(
        self,
        img_size: int = cfg.IMG_SIZE,
        use_strong: bool = cfg.USE_STRONG_AUGMENTATION,
        class_aug_factors: Dict[str, float] = cfg.CLASS_AUGMENTATION_FACTORS,
        random_seed: int = cfg.RANDOM_SEED
    ):
        """
        Initialize augmentation pipeline.
        
        Args:
            img_size: Image size (assumed square)
            use_strong: Whether to use strong augmentation
            class_aug_factors: Per-class augmentation intensity factors
            random_seed: Random seed for reproducibility
        """
        self.img_size = img_size
        self.use_strong = use_strong
        self.class_aug_factors = class_aug_factors
        self.random_seed = random_seed
        
        # Set random seed for reproducibility
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Define base augmentations (applied to all classes)
        self.base_augmentations = self._get_base_augmentations()
        
        # Define strong augmentations (additional for minority classes)
        self.strong_augmentations = self._get_strong_augmentations() if use_strong else None
        
        # Compose full augmentation pipeline
        self.pipeline = self._compose_pipeline()
        
        logger.info(f"Initialized AugmentationPipeline (use_strong={use_strong})")
    
    def _get_base_augmentations(self) -> List[BasicTransform]:
        """
        Get base augmentations applied to all classes.
        
        Returns:
            List of augmentation transforms
        """
        base = [
            # Horizontal flip (simulates brain asymmetry)
            A.HorizontalFlip(
                p=cfg.AUGMENTATION_CONFIG['horizontal_flip_prob']
            ),
            
            # Rotation (compensates for head tilt)
            A.Rotate(
                limit=cfg.AUGMENTATION_CONFIG['rotation_limit'],
                p=cfg.AUGMENTATION_CONFIG['rotation_prob'],
                border_mode=0,  # cv2.BORDER_CONSTANT
                fill=0  # Fill with 0 (black) - corrected parameter name
            ),
        ]
        
        return base
    
    def _get_strong_augmentations(self) -> List[BasicTransform]:
        """
        Get additional augmentations for minority classes.
        
        Returns:
            List of augmentation transforms
        """
        strong = [
            # Random brightness and contrast
            A.RandomBrightnessContrast(
                brightness_limit=cfg.STRONG_AUGMENTATION_CONFIG['brightness_contrast_range'],
                contrast_limit=cfg.STRONG_AUGMENTATION_CONFIG['brightness_contrast_range'],
                p=cfg.STRONG_AUGMENTATION_CONFIG['brightness_contrast_prob']
            ),
            
            # Gaussian noise (simulates scanner noise)
            A.GaussNoise(
                var_limit=cfg.STRONG_AUGMENTATION_CONFIG['gaussian_noise_var_range'],
                p=cfg.STRONG_AUGMENTATION_CONFIG['gaussian_noise_prob']
            ),
            
            # CLAHE (enhances local contrast)
            A.CLAHE(
                clip_limit=2.0,
                tile_grid_size=(8, 8),
                p=cfg.STRONG_AUGMENTATION_CONFIG['clahe_prob']
            ),
        ]
        
        return strong
    
    def _compose_pipeline(self) -> A.Compose:
        """
        Compose the augmentation pipeline.
        
        Returns:
            Albumentations Compose object
        """
        all_transforms = self.base_augmentations.copy()
        
        if self.strong_augmentations:
            all_transforms.extend(self.strong_augmentations)
        
        # Add random crop/resize to ensure consistent size
        all_transforms.append(
            A.RandomResizedCrop(
                size=(self.img_size, self.img_size),  # Required: tuple (height, width)
                scale=(0.8, 1.0),
                ratio=(0.9, 1.1),
                p=0.5
            )
        )
        
        return A.Compose(
            all_transforms,
            additional_targets={'mask': 'image'}  # If we ever add segmentation masks
        )
    
    def get_class_augmentation(self, class_name: str) -> A.Compose:
        """
        Get augmentation pipeline adjusted for specific class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Albumentations Compose with adjusted probabilities
        """
        factor = self.class_aug_factors.get(class_name, 1.0)
        
        if factor == 1.0:
            return self.pipeline
        
        # Adjust probabilities based on class factor
        adjusted_transforms = []
        
        for transform in self.pipeline.transforms:
            if hasattr(transform, 'p'):
                # Adjust probability but cap at 1.0
                new_p = min(transform.p * factor, 1.0)
                
                # Clone and update probability - use only public API
                import copy
                try:
                    # First try: use to_dict/from_dict (public API)
                    transform_dict = transform.to_dict()
                    transform_dict['p'] = new_p
                    transform_clone = A.from_dict(transform_dict)
                except (AttributeError, TypeError, KeyError):
                    # Second fallback: use deepcopy for transforms without to_dict
                    try:
                        transform_clone = copy.deepcopy(transform)
                        transform_clone.p = new_p
                    except Exception as e:
                        # Last resort: warn and use original
                        logger.warning(f"Could not clone/adjust transform {transform.__class__.__name__}: {e}")
                        transform_clone = transform
                adjusted_transforms.append(transform_clone)
            else:
                # Transforms without 'p' attribute pass through unchanged
                adjusted_transforms.append(transform)
        
        return A.Compose(
            adjusted_transforms,
            additional_targets=self.pipeline.additional_targets
        )
    
    def __call__(
        self,
        image: np.ndarray,
        class_name: Optional[str] = None,
        force_apply: bool = False
    ) -> np.ndarray:
        """
        Apply augmentations to image.
        
        Args:
            image: Input image (H, W, C) or (H, W) - should be uint8 [0-255]
            class_name: Class name for class-specific augmentation
            force_apply: Force augmentation even if class_name is None
            
        Returns:
            Augmented image (uint8 format)
        """
        # Ensure image is in uint8 format for albumentations
        if image.dtype != np.uint8:
            # If float in range [0, 1], scale to [0, 255]
            if image.max() <= 1.0 and image.min() >= 0.0:
                image = (image * 255).astype(np.uint8)
            # If float in typical uint8 range but wrong dtype
            elif image.min() >= 0 and image.max() <= 255:
                image = np.clip(image, 0, 255).astype(np.uint8)
            else:
                # Unexpected range (e.g., z-score normalized data)
                logger.warning(f"Image has unexpected value range [{image.min():.2f}, {image.max():.2f}]. "
                             f"Augmentation should be applied before normalization.")
                # Clip and convert anyway to avoid crash
                image = np.clip(image, 0, 255).astype(np.uint8)
        
        # Select appropriate pipeline
        if class_name is not None:
            aug_pipeline = self.get_class_augmentation(class_name)
        else:
            aug_pipeline = self.pipeline
        
        # Apply augmentations
        augmented = aug_pipeline(image=image)['image']
        
        return augmented
    
    def __repr__(self) -> str:
        """String representation."""
        return f"AugmentationPipeline(use_strong={self.use_strong})"


class WeakAugmentation(AugmentationPipeline):
    """
    Weak augmentation pipeline (for majority classes).
    """
    
    def __init__(self, **kwargs):
        """Initialize with weak augmentation."""
        kwargs['use_strong'] = False
        super().__init__(**kwargs)


class StrongAugmentation(AugmentationPipeline):
    """
    Strong augmentation pipeline (for minority classes).
    """
    
    def __init__(self, **kwargs):
        """Initialize with strong augmentation."""
        kwargs['use_strong'] = True
        super().__init__(**kwargs)


def create_augmentation_pipeline(
    use_strong: bool = cfg.USE_STRONG_AUGMENTATION,
    class_name: Optional[str] = None
) -> AugmentationPipeline:
    """
    Factory function to create appropriate augmentation pipeline.
    
    Args:
        use_strong: Whether to use strong augmentation
        class_name: Class name for class-specific adjustments
        
    Returns:
        Configured AugmentationPipeline
    """
    pipeline = AugmentationPipeline(use_strong=use_strong)
    
    if class_name is not None:
        return pipeline.get_class_augmentation(class_name)
    
    return pipeline


# Example usage in a training loop:
# def train_step(image, label, class_name, is_training=True):
#     if is_training:
#         image = augmentation_pipeline(image, class_name)
#     # Continue training...


if __name__ == "__main__":
    # Test code
    import matplotlib.pyplot as plt
    
    # Create test image (random noise)
    test_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    # Test different pipelines
    weak_pipeline = WeakAugmentation()
    strong_pipeline = StrongAugmentation()
    
    # Apply augmentations
    weak_aug = weak_pipeline(test_img, class_name='NonDemented')
    strong_aug = strong_pipeline(test_img, class_name='ModerateDemented')
    
    print(f"Original shape: {test_img.shape}")
    print(f"Weak aug shape: {weak_aug.shape}")
    print(f"Strong aug shape: {strong_aug.shape}")
    
    # Visualize results
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    
    axes[0].imshow(test_img)
    axes[0].set_title('Original')
    axes[0].axis('off')
    
    axes[1].imshow(weak_aug)
    axes[1].set_title('Weak Augmentation')
    axes[1].axis('off')
    
    axes[2].imshow(strong_aug)
    axes[2].set_title('Strong Augmentation')
    axes[2].axis('off')
    
    plt.tight_layout()
    plt.savefig(cfg.FIGURES_DIR / 'augmentation_examples.png')
    plt.show()
    
    print("Augmentation examples saved to figures directory")