# NeuroSight AI - System Architecture

## Overview

NeuroSight AI is a desktop application for early Alzheimer detection using MRI images and deep learning. The architecture separates the Qt C++ frontend from the Python ML backend, communicating via JSON messages through QProcess.

```
┌─────────────────────────────────────────────────────────────┐
│                   NeuroSight AI Desktop                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Qt C++ Frontend (Widgets)               │   │
│  │                                                      │   │
│  │  ┌───────────────┐         ┌──────────────────┐   │   │
│  │  │  MainWindow   │────────▶│  ModelHandler    │   │   │
│  │  │  (UI Logic)   │         │  (QProcess IPC)  │   │   │
│  │  └───────────────┘         └──────────────────┘   │   │
│  │         ▲                           │              │   │
│  │         │                           ▼              │   │
│  │    Signals/Slots          JSON Messages (stdio)   │   │
│  └──────────────────────────────────────────────────────┘   │
│         ▲                           │                        │
│         │                           ▼                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Python ML Backend (inference.py)             │   │
│  │                                                      │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────┐   │   │
│  │  │ Image Load   │▶ │ Preprocess   │▶ │ Model  │   │   │
│  │  └──────────────┘  └──────────────┘  └────────┘   │   │
│  │         ▲                                   │       │   │
│  │         │                                   ▼       │   │
│  │    Input Path                    ┌──────────────┐  │   │
│  │                                  │ Grad-CAM/    │  │   │
│  │                                  │ Heatmap Gen  │  │   │
│  │                                  └──────────────┘  │   │
│  │                                           │         │   │
│  │                                           ▼         │   │
│  │                                    Output JSON      │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ▲                                   │
│                           │                                   │
│                    {diagnosis, confidence,                   │
│                     heatmap_path}                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### 1. Qt C++ Frontend

#### MainWindow (mainwindow.h / mainwindow.cpp)

**Responsibilities**:
- Manage UI state and interactions
- Handle file selection (dialog + drag & drop)
- Display image previews
- Show results (diagnosis, confidence, heatmap)
- Update status messages

**Key Features**:
- QMainWindow-based application
- Signals/Slots pattern for async operations
- Drag & Drop support via QDragEnterEvent/QDropEvent
- Automatic UI element binding from .ui file

**Public Methods**:
```cpp
MainWindow(QWidget *parent = nullptr);
~MainWindow();
```

**Private Slots** (connected to UI signals):
```cpp
void onUploadButtonClicked();           // Handle upload button
void onAnalyzeButtonClicked();          // Handle analyze button
void onPredictionReceived(...);         // Handle model results
void onModelError(const QString &);     // Handle errors
void onProcessingStarted();             // Called when processing begins
void onProcessingFinished();            // Called when processing ends
```

**Drag & Drop**:
```cpp
void dragEnterEvent(QDragEnterEvent *event);
void dropEvent(QDropEvent *event);
```

#### ModelHandler (modelhandler.h / modelhandler.cpp)

**Responsibilities**:
- Manage Python process lifecycle
- Serialize input (image path)
- Deserialize output (JSON)
- Error handling and reporting

**Key Features**:
- QProcess for subprocess management
- Asynchronous execution (non-blocking)
- JSON parsing using QJsonDocument
- Signal-based callback mechanism

**Public Methods**:
```cpp
void predictImage(const QString &imagePath);
bool isProcessing() const;
QString getModelScriptPath() const;
```

**Signals**:
```cpp
void predictionReady(const QString &diagnosis, 
                     float confidence, 
                     const QString &heatmapPath);
void errorOccurred(const QString &errorMessage);
void processingStarted();
void processingFinished();
```

**Process Flow**:
```
User calls: predictImage("image.jpg")
    ↓
ModelHandler validates file
    ↓
Emit: processingStarted()
    ↓
QProcess::start("python", ["inference.py", "image.jpg"])
    ↓
Read stdout/stderr
    ↓
QProcess finishes
    ↓
Parse JSON output
    ↓
Emit: predictionReady(...) or errorOccurred(...)
    ↓
Emit: processingFinished()
```

### 2. Qt Designer UI File (mainwindow.ui)

**Format**: XML-based Qt UI description  
**Generated**: ui_mainwindow.h (auto-generated C++ header)

**Structure**:
```xml
<ui>
  <class>MainWindow</class>
  <widget class="QMainWindow" name="MainWindow">
    <widget class="QWidget" name="centralwidget">
      <!-- Layouts and widgets -->
    </widget>
  </widget>
</ui>
```

**Key Widgets**:
| Widget | Type | Purpose |
|--------|------|---------|
| uploadButton | QPushButton | Trigger file dialog |
| dragDropFrame | QFrame | Visual drop zone |
| analyzeButton | QPushButton | Trigger inference |
| imagePreviewLabel | QLabel | Display MRI |
| resultLabel | QLabel | Show diagnosis |
| confidenceLabel | QLabel | Show confidence % |
| heatmapLabel | QLabel | Display CAM |
| statusLabel | QLabel | Status messages |
| progressBar | QProgressBar | Processing indicator |

### 3. Python Backend (inference.py)

**Purpose**: Execute ML model inference and return results

**Input**: Image file path (command-line argument)

**Output**: JSON to stdout
```json
{
    "diagnosis": "Normal|Mild|Moderate|Severe",
    "confidence": 0.95,
    "heatmap_path": "/path/to/heatmap.png"
}
```

**Process**:
```
python inference.py /path/to/image.jpg
    ↓
Load image
    ↓
Preprocess (resize, normalize)
    ↓
Load model
    ↓
Run inference
    ↓
Generate heatmap (optional)
    ↓
Print JSON
    ↓
Exit with code 0 (success) or 1 (error)
```

**Class: Alzheimer_Model**

```python
class Alzheimer_Model:
    def __init__(self, model_path):
        # Load pre-trained model
        
    def preprocess_image(self, image_path):
        # Resize, normalize, convert to tensor
        
    def predict(self, image_path):
        # Run inference, return diagnosis + confidence
        
    def generate_grad_cam(self, image_path, output_path):
        # Generate heatmap visualization
```

## Data Flow

### Upload Flow
```
User Action          Qt Signal          ModelHandler          Python
───────────────────────────────────────────────────────────────────
Drag image  ──▶ dropEvent()
             ──▶ displayImage()
             ──▶ analyzeButton enabled
                         │
                         └─ Ready for analysis
```

### Analysis Flow
```
User Action          Qt Signal          ModelHandler          Python
───────────────────────────────────────────────────────────────────
Click Analyze  ──▶ onAnalyzeButtonClicked()
               ──▶ predictImage(path)
                      │
                      ├─ emit processingStarted()
                      │
                      ├─ QProcess::start("python", ["inference.py", path])
                      │                                      │
                      │                      ┌───────────────┘
                      │                      ▼
                      │         Load image & preprocess
                      │         Load model weights
                      │         Forward pass
                      │         Generate predictions
                      │         Create heatmap
                      │         Output JSON
                      │                      │
                      ├─ readyReadStandardOutput()
                      │  (capture JSON)
                      │
                      ├─ processFinished()
                      │
                      ├─ parseModelOutput(json)
                      │
                      ├─ emit predictionReady(...)
                      │
                      └─ Display results in UI
```

## Signal-Slot Connections

### Main Window Connections

```cpp
// Button clicks
uploadButton → onUploadButtonClicked
analyzeButton → onAnalyzeButtonClicked

// Model handler signals
modelHandler::predictionReady → onPredictionReceived
modelHandler::errorOccurred → onModelError
modelHandler::processingStarted → onProcessingStarted
modelHandler::processingFinished → onProcessingFinished
```

### Event Handlers

```cpp
onUploadButtonClicked()
├─ Open file dialog
├─ Validate selection
├─ Load image path
├─ Display preview
└─ Enable analyze button

onAnalyzeButtonClicked()
├─ Validate image selected
├─ Disable buttons
├─ Show progress bar
└─ Call modelHandler→predictImage()

onPredictionReceived(diagnosis, confidence, heatmap)
├─ Update result labels
├─ Display heatmap
├─ Update progress (100%)
└─ Show success message

onModelError(errorMsg)
├─ Show error dialog
├─ Update status label
├─ Re-enable buttons
└─ Clear progress bar

onProcessingStarted()
├─ Disable UI controls
├─ Show progress bar
├─ Update status

onProcessingFinished()
├─ Re-enable UI controls
└─ Complete progress bar
```

## Error Handling

### File Not Found
```
User selects invalid path
    ↓
onUploadButtonClicked() checks file existence
    ↓
Update status: "File not found"
```

### Model Process Errors
```
Python script fails
    ↓
QProcess::error() signal
    ↓
ModelHandler::onProcessError()
    ↓
Emit errorOccurred()
    ↓
MainWindow shows error dialog
```

### JSON Parse Errors
```
Invalid JSON from Python
    ↓
QJsonDocument::fromJson() returns null
    ↓
ModelHandler::parseModelOutput() fails
    ↓
Emit errorOccurred("Invalid JSON format")
```

## Threading & Async Behavior

### Single-Threaded Design
- Main GUI thread (event loop)
- Python subprocess runs independently
- QProcess handles communication

### Why QProcess?
- **Non-blocking**: Doesn't freeze UI
- **Cross-platform**: Works on Windows/Linux/macOS
- **Signal-based**: Integrates with Qt event loop
- **Subprocess isolation**: Model crashes don't kill app

### Async Flow
```
Main Thread (GUI)          Python Subprocess
─────────────────────────────────────────────
[Event Loop Running]
    ↓
[User click]
    ↓
[QProcess::start()]
            │
            ├─ Subprocess starts
            │        ↓
            │  [Load model]
            │  [Process image]
            │        ↓
            │ [Write JSON to stdout]
            │
[readyReadStandardOutput()]
[parseModelOutput()]
[Emit predictionReady()]
[Update UI]
```

## Performance Considerations

### Optimization Points

1. **Image Loading**
   - Validate dimensions before loading
   - Cache preprocessed images if re-running

2. **Model Inference**
   - Use GPU if available (PyTorch handles this)
   - Consider model quantization for speed
   - Model runs in subprocess (doesn't block UI)

3. **Heatmap Generation**
   - Optional feature (can be disabled)
   - Cache generated heatmaps

4. **UI Updates**
   - Use progress bar for feedback
   - All updates via signals/slots
   - Thread-safe by design

## File Organization

```
NeuroSightAI_Desktop/
├── src/                    # C++ source code
│   ├── main.cpp
│   ├── mainwindow.h/.cpp
│   └── modelhandler.h/.cpp
├── ui/                     # Qt Designer files
│   └── mainwindow.ui
├── resources/              # Images, stylesheets
│   └── resources.qrc
├── NeuroSightAI.pro       # Qt project file
├── CMakeLists.txt         # CMake build config
├── inference.py           # Python ML script
└── build/                 # Build output
```

## Extension Points

### Adding New Features

1. **Batch Processing**
   - Modify ModelHandler to queue multiple images
   - Add progress tracking per image

2. **Patient History**
   - Add SQLite database
   - Store results with timestamps

3. **Model Switching**
   - Parametrize model path
   - Support multiple model architectures

4. **Advanced Visualization**
   - Integrate Grad-CAM variants
   - Add region highlighting

5. **Export Reports**
   - Generate PDF with results
   - Add patient demographics form

## Dependencies

### C++ (Qt)
- Qt Core (5.12+)
- Qt Gui
- Qt Widgets
- Qt Network (optional, for future API integration)

### Python
- torch (PyTorch)
- torchvision
- PIL (Pillow)
- numpy

---

**Version**: 1.0  
**Last Updated**: May 2026
