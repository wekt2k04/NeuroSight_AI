# Setup & Build Guide

## System Requirements

### Windows
- Windows 7+ (Windows 10/11 recommended)
- Visual Studio 2019+ or MinGW-w64
- Qt 5.12+ or Qt 6.x
- Python 3.7+

### Linux (Ubuntu/Debian)
- Ubuntu 18.04+
- GCC 7+
- Qt 5.12+
- Python 3.7+

### macOS
- macOS 10.13+
- Xcode 10+
- Qt 5.12+
- Python 3.7+

## Prerequisites Installation

### Step 1: Install Qt

#### Windows
1. Download Qt Online Installer from [qt.io](https://www.qt.io/download)
2. Run installer
3. Create free account
4. Select **Qt 5.15 LTS** or **Qt 6.x**
5. Choose components:
   - ✅ Qt 5.15 (or 6.x)
   - ✅ MSVC 2019 64-bit (or your compiler)
   - ✅ Qt Creator
6. Install (≈5GB)

#### Linux (Ubuntu)
```bash
sudo apt-get update
sudo apt-get install qt5-qmake qt5-default qtbase5-dev qttools5-dev-tools
# Or for Qt 6:
sudo apt-get install qt6-base-dev qt6-tools-dev
```

#### macOS
```bash
brew install qt@5  # or qt (for Qt 6)
export PATH="/usr/local/opt/qt@5/bin:$PATH"
```

### Step 2: Install Python & Dependencies

#### Windows
1. Download Python 3.9+ from [python.org](https://www.python.org)
2. During installation: ✅ **Add Python to PATH**
3. Open Command Prompt, run:
   ```cmd
   pip install torch torchvision pillow numpy
   ```

#### Linux
```bash
sudo apt-get install python3 python3-pip
pip3 install torch torchvision pillow numpy
```

#### macOS
```bash
brew install python@3.9
pip3 install torch torchvision pillow numpy
```

### Step 3: Install CMake (Optional, for CMake builds)

#### Windows
Download from [cmake.org](https://cmake.org) or use:
```cmd
choco install cmake
```

#### Linux
```bash
sudo apt-get install cmake
```

#### macOS
```bash
brew install cmake
```

## Building the Project

### Method 1: Qt Creator (Recommended)

#### Step 1: Open Project
1. Launch Qt Creator
2. File → Open File or Project
3. Navigate to: `NeuroSightAI_Desktop/NeuroSightAI.pro`
4. Click Open

#### Step 2: Configure
1. In "Configure Project" dialog:
   - Select your Qt version (5.12+)
   - Choose compiler (MSVC/GCC/Clang)
   - Click Configure Project

#### Step 3: Build
1. Build → Build All (or Ctrl+B)
2. Wait for compilation (2-5 minutes)
3. Check output for errors

#### Step 4: Run
1. Build → Run (or Ctrl+R)
2. Or click the green Run button
3. Application window should open

### Method 2: Command Line Build

#### Windows (MSVC)
```cmd
cd NeuroSightAI_Desktop
mkdir build
cd build
qmake ../NeuroSightAI.pro -spec win32-msvc
nmake
```

#### Windows (MinGW)
```cmd
cd NeuroSightAI_Desktop
mkdir build
cd build
qmake ../NeuroSightAI.pro -spec win32-g++
mingw32-make
```

#### Linux/macOS
```bash
cd NeuroSightAI_Desktop
mkdir build
cd build
qmake ../NeuroSightAI.pro
make
```

### Method 3: CMake Build

#### All Platforms
```bash
cd NeuroSightAI_Desktop
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
```

## Verifying Installation

### Check Qt Version
```bash
qmake --version
```
Output should show Qt 5.12+ or 6.x

### Check Python
```bash
python --version
# And PyTorch:
python -c "import torch; print(torch.__version__)"
```

### Check Compiler
```bash
# MSVC
cl.exe /?

# GCC
g++ --version

# Clang
clang++ --version
```

## Project Configuration

### Step 1: Add Your Model

1. Place your trained model (`.pth` file) in project root:
   ```
   NeuroSightAI_Desktop/
   ├── model.pth          ← Your trained model here
   ├── inference.py
   ├── NeuroSightAI.pro
   └── ...
   ```

2. Update `inference.py`:
   ```python
   # Around line 50
   model_path = os.path.join(os.path.dirname(__file__), "model.pth")
   model = Alzheimer_Model(model_path)
   ```

### Step 2: Implement Model Loading

Edit `inference.py` - `_load_model()` method:

```python
def _load_model(self, model_path):
    """Load your actual trained model"""
    
    # Example for EfficientNet:
    import torchvision.models as models
    model = models.efficientnet_b0(pretrained=False)
    
    # Modify final layer for 4 classes
    num_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(num_features, 4)
    
    # Load weights
    model.load_state_dict(torch.load(model_path, map_location=self.device))
    
    model.to(self.device)
    model.eval()
    return model
```

### Step 3: Update Image Preprocessing

Edit `inference.py` - `preprocess_image()` method:

```python
def preprocess_image(self, image_path):
    """Match your model's input requirements"""
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),      # Adjust to your model input size
        transforms.Grayscale(num_output_channels=3),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],    # Or your model's normalization
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    image = Image.open(image_path)
    image_tensor = transform(image).unsqueeze(0)
    return image_tensor
```

### Step 4: Implement Grad-CAM (Optional)

For visualization, implement `generate_grad_cam()`:

```python
def generate_grad_cam(self, image_path, output_path="heatmap.png"):
    """Generate Class Activation Map"""
    
    from torchvision.transforms.functional import to_pil_image
    
    # Load and preprocess image
    image_tensor = self.preprocess_image(image_path).to(self.device)
    
    # Register hook to capture conv features
    features = []
    def hook(module, input, output):
        features.append(output.detach())
    
    # Register hook on final conv layer
    # (Adjust based on your architecture)
    self.model.features[-1].register_forward_hook(hook)
    
    # Forward pass with gradients
    image_tensor.requires_grad_()
    outputs = self.model(image_tensor)
    predicted_class = torch.argmax(outputs, 1).item()
    
    # Compute gradients
    self.model.zero_grad()
    outputs[0, predicted_class].backward()
    
    # Generate heatmap
    gradients = image_tensor.grad.data[0].cpu()
    features_data = features[-1][0].cpu()
    
    # Simple grad-CAM
    weights = gradients.mean(dim=(1, 2), keepdim=True)
    cam = (weights * features_data).sum(dim=0)
    
    # Normalize and save
    cam = torch.relu(cam)
    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
    
    # Resize to original image size
    original_image = Image.open(image_path)
    cam_resized = torch.nn.functional.interpolate(
        cam.unsqueeze(0).unsqueeze(0),
        size=original_image.size[::-1],
        mode='bilinear'
    ).squeeze()
    
    # Save heatmap
    cam_image = to_pil_image(cam_resized)
    cam_image.save(output_path)
    
    return output_path
```

## Testing the Application

### Test 1: UI Loads
1. Run application
2. Verify all UI elements appear
3. Check colors and layouts match mockup

### Test 2: File Upload
1. Click "Browse Files"
2. Select any image file
3. Verify:
   - File path displays
   - Image preview appears
   - Analyze button enables

### Test 3: Drag & Drop
1. Drag image to drop zone
2. Verify same behavior as upload

### Test 4: Analysis
1. Upload valid MRI image (or any image for testing)
2. Click Analyze
3. Verify:
   - Progress bar appears
   - Buttons disable
   - Python process starts
   - Results appear after processing

### Test 5: Error Handling
1. Try uploading non-existent file
2. Try analyzing without upload
3. Verify error messages appear

## Troubleshooting

### Build Errors

#### "Qt not found"
- Verify Qt is installed
- In Qt Creator: Tools → Options → Kits
- Verify kit configuration
- Try: `qmake --version`

#### "Python not found"
- Check: `python --version`
- Add to PATH if needed
- Update `inference.py` with full Python path

#### "moc/uic not found"
- Rebuild: Clean → Build → Run
- Or manually: `qmake` then `make clean && make`

#### Compiler errors
- Verify C++17 support: Project → Build Settings
- Add: `CONFIG += c++17`

### Runtime Errors

#### "Cannot find Python"
- Fix 1: Add Python to system PATH
- Fix 2: In `modelhandler.cpp`, line with `pythonProcess->start()`:
  ```cpp
  // Change from:
  pythonProcess->start("python", arguments);
  
  // To:
  pythonProcess->start("C:\\Python39\\python.exe", arguments);
  ```

#### "Model file not found"
- Check: Is `model.pth` in project root?
- Verify path in `inference.py`
- Try full absolute path

#### "JSON parse error"
- Run inference.py manually:
  ```bash
  python inference.py path/to/image.jpg
  ```
- Check output is valid JSON
- Update parser in `modelhandler.cpp`

#### Application crashes on analyze
- Check Python output: Look at stderr messages
- Verify image format supported
- Try with standard format (.jpg, .png)

## Performance Optimization

### Faster Startup
- Use MinRelSize build: `-DCMAKE_BUILD_TYPE=MinRelSize`
- Precompile headers
- Strip debug symbols

### Faster Inference
- Enable GPU: PyTorch detects CUDA automatically
- Quantize model: `torch.quantization.quantize_dynamic()`
- Use batch processing for multiple images

### Faster UI
- Cache preprocessed images
- Use QThread for long operations (already handled by QProcess)

## Deployment

### Windows Executable Distribution

1. Build in Release mode
2. Collect files:
   ```
   NeuroSight_Dist/
   ├── NeuroSightAI.exe
   ├── inference.py
   ├── model.pth
   ├── requirements.txt
   └── Qt5Core.dll, Qt5Gui.dll, etc. (use windeployqt)
   ```

3. Use `windeployqt`:
   ```cmd
   windeployqt.exe NeuroSightAI.exe --release
   ```

### Linux/macOS Distribution
- Create AppImage (Linux) or .dmg (macOS)
- Or provide source + build instructions
- Ship with requirements.txt

## Next Steps

1. ✅ Build and run successfully
2. ✅ Add your trained model
3. ✅ Test with real MRI data
4. ✅ Customize UI styling
5. ✅ Package for distribution

---

**If you encounter issues, check:**
1. Qt version compatibility
2. Python environment
3. Model file location
4. Compiler errors in output

**For help**: Refer to other documentation files:
- `README.md` - Project overview
- `UI_DESIGNER_GUIDE.md` - UI building
- `ARCHITECTURE.md` - System design

---

**Last Updated**: May 2026
