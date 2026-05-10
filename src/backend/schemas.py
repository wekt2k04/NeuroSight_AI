from pydantic import BaseModel


class PredictionResponse(BaseModel):
    diagnosis: str
    confidence: float
    heatmap_path: str | None = None


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
