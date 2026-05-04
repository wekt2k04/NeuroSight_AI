# NeuroSight AI - Complete Project Index

## 📋 Quick Start

1. **Build Project**: Open `NeuroSightAI.pro` in Qt Creator → Build
2. **Add Model**: Place `model.pth` in project root
3. **Configure Model**: Edit `inference.py` with your model architecture
4. **Run**: Press Ctrl+R or click Run button
5. **Use**: Upload MRI image → Click Analyze → View results

---

## 📁 Complete File Structure

### Root Directory
```
NeuroSightAI_Desktop/
├── NeuroSightAI.pro              [Qt project configuration]
├── CMakeLists.txt                [CMake build configuration]
├── inference.py                  [Python ML inference script]
├── model.pth                      [Your trained PyTorch model - OPTIONAL]
├── requirements.txt              [Python dependencies list]
│
├── README.md                      [Project overview & quick start]
├── SETUP_GUIDE.md                [Build & installation guide]
├── UI_DESIGNER_GUIDE.md          [Qt Designer step-by-step]
├── UI_MOCKUP.md                  [Visual interface layout]
├── ARCHITECTURE.md               [System design & components]
│
├── src/                          [C++ Source Code]
│   ├── main.cpp
│   ├── mainwindow.h
│   ├── mainwindow.cpp
│   ├── modelhandler.h
│   └── modelhandler.cpp
│
├── ui/                           [Qt Designer UI Files]
│   └── mainwindow.ui             [Generated ui_mainwindow.h from this]
│
├── resources/                    [Application Resources]
│   ├── resources.qrc             [Resource manifest]
│   ├── icon.png                  [Application icon - OPTIONAL]
│   └── style.qss                 [Qt stylesheet - OPTIONAL]
│
├── build/                        [Build Output - Auto Generated]
│   ├── Makefile
│   ├── ui_mainwindow.h           [Generated from .ui file]
│   └── NeuroSightAI(.exe/.app)   [Compiled executable]
│
└── models/                       [Model Storage - OPTIONAL]
    └── (place model versions here)
```

---

## 📄 File Descriptions

### Configuration Files

#### `NeuroSightAI.pro` [Qt Project File]
**Purpose**: Qt build configuration using qmake  
**Language**: Qt Project Format  
**What to edit**: Add new .cpp/.h files, link libraries  
**Key sections**:
- `SOURCES`: Lists C++ source files
- `HEADERS`: Lists header files
- `FORMS`: Lists .ui files
- `QT += widgets`: Enables Qt modules

#### `CMakeLists.txt` [CMake Configuration]
**Purpose**: Alternative build system (instead of qmake)  
**Language**: CMake  
**When to use**: If you prefer CMake over Qt Creator  
**Key sections**:
- `find_package(Qt5 ...)`: Finds Qt libraries
- `add_executable`: Builds executable
- `target_link_libraries`: Links dependencies

#### `requirements.txt` [Python Dependencies]
**Purpose**: Lists Python packages needed  
**How to use**:
```bash
pip install -r requirements.txt
```
**Contents**:
```
torch>=1.9.0
torchvision>=0.10.0
Pillow>=8.0
numpy>=1.19.0
```

---

### Documentation Files

#### `README.md` [Project Overview]
**Purpose**: High-level project description  
**Includes**:
- ✅ Project structure
- ✅ Quick start guide
- ✅ Component overview
- ✅ Integration steps
- ✅ Usage workflow
- ✅ Troubleshooting

**Read this first** to understand the project

#### `SETUP_GUIDE.md` [Build & Installation]
**Purpose**: Complete setup from scratch  
**Includes**:
- ✅ System requirements
- ✅ Prerequisites installation
- ✅ Building on Windows/Linux/macOS
- ✅ Project configuration
- ✅ Testing procedures
- ✅ Deployment instructions

**Read this to**: Build and run the project

#### `UI_DESIGNER_GUIDE.md` [UI Building Tutorial]
**Purpose**: Step-by-step UI creation  
**Includes**:
- ✅ Opening Qt Designer
- ✅ Building each UI section (header, panels, footer)
- ✅ Setting properties for each widget
- ✅ Component checklist
- ✅ Saving and compiling
- ✅ Testing and customization

**Read this to**: Modify or rebuild the UI in Qt Designer

#### `UI_MOCKUP.md` [Visual Design Reference]
**Purpose**: Visual representation of interface  
**Includes**:
- ✅ ASCII mockup of full interface
- ✅ Detailed component views
- ✅ Color scheme with hex codes
- ✅ State change diagrams
- ✅ Responsive behavior
- ✅ Interaction flow

**Read this to**: Understand the visual design

#### `ARCHITECTURE.md` [System Design]
**Purpose**: Technical architecture and design patterns  
**Includes**:
- ✅ Component descriptions
- ✅ Data flow diagrams
- ✅ Signal-slot connections
- ✅ Error handling strategy
- ✅ Threading & async behavior
- ✅ Extension points

**Read this to**: Understand how components work together

---

### Source Code Files (C++/Qt)

#### `src/main.cpp` [Application Entry Point]
**Lines**: ~20  
**Purpose**: Create and run QApplication  
**Contains**:
- Application initialization
- Main window creation
- Event loop start

**Edit when**: Need to customize application startup

```cpp
#include <QApplication>
#include "mainwindow.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    MainWindow window;
    window.show();
    return app.exec();
}
```

#### `src/mainwindow.h` [Main Window Header]
**Lines**: ~60  
**Purpose**: Declare main window class and signals/slots  
**Contains**:
- `MainWindow` class declaration
- Signal definitions
- Slot declarations
- Private members (UI components)

**Key methods**:
```cpp
explicit MainWindow(QWidget *parent = nullptr);
~MainWindow();

private slots:
void onUploadButtonClicked();
void onAnalyzeButtonClicked();
void onPredictionReceived(...);
```

**Edit when**: Add new UI features, signals, or slots

#### `src/mainwindow.cpp` [Main Window Implementation]
**Lines**: ~250  
**Purpose**: Implement main window logic  
**Contains**:
- Constructor/destructor
- Signal-slot connections
- File dialog handling
- Image display logic
- Results display
- Status updates

**Key functions**:
- `connectSignalsAndSlots()`: Wire up signals
- `onUploadButtonClicked()`: Handle file upload
- `onAnalyzeButtonClicked()`: Send image to model
- `onPredictionReceived()`: Display results
- `displayImage()`: Show MRI preview

**Edit when**: Change behavior or add features

#### `src/modelhandler.h` [Model Handler Header]
**Lines**: ~50  
**Purpose**: Declare model communication class  
**Contains**:
- `ModelHandler` class definition
- QProcess member
- Signals for callbacks
- Public methods for inference

**Key signals**:
```cpp
void predictionReady(const QString &diagnosis, 
                     float confidence, 
                     const QString &heatmapPath);
void errorOccurred(const QString &errorMessage);
void processingStarted();
void processingFinished();
```

**Edit when**: Add new signals or change process communication

#### `src/modelhandler.cpp` [Model Handler Implementation]
**Lines**: ~200  
**Purpose**: Implement Python subprocess communication  
**Contains**:
- QProcess initialization
- Process lifecycle management
- JSON parsing
- Error handling
- Signal emission

**Key functions**:
- `predictImage()`: Send image to Python
- `parseModelOutput()`: Parse JSON response
- `onProcessFinished()`: Handle process completion
- `onProcessError()`: Handle errors

**Edit when**: Change how Python is called or output is parsed

---

### UI Files (Qt Designer)

#### `ui/mainwindow.ui` [UI Definition - XML]
**Format**: XML (auto-generated by Qt Designer)  
**Purpose**: Define user interface layout  
**Contains**:
- Window properties
- Widget hierarchy
- Layout definitions
- Widget properties (text, colors, sizes)
- Signals/slots connections (optional)

**Structure**:
```xml
<ui>
  <class>MainWindow</class>
  <widget class="QMainWindow" name="MainWindow">
    <property name="geometry">...</property>
    <widget class="QWidget" name="centralwidget">
      <!-- UI elements -->
    </widget>
  </widget>
</ui>
```

**Generated File**: `build/ui_mainwindow.h`
- Auto-generated C++ header
- Contains `setupUi()` function
- Called in `MainWindow` constructor
- **DO NOT EDIT** - regenerate from .ui file

**Edit when**: 
- Change layout
- Modify colors/sizes
- Add/remove widgets
- Use Qt Designer to edit

---

### Resource Files

#### `resources/resources.qrc` [Resource Manifest]
**Format**: XML resource description  
**Purpose**: Bundle images, icons, stylesheets  
**Contains**: References to resources

```xml
<qresource prefix="/">
    <file>resources/icon.png</file>
    <file>resources/style.qss</file>
</qresource>
```

**Usage in code**:
```cpp
QPixmap icon(":/resources/icon.png");
```

**Edit when**: Add new images or stylesheets

#### `resources/style.qss` [Qt Stylesheet]
**Format**: Qt Style Sheets (CSS-like)  
**Purpose**: Global application styling  
**Example**:
```qss
QPushButton {
    background-color: #2ecc71;
    color: white;
    border-radius: 5px;
}
```

**Edit when**: Change application colors/fonts

#### `resources/icon.png` [Application Icon]
**Format**: PNG image (256x256 recommended)  
**Purpose**: Window icon and taskbar icon  
**Edit when**: Want custom application icon

---

### Python Backend

#### `inference.py` [ML Inference Script]
**Lines**: ~250  
**Language**: Python 3.7+  
**Purpose**: Run model inference on MRI image  
**Input**: Image file path (command line arg)  
**Output**: JSON to stdout

**Class: `Alzheimer_Model`**
```python
class Alzheimer_Model:
    def __init__(self, model_path):      # Load model
    def preprocess_image(self, path):    # Prepare image
    def predict(self, path):              # Run inference
    def generate_grad_cam(self, path):   # Create heatmap
```

**Expected JSON Output**:
```json
{
    "diagnosis": "Normal|Mild|Moderate|Severe",
    "confidence": 0.95,
    "heatmap_path": "/path/to/heatmap.png"
}
```

**Edit to**:
1. Load your trained model
2. Update preprocessing
3. Implement Grad-CAM
4. Handle your model architecture

#### `model.pth` [Trained PyTorch Model]
**Format**: PyTorch binary (.pth)  
**Purpose**: Pre-trained neural network weights  
**What to do**: 
1. Train your model (outside this project)
2. Save as: `model.pth`
3. Place in project root
4. Update `inference.py` to load it

**Created by**: Your separate training pipeline

---

## 🔗 File Dependencies

```
main.cpp
  └─ mainwindow.h
      └─ modelhandler.h
          └─ QProcess (Qt library)

mainwindow.cpp
  └─ mainwindow.h
  └─ ui_mainwindow.h (generated from mainwindow.ui)
  └─ modelhandler.h

modelhandler.cpp
  └─ modelhandler.h
  └─ QJsonDocument (Qt library)

mainwindow.ui
  └─ ui_mainwindow.h (auto-generated)

inference.py
  └─ torch, torchvision (external packages)
  └─ model.pth (your trained model)

NeuroSightAI.pro
  └─ src/*.cpp, src/*.h
  └─ ui/*.ui
  └─ resources/*.qrc
```

---

## 📊 Coding Statistics

| File | Lines | Language | Purpose |
|------|-------|----------|---------|
| main.cpp | 20 | C++ | Entry point |
| mainwindow.h | 60 | C++ | Window class |
| mainwindow.cpp | 250 | C++ | Window logic |
| modelhandler.h | 50 | C++ | Model class |
| modelhandler.cpp | 200 | C++ | Inference |
| mainwindow.ui | 300 | XML | UI layout |
| inference.py | 250 | Python | ML inference |
| **Total** | **1,130** | Mixed | **Complete app** |

---

## 🎯 Typical Workflows

### Workflow 1: Build & Run
```
1. Open NeuroSightAI.pro in Qt Creator
2. Click Build (Ctrl+B)
3. Click Run (Ctrl+R)
4. Application opens
```

### Workflow 2: Modify UI
```
1. Double-click mainwindow.ui
2. Qt Designer opens
3. Drag/drop to modify layout
4. Save (Ctrl+S)
5. Qt Creator auto-regenerates ui_mainwindow.h
6. Rebuild (Ctrl+B)
```

### Workflow 3: Add New Feature
```
1. Edit mainwindow.h - add slot
2. Edit mainwindow.cpp - implement
3. Edit mainwindow.ui - add button
4. Connect signal in mainwindow.cpp
5. Test with Build & Run
```

### Workflow 4: Integrate Your Model
```
1. Save model as model.pth in project root
2. Edit inference.py:
   - Update _load_model()
   - Update preprocess_image()
   - Update generate_grad_cam()
3. Test Python script manually
4. Run Qt application
5. Upload image and click Analyze
```

---

## ✅ Checklist Before Deployment

- ✅ All code compiles without warnings
- ✅ Model file (`model.pth`) added
- ✅ `inference.py` updated for your model
- ✅ UI tested on your screen size
- ✅ File upload works (browse + drag&drop)
- ✅ Image preprocessing matches model requirements
- ✅ Error messages display correctly
- ✅ Heatmap generates (if implementing)
- ✅ Progress bar works
- ✅ Application exits cleanly
- ✅ Python executable found (or add to PATH)
- ✅ All dependencies installed (pip install -r requirements.txt)

---

## 🔍 Finding Things in Code

### I want to change...

| What | Where | What to edit |
|------|-------|-------------|
| Upload button appearance | `ui/mainwindow.ui` | uploadButton properties |
| Upload button action | `mainwindow.cpp` | `onUploadButtonClicked()` |
| Analyze button color | `ui/mainwindow.ui` | analyzeButton → StyleSheet |
| How results display | `mainwindow.cpp` | `onPredictionReceived()` |
| Model loading | `inference.py` | `_load_model()` |
| Image preprocessing | `inference.py` | `preprocess_image()` |
| Error messages | `modelhandler.cpp` | Error handling code |
| Application title | `mainwindow.cpp` | `setWindowTitle()` |
| Window size | `mainwindow.cpp` | `resize()` or ui file |
| Status bar text | `mainwindow.cpp` | `updateStatusMessage()` |
| Progress bar behavior | `mainwindow.cpp` | progressBar operations |
| Drag & drop | `mainwindow.cpp` | `dropEvent()` |

---

## 📞 Getting Help

### For Qt/C++ Issues
- Check: `SETUP_GUIDE.md` - Troubleshooting section
- Check: Qt documentation at qt.io
- Search: Qt online help in Qt Creator

### For UI Issues
- Check: `UI_DESIGNER_GUIDE.md`
- Check: `UI_MOCKUP.md` for reference layout
- Qt Designer has built-in help (F1)

### For Python/ML Issues
- Check: `inference.py` comments
- Test: Run `python inference.py image.jpg` manually
- Check: PyTorch documentation

### For Build Issues
- Check: `SETUP_GUIDE.md` - Build section
- Verify: Qt, compiler, Python all installed
- Verify: Object names match between .ui and .cpp

---

## 📚 Related Documentation

- **README.md** - Start here for overview
- **SETUP_GUIDE.md** - Build & install instructions
- **UI_DESIGNER_GUIDE.md** - Modify UI in Qt Designer
- **UI_MOCKUP.md** - See visual design
- **ARCHITECTURE.md** - Understand system design

---

**Last Updated**: May 2026  
**Version**: 1.0.0  
**Status**: Ready for development
