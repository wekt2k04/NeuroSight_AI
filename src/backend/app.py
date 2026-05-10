import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.ai_engine.loader import load_model
from src.backend.schemas import PredictionResponse, HealthResponse
from src.backend.services.prediction_service import PredictionService

app = FastAPI(title="NeuroSightAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.environ.get('MODEL_PATH', 'models/model.onnx')
MULTIPART_AVAILABLE = True

try:
    engine = load_model(MODEL_PATH)
    prediction_service = PredictionService(engine)
except Exception as e:
    engine = None
    prediction_service = None

@app.get('/health', response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", model_loaded=prediction_service is not None)

try:
    @app.post('/predict', response_model=PredictionResponse)
    async def predict(file: UploadFile = File(...)):
        if prediction_service is None:
            raise HTTPException(status_code=503, detail="Model not loaded")
        try:
            result = prediction_service.predict_file(file.filename, await file.read())
            return PredictionResponse(
                diagnosis=result.diagnosis,
                confidence=result.confidence,
                heatmap_path=result.heatmap_path,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
except RuntimeError:
    MULTIPART_AVAILABLE = False

    @app.post('/predict', response_model=PredictionResponse)
    async def predict_unavailable():
        raise HTTPException(
            status_code=503,
            detail='python-multipart is required for file uploads. Install it with: pip install python-multipart',
        )
