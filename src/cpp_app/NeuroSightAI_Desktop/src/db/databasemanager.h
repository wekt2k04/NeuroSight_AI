#ifndef DATABASEMANAGER_H
#define DATABASEMANAGER_H

#include <QObject>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QSqlQueryModel>
#include <QSettings>
#include <QString>

struct CurrentUser {
    int id = -1;
    QString username;
    QString fullName;
    QString email;
    QString role;
};

class DatabaseManager : public QObject
{
    Q_OBJECT
public:
    static DatabaseManager* instance();

    bool connectToDatabase();
    void closeDatabase();
    bool executeQuery(QSqlQuery &query, QString *outError = nullptr);

    bool initializeSchema(const QString &sqlScriptPath);
    bool ensureSchemaObjects(QString *outError = nullptr);

    bool createUser(const QString &fullName, const QString &email, const QString &username,
                    const QString &passwordPlain, const QString &role = "Radiologist", QString *outError = nullptr);

    bool authenticateUser(const QString &usernameOrEmail, const QString &passwordPlain, QString *outError = nullptr);

    bool savePrediction(const QString &patientCode, const QString &predictionClass, double confidencePercent,
                        const QString &imagePath, const QString &heatmapPath, QString *outError = nullptr);

    bool logLogin(int userId, QString *outError = nullptr);
    bool logLogout(int userId, QString *outError = nullptr);
    bool deletePrediction(int predictionId, QString *outError = nullptr);

    QSqlQueryModel* predictionModelForCurrentUser();
    QSqlQueryModel* predictionHistoryModel(const QString &filter = QString());
    QSqlQueryModel* searchablePredictionsModel(const QString &filter = QString());

    const CurrentUser& currentUser() const { return m_currentUser; }

    QSettings* settings() { return &m_settings; }

signals:
    void connected();
    void disconnected();

private:
    explicit DatabaseManager(QObject *parent = nullptr);
    bool ensureOpen();

    QSqlDatabase m_db;
    CurrentUser m_currentUser;
    QSettings m_settings;

    static DatabaseManager *s_instance;
};

#endif // DATABASEMANAGER_H
