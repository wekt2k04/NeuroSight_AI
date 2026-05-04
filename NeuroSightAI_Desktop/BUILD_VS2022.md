# Building NeuroSight AI with VS 2022 Developer Command Prompt

## Prerequisites

- **Visual Studio 2022** with MSVC toolchain installed
- **Qt 6.x** (version 18.0+) installed with MSVC binaries
- **Python 3.8+** 
- **CMake 3.16+** (or use qmake)
- **Git** (optional, for version control)

## Setup Steps

### 1. Verify Qt Installation

Find your Qt 6 installation path (typically `C:\Qt\6.x\msvc2022_64` for MSVC 2022).

```powershell
# Example Qt path (adjust to your installation):
$QT_PATH = "C:\Qt\6.x\msvc2022_64"
```

### 2. Create and Activate Python Virtual Environment

```powershell
cd c:\Users\kheza\Downloads\Neurosight_AI\NeuroSightAI_Desktop

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Place Your ONNX Model

Copy your trained model to the project root:

```powershell
# Copy your model.onnx to:
# c:\Users\kheza\Downloads\Neurosight_AI\NeuroSightAI_Desktop\model.onnx
copy path\to\your\model.onnx model.onnx
```

## Build & Run

### Option A: Using CMake (Recommended)

1. **Open VS 2022 Developer Command Prompt** (search "Developer Command Prompt for VS 2022")

2. **Navigate to project:**

```powershell
cd c:\Users\kheza\Downloads\Neurosight_AI\NeuroSightAI_Desktop
```

3. **Create build directory and configure:**

```powershell
# Set your Qt path
set QT_PATH=C:\Qt\6.x\msvc2022_64

# Create build folder
mkdir build
cd build

# Configure with CMake (using Ninja or NMake)
cmake .. -G "NMake Makefiles" -DCMAKE_PREFIX_PATH=%QT_PATH% -DCMAKE_BUILD_TYPE=Release
```

Or with Visual Studio generator (creates .sln file):

```powershell
cmake .. -G "Visual Studio 17 2022" -DCMAKE_PREFIX_PATH=%QT_PATH%
```

4. **Build:**

```powershell
# With NMake Makefiles:
cmake --build . --config Release

# Or with Visual Studio (after generating .sln):
cmake --build . --config Release
# Then open NeuroSightAI.sln in Visual Studio and build
```

5. **Run the executable:**

```powershell
# Navigate to release folder
cd Release

# Set Python path so app can find inference.py
set PYTHONPATH=..\..\

# Run
.\NeuroSightAI.exe
```

### Option B: Using qmake

1. **Open VS 2022 Developer Command Prompt**

2. **Navigate to project and setup paths:**

```powershell
cd c:\Users\kheza\Downloads\Neurosight_AI\NeuroSightAI_Desktop

# Set Qt paths
set QT_PATH=C:\Qt\6.x\msvc2022_64
set PATH=%QT_PATH%\bin;%PATH%
```

3. **Create build directory:**

```powershell
mkdir build
cd build
```

4. **Run qmake and build:**

```powershell
# Generate Makefile from .pro
qmake ..\NeuroSightAI.pro -spec win32-msvc

# Build with nmake
nmake release
```

5. **Run:**

```powershell
cd release

# Set environment
set PYTHONPATH=..\..\
set PATH=%QT_PATH%\bin;%PATH%

.\NeuroSightAI.exe
```

## Test Python Inference Standalone

Before running the full app, test the inference script:

```powershell
# From project root with venv activated
.venv\Scripts\Activate.ps1
python inference.py model.onnx sample_mri_image.jpg
```

Expected output:
```json
{"diagnosis": "Normal", "confidence": 0.95, "heatmap_path": ""}
```

## Troubleshooting

### "Qt platform plugin could not be found"
- Ensure Qt bin directory is in PATH
- Copy `platforms` folder from Qt to build output directory

### "Cannot find Python interpreter"
- Ensure Python is in PATH or specify full path in ModelHandler code
- Activate the `.venv` before running the app

### CMake configure fails
- Verify `CMAKE_PREFIX_PATH` points to correct Qt 6 installation
- Check that Qt was built with MSVC 2022 (not MinGW)

### Model not found
- Place `model.onnx` in project root directory
- Or update path in `inference.py` main() function

## Full Quick Start (Copy-Paste)

```powershell
# 1. Activate Python venv and install deps
cd c:\Users\kheza\Downloads\Neurosight_AI\NeuroSightAI_Desktop
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Open Developer Command Prompt and set environment
cd c:\Users\kheza\Downloads\Neurosight_AI\NeuroSightAI_Desktop
set QT_PATH=C:\Qt\6.x\msvc2022_64
set PATH=%QT_PATH%\bin;%PATH%

# 3. Build with CMake
mkdir build
cd build
cmake .. -G "NMake Makefiles" -DCMAKE_PREFIX_PATH=%QT_PATH% -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release

# 4. Run
cd Release
set PYTHONPATH=..\..\
.\NeuroSightAI.exe
```

Replace `C:\Qt\6.x\msvc2022_64` with your actual Qt 6 installation path.
