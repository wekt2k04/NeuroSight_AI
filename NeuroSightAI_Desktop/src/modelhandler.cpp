#include "modelhandler.h"
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QStandardPaths>
#include <QCoreApplication>
#include <QDebug>
#include <QFile>

ModelHandler::ModelHandler(QObject *parent)
    : QObject(parent)
    , pythonProcess(nullptr)
    , isRunning(false)
{
    pythonProcess = new QProcess(this);
    
    // Connect process signals
    connect(pythonProcess, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
            this, &ModelHandler::onProcessFinished);
    connect(pythonProcess, &QProcess::errorOccurred,
            this, &ModelHandler::onProcessError);
    connect(pythonProcess, &QProcess::readyReadStandardOutput,
            this, &ModelHandler::onReadyReadStandardOutput);
    connect(pythonProcess, &QProcess::readyReadStandardError,
            this, &ModelHandler::onReadyReadStandardError);
    
    // Set model script path (relative to application directory)
    modelScriptPath = QCoreApplication::applicationDirPath() + "/inference.py";
}

ModelHandler::~ModelHandler()
{
    if (pythonProcess && pythonProcess->state() == QProcess::Running) {
        pythonProcess->terminate();
        pythonProcess->waitForFinished(3000);
    }
}

/**
 * Send image to Python model for inference
 */
void ModelHandler::predictImage(const QString &imagePath)
{
    if (isRunning) {
        emit errorOccurred("A prediction is already in progress.");
        return;
    }
    
    // Check if image file exists
    QFile imageFile(imagePath);
    if (!imageFile.exists()) {
        emit errorOccurred("Image file not found: " + imagePath);
        return;
    }
    
    // Check if Python script exists
    QFile scriptFile(modelScriptPath);
    if (!scriptFile.exists()) {
        emit errorOccurred("Model script not found. Place 'inference.py' in the application directory.");
        return;
    }
    
    isRunning = true;
    emit processingStarted();
    
    // Prepare arguments for Python script
    QStringList arguments;
    arguments << modelScriptPath << imagePath;
    
    // Start Python process
    // Note: Make sure Python is in PATH or provide full path to python executable
    pythonProcess->start("python", arguments);
    
    if (!pythonProcess->waitForStarted()) {
        isRunning = false;
        emit errorOccurred("Failed to start Python process. Ensure Python is installed and in PATH.");
        emit processingFinished();
    }
}

/**
 * Check if currently processing
 */
bool ModelHandler::isProcessing() const
{
    return isRunning;
}

/**
 * Get model script path
 */
QString ModelHandler::getModelScriptPath() const
{
    return modelScriptPath;
}

/**
 * Handle process finished
 */
void ModelHandler::onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    isRunning = false;
    
    if (exitStatus == QProcess::NormalExit && exitCode == 0) {
        // Parse the output from Python script
        parseModelOutput(lastOutput);
    } else {
        QString errorMsg = QString::fromUtf8(pythonProcess->readAllStandardError());
        if (errorMsg.isEmpty()) {
            errorMsg = "Python process exited with code: " + QString::number(exitCode);
        }
        emit errorOccurred(errorMsg);
    }
    
    emit processingFinished();
    lastOutput.clear();
}

/**
 * Handle process error
 */
void ModelHandler::onProcessError(QProcess::ProcessError error)
{
    isRunning = false;
    
    QString errorMessage;
    switch (error) {
        case QProcess::FailedToStart:
            errorMessage = "Failed to start Python process. Check if Python is installed and in PATH.";
            break;
        case QProcess::Crashed:
            errorMessage = "Python process crashed.";
            break;
        case QProcess::Timedout:
            errorMessage = "Python process timed out.";
            break;
        default:
            errorMessage = "Unknown error occurred.";
    }
    
    emit errorOccurred(errorMessage);
    emit processingFinished();
}

/**
 * Read standard output from Python process
 */
void ModelHandler::onReadyReadStandardOutput()
{
    QByteArray output = pythonProcess->readAllStandardOutput();
    lastOutput.append(QString::fromUtf8(output));
}

/**
 * Read standard error from Python process
 */
void ModelHandler::onReadyReadStandardError()
{
    QByteArray errorOutput = pythonProcess->readAllStandardError();
    QString error = QString::fromUtf8(errorOutput);
    qWarning() << "Python stderr:" << error;
}

/**
 * Parse JSON output from Python model
 * Expected format:
 * {
 *   "diagnosis": "Normal",
 *   "confidence": 0.95,
 *   "heatmap_path": "/path/to/heatmap.png"
 * }
 */
void ModelHandler::parseModelOutput(const QString &jsonOutput)
{
    // Try to find JSON in output (may have other text)
    int jsonStart = jsonOutput.indexOf('{');
    int jsonEnd = jsonOutput.lastIndexOf('}');
    
    if (jsonStart < 0 || jsonEnd < 0) {
        emit errorOccurred("Invalid model output format. Expected JSON response.");
        return;
    }
    
    QString jsonStr = jsonOutput.mid(jsonStart, jsonEnd - jsonStart + 1);
    
    QJsonDocument doc = QJsonDocument::fromJson(jsonStr.toUtf8());
    if (!doc.isObject()) {
        emit errorOccurred("Failed to parse model output JSON.");
        return;
    }
    
    QJsonObject obj = doc.object();
    
    // Extract diagnosis
    if (!obj.contains("diagnosis")) {
        emit errorOccurred("Missing 'diagnosis' in model output.");
        return;
    }
    QString diagnosis = obj["diagnosis"].toString();
    
    // Extract confidence
    float confidence = 0.0f;
    if (obj.contains("confidence")) {
        confidence = obj["confidence"].toDouble() * 100; // Convert to percentage
    }
    
    // Extract heatmap path
    QString heatmapPath = "";
    if (obj.contains("heatmap_path")) {
        heatmapPath = obj["heatmap_path"].toString();
    }
    
    // Validate diagnosis
    QStringList validDiagnoses = {"Normal", "Mild", "Moderate", "Severe"};
    if (!validDiagnoses.contains(diagnosis)) {
        emit errorOccurred("Invalid diagnosis returned: " + diagnosis);
        return;
    }
    
    // Emit success signal
    emit predictionReady(diagnosis, confidence, heatmapPath);
}
