#include "modelhandler.h"
#include <QCoreApplication>
#include <QDir>
#include <QImage>
#include <QPainter>
#include <QColor>
#include <QDebug>
#include <algorithm>
#include <vector>
#include <cmath>

const std::vector<QString> CLASS_LABELS = {
    "NonDemented", "VeryMildDemented", "MildDemented", "ModerateDemented"
};

ModelHandler::ModelHandler(QObject *parent)
    : QObject(parent), running(false)
{
    env = std::make_unique<Ort::Env>(ORT_LOGGING_LEVEL_WARNING, "NeuroSight_Inference");
}

ModelHandler::~ModelHandler() {}

bool ModelHandler::initializeModel()
{
    if (session) return true;
    try {
        QDir exeDir(QCoreApplication::applicationDirPath());
        QString modelPathStr = exeDir.absoluteFilePath("best_model.onnx");
        if (!QFile::exists(modelPathStr)) {
            modelPathStr = exeDir.absoluteFilePath("../../../../../models/weights/best_model.onnx");
        }
        
        if (!QFile::exists(modelPathStr)) return false;

#ifdef _WIN32
        std::wstring modelPath = modelPathStr.toStdWString();
#else
        std::string modelPath = modelPathStr.toStdString();
#endif

        Ort::SessionOptions sessionOptions;
        sessionOptions.SetIntraOpNumThreads(1);
        session = std::make_unique<Ort::Session>(*env, modelPath.c_str(), sessionOptions);
        return true;
    } catch (...) {
        return false;
    }
}

void ModelHandler::predictImage(const QString &imagePath)
{
    if (running) {
        emit errorOccurred("Une analyse est déjà en cours.");
        return;
    }
    running = true;
    emit processingStarted();

    if (!initializeModel()) {
        finalizeWithError("Impossible de charger le modèle best_model.onnx.");
        return;
    }

    QImage img;
    if (!img.load(imagePath)) {
        finalizeWithError("Impossible de lire l'image sélectionnée.");
        return;
    }

    img = img.convertToFormat(QImage::Format_RGB888);
    img = img.scaled(224, 224, Qt::IgnoreAspectRatio, Qt::SmoothTransformation);

    const int channels = 3, height = 224, width = 224;
    std::vector<float> inputTensorValues(channels * height * width);
    float mean[] = {0.485f, 0.456f, 0.406f};
    float std[] = {0.229f, 0.224f, 0.225f};

    for (int y = 0; y < height; ++y) {
        const uchar* line = img.scanLine(y);
        for (int x = 0; x < width; ++x) {
            inputTensorValues[0 * height * width + y * width + x] = (line[x * 3] / 255.0f - mean[0]) / std[0];
            inputTensorValues[1 * height * width + y * width + x] = (line[x * 3 + 1] / 255.0f - mean[1]) / std[1];
            inputTensorValues[2 * height * width + y * width + x] = (line[x * 3 + 2] / 255.0f - mean[2]) / std[2];
        }
    }

    try {
        Ort::MemoryInfo memoryInfo = Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);
        std::vector<int64_t> inputDims = {1, 3, 224, 224}; 
        Ort::Value inputTensor = Ort::Value::CreateTensor<float>(
            memoryInfo, inputTensorValues.data(), inputTensorValues.size(), inputDims.data(), inputDims.size());

        // ATTENTION : On attend maintenant 2 sorties (Logits et Heatmaps)
        const char* inputNames[] = {"input"};
        const char* outputNames[] = {"logits", "cam_heatmaps"};

        auto outputTensors = session->Run(
            Ort::RunOptions{nullptr}, inputNames, &inputTensor, 1, outputNames, 2);

        // --- 1. GESTION DU DIAGNOSTIC (Logits) ---
        float* logits = outputTensors[0].GetTensorMutableData<float>();
        float maxLogit = logits[0];
        for(int i=1; i<4; i++) maxLogit = std::max(maxLogit, logits[i]);
        
        float sumExp = 0.0f;
        std::vector<float> probabilities(4);
        for(int i=0; i<4; i++) {
            probabilities[i] = std::exp(logits[i] - maxLogit);
            sumExp += probabilities[i];
        }

        int bestIndex = 0;
        float maxConfidence = 0.0f;
        for(int i=0; i<4; i++) {
            probabilities[i] /= sumExp;
            if(probabilities[i] > maxConfidence) {
                maxConfidence = probabilities[i];
                bestIndex = i;
            }
        }
        QString diagnosis = CLASS_LABELS[bestIndex];

        // --- 2. GESTION DE LA GRAD-CAM (Heatmap) ---
        // Le tenseur 1 a la forme (1, 4, 7, 7)
        float* cam_data = outputTensors[1].GetTensorMutableData<float>();
        
        // On se décale pour lire uniquement la grille 7x7 de la classe gagnante
        float* best_cam = cam_data + (bestIndex * 49); 

        // Recherche du Min et Max pour normaliser entre 0 et 1
        float minVal = best_cam[0], maxVal = best_cam[0];
        for (int i = 1; i < 49; i++) {
            minVal = std::min(minVal, best_cam[i]);
            maxVal = std::max(maxVal, best_cam[i]);
        }
        float range = maxVal - minVal;
        if (range < 1e-5f) range = 1e-5f; // Éviter la division par zéro

        // Création de la petite image 7x7
        QImage heatmap7x7(7, 7, QImage::Format_ARGB32);
        for (int y = 0; y < 7; ++y) {
            for (int x = 0; x < 7; ++x) {
                float val = (best_cam[y * 7 + x] - minVal) / range;
                
                // Formule de la Jet Colormap (Bleu -> Vert -> Rouge)
                int r = std::clamp(255.0f * (1.5f - std::abs(4.0f * val - 3.0f)), 0.0f, 255.0f);
                int g = std::clamp(255.0f * (1.5f - std::abs(4.0f * val - 2.0f)), 0.0f, 255.0f);
                int b = std::clamp(255.0f * (1.5f - std::abs(4.0f * val - 1.0f)), 0.0f, 255.0f);
                
                // Transparence proportionnelle : les zones inactives sont invisibles, les zones actives opaques
                int alpha = val * 200; 
                heatmap7x7.setPixelColor(x, y, QColor(r, g, b, alpha));
            }
        }

        // Lissage et redimensionnement à la taille de l'IRM
        QImage heatmap224 = heatmap7x7.scaled(224, 224, Qt::IgnoreAspectRatio, Qt::SmoothTransformation);

        // Superposition (Fusion) sur l'image IRM originale
        QImage finalImage = img;
        QPainter painter(&finalImage);
        painter.drawImage(0, 0, heatmap224);
        painter.end();

        // Sauvegarde dans un dossier temporaire pour que l'interface graphique puisse l'afficher
        QString tempPath = QDir::temp().absoluteFilePath("neurosight_heatmap.png");
        finalImage.save(tempPath);

        // Fin de l'analyse, on envoie tout à l'interface
        running = false;
        emit predictionReady(diagnosis, maxConfidence, tempPath);
        emit processingFinished();

    } catch (const Ort::Exception& e) {
        finalizeWithError(QString("Erreur pendant l'inférence: %1").arg(e.what()));
    }
}

bool ModelHandler::isProcessing() const { return running; }

void ModelHandler::finalizeWithError(const QString &message) {
    running = false;
    emit errorOccurred(message);
    emit processingFinished();
}