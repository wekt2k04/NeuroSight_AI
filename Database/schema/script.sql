-- =====================================================
-- NeuroSight AI - SQLite Core Schema
-- =====================================================

-- Activation des clés étrangères pour SQLite
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    anonymous_code TEXT NOT NULL UNIQUE,
    age_group TEXT CHECK(age_group IN ('0-50', '51-65', '66-75', '76-85', '85+')) NOT NULL,
    gender TEXT CHECK(gender IN ('M', 'F', 'O')) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('Radiologist', 'Admin', 'DataScientist')) NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    last_login DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mri_scans (
    scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    scan_date DATE NOT NULL,
    file_path TEXT NOT NULL,
    file_format TEXT CHECK(file_format IN ('DICOM', 'NIfTI', 'JPEG', 'PNG')) NOT NULL,
    image_dimensions TEXT NOT NULL,
    processing_time_ms INTEGER NOT NULL CHECK(processing_time_ms BETWEEN 0 AND 5000),
    is_raw_data INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS diagnoses (
    diagnosis_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,
    classification TEXT CHECK(classification IN ('NonDemented', 'VeryMildDemented', 'MildDemented', 'ModerateDemented')) NOT NULL,
    confidence_score REAL NOT NULL CHECK(confidence_score BETWEEN 0 AND 100),
    processing_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_validated INTEGER NOT NULL DEFAULT 0,
    validated_by_user_id INTEGER DEFAULT NULL,
    validated_at DATETIME DEFAULT NULL,
    radiologist_notes TEXT DEFAULT NULL,
    FOREIGN KEY (scan_id) REFERENCES mri_scans (scan_id) ON DELETE RESTRICT,
    FOREIGN KEY (validated_by_user_id) REFERENCES users (user_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS heatmaps (
    heatmap_id INTEGER PRIMARY KEY AUTOINCREMENT,
    diagnosis_id INTEGER NOT NULL UNIQUE,
    heatmap_file_path TEXT NOT NULL,
    algorithm_used TEXT CHECK(algorithm_used IN ('Grad-CAM', 'CAM', 'Grad-CAM++')) NOT NULL DEFAULT 'Grad-CAM',
    overlay_opacity REAL NOT NULL DEFAULT 0.50 CHECK(overlay_opacity BETWEEN 0 AND 1),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (diagnosis_id) REFERENCES diagnoses (diagnosis_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS analysis_reports (
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
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT NULL,
    action_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    logged_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
);