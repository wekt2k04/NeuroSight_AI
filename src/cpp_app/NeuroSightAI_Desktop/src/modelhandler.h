#ifndef MODELHANDLER_H
#define MODELHANDLER_H

#include <QObject>
#include <QString>
#include <QThread>
#include <QProcess>

class InferenceWorker : public QObject {
    Q_OBJECT
public:
    explicit InferenceWorker(QObject *parent = nullptr);
    ~InferenceWorker() override;

public slots:
    void run(const QString &imagePath);

signals:
    void predictionReady(const QString &diagnosis, float confidence, const QString &heatmapPath);
    void errorOccurred(const QString &errorMessage);

private:
    QString findPython() const;
    QString findScript() const;
};

class ModelHandler : public QObject {
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
    bool             m_running;
    QThread         *m_thread;
    InferenceWorker *m_worker;
};

#endif // MODELHANDLER_H