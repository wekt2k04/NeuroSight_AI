#ifndef MODELHANDLER_H
#define MODELHANDLER_H

#include <QObject>
#include <QString>
#include <memory>

// Inclusion de l'API C++ de ONNX Runtime
#include <onnxruntime_cxx_api.h>

class ModelHandler : public QObject
{
    Q_OBJECT

public:
    explicit ModelHandler(QObject *parent = nullptr);
    ~ModelHandler() override;

    void predictImage(const QString &imagePath);
    bool isProcessing() const;

signals:
    void processingStarted();
    void predictionReady(const QString &diagnosis, float confidence, const QString &heatmapPath);
    void errorOccurred(const QString &errorMessage);
    void processingFinished();

private:
    bool running;
    
    // Composants ONNX Runtime
    std::unique_ptr<Ort::Env> env;
    std::unique_ptr<Ort::Session> session;
    
    // Fonctions utilitaires internes
    bool initializeModel();
    void finalizeWithError(const QString &message);
};

#endif // MODELHANDLER_H