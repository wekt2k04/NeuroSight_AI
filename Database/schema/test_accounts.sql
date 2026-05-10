-- =====================================================
-- NeuroSight AI - Test Accounts (SQLite Version)
-- =====================================================

-- Mot de passe : Admin1234!
INSERT OR IGNORE INTO users (full_name, username, email, password_hash, role, created_at)
VALUES (
    'System Admin',
    'admin',
    'admin@neurosight.local',
    '5ce41ada64f1e8ffb0acfaafa622b141438f3a5777785e7f0b830fb73e40d3d6',
    'Admin',
    datetime('now', 'localtime')
);

-- Mot de passe : Radiologist123!
INSERT OR IGNORE INTO users (full_name, username, email, password_hash, role, created_at)
VALUES (
    'Radiologist Demo',
    'radiologist',
    'radiologist@neurosight.local',
    '124394c828e9a9ef639e5b6c89bc72baaff2913711a96ffa4ba823fa996bb505',
    'Radiologist',
    datetime('now', 'localtime')
);