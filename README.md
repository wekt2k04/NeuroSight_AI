# 🧠 NeuroSight AI

Intelligent Early Detection System for Alzheimer's Disease using Deep Learning (EfficientNet) & Medical Imaging.

## 📋 Project Overview

NeuroSight AI is an engineering project developed at ENSA Safi (Ecole Nationale des Sciences Appliquées). Our goal is to assist radiologists by providing a Computer-Aided Diagnosis (CAD) tool capable of detecting early signs of Alzheimer's disease in MRI scans. The system combines a powerful AI model with a secure, offline Desktop application.

## 🚀 Key Features

- **High Accuracy**: Uses EfficientNet (Transfer Learning) for state-of-the-art classification.
- **Explainable AI (XAI)**: Generates Grad-CAM Heatmaps to visualize brain atrophy zones.
- **Privacy First**: 100% Local processing (C++ Desktop App). No patient data is sent to the cloud.
- **Speed**: Diagnosis in under 5 seconds.

## 🛠️ Tech Stack & Architecture

| Component | Technology | Role |
|-----------|-----------|------|
| AI Engine | Python / PyTorch | Model training on Kaggle (GPU). Uses EfficientNet architecture. |
| Application | C++ / Qt Framework | Fast, native desktop interface for the doctor. |
| Inference | ONNX Runtime | Bridges the Python model to the C++ application. |
| Data | Kaggle MRI Dataset | 4 Classes: Non-Demented, Very Mild, Mild, Moderate. |

## 📂 Project Structure

```
NeuroSight_AI/
├── data/                # Raw MRI images (Local only)
├── notebooks/           # Kaggle Notebooks for training & exploration
│   └── NeuroSight_Analysis.ipynb
├── src/                 # Source code
│   ├── cpp_app/         # C++ Qt Desktop Application
│   └── ai_engine/       # Python scripts for preprocessing
├── models/              # Trained models (.pth and .onnx)
└── docs/                # Academic reports and diagrams
```

## 🔄 Workflow & Methodology

We follow a strict MLOps pipeline:

1. **Training**: Performed on Kaggle Kernels to leverage NVIDIA GPUs.
2. **Versioning**: Code is pushed to GitHub branches (dev-wilfried & dev-leila).
3. **Deployment**: The trained model is exported and loaded into the C++ App.

## 👥 Authors

**Project realized by Engineering Students (GIIA):**
- 👨‍💻 **Wilfried TSETSE** (@wekt2k04) - AI & DevOps Lead
- 👩‍💻 **Leila KHEZAZ** (@laila-kz) - Data Engineering & App Dev

**Supervisor:**
- 🎓 **Mme Manal ZETTAM** (Professor at ENSA Safi)

## ⚖️ License

This project is licensed under the MIT License - see the LICENSE file for details.

**Disclaimer**: NeuroSight AI is an academic prototype. It is not a certified medical device and should not be used for actual clinical diagnosis without certification.