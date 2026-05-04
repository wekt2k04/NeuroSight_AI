# NeuroSight AI - Quick Reference Card

## 🚀 Build in 3 Commands

```bash
# 1. Open project
Qt Creator → File → Open NeuroSightAI.pro

# 2. Build
Ctrl+B (or Build → Build All)

# 3. Run
Ctrl+R (or Build → Run)
```

---

## 📁 Key Files You Need

| File | What to Do | Time |
|------|-----------|------|
| `inference.py` | Add your model loading code | 20 min |
| `model.pth` | Place your trained model here | 5 min |
| `mainwindow.ui` | Modify UI (optional) | Varies |
| `ui_mainwindow.h` | AUTO-GENERATED (don't edit) | - |

---

## 🔧 3-Step Integration

### Step 1: Copy Model
```
Place model.pth in: NeuroSightAI_Desktop/
```

### Step 2: Edit inference.py
```python
# Around line 50, replace:
def _load_model(self, model_path):
    # Load your actual model here
    model = torch.load(model_path)
    return model
```

### Step 3: Test
```bash
python inference.py path/to/image.jpg
# Should output: {"diagnosis": "Normal", "confidence": 0.9, ...}
```

---

## 📚 Documentation Map

```
START HERE
    ↓
README.md (5 min)
    ↓
SETUP_GUIDE.md (15 min) ← Build instructions
    ↓
IMPLEMENTATION_GUIDE.md (10 min) ← Model integration
    ↓
UI_DESIGNER_GUIDE.md (30 min) ← Modify UI (optional)
    ↓
ARCHITECTURE.md (20 min) ← How it works
```

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails | Check Qt version (5.12+), compiler installed |
| Python not found | Add Python to PATH, or update code with full path |
| Model error | Run `python inference.py` manually to debug |
| UI looks wrong | Regenerate ui_mainwindow.h from .ui file |
| Results not showing | Check Python JSON output format |

---

## 💡 Object Names (For Reference)

```
uploadButton            ← Browse button
analyzeButton           ← Start analysis (green)
imagePreviewLabel       ← MRI image display
resultLabel             ← Disease stage result
confidenceLabel         ← Confidence %
heatmapLabel            ← Heatmap display
statusLabel             ← Status messages
progressBar             ← Processing indicator
diseaseStageLabel       ← Result display field
```

---

## 🎯 Expected Results

### Python Output
```json
{
    "diagnosis": "Mild",
    "confidence": 0.87,
    "heatmap_path": "heatmap.png"
}
```

### Diagnosis Classes
```
"Normal"      (healthy)
"Mild"        (mild dementia)
"Moderate"    (moderate dementia)
"Severe"      (severe dementia)
```

### Confidence Range
```
0.0 to 1.0 (or 0% to 100%)
```

---

## ⚡ Command Line Essentials

```bash
# Check Qt
qmake --version

# Check Python
python --version
python -c "import torch; print(torch.__version__)"

# Build
mkdir build && cd build
qmake ../NeuroSightAI.pro
make

# Test inference script
cd ..
python inference.py test.jpg

# Run app
./build/NeuroSightAI
```

---

## 📋 Pre-Launch Checklist

- [ ] Qt 5.12+ installed
- [ ] C++ compiler installed
- [ ] Python 3.7+ installed
- [ ] PyTorch installed: `pip install torch`
- [ ] model.pth in project root
- [ ] inference.py updated
- [ ] Application builds without errors
- [ ] Python script outputs valid JSON

---

## 🔗 Project Structure

```
NeuroSightAI_Desktop/
├── src/              ← C++ code
├── ui/               ← UI design
├── resources/        ← Images, styles
├── inference.py      ← Python ML
├── model.pth         ← Your model
├── NeuroSightAI.pro  ← Build config
└── docs/             ← Guides
```

---

## 🎨 UI Customization

### Change Button Color
1. Open mainwindow.ui in Qt Designer
2. Right-click button
3. → Properties → StyleSheet
4. Add: `background-color: #YourColor;`

### Change Window Title
Edit mainwindow.cpp line ~40:
```cpp
this->setWindowTitle("Your Title");
```

### Change Image Size
Edit mainwindow.cpp in displayImage():
```cpp
QPixmap scaled = pixmap.scaledToWidth(300, ...);
// Change 300 to desired width
```

---

## 💾 Before Committing/Deploying

```bash
# Clean build
rm -rf build/
mkdir build
cd build
qmake ../NeuroSightAI.pro
make

# Test everything
./NeuroSightAI
# Test upload, analyze, results

# Package (Windows)
windeployqt.exe NeuroSightAI.exe

# Copy these files together:
NeuroSightAI.exe
inference.py
model.pth
Qt5Core.dll
Qt5Gui.dll
Qt5Widgets.dll
# ... other Qt DLLs
```

---

## 📞 Need Help?

1. Check SETUP_GUIDE.md → Troubleshooting
2. Check PROJECT_INDEX.md → Finding Things
3. Read ARCHITECTURE.md → How It Works
4. See IMPLEMENTATION_GUIDE.md → Integration Steps

---

## 📊 Performance Targets

| Metric | Target |
|--------|--------|
| App startup | < 1 second |
| Model load | 5-10 seconds |
| Inference | 1-3 seconds |
| Heatmap | 1-5 seconds |
| Total | 2-8 seconds |

---

## ✅ Success Indicators

- ✅ Qt application builds
- ✅ UI appears with all elements
- ✅ Can upload image (browse + drag&drop)
- ✅ Can click Analyze
- ✅ Progress bar shows
- ✅ Results display after processing
- ✅ Error handling works

---

**Version**: 1.0 | **Last Updated**: May 2026 | **Status**: Ready
