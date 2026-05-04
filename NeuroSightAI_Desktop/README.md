# NeuroSight AI - Desktop Application Setup Guide

## ⚡ Quick Build with VS 2022

**Using Qt 6.x (18.0+) with MSVC?** See [BUILD_VS2022.md](BUILD_VS2022.md) for complete setup and build commands.

TL;DR:
```powershell
cd c:\Users\kheza\Downloads\Neurosight_AI\NeuroSightAI_Desktop
.venv\Scripts\Activate.ps1
set QT_PATH=C:\Qt\6.x\msvc2022_64
mkdir build && cd build
cmake .. -G "NMake Makefiles" -DCMAKE_PREFIX_PATH=%QT_PATH% -DCMAKE_BUILD_TYPE=Release
cmake --build .
cd Release && .\NeuroSightAI.exe
```

## Project Structure

```
NeuroSightAI_Desktop/
├── NeuroSightAI.pro                 # Qt project file
├── CMakeLists.txt                   # CMake build configuration
├── README.md                        # This file
├── setup_guide.md                   # Detailed setup instructions
├── UI_DESIGNER_GUIDE.md             # Qt Designer step-by-step guide
│
├── src/                             # Source code
│   ├── main.cpp                     # Application entry point
│   ├── mainwindow.h                 # Main window header
│   ├── mainwindow.cpp               # Main window implementation
│   ├── modelhandler.h               # Model handler header
│   └── modelhandler.cpp             # Model handler implementation
│
├── ui/                              # Qt Designer files
│   └── mainwindow.ui                # Main window UI definition (XML)
│
├── resources/                       # Application resources
│   ├── resources.qrc                # Resource file (images, styles)
│   ├── style.qss                    # Qt stylesheet
│   └── icon.png                     # Application icon
│
├── build/                           # Build output directory
│   └── (generated files)
│
└── inference.py                     # Python model inference script
   └── models/                      # Trained model directory
      └── model.onnx               # Your trained ONNX model
```

## Quick Start

### Prerequisites
- **Qt 6.x (18.0+)** with MSVC 2022 binaries (or Qt 5.12+ with compatible compiler)
- **C++17 compatible compiler** (MSVC 2022, GCC, Clang)
- **CMake 3.16+** (optional, for CMake builds; qmake is built-in with Qt)
- **Python 3.8+** with ONNX Runtime

### Building with Qt Creator

1. **Open Project**
   - Launch Qt Creator
   - File → Open File or Project
   - Select `NeuroSightAI.pro`

2. **Configure Kit**
   - Select your Qt version (5.12+)
   - Choose MSVC, GCC, or Clang compiler
   - Click Configure Project

3. **Build**
   - Build → Build All
   - Or press Ctrl+B

4. **Run**
   - Build → Run
   - Or press Ctrl+R

## Component Overview

### C++ Backend (Qt Widgets)

#### `mainwindow.h / mainwindow.cpp`
- **Purpose**: Main application window
- **Features**:
  - File upload dialog with drag & drop support
  - Image preview
  - UI element management
  - Signal/slot connections

#### `modelhandler.h / modelhandler.cpp`
- **Purpose**: Async communication with Python model
- **Features**:
  - QProcess management
  - JSON output parsing
  - Error handling
  - Signals for async callbacks

#### `main.cpp`
- **Purpose**: Application entry point
- **Creates**: QApplication and MainWindow

### UI Components (Qt Designer)

**Object Names** (used in C++ code):
- `uploadButton`: Browse/upload file button
- `analyzeButton`: Analyze image button
- `imagePathLabel`: Display selected file path
- `imagePreviewLabel`: Show MRI image preview
- `resultLabel`: Show diagnosis result
- `diseaseStageLabel`: Display disease stage
- `confidenceLabel`: Show confidence percentage
- `heatmapLabel`: Display Class Activation Map
- `statusLabel`: Status messages
- `progressBar`: Processing progress indicator

### Python Backend (`inference.py`)

**Input**: Image file path via command line
**Output**: JSON with diagnosis and confidence

**Expected JSON format**:
```json
{
    "diagnosis": "Normal|Mild|Moderate|Severe",
    "confidence": 0.95,
    "heatmap_path": "/path/to/heatmap.png"
}
```

## Integration Steps

### Step 1: Add Your Trained Model
1. Place `model.onnx` in the project root
2. Update `inference.py`:
   ```python
   model = Alzheimer_Model("model.onnx")  # Update path if needed
   ```

### Step 2: Implement Model Loading
Edit `inference.py` and adapt preprocessing if needed. ONNX model loading is already implemented via ONNX Runtime:
```python
def _load_model(self, model_path):
   session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
   return session
```

### Step 3: Implement Image Preprocessing
Update the `preprocess_image()` method to match your model's requirements:
```python
def preprocess_image(self, image_path):
    # Your preprocessing pipeline
   # Return np.float32 tensor in NCHW expected by ONNX model
   pass
```

### Step 4: Implement Grad-CAM Heatmap (Optional)
Add visualization code to `generate_grad_cam()`:
```python
def generate_grad_cam(self, image_path, output_path="heatmap.png"):
    # Implement Grad-CAM or other visualization
    # Generate heatmap.png and return its path
    pass
```

### Step 5: Build and Run
```bash
# Build in Qt Creator or command line:
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build .

# Run:
./NeuroSightAI
```

## Usage Workflow

1. **Launch Application**
   - Double-click NeuroSightAI executable

2. **Upload Image**
   - Click "Browse Files" or drag & drop an MRI image
   - Supported formats: `.jpg`, `.png`, `.nii`, `.dcm`

3. **View Preview**
   - Image appears in the preview panel

4. **Analyze**
   - Click "🚀 Analyze Image"
   - Progress bar shows processing status

5. **View Results**
   - Diagnosis stage displayed
   - Confidence score shown
   - Class Activation Map (heatmap) visible
   - Status message updated

## Troubleshooting

### Python Process Won't Start
- **Check**: Is Python in system PATH?
- **Fix**: Add Python to PATH or provide full path in code
- **Alternative**: Use QProcess to specify python.exe full path

### Model Not Found
- **Check**: Is `model.onnx` in the project directory?
- **Check**: Is path correct in `inference.py`?
- **Fix**: Copy model file to correct location

### JSON Parse Error
- **Check**: Is `inference.py` outputting valid JSON?
- **Debug**: Run Python script manually:
  ```bash
  python inference.py path/to/image.jpg
  ```
- **Should output**: Valid JSON string

### UI Elements Not Appearing
- **Check**: Are object names correct in .ui file?
- **Fix**: Regenerate ui_mainwindow.h from .ui file:
  ```bash
  uic ui/mainwindow.ui -o ui_mainwindow.h
  ```

## Advanced Customization

### Styling
Edit `resources/style.qss` for global application styling

### Dark Mode
Add to `main.cpp`:
```cpp
QApplication::setStyle(QStyleFactory::create("Fusion"));
QPalette darkPalette;
// ... configure colors
app.setPalette(darkPalette);
```

### Batch Processing
Extend `ModelHandler` to process multiple images

### Database Integration
Add patient history storage with SQLite

## Performance Optimization

1. **GPU Acceleration**: Model uses CUDA if available
2. **Model Quantization**: Consider quantizing model for faster inference
3. **Async Processing**: Already implemented via QProcess
4. **Caching**: Cache frequently used predictions

## Documentation Files

- `UI_DESIGNER_GUIDE.md`: Step-by-step UI building instructions
- `setup_guide.md`: Detailed environment setup
- `ARCHITECTURE.md`: Complete system architecture
- `API.md`: C++ API reference

## Support & License

For issues or questions, refer to the complete documentation or contact the development team.

---
**Version**: 1.0.0  
**Last Updated**: May 2026
