# NeuroSight AI

NeuroSight AI is a local, offline-first medical imaging project for classifying Alzheimer-related MRI scans. The repository combines a Python inference backend, a Qt desktop client, and ONNX-based model execution so the full workflow can run without cloud services or deployment overhead.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![C++ Version](https://img.shields.io/badge/c%2B%2B-17-blue)

## Purpose

The project exists to provide a reproducible research and development environment for MRI-based classification. Its focus is practical rather than infrastructure-heavy: load a trained ONNX model, expose it through a small FastAPI service, and consume it from a native Qt desktop application.

## Architecture

The codebase is organized as a layered application with clear boundaries:

```text
Qt Desktop App (C++/Qt)
  ↓
FastAPI Backend (HTTP facade)
  ↓
Prediction Service (file handling and orchestration)
  ↓
ONNX Inference Engine (model execution)
  ↓
Trained Model (models/weights/best_model.onnx)
```

### Main layers

- `src/cpp_app/NeuroSightAI_Desktop/` contains the native desktop application built with Qt and CMake.
- `src/backend/` exposes the prediction workflow through FastAPI.
- `src/ai_engine/` owns model loading, preprocessing, and ONNX runtime execution.
- `src/data_pipeline/` provides dataset preparation utilities.
- `scripts/` contains model export and model generation helpers.
- `tests/` validates backend imports and prediction service behavior.

## Design Patterns

The implementation uses a small set of patterns that match the actual code:

- **Factory**: `src/ai_engine/factory.py` creates the ONNX runtime session and returns a ready-to-use inference engine.
- **Protocol / Strategy boundary**: `src/ai_engine/engine.py` defines the `InferenceEngine` contract, allowing the prediction layer to depend on an interface instead of a concrete runtime.
- **Service Layer**: `src/backend/services/prediction_service.py` handles temporary file creation and delegates prediction work to the engine.
- **Facade**: `src/backend/app.py` provides the HTTP surface with `/health` and `/predict` endpoints.
- **DTO / Domain Model**: `src/ai_engine/domain.py` and `src/backend/schemas.py` define the data exchanged across layers.

The result is a separation between transport, orchestration, and model execution. That keeps the code testable and makes it easier to swap runtimes or extend the desktop client without rewriting the backend.

## Technology Stack

| Component | Technology | Role |
|---|---|---|
| Backend API | FastAPI | Exposes health and prediction endpoints |
| Inference Runtime | ONNX Runtime | Executes the exported model locally |
| Python Environment | Anaconda / Conda | Isolated development setup |
| Desktop App | C++17 / Qt | Native local user interface |
| Build System | CMake 3.16+ | Builds the Qt desktop application |
| Model Assets | ONNX / PyTorch | Stores trained weights and exported inference model |

## Repository Layout

```text
NeuroSight_AI/
├── README.md
├── LICENSE
├── requirements.txt
├── data/
├── docs/
├── models/
├── notebooks/
├── scripts/
├── src/
└── tests/
```

### Key source folders

- `src/backend/app.py` wires the FastAPI app, CORS setup, and prediction endpoint.
- `src/backend/services/prediction_service.py` manages temporary uploads and prediction calls.
- `src/ai_engine/factory.py` loads the ONNX model and chooses the available execution provider.
- `src/ai_engine/engine.py` preprocesses input images and turns model output into a `PredictionResult`.
- `src/cpp_app/NeuroSightAI_Desktop/CMakeLists.txt` configures the Qt desktop build.

## Local Development Setup

### 1. Python environment with Anaconda

```bash
conda create -n neurosight python=3.11 -y
conda activate neurosight
pip install -r requirements.txt
```

### 2. Run the backend

```bash
python -m uvicorn src.backend.app:app --reload --host 127.0.0.1 --port 8000
```

The backend exposes:

- `GET /health` for readiness checks
- `POST /predict` for MRI image classification

### 3. Build the desktop application with CMake and Qt

Requirements for the desktop client:

- C++17 toolchain
- CMake 3.16 or newer
- Qt 6.x
- ONNX Runtime libraries in `src/cpp_app/NeuroSightAI_Desktop/third_party/onnxruntime/`

Build steps:

```bash
cd src/cpp_app/NeuroSightAI_Desktop
cmake -S . -B build
cmake --build build --config Release
```

On Windows, Visual Studio 2022 is the intended generator. On Linux and macOS, use the Qt-supported C++ compiler installed on the machine.

### 4. Launch the desktop app

After a successful build, run the generated executable from the `build` directory. The desktop client expects the backend to be available locally and the exported model to be present at `models/weights/best_model.onnx`.

## Project Data Flow

1. An MRI image is selected in the desktop application or submitted to the backend.
2. The backend stores the upload temporarily and passes the file path to the inference engine.
3. `OnnxInferenceEngine` preprocesses the image, runs the model, and produces a prediction.
4. The response is converted to a stable schema and returned to the client.

## Testing

```bash
python -m pytest tests -v
```

The tests focus on module import health and the prediction service workflow, which are the most important integration points for this repository.

## Notes

- The project is intentionally kept free of Docker and deployment-specific packaging.
- Generated build artifacts and caches are ignored through `.gitignore`.
- Model weights in `models/weights/` are treated as project assets and should remain under version control if they are part of the reproducible workflow.

## License

MIT License. See [LICENSE](LICENSE) for details.
