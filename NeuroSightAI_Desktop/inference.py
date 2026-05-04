#!/usr/bin/env python3
"""
NeuroSight AI - Inference Script
This script receives an MRI image path and returns diagnosis with confidence score
and a Class Activation Map (CAM) heatmap.

The C++ application calls this script via QProcess with the image path as argument.

Expected output format (JSON):
{
    "diagnosis": "Normal|Mild|Moderate|Severe",
    "confidence": 0.95,
    "heatmap_path": "/path/to/heatmap.png"
}
"""

import sys
import json
import os
import numpy as np

# ONNX Runtime imports
try:
    import onnxruntime as ort
    from PIL import Image
except ImportError as e:
    print(f"Error: Required libraries not found. Install ONNX Runtime deps: {e}")
    sys.exit(1)


class Alzheimer_Model:
    """
    Wrapper for the pre-trained Alzheimer detection model.
    Replace this with your actual model implementation.
    """
    
    def __init__(self, model_path="model.onnx"):
        """
        Initialize the model.
        
        Args:
            model_path: Path to the saved model weights
        """
        self.session = self._load_model(model_path)
        self.diagnosis_classes = ["Normal", "Mild", "Moderate", "Severe"]
        
    def _load_model(self, model_path):
        """Load the pre-trained model"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        # Prefer GPU provider if available, otherwise CPU.
        available_providers = ort.get_available_providers()
        providers = ["CPUExecutionProvider"]
        if "CUDAExecutionProvider" in available_providers:
            providers.insert(0, "CUDAExecutionProvider")

        session = ort.InferenceSession(model_path, providers=providers)
        return session
    
    def preprocess_image(self, image_path):
        """
        Preprocess MRI image for model inference.
        
        Args:
            image_path: Path to the MRI image
            
        Returns:
            Preprocessed image array for ONNX input (NCHW)
        """
        # Adjust this preprocessing to exactly match your model training pipeline.
        image = Image.open(image_path).convert("RGB")
        image = image.resize((224, 224), Image.Resampling.BILINEAR)

        image_np = np.asarray(image, dtype=np.float32) / 255.0

        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        image_np = (image_np - mean) / std

        # HWC -> CHW
        image_np = np.transpose(image_np, (2, 0, 1))
        # Add batch dimension: NCHW
        image_np = np.expand_dims(image_np, axis=0).astype(np.float32)

        return image_np
    
    def predict(self, image_path):
        """
        Run inference on the image.
        
        Args:
            image_path: Path to the MRI image
            
        Returns:
            Tuple of (diagnosis, confidence_score)
        """
        image_input = self.preprocess_image(image_path)

        input_name = self.session.get_inputs()[0].name
        output_names = [output.name for output in self.session.get_outputs()]
        outputs = self.session.run(output_names, {input_name: image_input})

        if len(outputs) == 0:
            raise RuntimeError("ONNX model produced no outputs.")

        logits = np.array(outputs[0], dtype=np.float32)
        logits = np.squeeze(logits)

        if logits.ndim != 1:
            raise RuntimeError(f"Unexpected ONNX output shape: {logits.shape}")

        if logits.shape[0] != len(self.diagnosis_classes):
            raise RuntimeError(
                f"Expected {len(self.diagnosis_classes)} classes, got {logits.shape[0]}"
            )

        # Softmax in numpy
        exp_logits = np.exp(logits - np.max(logits))
        probabilities = exp_logits / np.sum(exp_logits)

        predicted_class = int(np.argmax(probabilities))
        diagnosis = self.diagnosis_classes[predicted_class]
        confidence_score = float(probabilities[predicted_class])
        
        return diagnosis, confidence_score
    
    def generate_grad_cam(self, image_path, output_path="heatmap.png"):
        """
        Generate Grad-CAM heatmap for explainability.
        
        Args:
            image_path: Path to the MRI image
            output_path: Where to save the heatmap
            
        Returns:
            Path to the generated heatmap
        """
        # Standard ONNX export does not keep autograd graph, so Grad-CAM is not
        # directly available here. Keep this optional for a separate pipeline.
        return None


def main():
    """
    Main entry point called by the C++ application.
    Expected command line: python inference.py <image_path>
    """
    
    if len(sys.argv) < 2:
        error_response = {
            "error": "No image path provided",
            "diagnosis": None,
            "confidence": 0.0,
            "heatmap_path": None
        }
        print(json.dumps(error_response))
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Validate image path
    if not os.path.exists(image_path):
        error_response = {
            "error": f"Image file not found: {image_path}",
            "diagnosis": None,
            "confidence": 0.0,
            "heatmap_path": None
        }
        print(json.dumps(error_response))
        sys.exit(1)
    
    try:
        # Use ONNX model file in the app directory.
        model_path = os.path.join(os.path.dirname(__file__), "model.onnx")
        model = Alzheimer_Model(model_path)
        
        # Run inference
        diagnosis, confidence = model.predict(image_path)
        
        # Generate heatmap (optional)
        heatmap_path = model.generate_grad_cam(image_path)
        
        # Prepare response
        response = {
            "diagnosis": diagnosis,
            "confidence": float(confidence),
            "heatmap_path": heatmap_path if heatmap_path else ""
        }
        
        # Print as JSON (captured by C++ QProcess)
        print(json.dumps(response))
        
    except Exception as e:
        error_response = {
            "error": str(e),
            "diagnosis": None,
            "confidence": 0.0,
            "heatmap_path": None
        }
        print(json.dumps(error_response), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
