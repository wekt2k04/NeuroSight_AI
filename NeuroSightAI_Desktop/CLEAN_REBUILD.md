# Clean Rebuild Instructions for NeuroSight AI

If you encounter UI file or NMAKE errors, follow these steps for a complete clean rebuild:

## Clean Rebuild (VS 2022 Developer Command Prompt)

```powershell
# 1. Navigate to project root
cd c:\Users\kheza\Downloads\Neurosight_AI\NeuroSightAI_Desktop

# 2. Activate Python venv
.venv\Scripts\Activate.ps1

# 3. Set Qt path
set QT_PATH=C:\Qt\6.x\msvc2022_64

# 4. Remove old build directory completely
rmdir /s /q build

# 5. Create fresh build directory
mkdir build
cd build

# 6. Configure with CMake (clean slate)
cmake .. -G "NMake Makefiles" -DCMAKE_PREFIX_PATH=%QT_PATH% -DCMAKE_BUILD_TYPE=Release

# 7. Build
cmake --build .

# 8. Run
cd Release
set PYTHONPATH=..\..\
.\NeuroSightAI.exe
```

## What was fixed

- **UI file path**: Changed from full paths to relative paths (Qt6 AUTOUIC now finds `ui/mainwindow.ui` correctly)
- **Include directories**: Cleaned up to include binary directory where uic generates headers
- **NMAKE error**: Removed problematic POST_BUILD custom command that was causing the build to fail

## If you still get errors

1. **"ui_mainwindow.h: No such file"** → Run `cmake --build .` again (sometimes uic needs a second pass)
2. **"Qt path not found"** → Verify your Qt installation path and update `%QT_PATH%` variable
3. **DLL not found at runtime** → Add `%QT_PATH%\bin` to PATH before running the exe

## Alternative: Using Visual Studio instead of NMake

If you prefer to use Visual Studio's build system:

```powershell
cd c:\Users\kheza\Downloads\Neurosight_AI\NeuroSightAI_Desktop
rmdir /s /q build
mkdir build
cd build

# Generate Visual Studio solution
cmake .. -G "Visual Studio 17 2022" -DCMAKE_PREFIX_PATH=%QT_PATH%

# Then open and build in Visual Studio:
# start NeuroSightAI.sln
```
