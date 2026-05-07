"""Compatibility loader used by the backend and tests.

Kept as a thin wrapper so the app can depend on a single stable factory API.
"""

from .factory import create_inference_engine


def load_model(model_path: str):
    return create_inference_engine(model_path)
