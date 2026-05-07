# 🧠 NeuroSight AI

**Intelligent Early Detection System for Alzheimer's Disease using Deep Learning & Medical Imaging**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![C++ Version](https://img.shields.io/badge/c%2B%2B-17-blue)

---

## 📋 Project Overview

NeuroSight AI is an intelligent CAD (Computer-Aided Diagnosis) system designed to assist radiologists in detecting early signs of Alzheimer's disease from MRI scans. Built with EfficientNet transfer learning and explainable AI (Grad-CAM heatmaps), the system provides fast, accurate, and interpretable diagnoses in a secure, offline-first architecture.

**Core Values:**
- 🔒 **Privacy-First**: 100% local processing—no patient data leaves the device
- ⚡ **Fast**: Diagnosis results in under 5 seconds
- 🎯 **Accurate**: EfficientNet transfer learning on 6,400+ MRI images
- 🔍 **Explainable**: Grad-CAM visualizations show model reasoning
- 🏗️ **Professional**: Production-ready architecture with testable components

---

## 🏛️ Architecture

NeuroSight AI follows a **layered, decoupled architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│   Desktop Application (C++ / Qt)        │  User Interface
├─────────────────────────────────────────┤
│   REST API (FastAPI / Uvicorn)          │  HTTP Layer
├─────────────────────────────────────────┤
│   Business Logic (Python Services)      │  Application Layer
├─────────────────────────────────────────┤
│   AI Engine (ONNX Runtime)              │  Inference Layer
├─────────────────────────────────────────┤
│   Trained Model (EfficientNet)          │  ML Layer
└─────────────────────────────────────────┘
```

**Design Patterns Used:**
- **Factory Pattern**: `src/ai_engine/factory.py` — Creates inference engine instances
- **Strategy Pattern**: `src/ai_engine/engine.py` — Multiple inference strategies
- **Service Layer**: `src/backend/services/prediction_service.py` — Orchestrates predictions
- **DTO/Domain Objects**: `src/ai_engine/domain.py`, `src/backend/schemas.py` — Type-safe data transfer
- **Facade Pattern**: `src/backend/app.py` — Clean REST API surface

**Benefit**: Each layer is independently testable, replaceable, and maintainable.

---

## 📦 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **AI Model** | PyTorch / EfficientNet | Transfer learning on MRI classification |
| **Model Export** | ONNX | Cross-platform, framework-agnostic inference |
| **Backend API** | FastAPI | REST endpoints for predictions |
| **Desktop UI** | C++ 17 / Qt 6.x | Native, lightweight interface for radiologists |
| **Inference Runtime** | ONNX Runtime | Fast CPU/GPU inference in C++ and Python |
| **Build System** | CMake | Cross-platform C++ build orchestration |
| **Python Runtime** | Anaconda / Conda | Isolated Python environment management |
| **Dataset** | Kaggle MRI Dataset | 6,400 images, 4 dementia levels |

---

## 📂 Project Structure

```
NeuroSight_AI/
├── README.md                    # Main documentation (this file)
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
│
├── src/                         # Main source code
│   ├── ai_engine/              # AI model loading and inference
│   │   ├── factory.py          # Model engine factory
│   │   ├── engine.py           # Inference strategies
│   │   ├── inference.py        # High-level inference API
│   │   ├── loader.py           # Model weight loading
│   │   ├── domain.py           # Data structures
│   │   └── __init__.py
│   │
│   ├── backend/                # FastAPI REST backend
│   │   ├── app.py              # FastAPI application and routes
│   │   ├── schemas.py          # Pydantic request/response models
│   │   ├── services/           # Business logic services
│   │   │   ├── prediction_service.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   ├── cpp_app/                # Qt Desktop Application (C++)
│   │   ├── NeuroSightAI_Desktop/
│   │   │   ├── CMakeLists.txt  # CMake build configuration
│   │   │   ├── NeuroSightAI.pro # Qt project file (alternative to CMake)
│   │   │   ├── src/            # C++ source files
│   │   │   │   ├── main.cpp
│   │   │   │   ├── mainwindow.cpp/h
│   │   │   │   └── modelhandler.cpp/h
│   │   │   ├── ui/             # Qt Designer UI files
│   │   │   ├── resources/      # Images, stylesheets
│   │   │   ├── third_party/    # ONNX Runtime includes
│   │   │   └── build/          # CMake build output (generated)
│   │   └── README.md
│   │
│   ├── data_pipeline/          # Data preprocessing
│   │   ├── etl.py
│   │   ├── impl.py
│   │   └── __init__.py
│   │
│   ├── python/                 # Additional Python utilities
│   │   ├── inference.py
│   │   └── __init__.py
│   │
│   ├── cli/                    # Command-line interface
│   │   └── manage.py
│   │
│   └── __init__.py
│
├── models/                      # Trained model weights
│   └── weights/
│       ├── best_model.pt       # PyTorch checkpoint
│       └── best_model.onnx     # ONNX model (for deployment)
│
├── scripts/                     # Utility scripts
│   ├── export_to_onnx.py       # Convert PyTorch → ONNX
│   └── generate_best_model.py  # Model training/generation
│
├── notebooks/                   # Jupyter notebooks for experimentation
│   ├── 01_data_audit.ipynb
│   ├── NeuroSight_Analysis.ipynb
│   └── reports/
│       ├── audit_report.md
│       └── figures/
│
├── tests/                       # Unit and integration tests
│   ├── test_backend_import.py
│   ├── test_data_pipeline_import.py
│   └── test_prediction_service.py
│
├── data/                        # Local dataset storage
│   └── samples/                # Sample MRI images
│
└── docs/                        # Documentation (reserved for academic papers, guides)
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (preferably via Anaconda)
- **CMake 3.20+** (for building C++ desktop app)
- **Qt 6.x** (for desktop UI; can be installed via Qt Online Installer or package manager)
- **ONNX Runtime** (automatically installed via pip)
- **Git**

### Step 1: Set Up Python Environment

#### Option A: Using Anaconda (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/NeuroSight_AI.git
cd NeuroSight_AI

# Create Anaconda environment
conda create -n neurosight python=3.11 -y
conda activate neurosight

# Install Python dependencies
pip install -r requirements.txt
```

#### Option B: Using venv

```bash
git clone https://github.com/your-org/NeuroSight_AI.git
cd NeuroSight_AI

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
# Test Python backend imports
python -m pytest tests/ -v

# Test backend API startup
python -m uvicorn src.backend.app:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

API will be available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

---

## 🖥️ Building the Desktop Application (C++ / Qt)

### Prerequisites for Desktop Build

- **Windows**: Visual Studio 2022 (MSVC 2022) or MinGW
- **Linux/macOS**: GCC/Clang with standard development tools
- **Qt 6.x**: [Download Qt](https://www.qt.io/download-open-source) or install via:
  - **Linux (Ubuntu/Debian)**: `sudo apt-get install qt6-base-dev qt6-tools-dev`
  - **macOS**: `brew install qt6`
  - **Windows**: Use Qt Online Installer or `vcpkg install qt6`

### Build Steps

```bash
cd src/cpp_app/NeuroSightAI_Desktop

# Create build directory
mkdir build
cd build

# Configure with CMake
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build the application
cmake --build . --config Release

# On Windows (Visual Studio):
cmake --build . --config Release --verbose

# On Linux/macOS:
cmake --build . -- -j$(nproc)
```

**Alternatively (using Qt Creator):**
```bash
# Open project in Qt Creator
cd src/cpp_app/NeuroSightAI_Desktop
# File → Open Project → Select NeuroSightAI.pro or CMakeLists.txt
# Click "Build" or press Ctrl+B
```

### Run the Desktop Application

```bash
# After successful build, run the executable
# Windows:
./Release/NeuroSightAI.exe

# Linux/macOS:
./NeuroSightAI
```

**Required for Runtime:**
- The backend FastAPI server must be running on `http://localhost:8000`
- Model weights must be present in `models/weights/best_model.onnx`

---

## 🧪 Testing

### Run All Tests

```bash
# Activate environment
conda activate neurosight  # or source venv/bin/activate

# Run pytest suite
python -m pytest tests/ -v --tb=short
```

### Individual Test Files

```bash
# Test backend imports
python -m pytest tests/test_backend_import.py -v

# Test prediction service
python -m pytest tests/test_prediction_service.py -v

# Test data pipeline
python -m pytest tests/test_data_pipeline_import.py -v
```

---

## 🔄 Development Workflow

### Training a New Model

```bash
# Preprocess data
python src/data_pipeline/etl.py --input raw_data/ --output data/processed/

# Train the model (see notebooks/NeuroSight_Analysis.ipynb)
python scripts/generate_best_model.py --epochs 50 --batch-size 32

# Export to ONNX for deployment
python scripts/export_to_onnx.py --input models/best_model.pt --output models/weights/best_model.onnx
```

### Running Backend API in Development

```bash
# With auto-reload
python -m uvicorn src.backend.app:app --reload --port 8000

# With debug logging
LOGLEVEL=DEBUG python -m uvicorn src.backend.app:app --reload --port 8000
```

### Accessing API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📊 API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Predict MRI Image

```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@path/to/mri_image.jpg"
```

**Response:**
```json
{
  "prediction": "Mild Dementia",
  "confidence": 0.94,
  "class": 2,
  "heatmap_url": "/static/heatmap_xyz.png"
}
```

---

## 🔒 Privacy & Security

- ✅ **No Cloud Storage**: All patient data remains on-premises
- ✅ **No Telemetry**: No tracking or analytics
- ✅ **Offline-First**: Desktop app works without internet
- ✅ **Encrypted Communication**: HTTPS recommended for enterprise deployments
- ✅ **HIPAA Considerations**: Suitable for healthcare environments with proper compliance setup

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

**Copyright © 2026 Wilfried TSETSE & Leila KHEZAZ**

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** changes with clear messages: `git commit -m "Add your feature"`
4. **Push** to your fork: `git push origin feature/your-feature`
5. **Submit** a Pull Request with a description

### Code Standards

- Python: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with Black formatter
- C++: Follow C++17 standards, aim for readable and maintainable code
- Tests: All new features must include unit tests
- Documentation: Update README and docstrings as needed

---

## 📚 Documentation

- **[C++ Build Guide](src/cpp_app/README.md)** — Detailed desktop app build instructions
- **[C++ Setup Guide](src/cpp_app/NeuroSightAI_Desktop/SETUP_GUIDE.md)** — Environment setup for C++ development
- **[Data Audit Report](notebooks/reports/audit_report.md)** — Dataset analysis and statistics

---

## 🐛 Troubleshooting

### Python Dependencies Issue

```bash
# Ensure pip is up-to-date
pip install --upgrade pip setuptools wheel

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Qt Build Fails

```bash
# Verify Qt installation
qmake --version
cmake --version

# On Windows with Visual Studio, explicitly set generator:
cd build
cmake .. -G "Visual Studio 17 2022"
```

### ONNX Runtime Issues

```bash
# Install latest ONNX Runtime
pip install --upgrade onnxruntime

# For GPU acceleration (CUDA):
pip install onnxruntime-gpu
```

### Backend API Connection Issues

```bash
# Verify FastAPI is running
curl http://localhost:8000/health

# Check if port 8000 is in use
netstat -an | grep 8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows
```

---

## 📞 Support & Contact

For questions, issues, or discussions:

- **GitHub Issues**: [Open an issue](https://github.com/your-org/NeuroSight_AI/issues)
- **Email**: wilfried.tsetse@ensa-safi.ac.ma

---

## 🎯 Roadmap

- [ ] GPU acceleration with TensorRT
- [ ] Web-based UI (React/Vue.js)
- [ ] Multi-model ensemble support
- [ ] DICOM file format support
- [ ] Continuous integration/deployment pipeline
- [ ] Advanced analytics dashboard

---

## 👥 Project Authors

**Developed by Engineering Students (GIIA - 2e year):**

- 👨‍💻 **Wilfried TSETSE** — AI Engine & Backend Development
- 👩‍💻 **Leila KHEZAZ** — Data Pipeline & Desktop Application

**Institution**: ENSA Safi (Ecole Nationale des Sciences Appliquées)  
**Supervisor**: Mme Manal ZETTAM

---

**Made with ❤️ at ENSA Safi** 🇲🇦

*NeuroSight AI is an academic prototype. It is not a certified medical device and should not be used for actual clinical diagnosis without proper regulatory certification.*
