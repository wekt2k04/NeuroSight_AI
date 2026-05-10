#include "modelhandler.h"
#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QProcess>
#include <QProcessEnvironment>
#include <QJsonDocument>
#include <QJsonObject>
#include <QDebug>


InferenceWorker::InferenceWorker(QObject *parent) : QObject(parent) {}
InferenceWorker::~InferenceWorker() {}


QString InferenceWorker::findPython() const
{
    QStringList candidates = {
        "C:/ProgramData/anaconda3/envs/neurosight_ai_env/python.exe",
        "C:/Users/Wilfried/anaconda3/envs/neurosight_ai_env/python.exe",
        "C:/Users/Wilfried/AppData/Local/anaconda3/envs/neurosight_ai_env/python.exe",
    };
    for (const QString &p : candidates)
        if (QFile::exists(p)) return p;
    return "python";
}


QString InferenceWorker::findScript() const
{
    QDir exeDir(QCoreApplication::applicationDirPath());
    QStringList relPaths = {
        "neurosight_inference.py",
        "../../../../../neurosight_inference.py",
        "../../../../neurosight_inference.py",
        "../../../neurosight_inference.py",
    };
    for (const QString &rel : relPaths) {
        QString abs = exeDir.absoluteFilePath(rel);
        if (QFile::exists(abs)) return QDir::cleanPath(abs);
    }
    return QString();
}


void InferenceWorker::run(const QString &imagePath)
{
    QString python = findPython();
    QString script = findScript();

    if (script.isEmpty()) {
        emit errorOccurred("Script neurosight_inference.py introuvable.");
        return;
    }

    QString heatmapPath = QDir::temp().absoluteFilePath("neurosight_heatmap.png");

    QProcessEnvironment env = QProcessEnvironment::systemEnvironment();
    env.insert("PYTHONIOENCODING", "utf-8");
    env.insert("PYTHONUTF8", "1");

    QProcess proc;
    proc.setProcessChannelMode(QProcess::SeparateChannels);
    proc.setProcessEnvironment(env);
    proc.start(python, { "-u", script, imagePath, heatmapPath });

    if (!proc.waitForStarted(5000)) {
        emit errorOccurred("Impossible de lancer Python. Verifiez le PATH.");
        return;
    }
    if (!proc.waitForFinished(60000)) {
        proc.kill();
        emit errorOccurred("Timeout : inference > 60s.");
        return;
    }

    QByteArray output = proc.readAllStandardOutput().trimmed();

    if (proc.exitCode() != 0 || output.isEmpty()) {
        QByteArray errOutput = proc.readAllStandardError();
        emit errorOccurred(QString("Erreur Python : %1").arg(QString::fromUtf8(errOutput)));
        return;
    }

    // Extraire uniquement la ligne JSON (ignore warnings Matplotlib sur stderr)
    QByteArray jsonLine;
    for (const QByteArray &line : output.split('\n')) {
        QByteArray trimmed = line.trimmed();
        if (trimmed.startsWith('{')) { jsonLine = trimmed; break; }
    }

    if (jsonLine.isEmpty()) {
        emit errorOccurred("Pas de JSON dans la sortie : " + QString::fromUtf8(output));
        return;
    }

    QJsonParseError err;
    QJsonDocument doc = QJsonDocument::fromJson(jsonLine, &err);
    if (doc.isNull()) {
        emit errorOccurred(QString("Reponse invalide : %1 | %2")
                           .arg(err.errorString(), QString::fromUtf8(jsonLine)));
        return;
    }

    QJsonObject obj   = doc.object();
    QString diagnosis = obj.value("predicted_class").toString("Unknown");
    float confidence  = static_cast<float>(obj.value("confidence").toDouble(0.0));
    QString heatmap   = obj.value("heatmap_path").toString(heatmapPath);

    emit predictionReady(diagnosis, confidence, heatmap);
}


ModelHandler::ModelHandler(QObject *parent)
    : QObject(parent), m_running(false)
    , m_thread(new QThread(this))
    , m_worker(new InferenceWorker)
{
    m_worker->moveToThread(m_thread);

    connect(m_worker, &InferenceWorker::predictionReady,
            this, [this](const QString &d, float c, const QString &h) {
        m_running = false;
        emit predictionReady(d, c, h);
        emit processingFinished();
    });
    connect(m_worker, &InferenceWorker::errorOccurred,
            this, [this](const QString &e) {
        m_running = false;
        emit errorOccurred(e);
        emit processingFinished();
    });
    connect(m_thread, &QThread::finished, m_worker, &QObject::deleteLater);
    m_thread->start();
}


ModelHandler::~ModelHandler()
{
    m_thread->quit();
    m_thread->wait(3000);
}


void ModelHandler::predictImage(const QString &imagePath)
{
    if (m_running) {
        emit errorOccurred("Une analyse est deja en cours.");
        return;
    }
    m_running = true;
    emit processingStarted();
    QMetaObject::invokeMethod(m_worker, "run", Qt::QueuedConnection,
                              Q_ARG(QString, imagePath));
}


bool ModelHandler::isProcessing() const { return m_running; }