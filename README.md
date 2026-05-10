# 🧠 NeuroSight AI

**Intelligent Early Detection System for Alzheimer's Disease using Deep Learning & Medical Imaging**
---

## 📋 Project Overview

NeuroSight AI is an intelligent CAD (Computer-Aided Diagnosis) system designed to assist radiologists in detecting early signs of Alzheimer's disease from MRI scans. Built with EfficientNet transfer learning and explainable AI (Grad-CAM heatmaps), the system provides fast, accurate, and interpretable diagnoses in a secure, offline-first architecture.

The system classifies MRI brain scans into **four dementia stages**:

| Class | Label | Clinical Meaning |
|-------|-------|-----------------|
| 0 | Non Demented | No signs of cognitive decline |
| 1 | Very Mild Demented | Earliest detectable changes |
| 2 | Mild Demented | Noticeable memory and cognitive issues |
| 3 | Moderate Demented | Significant functional impairment |

**Core Values:**
- 🔒 **Privacy-First**: 100% local processing — no patient data leaves the device
- ⚡ **Fast**: Diagnosis results in under 5 seconds
- 🎯 **Accurate**: EfficientNet transfer learning on 6,400+ MRI images
- 🔍 **Explainable**: Grad-CAM visualizations highlight model reasoning
- 🏗️ **Professional**: Production-ready architecture with decoupled, testable components

> ⚠️ **Medical Disclaimer**: NeuroSight AI is an academic prototype. It is not a certified medical device and must not be used for clinical diagnosis without proper regulatory certification.

***

## 🏛️ Architecture

NeuroSight AI follows a **layered, decoupled architecture** with clear separation of concerns between the AI engine, the backend API, and the desktop UI.

```
┌────────────────────────────────────────────────────────────────┐
│              Desktop Application (C++ / Qt 6)                  │
│   LoginWindow · RegisterWindow · MainWindow · ModelHandler     │
│   DatabaseManager · SessionManager · AuthUtils                 │
├────────────────────────────────────────────────────────────────┤
│                   ONNX Runtime (C++ side)                      │
│       Direct in-process inference — no HTTP round-trip         │
├──────────────────────────┬─────────────────────────────────────┤
│    REST API (FastAPI)    │        AI Engine (Python)            │
│  app.py · schemas.py     │  engine.py · factory.py             │
│  prediction_service.py   │  inference.py · loader.py           │
├──────────────────────────┴─────────────────────────────────────┤
│               Trained Model (EfficientNet B0)                  │
│       best_model.pt (PyTorch) → best_model.onnx (ONNX)        │
├────────────────────────────────────────────────────────────────┤
│              Local SQLite Database (neurosight.db)             │
│  patients · mri_scans · diagnoses · heatmaps · predictions     │
│  users · login_logs · audit_logs · analysis_reports            │
└────────────────────────────────────────────────────────────────┘
```

### Two Inference Paths

The project implements **two independent inference paths**, which can be used interchangeably depending on the deployment context:

| Path | Stack | Use case |
|------|-------|----------|
| **C++ Direct** | Qt + ONNX Runtime C++ | Desktop app — offline, no server needed |
| **Python REST** | FastAPI + ONNX Runtime Python | API server — for integration or testing |

In the desktop app, inference is handled **directly in C++** via `ModelHandler` and the ONNX Runtime C++ API — no Python process or HTTP call is required at runtime.

***

## 🎨 Design Patterns

| Pattern | File | Role |
|---------|------|------|
| **Factory** | `src/ai_engine/factory.py` | Creates inference engine instances from config |
| **Strategy** | `src/ai_engine/engine.py` | Swappable inference backends (ONNX, PyTorch) |
| **Service Layer** | `src/backend/services/prediction_service.py` | Orchestrates prediction + heatmap pipeline |
| **DTO / Domain Objects** | `src/ai_engine/domain.py`, `src/backend/schemas.py` | Type-safe data transfer between layers |
| **Facade** | `src/backend/app.py` | Single clean REST surface over the AI engine |
| **Singleton** | `DatabaseManager::instance()`, `SessionManager::instance()` | Single shared DB and session state in Qt app |
| **Repository** | `DatabaseManager` | Centralized data access layer for all SQL operations |

***

## 📦 Tech Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **AI Model** | PyTorch / EfficientNet B0 | 2.x | Transfer learning on MRI classification |
| **Model Export** | ONNX | 1.x | Cross-platform, framework-agnostic model format |
| **Inference Runtime** | ONNX Runtime | 1.20.1 | Fast CPU inference in both C++ and Python |
| **Backend API** | FastAPI + Uvicorn | latest | REST endpoints for Python-side predictions |
| **Desktop UI** | Qt 6.x + C++17 | 6.x | Native offline GUI for radiologists |
| **Build System** | CMake | 3.20+ | Cross-platform C++ build orchestration |
| **Database** | SQLite (via Qt SQL) | 3.x | Local persistent storage, no server required |
| **Explainability** | Grad-CAM | — | Saliency heatmaps overlaid on MRI scans |
| **Python Runtime** | Anaconda / Conda | — | Isolated environment management |
| **Dataset** | Kaggle MRI Dataset | — | 6,400 images across 4 dementia levels |

***

## 📂 Project Structure

```
NeuroSight_AI/
├── .gitignore
├── LICENSE                          # MIT License
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
│
├── Database/                        # Database design artifacts
│   ├── schema/
│   │   ├── script.sql              # Full SQLite schema (DDL)
│   │   └── test_accounts.sql       # Seed data for testing
│   └── uml/
│       ├── class_diagram.puml
│       ├── entity-relationship_diagram.puml
│       ├── sequence_diagram.puml
│       └── use_case.puml
│
├── notebooks/
│   └── NeuroSight_Analysis.ipynb   # Training, EDA, evaluation notebook
│
├── scripts/
│   ├── export_to_onnx.py           # Convert PyTorch → ONNX
│   └── generate_best_model.py      # Model training entry point
│
├── models/                          # Model weights (not committed — see note)
│   └── weights/
│       ├── best_model.pt           # PyTorch checkpoint
│       ├── best_model.onnx         # ONNX deployment model
│       └── best_model.onnx.data    # ONNX external data file
│
└── src/
    ├── __init__.py
    │
    ├── ai_engine/                   # Core AI module (Python)
    │   ├── domain.py               # Data classes: PredictionResult, ModelInput
    │   ├── engine.py               # Abstract inference engine + ONNX impl
    │   ├── factory.py              # Engine factory (creates engine from config)
    │   ├── inference.py            # High-level API: preprocess → infer → postprocess
    │   ├── loader.py               # Model weight loading utilities
    │   └── __init__.py
    │
    ├── backend/                     # FastAPI REST server (Python)
    │   ├── app.py                  # FastAPI app, routes, CORS, startup
    │   ├── schemas.py              # Pydantic request/response schemas
    │   ├── services/
    │   │   ├── prediction_service.py  # Orchestrates inference + Grad-CAM
    │   │   └── __init__.py
    │   └── __init__.py
    │
    ├── cli/
    │   └── manage.py               # CLI management commands
    │
    ├── data_pipeline/               # Data preprocessing
    │   ├── etl.py                  # Extract-Transform-Load pipeline
    │   ├── impl.py                 # Transformation implementations
    │   └── __init__.py
    │
    ├── python/                      # Python inference utilities
    │   ├── inference.py            # Standalone inference script
    │   └── __init__.py
    │
    └── cpp_app/
        ├── README.md
        └── NeuroSightAI_Desktop/
            ├── CMakeLists.txt          # CMake build config
            ├── NeuroSightAI.pro        # Qt Creator project file
            ├── config.ini.example      # Runtime config template
            ├── BUILD_VS2022.md         # Windows build guide
            ├── SETUP_GUIDE.md          # Full environment setup guide
            ├── DATABASE_AUTH_INTEGRATION.md
            │
            ├── src/                    # C++ source files
            │   ├── main.cpp
            │   ├── mainwindow.cpp/h    # Main 4-step workflow window
            │   ├── loginwindow.cpp/h   # Login screen
            │   ├── registerwindow.cpp/h
            │   ├── modelhandler.cpp/h  # ONNX inference + Grad-CAM
            │   ├── authutils.cpp/h     # Password hashing (SHA-256)
            │   ├── sessionmanager.cpp/h
            │   └── db/
            │       ├── databasemanager.cpp  # All SQL operations
            │       └── databasemanager.h
            │
            ├── ui/
            │   └── mainwindow.ui       # Qt Designer UI layout
            │
            ├── resources/
            │   ├── icon.png
            │   ├── resources.qrc       # Qt resource bundle
            │   └── style.qss           # App-wide QSS stylesheet
            │
            └── third_party/
                └── onnxruntime/        # ONNX Runtime 1.20.1 headers + lib
                    ├── include/
                    └── lib/
```

> **Note on model weights**: `*.onnx`, `*.onnx.data`, and `*.pt` files are excluded from Git due to their size. Place them in `models/weights/` before building, or re-export them via `scripts/export_to_onnx.py`.

***

## 🔄 Clinical Workflow

The desktop application guides the user through a **4-step neuroscience-guided workflow**:

```
Step 1 — Acquire Scan          Step 2 — Review Input
┌──────────────────────┐       ┌──────────────────────┐
│  Upload MRI (.jpg /  │──────▶│  Visual validation   │
│  .png / .jpeg)       │       │  of the loaded scan  │
└──────────────────────┘       └──────────┬───────────┘
                                           │
Step 4 — Interpret Outcome     Step 3 — Run Inference
┌──────────────────────┐       ┌──────────────────────┐
│  Confidence score    │◀──────│  ONNX Runtime        │
│  Disease stage label │       │  preprocessing       │
│  Grad-CAM heatmap    │       │  + EfficientNet fwd  │
│  History saved to DB │       │  pass + Grad-CAM     │
└──────────────────────┘       └──────────────────────┘
```

### Step-by-step details

**Step 1 — Acquire Scan**
The user drags and drops (or browses for) an MRI image. The filename is parsed to extract the `patient_code` (e.g., `OAS1_0028_MR1`), which serves as the anonymous patient identifier throughout the session.

**Step 2 — Review Input**
The loaded scan is displayed in the Visual Validation panel. The user confirms the image quality before running inference.

**Step 3 — Run Inference**
`ModelHandler` takes over:
1. Loads the ONNX model via ONNX Runtime C++ API
2. Preprocesses the image: resize to 224×224, normalize to `[0,1]`, convert to `NCHW` tensor
3. Runs the forward pass → raw logits → softmax → confidence scores per class
4. Generates the **Grad-CAM heatmap** by computing the gradient of the top class score with respect to the last convolutional layer activations
5. Overlays the heatmap (jet colormap) onto the original MRI image

**Step 4 — Interpret Outcome**
The interpretation panel displays:
- **Disease Stage**: Non Demented / Very Mild Demented / Mild Demented / Moderate Demented
- **Confidence**: percentage score of the predicted class
- **Grad-CAM Heatmap**: color-coded saliency map showing which brain regions influenced the diagnosis
- The result is **saved to the local SQLite database** via a full transactional pipeline

***

## 🗄️ Database Schema

The local SQLite database (`neurosight.db`) stores the complete clinical history in a normalized schema:

```
patients ──────────────────────── mri_scans
  patient_id (PK)                   scan_id (PK)
  anonymous_code (UNIQUE)           patient_id (FK)
  age_group                         scan_date
  gender                            file_path
  created_at                        file_format (DICOM/NIfTI/JPEG/PNG)
                                    image_dimensions
                                    processing_time_ms

mri_scans ─────────────────────── diagnoses
                                    diagnosis_id (PK)
                                    scan_id (FK)
                                    classification (NonDemented/...)
                                    confidence_score
                                    is_validated
                                    validated_by_user_id (FK → users)
                                    validated_at
                                    radiologist_notes

diagnoses ─────────────────────── heatmaps
                                    heatmap_id (PK)
                                    diagnosis_id (FK, UNIQUE)
                                    heatmap_file_path
                                    algorithm_used (Grad-CAM)
                                    overlay_opacity

diagnoses ─────────────────────── analysis_reports
                                    report_id (PK)
                                    diagnosis_id (FK)
                                    user_id (FK)
                                    pdf_file_path
                                    download_count

users ──────────────────────────── login_logs
  user_id (PK)                      id (PK)
  full_name                         user_id (FK)
  username (UNIQUE)                 login_time
  email (UNIQUE)                    logout_time
  password_hash (SHA-256)
  role (Radiologist/Admin/DataScientist)

                                    audit_logs
                                    log_id (PK)
                                    user_id (FK)
                                    action_type
                                    entity_type
                                    entity_id
                                    logged_at

predictions (denormalized UI cache)
  id (PK)
  user_id (FK)
  patient_name
  prediction_class
  confidence_score
  image_path
  created_at
```

### Key design decisions

- **`predictions` table** is a denormalized cache for the UI History page — avoids multi-table JOINs for fast loading
- **`diagnoses.classification`** uses normalized snake_case values (`NonDemented`, `VeryMildDemented`, etc.) to satisfy the CHECK constraint; the UI displays the human-readable form (`Non Demented`)
- **`PRAGMA foreign_keys = ON`** is enforced at every connection — cascading deletes and referential integrity are guaranteed
- All timestamps use `datetime('now', 'localtime')` for local time consistency
- Passwords are hashed with **SHA-256** via `authutils.cpp` — no plaintext is ever stored

***

## 🔐 Authentication & Session Management

The desktop app implements a full authentication flow:

- **Registration**: `RegisterWindow` calls `DatabaseManager::createUser()` — checks for duplicate username/email, hashes the password, inserts into `users`
- **Login**: `LoginWindow` calls `DatabaseManager::authenticateUser()` — verifies hash, loads `CurrentUser` struct, records `last_login` and `login_logs` entry
- **Session**: `SessionManager` (singleton) holds the active user's `id`, `username`, `role`, and `isLoggedIn` state throughout the app lifetime
- **Role-based visibility**: Admin users see all predictions in history; Radiologist/DataScientist users see only their own entries
- **Logout**: `SessionManager::logout()` clears the session and calls `DatabaseManager::logLogout()` to timestamp the session end in `login_logs`

***

## 🧠 AI Engine Details

### Model: EfficientNet B0

- **Architecture**: EfficientNet B0 with pretrained ImageNet weights (transfer learning)
- **Fine-tuning**: All layers unfrozen after initial head training; trained on 6,400+ MRI images
- **Input**: RGB image resized to `224×224`, normalized to `[0, 1]`
- **Output**: 4-class softmax probabilities
- **Export**: Converted to ONNX format via `torch.onnx.export()` with dynamic batch axis

### Preprocessing Pipeline (C++ side)

```
Raw image (any size, any format)
        ↓
QImage::scaled(224, 224, Qt::IgnoreAspectRatio)
        ↓
Convert pixel values → float [0.0, 1.0]
        ↓
Arrange as NCHW tensor [1, 3, 224, 224]
        ↓
ONNX Runtime Inference → logits [1, 4]
        ↓
Softmax → confidence scores
        ↓
argmax → predicted class
```

### Grad-CAM Heatmap Generation

Grad-CAM (Gradient-weighted Class Activation Mapping) highlights the image regions most influential to the model's prediction:

1. Extract activations from the **last convolutional layer**
2. Compute the gradient of the top class score with respect to those activations
3. Global average pool the gradients → class-specific weights
4. Weighted combination of activation maps → raw heatmap
5. ReLU + normalize to `[0, 1]`
6. Resize to original image dimensions
7. Apply **jet colormap** (blue = low importance → red = high importance)
8. Alpha-blend with original MRI scan at 50% opacity

***

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (via Anaconda recommended)
- **CMake 3.20+**
- **Qt 6.x** (Qt Online Installer or package manager)
- **Visual Studio 2022** (Windows) or GCC/Clang (Linux/macOS)
- **Git**

### Step 1: Clone & Set Up Python Environment

```bash
git clone https://github.com/wekt2k04/NeuroSight_AI.git
cd NeuroSight_AI

# Anaconda (recommended)
conda create -n neurosight_ai_env python=3.11 -y
conda activate neurosight_ai_env
pip install -r requirements.txt
```

### Step 2: Obtain Model Weights

Model weights are not committed to Git due to size. Either:

**Option A — Re-export from the notebook:**
```bash
# Run the training notebook, then export:
python scripts/export_to_onnx.py \
  --input models/weights/best_model.pt \
  --output models/weights/best_model.onnx
```

**Option B — Place pre-trained files manually:**
```
models/weights/best_model.onnx
models/weights/best_model.onnx.data
```

### Step 3: Configure the Desktop App

```bash
cd src/cpp_app/NeuroSightAI_Desktop
cp config.ini.example build_cli/Debug/config.ini
# Edit config.ini: set model_path to the absolute path of best_model.onnx
```

### Step 4: Build the Desktop App (Windows / Visual Studio 2022)

```powershell
cd src\cpp_app\NeuroSightAI_Desktop

# Configure (first time only)
cmake -S . -B build_cli -G "Visual Studio 17 2022" -A x64 `
  -DCMAKE_BUILD_TYPE=Debug

# Build
cmake --build build_cli --config Debug --target NeuroSightAI

# Run
.\build_cli\Debug\NeuroSightAI.exe
```

**Linux / macOS:**
```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -- -j$(nproc)
./build/NeuroSightAI
```

### Step 5 (Optional): Run the Python REST Backend

```bash
conda activate neurosight_ai_env
uvicorn src.backend.app:app --reload --host 0.0.0.0 --port 8000
```

API available at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

***

## 🖥️ Desktop App — First Run

1. Launch `NeuroSightAI.exe`
2. **Register** a new account (role: `Radiologist`, `Admin`, or `DataScientist`)
3. **Login** with your credentials
4. **Upload** an MRI scan (`.jpg`, `.jpeg`, `.png`)
5. **Run inference** — the 4-step workflow completes automatically
6. **View results**: disease stage, confidence score, Grad-CAM heatmap
7. Results are **automatically saved** to the local SQLite database

To inspect the database directly:
```powershell
sqlite3 src\cpp_app\NeuroSightAI_Desktop\build_cli\Debug\neurosight.db
sqlite> SELECT patient_name, prediction_class, confidence_score, created_at FROM predictions ORDER BY created_at DESC;
```

***

## 📊 API Endpoints (Python Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/predict` | Upload MRI image → prediction + heatmap |

### Predict endpoint

```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@path/to/mri_scan.jpg"
```

**Response:**
```json
{
  "prediction": "Mild Demented",
  "confidence": 0.94,
  "class_index": 2,
  "heatmap_url": "/static/heatmap_abc123.png"
}
```

***

## 🔄 Development Workflow

### Train / Retrain the Model

```bash
# 1. Explore data and train in the notebook
jupyter notebook notebooks/NeuroSight_Analysis.ipynb

# 2. Or run training directly
python scripts/generate_best_model.py --epochs 50 --batch-size 32

# 3. Export to ONNX
python scripts/export_to_onnx.py \
  --input models/weights/best_model.pt \
  --output models/weights/best_model.onnx
```

### Rebuild Qt App After Code Changes

```powershell
cd src\cpp_app\NeuroSightAI_Desktop
cmake --build build_cli --config Debug --target NeuroSightAI
.\build_cli\Debug\NeuroSightAI.exe
```

### Reset the Local Database

```powershell
Remove-Item src\cpp_app\NeuroSightAI_Desktop\build_cli\Debug\neurosight.db -Force
# Relaunch the app — schema is recreated automatically on first run
```

***

## 🔒 Privacy & Security

- ✅ **No Cloud**: All patient data is stored locally, never transmitted
- ✅ **No Telemetry**: Zero analytics or tracking
- ✅ **Offline-First**: Desktop app functions without any internet connection
- ✅ **Password hashing**: SHA-256 — no plaintext passwords stored
- ✅ **Audit trail**: Every diagnosis creation is logged in `audit_logs`
- ✅ **Anonymous codes**: Patients are identified by anonymized codes, not personal information
- ✅ **HIPAA-oriented**: Architecture designed to minimize PII exposure

***

## 🐛 Troubleshooting

### ONNX model not found at startup

```
Verify that build_cli/Debug/best_model.onnx exists.
Check config.ini: model_path must point to the .onnx file.
```

### `file_format` CHECK constraint error on save

The `mri_scans` table only accepts `JPEG`, `PNG`, `DICOM`, `NIfTI`.
`.jpg` files are automatically normalized to `JPEG` in `databasemanager.cpp`.
If you see this error after a fresh build, delete `neurosight.db` and restart.

### Qt build fails — Qt not found

```powershell
# Set Qt path explicitly
cmake -S . -B build_cli -G "Visual Studio 17 2022" `
  -DCMAKE_PREFIX_PATH="C:\Qt\6.x.x\msvc2022_64"
```

### Python backend import errors

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --force-reinstall
```

### ONNX Runtime version mismatch

The C++ app uses ONNX Runtime **1.20.1** (headers in `third_party/onnxruntime/`).
Ensure `onnxruntime.dll` in `build_cli/Debug/` matches this version exactly.

***

## 📚 Additional Documentation

- **[C++ Build Guide (VS2022)](src/cpp_app/NeuroSightAI_Desktop/BUILD_VS2022.md)**
- **[Environment Setup Guide](src/cpp_app/NeuroSightAI_Desktop/SETUP_GUIDE.md)**
- **[Database & Auth Integration](src/cpp_app/NeuroSightAI_Desktop/DATABASE_AUTH_INTEGRATION.md)**
- **[Database Schema (SQL)](Database/schema/script.sql)**
- **[UML Diagrams](Database/uml/)**

***

## 🎯 Roadmap

- [ ] PDF report generation from `analysis_reports` table
- [ ] Radiologist validation workflow (`diagnoses.is_validated`)
- [ ] Statistics dashboard (scan distribution, confidence trends)
- [ ] DICOM file format support
- [ ] GPU acceleration via ONNX Runtime CUDA provider
- [ ] Web UI (Vue.js / React) as alternative frontend
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Multi-model ensemble support

***

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** with clear messages following [Conventional Commits](https://www.conventionalcommits.org/)
4. **Push**: `git push origin feature/your-feature`
5. **Submit** a Pull Request with a clear description

**Code standards:**
- Python: PEP 8 + Black formatter
- C++: C++17, readable and maintainable, Qt coding conventions
- All new features must include unit tests where applicable

***

## 📜 License

Licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

**Copyright © 2026 Wilfried TSETSE & Leila KHEZAZ**

***

## 👥 Authors

**Developed by 4th-year Engineering Students (Data Science & AI — GIIA S4):**

- 👨‍💻 **Wilfried TSETSE** — AI Engine, C++ Desktop App, Database Architecture, Backend
- 👩‍💻 **Leila KHEZAZ** — Data Pipeline, Model Training, Explainability (Grad-CAM)

**Institution**: ENSA Safi (École Nationale des Sciences Appliquées de Safi), Morocco
**Supervisor**: Mme Manal ZETTAM

***

**Made with ❤️ at ENSA Safi** 🇲🇦