# NeuroSight AI

NeuroSight AI is a medical-imaging codebase for MRI-based Alzheimer-related classification. The repository contains two separate runtime surfaces: a Python FastAPI backend that performs ONNX inference, and a Qt/C++ desktop application that also performs ONNX Runtime inference directly inside the client. In addition, the repo includes a research-style data pipeline, training/export scripts, notebooks, tests, and the tracked model weights.

The project is intentionally local-first. There is no Docker support in the repository anymore, and the cleaned workspace is meant to stay source-only: code, models, data samples, notebooks, and documentation.

## What Is Actually In This Repository

- `src/backend/` contains the FastAPI service with `/health` and `/predict`.
- `src/ai_engine/` contains the Python ONNX inference layer and compatibility wrappers.
- `src/cpp_app/NeuroSightAI_Desktop/` contains the Qt desktop client and its CMake project.
- `src/data_pipeline/` contains the reusable ETL pipeline extracted from notebook work.
- `scripts/` contains model export and model generation helpers.
- `tests/` contains import and service tests.
- `models/weights/` stores the tracked model artifacts.
- `data/` stores sample MRI images and local data assets.
- `notebooks/` stores exploratory analysis and audit notebooks.

## Architecture

The codebase is organized as a set of thin layers around a shared ONNX model artifact.

```text
Python backend
  FastAPI app -> prediction service -> ONNX inference engine

Desktop client
  Qt UI -> ModelHandler -> ONNX Runtime session

Research utilities
  data pipeline -> notebooks -> scripts -> trained/exported model files
```

### Python Backend Flow

The backend is defined in `src/backend/app.py` and does the following:

- creates a FastAPI app
- enables permissive CORS
- loads a model through `src.ai_engine.loader.load_model()`
- exposes `GET /health`
- exposes `POST /predict` when multipart file uploads are available

The backend uses `PredictionService` to save an uploaded file to a temporary path, run inference, and then delete the temporary file.

### Python Inference Layer

The ONNX path is implemented in `src/ai_engine/`:

- `factory.py` resolves the model path and creates an `onnxruntime.InferenceSession`
- `engine.py` defines an `InferenceEngine` protocol and the `OnnxInferenceEngine` implementation
- `engine.py` preprocesses images to `224x224`, normalizes them with ImageNet-style statistics, and returns a softmaxed `PredictionResult`
- `domain.py` defines the `PredictionResult` dataclass
- `loader.py` is a thin compatibility wrapper so the backend can keep a stable import path

### Desktop Client Flow

The desktop app is in `src/cpp_app/NeuroSightAI_Desktop/` and is not a wrapper around the Python backend. It loads ONNX Runtime directly in C++.

- `main.cpp` starts the Qt application and opens the main window
- `mainwindow.*` manages the UI workflow, drag-and-drop, shortcuts, progress state, and result display
- `modelhandler.*` loads `best_model.onnx`, runs ONNX inference, computes probabilities, builds a Grad-CAM-style heatmap overlay, and emits the result back to the UI

The desktop app uses a workflow state machine with these states:

- `AwaitingImage`
- `ImageReady`
- `Analyzing`
- `ResultReady`
- `ErrorState`

## Design Patterns That Are Actually Present

- **Factory**: `src/ai_engine/factory.py` encapsulates model-session creation.
- **Protocol / Strategy Boundary**: `src/ai_engine/engine.py` defines `InferenceEngine` as a protocol and provides `OnnxInferenceEngine` as the concrete implementation.
- **Facade**: `src/backend/app.py` keeps the HTTP surface thin and delegates work outward.
- **Service Layer**: `src/backend/services/prediction_service.py` owns upload-to-file and file-to-prediction orchestration.
- **DTO / Domain Model**: `src/ai_engine/domain.py` and `src/backend/schemas.py` define the data passed between layers.
- **UI State Machine**: `src/cpp_app/NeuroSightAI_Desktop/src/mainwindow.*` drives the desktop workflow through explicit states.

## Important Truths And Caveats

This section exists because the source code contains a few real-world mismatches that should not be glossed over.

1. **The backend default model path is not the same as the tracked model location.**
   - `src/backend/app.py` defaults to `models/model.onnx`.
   - The repository actually tracks weights under `models/weights/`.
   - If you run the backend, set `MODEL_PATH` to a real ONNX file path.

2. **The Python engine and the desktop app use different label strings.**
   - Python inference uses `Normal`, `Mild`, `Moderate`, `Severe` in `src/ai_engine/engine.py`.
   - The C++ app uses `NonDemented`, `VeryMildDemented`, `MildDemented`, `ModerateDemented` in `modelhandler.cpp`.
   - The documentation should not pretend those labels are unified.

3. **The desktop client does not call the backend at runtime.**
   - The C++ code loads ONNX directly.
   - The backend is a separate runtime path for API-based use.

4. **File upload support depends on `python-multipart`.**
   - If that package is unavailable, the backend exposes a 503 message for upload-based prediction.

5. **There is no Docker workflow in this repository now.**
   - Dockerfile and compose files were intentionally removed.

## Local Development Setup

### 1. Create a Conda Environment

Use Anaconda or Miniconda to create an isolated Python environment.

```bash
conda create -n neurosight python=3.10 -y
conda activate neurosight
pip install -r requirements.txt
```

If you prefer `venv`, that also works, but the repository documentation now favors Conda because it is the cleanest way to reproduce the Python runtime.

### 2. Prepare a Valid ONNX Model File

The backend and desktop app both expect an ONNX model file to exist somewhere on disk.

- For the backend, set `MODEL_PATH` to the ONNX file you want to load.
- For the desktop app, place `best_model.onnx` next to the executable or keep the repository layout so the fallback path can find `models/weights/best_model.onnx`.

### 3. Run The FastAPI Backend

```bash
python -m uvicorn src.backend.app:app --reload --host 0.0.0.0 --port 8000
```

The backend provides:

- `GET /health`
- `POST /predict` with multipart file upload

The health response reports whether the model was loaded successfully.

### 4. Run The Desktop Client

Open `src/cpp_app/NeuroSightAI_Desktop/CMakeLists.txt` in Qt Creator or build it from the command line.

```bash
cd src/cpp_app/NeuroSightAI_Desktop
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
```

The checked-in CMake project expects:

- Qt 6
- ONNX Runtime files under `third_party/onnxruntime/`
- a working local model file

On Windows, the CMake file copies `onnxruntime.dll` next to the executable after build.

### 5. Run Tests

```bash
python -m pytest tests -v
```

## Data Pipeline

`src/data_pipeline/etl.py` exposes the public data-preparation entry point used by scripts and notebooks. The implementation in `src/data_pipeline/impl.py` is more specialized than a generic loader; it currently contains:

- CSV or Excel metadata loading
- iterative imputation with scikit-learn
- patient-aware grouping logic
- class balancing with `WeightedRandomSampler`
- image augmentation and normalization
- cached in-memory image loading for faster iteration

That pipeline is useful for the research workflow, but it is not the same thing as the runtime API.

## Scripts

- `scripts/export_to_onnx.py` exports the trained PyTorch model to ONNX.
- `scripts/generate_best_model.py` creates or regenerates the model checkpoint used by the project.

## Documentation And Notebook Material

- `notebooks/01_data_audit.ipynb` contains data-audit work.
- `notebooks/NeuroSight_Analysis.ipynb` contains analysis and experimentation work.
- `notebooks/reports/audit_report.md` records the audit output.

## What This Project Is For

The repository is best understood as a compact medical-imaging engineering workspace with three purposes:

1. train or regenerate a model offline
2. run inference through a Python API
3. run the same model through a native Qt desktop client

The architecture is intentionally simple enough to inspect, yet modular enough that the model layer, HTTP layer, UI layer, and preprocessing layer can evolve independently.

## License

MIT License. See [LICENSE](LICENSE).
