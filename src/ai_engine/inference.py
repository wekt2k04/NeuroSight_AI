"""Compatibility layer for legacy imports.

The actual strategy implementation lives in `src.ai_engine.engine`.
"""

from .domain import PredictionResult
from .engine import OnnxInferenceEngine as AlzheimerModel

__all__ = ["AlzheimerModel", "PredictionResult"]
