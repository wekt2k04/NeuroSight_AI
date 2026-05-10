#include "db/databasemanager.h"

#include <QApplication>
#include <QCoreApplication>
#include <QFileInfo>
#include <QSqlError>
#include <QSqlQuery>
#include <QFile>
#include <QDir>
#include <QDebug>

#include "authutils.h"
#include "sessionmanager.h"

DatabaseManager* DatabaseManager::s_instance = nullptr;

DatabaseManager::DatabaseManager(QObject *parent)
    : QObject(parent)
    , m_settings(QCoreApplication::applicationDirPath() + "/config.ini", QSettings::IniFormat)
{
}

DatabaseManager* DatabaseManager::instance()
{
    if (!s_instance) s_instance = new DatabaseManager(qApp);
    return s_instance;
}

bool DatabaseManager::ensureOpen()
{
    if (m_db.isOpen()) return true;
    if (m_db.isValid()) return m_db.open();
    return connectToDatabase();
}

bool DatabaseManager::executeQuery(QSqlQuery &query, QString *outError)
{
    if (!query.exec()) {
        qWarning() << "SQL error:" << query.lastError().text();
        if (outError) *outError = query.lastError().text();
        return false;
    }
    return true;
}

bool DatabaseManager::connectToDatabase()
{
    QString dbPath = QCoreApplication::applicationDirPath() + "/neurosight.db";
    qDebug() << "[DB] connectToDatabase path:" << dbPath;

    if (QSqlDatabase::contains("neurosight_connection")) {
        m_db = QSqlDatabase::database("neurosight_connection");
    } else {
        m_db = QSqlDatabase::addDatabase("QSQLITE", "neurosight_connection");
        m_db.setDatabaseName(dbPath);
    }

    if (!m_db.open()) {
        qWarning() << "[DB] Database connection failed:" << m_db.lastError().text();
        return false;
    }

    QSqlQuery pragmaQuery(m_db);
    pragmaQuery.exec("PRAGMA foreign_keys = ON;");

    ensureSchemaObjects(nullptr);
    emit connected();
    return true;
}

void DatabaseManager::closeDatabase()
{
    if (m_db.isOpen()) m_db.close();
    if (QSqlDatabase::contains("neurosight_connection"))
        QSqlDatabase::removeDatabase("neurosight_connection");
    emit disconnected();
}

bool DatabaseManager::initializeSchema(const QString &sqlScriptPath)
{
    if (!ensureOpen()) return false;

    QFile f(sqlScriptPath);
    if (!f.open(QIODevice::ReadOnly | QIODevice::Text)) {
        qWarning() << "Unable to open SQL script:" << sqlScriptPath;
        return false;
    }

    QString content = QString::fromUtf8(f.readAll());
    f.close();

    QStringList statements = content.split(';', Qt::SkipEmptyParts);
    QSqlQuery query(m_db);
    for (QString s : statements) {
        s = s.trimmed();
        if (s.isEmpty()) continue;
        if (!query.exec(s)) {
            qWarning() << "Schema exec failed:" << query.lastError().text()
                       << "Statement:" << s.left(120);
        }
    }
    return ensureSchemaObjects(nullptr);
}

bool DatabaseManager::ensureSchemaObjects(QString *outError)
{
    if (!ensureOpen()) {
        if (outError) *outError = "Database not connected.";
        return false;
    }

    const QStringList ddlStatements = {
        R"(CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            anonymous_code TEXT NOT NULL UNIQUE,
            age_group TEXT CHECK(age_group IN ('0-50','51-65','66-75','76-85','85+')) NOT NULL,
            gender TEXT CHECK(gender IN ('M','F','O')) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ))",

        R"(CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('Radiologist','Admin','DataScientist')) NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            last_login DATETIME DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ))",

        R"(CREATE TABLE IF NOT EXISTS mri_scans (
            scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            scan_date DATE NOT NULL,
            file_path TEXT NOT NULL,
            file_format TEXT CHECK(file_format IN ('DICOM','NIfTI','JPEG','PNG')) NOT NULL,
            image_dimensions TEXT NOT NULL,
            processing_time_ms INTEGER NOT NULL CHECK(processing_time_ms BETWEEN 0 AND 5000),
            is_raw_data INTEGER NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE RESTRICT
        ))",

        R"(CREATE TABLE IF NOT EXISTS diagnoses (
            diagnosis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER NOT NULL,
            classification TEXT CHECK(classification IN ('NonDemented','VeryMildDemented','MildDemented','ModerateDemented')) NOT NULL,
            confidence_score REAL NOT NULL CHECK(confidence_score BETWEEN 0 AND 100),
            processing_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_validated INTEGER NOT NULL DEFAULT 0,
            validated_by_user_id INTEGER DEFAULT NULL,
            validated_at DATETIME DEFAULT NULL,
            radiologist_notes TEXT DEFAULT NULL,
            FOREIGN KEY (scan_id) REFERENCES mri_scans (scan_id) ON DELETE RESTRICT,
            FOREIGN KEY (validated_by_user_id) REFERENCES users (user_id) ON DELETE SET NULL
        ))",

        R"(CREATE TABLE IF NOT EXISTS heatmaps (
            heatmap_id INTEGER PRIMARY KEY AUTOINCREMENT,
            diagnosis_id INTEGER NOT NULL UNIQUE,
            heatmap_file_path TEXT NOT NULL,
            algorithm_used TEXT CHECK(algorithm_used IN ('Grad-CAM','CAM','Grad-CAM++')) NOT NULL DEFAULT 'Grad-CAM',
            overlay_opacity REAL NOT NULL DEFAULT 0.50 CHECK(overlay_opacity BETWEEN 0 AND 1),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (diagnosis_id) REFERENCES diagnoses (diagnosis_id) ON DELETE CASCADE
        ))",

        R"(CREATE TABLE IF NOT EXISTS analysis_reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            diagnosis_id INTEGER NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            pdf_file_path TEXT NOT NULL,
            report_format TEXT NOT NULL DEFAULT 'PDF/A-1b',
            generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_download_at DATETIME DEFAULT NULL,
            download_count INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (diagnosis_id) REFERENCES diagnoses (diagnosis_id) ON DELETE RESTRICT,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE RESTRICT
        ))",

        R"(CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT NULL,
            action_type TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            logged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
        ))",

        R"(CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            logout_time DATETIME DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        ))",

        R"(CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT NULL,
            patient_name TEXT NOT NULL,
            prediction_class TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            image_path TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
        ))"
    };

    for (const QString &sql : ddlStatements) {
        QSqlQuery q(m_db);
        if (!q.exec(sql)) {
            qWarning() << "[DB] Schema DDL failed:" << q.lastError().text();
            if (outError) *outError = q.lastError().text();
            return false;
        }
    }
    return true;
}

bool DatabaseManager::createUser(const QString &fullName, const QString &email, const QString &username,
                                 const QString &passwordPlain, const QString &role, QString *outError)
{
    if (!ensureOpen()) {
        if (outError) *outError = "Database not connected.";
        return false;
    }

    QString hashed = hashPassword(passwordPlain);

    QSqlQuery exists(m_db);
    exists.prepare("SELECT user_id FROM users WHERE username = :username OR email = :email LIMIT 1");
    exists.bindValue(":username", username);
    exists.bindValue(":email", email);
    if (!exists.exec()) {
        if (outError) *outError = exists.lastError().text();
        return false;
    }
    if (exists.next()) {
        if (outError) *outError = "Username or email already exists.";
        return false;
    }

    QSqlQuery q(m_db);
    q.prepare("INSERT INTO users (full_name, username, email, password_hash, role, created_at) "
              "VALUES (:full_name, :username, :email, :phash, :role, datetime('now', 'localtime'))");
    q.bindValue(":full_name", fullName);
    q.bindValue(":username", username);
    q.bindValue(":email", email);
    q.bindValue(":phash", hashed);
    q.bindValue(":role", role);

    return executeQuery(q, outError);
}

bool DatabaseManager::authenticateUser(const QString &usernameOrEmail, const QString &passwordPlain, QString *outError)
{
    if (!ensureOpen()) {
        if (outError) *outError = "Database not connected.";
        return false;
    }

    QSqlQuery q(m_db);
    q.prepare("SELECT user_id, username, email, role, password_hash, full_name "
              "FROM users WHERE username = :u OR email = :u LIMIT 1");
    q.bindValue(":u", usernameOrEmail);
    if (!q.exec()) {
        if (outError) *outError = q.lastError().text();
        return false;
    }
    if (!q.next()) {
        if (outError) *outError = "User not found.";
        return false;
    }

    QString dbHash = q.value("password_hash").toString();
    if (!verifyPassword(passwordPlain, dbHash)) {
        if (outError) *outError = "Invalid credentials.";
        return false;
    }

    m_currentUser.id       = q.value("user_id").toInt();
    m_currentUser.username = q.value("username").toString();
    m_currentUser.email    = q.value("email").toString();
    m_currentUser.role     = q.value("role").toString();
    m_currentUser.fullName = q.value("full_name").toString();

    QSqlQuery u(m_db);
    u.prepare("UPDATE users SET last_login = datetime('now', 'localtime') WHERE user_id = :id");
    u.bindValue(":id", m_currentUser.id);
    u.exec();

    logLogin(m_currentUser.id, nullptr);
    return true;
}

// ── Normalise "Non Demented" → "NonDemented" pour la contrainte CHECK ──
static QString normalizeClass(const QString &cls)
{
    QString s = cls;
    s.remove(' ');
    return s;
}

// ── Normalise l'extension de fichier : "JPG" → "JPEG" pour la contrainte CHECK ──
static QString normalizeFormat(const QString &ext)
{
    QString e = ext.toUpper();
    if (e == "JPG") e = "JPEG";
    return e;
}

bool DatabaseManager::savePrediction(const QString &patientCode, const QString &predictionClass, double confidencePercent,
                                     const QString &imagePath, const QString &heatmapPath, QString *outError)
{
    if (!ensureOpen()) {
        if (outError) *outError = "Database not connected.";
        return false;
    }

    const QString normClass  = normalizeClass(predictionClass);
    const QString normFormat = normalizeFormat(QFileInfo(imagePath).suffix());

    qDebug() << "[savePrediction] patientCode:" << patientCode
             << "| predictionClass:" << predictionClass
             << "| normClass:" << normClass
             << "| normFormat:" << normFormat
             << "| confidence:" << confidencePercent
             << "| imagePath:" << imagePath
             << "| heatmapPath:" << heatmapPath
             << "| currentUser.id:" << m_currentUser.id;

    m_db.transaction();

    // 1) Ensure patient exists
    QSqlQuery q(m_db);
    q.prepare("SELECT patient_id FROM patients WHERE anonymous_code = :code LIMIT 1");
    q.bindValue(":code", patientCode);
    if (!q.exec()) {
        qDebug() << "[savePrediction] ❌ patients SELECT failed:" << q.lastError().text();
        m_db.rollback();
        if (outError) *outError = q.lastError().text();
        return false;
    }

    int patient_id = -1;
    if (q.next()) {
        patient_id = q.value(0).toInt();
        qDebug() << "[savePrediction] existing patient_id:" << patient_id;
    } else {
        QSqlQuery ins(m_db);
        ins.prepare("INSERT INTO patients (anonymous_code, age_group, gender, created_at) "
                    "VALUES (:code, '0-50', 'O', datetime('now', 'localtime'))");
        ins.bindValue(":code", patientCode);
        if (!ins.exec()) {
            qDebug() << "[savePrediction] ❌ patients INSERT failed:" << ins.lastError().text();
            m_db.rollback();
            if (outError) *outError = ins.lastError().text();
            return false;
        }
        patient_id = ins.lastInsertId().toInt();
        qDebug() << "[savePrediction] new patient_id:" << patient_id;
    }

    // 2) Insert mri_scans
    QSqlQuery insScan(m_db);
    insScan.prepare("INSERT INTO mri_scans (patient_id, scan_date, file_path, file_format, "
                    "image_dimensions, processing_time_ms, is_raw_data, created_at) "
                    "VALUES (:pid, date('now'), :fp, :fmt, :dims, :ptime, 1, datetime('now', 'localtime'))");
    insScan.bindValue(":pid",  patient_id);
    insScan.bindValue(":fp",   imagePath);
    insScan.bindValue(":fmt",  normFormat);   // ✅ "JPEG" pas "JPG"
    insScan.bindValue(":dims", QString("%1x%2").arg(224).arg(224));
    insScan.bindValue(":ptime", 0);
    if (!insScan.exec()) {
        qDebug() << "[savePrediction] ❌ mri_scans INSERT failed:" << insScan.lastError().text()
                 << "| format used:" << normFormat;
        m_db.rollback();
        if (outError) *outError = insScan.lastError().text();
        return false;
    }
    int scan_id = insScan.lastInsertId().toInt();
    qDebug() << "[savePrediction] scan_id:" << scan_id;

    // 3) Insert diagnosis
    QSqlQuery insDiag(m_db);
    insDiag.prepare("INSERT INTO diagnoses (scan_id, classification, confidence_score, "
                    "processing_timestamp, is_validated) "
                    "VALUES (:sid, :cls, :conf, datetime('now', 'localtime'), 0)");
    insDiag.bindValue(":sid",  scan_id);
    insDiag.bindValue(":cls",  normClass);   // ✅ "NonDemented" pas "Non Demented"
    insDiag.bindValue(":conf", confidencePercent);
    if (!insDiag.exec()) {
        qDebug() << "[savePrediction] ❌ diagnoses INSERT failed:" << insDiag.lastError().text()
                 << "| normClass:" << normClass;
        m_db.rollback();
        if (outError) *outError = insDiag.lastError().text();
        return false;
    }
    int diag_id = insDiag.lastInsertId().toInt();
    qDebug() << "[savePrediction] diag_id:" << diag_id;

    // 4) Insert heatmap if provided
    if (!heatmapPath.isEmpty()) {
        QSqlQuery insHeat(m_db);
        insHeat.prepare("INSERT INTO heatmaps (diagnosis_id, heatmap_file_path, algorithm_used, "
                        "overlay_opacity, created_at) "
                        "VALUES (:did, :fp, 'Grad-CAM', 0.5, datetime('now', 'localtime'))");
        insHeat.bindValue(":did", diag_id);
        insHeat.bindValue(":fp",  heatmapPath);
        if (!insHeat.exec()) {
            qDebug() << "[savePrediction] ❌ heatmaps INSERT failed:" << insHeat.lastError().text();
            m_db.rollback();
            if (outError) *outError = insHeat.lastError().text();
            return false;
        }
    }

    // 5) Denormalized history row (UI)
    QSqlQuery history(m_db);
    history.prepare("INSERT INTO predictions (user_id, patient_name, prediction_class, "
                    "confidence_score, image_path, created_at) "
                    "VALUES (:uid, :pname, :cls, :conf, :img, datetime('now', 'localtime'))");
    history.bindValue(":uid",   m_currentUser.id > 0 ? QVariant(m_currentUser.id) : QVariant());
    history.bindValue(":pname", patientCode);
    history.bindValue(":cls",   predictionClass);   // version lisible pour l'UI
    history.bindValue(":conf",  confidencePercent);
    history.bindValue(":img",   imagePath);
    if (!executeQuery(history, outError)) {
        qDebug() << "[savePrediction] ❌ predictions INSERT failed:" << *outError;
        m_db.rollback();
        return false;
    }

    // 6) Audit log
    QSqlQuery audit(m_db);
    audit.prepare("INSERT INTO audit_logs (user_id, action_type, entity_type, entity_id, logged_at) "
                  "VALUES (:uid, 'create', 'diagnosis', :eid, datetime('now', 'localtime'))");
    audit.bindValue(":uid", m_currentUser.id > 0 ? QVariant(m_currentUser.id) : QVariant());
    audit.bindValue(":eid", diag_id);
    audit.exec();

    m_db.commit();
    qDebug() << "[savePrediction] ✅ commit OK";
    return true;
}

bool DatabaseManager::logLogin(int userId, QString *outError)
{
    QSqlQuery q(m_db);
    q.prepare("INSERT INTO login_logs (user_id, login_time) VALUES (:uid, datetime('now', 'localtime'))");
    q.bindValue(":uid", userId);
    return executeQuery(q, outError);
}

bool DatabaseManager::logLogout(int userId, QString *outError)
{
    QSqlQuery q(m_db);
    q.prepare("UPDATE login_logs SET logout_time = datetime('now', 'localtime') "
              "WHERE user_id = :uid AND logout_time IS NULL ORDER BY login_time DESC LIMIT 1");
    q.bindValue(":uid", userId);
    return executeQuery(q, outError);
}

bool DatabaseManager::deletePrediction(int predictionId, QString *outError)
{
    QSqlQuery q(m_db);
    q.prepare("DELETE FROM predictions WHERE id = :id");
    q.bindValue(":id", predictionId);
    return executeQuery(q, outError);
}

QSqlQueryModel* DatabaseManager::predictionModelForCurrentUser()
{
    if (!ensureOpen()) return nullptr;

    QSqlQueryModel *model = new QSqlQueryModel();
    QString query = R"(
        SELECT d.diagnosis_id AS id, p.anonymous_code AS patient_code,
               d.classification, d.confidence_score, m.file_path, d.processing_timestamp
        FROM diagnoses d
        JOIN mri_scans m ON m.scan_id = d.scan_id
        JOIN patients p ON p.patient_id = m.patient_id
        ORDER BY d.processing_timestamp DESC
    )";
    model->setQuery(query, m_db);
    return model;
}

QSqlQueryModel* DatabaseManager::predictionHistoryModel(const QString &filter)
{
    if (!ensureOpen()) return nullptr;
    auto *model = new QSqlQueryModel();
    QString sql = "SELECT id, user_id, patient_name, prediction_class, confidence_score, image_path, created_at FROM predictions";

    const bool isAdmin = SessionManager::instance()->isLoggedIn()
                      && SessionManager::instance()->currentRole().compare("Admin", Qt::CaseInsensitive) == 0;

    if (!isAdmin && SessionManager::instance()->isLoggedIn())
        sql += " WHERE user_id = :user_id";

    if (!filter.trimmed().isEmpty()) {
        sql += sql.contains("WHERE")
            ? " AND (patient_name LIKE :filter OR prediction_class LIKE :filter)"
            : " WHERE (patient_name LIKE :filter OR prediction_class LIKE :filter)";
    }

    sql += " ORDER BY created_at DESC";

    QSqlQuery q(m_db);
    q.prepare(sql);
    if (!isAdmin && SessionManager::instance()->isLoggedIn())
        q.bindValue(":user_id", SessionManager::instance()->currentUserId());
    if (!filter.trimmed().isEmpty())
        q.bindValue(":filter", "%" + filter + "%");
    q.exec();
    model->setQuery(std::move(q));
    return model;
}

QSqlQueryModel* DatabaseManager::searchablePredictionsModel(const QString &filter)
{
    return predictionHistoryModel(filter);
}