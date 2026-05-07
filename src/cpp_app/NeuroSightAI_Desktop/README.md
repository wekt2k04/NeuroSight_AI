# NeuroSight AI Desktop

Qt desktop client for MRI analysis. The app calls the Python inference bridge with `QProcess` and exchanges JSON over stdout.

## Current Layout

```
NeuroSightAI_Desktop/
├── BUILD_VS2022.md
├── CMakeLists.txt
├── NeuroSightAI.pro
├── README.md
├── SETUP_GUIDE.md
├── resources/
├── src/
│   ├── main.cpp
│   ├── mainwindow.h
│   ├── mainwindow.cpp
│   ├── modelhandler.h
│   └── modelhandler.cpp
└── ui/
    └── mainwindow.ui
```

The Python bridge used by the desktop app is at:

`../../python/inference.py` (resolved by `ModelHandler` search paths)

Default model weights path expected by the bridge:

`models/weights/best_model.pt`

## Quick Build (Qt Creator)

1. Open `NeuroSightAI.pro`.
2. Select a Qt 6+ kit.
3. Build (`Ctrl+B`).
4. Run (`Ctrl+R`).

For VS2022 + CMake/NMake flow, use `BUILD_VS2022.md`.

## JSON Contract (Python -> Qt)

Desktop expects one JSON object on stdout per run:

```json
{
  "prediction": "NonDemented|VeryMildDemented|MildDemented|ModerateDemented",
  "diagnosis": "NonDemented|VeryMildDemented|MildDemented|ModerateDemented",
  "confidence": 0.0,
  "error": null,
  "heatmap_path": ""
}
```

Notes:

- `confidence` is normalized in `[0, 1]`.
- UI converts confidence to percent for display.
- On failure, `error` is populated and process exits non-zero.

## Runtime Checks

1. Ensure Python dependencies from workspace root `requirements.txt` are installed.
2. Ensure `models/weights/best_model.pt` exists.
3. Launch desktop and run analysis on a valid image (`.jpg`, `.jpeg`, `.png`, `.bmp`, `.tif`, `.tiff`).

### Common Failures

- If the app reports model weights missing, provide `models/weights/best_model.pt`.
- If the app reports JSON parse errors, run `src/python/inference.py` manually and verify it emits one JSON object to stdout.
- If `/predict` import warns about multipart support in backend-only runs, install `python-multipart` in the active environment.
