from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.ai_engine.domain import PredictionResult


@dataclass
class PredictionService:
    engine: object

    def predict_file(self, upload_filename: str, upload_bytes: bytes) -> PredictionResult:
        suffix = Path(upload_filename).suffix or ".tmp"
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(upload_bytes)
            temp_path = Path(temp_file.name)

        try:
            return self.engine.predict(str(temp_path))
        finally:
            temp_path.unlink(missing_ok=True)
