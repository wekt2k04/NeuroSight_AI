#ifndef MODELHANDLER_H
#define MODELHANDLER_H

#include <QObject>
#include <QProcess>
#include <QString>

/**
 * @class ModelHandler
 * @brief Handles communication with the Python ML model
 * 
 * This class manages:
 * - Running the Python inference script
 * - Passing image paths to the model
 * - Parsing prediction results
 * - Error handling
 */
class ModelHandler : public QObject {
    Q_OBJECT

public:
    explicit ModelHandler(QObject *parent = nullptr);
    ~ModelHandler();

    /**
     * @brief Send image to model for inference
     * @param imagePath Full path to the MRI image
     */
    void predictImage(const QString &imagePath);

    /**
     * @brief Check if model process is currently running
     * @return true if processing, false otherwise
     */
    bool isProcessing() const;

    /**
     * @brief Get the path to the Python model script
     */
    QString getModelScriptPath() const;

signals:
    /**
     * @brief Emitted when prediction is complete
     * @param diagnosis Disease stage (Normal, Mild, Moderate, Severe)
     * @param confidence Prediction confidence score (0-100)
     * @param heatmapPath Path to generated heatmap image
     */
    void predictionReady(const QString &diagnosis, float confidence, const QString &heatmapPath);

    /**
     * @brief Emitted when an error occurs
     * @param errorMessage Description of the error
     */
    void errorOccurred(const QString &errorMessage);

    /**
     * @brief Emitted when processing starts
     */
    void processingStarted();

    /**
     * @brief Emitted when processing finishes
     */
    void processingFinished();

private slots:
    /**
     * @brief Handle process finished signal
     */
    void onProcessFinished(int exitCode, QProcess::ExitStatus exitStatus);

    /**
     * @brief Handle process error signal
     */
    void onProcessError(QProcess::ProcessError error);

    /**
     * @brief Handle standard output from process
     */
    void onReadyReadStandardOutput();

    /**
     * @brief Handle standard error from process
     */
    void onReadyReadStandardError();

private:
    /**
     * @brief Parse JSON output from Python script
     * @param jsonOutput Raw JSON string from stdout
     */
    void parseModelOutput(const QString &jsonOutput);

    QProcess *pythonProcess;
    QString modelScriptPath;
    QString lastOutput;
    bool isRunning;
};

#endif // MODELHANDLER_H
