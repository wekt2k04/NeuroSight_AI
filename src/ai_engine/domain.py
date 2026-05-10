from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PredictionResult:
    diagnosis: str
    confidence: float
    heatmap_path: Optional[str] = None
