# NeuroSight AI Database and Authentication Integration

## Overview

This desktop application now boots through a login-first flow, connects to MySQL through `DatabaseManager`, stores the authenticated user in `SessionManager`, and persists prediction history after each successful MRI inference.

## Class Responsibilities

- `DatabaseManager`
  - Opens/closes the MySQL connection
  - Initializes the schema and enriches missing columns safely
  - Creates users, authenticates users, stores prediction history, and tracks login/logout events
  - Returns history models for the UI
- `SessionManager`
  - Stores the current user id, username, role, and login state
- `LoginWindow`
  - Validates credentials and opens the registration dialog
- `RegisterWindow`
  - Validates registration input and creates new users
- `MainWindow`
  - Keeps the MRI workflow intact
  - Saves each successful prediction to the database
  - Hosts the history dock with search and delete actions
- `ModelHandler`
  - Unchanged prediction pipeline

## Database Schema

The project uses the provided MySQL schema in `Database/schema/script.sql` and enriches it at startup with:

- `users.full_name`
- `users.is_active`
- `users.last_login`
- `predictions`
- `login_logs`

The app also continues using the existing core tables from your script for MRI and diagnosis records.

## Authentication Flow

1. App starts.
2. `DatabaseManager` connects to MySQL.
3. Schema is created or enriched if needed.
4. `LoginWindow` opens.
5. On success, `SessionManager` stores the user session.
6. `MainWindow` opens.
7. Logout records the logout time and returns to login mode.

## Prediction Persistence Flow

1. User uploads MRI image.
2. Existing inference flow runs unchanged.
3. After a successful prediction, `MainWindow` calls `DatabaseManager::savePrediction(...)`.
4. The app stores:
   - user id
   - patient name
   - prediction class
   - confidence score
   - MRI image path
   - timestamp
5. The history dock refreshes automatically.

## Build Notes

Required Qt modules:

- `Qt Core`
- `Qt Gui`
- `Qt Widgets`
- `Qt Network`
- `Qt Sql`

Required Qt version:

- Qt 6.x

Required MySQL version:

- MySQL 8.0 or newer recommended

## Config File

Create `config.ini` next to the desktop app executable based on `config.ini.example`:

```ini
[mysql]
host=127.0.0.1
port=3306
user=root
password=
database=NeuroSightAI

[remember]
enabled=false
username=
```

## Run Instructions

1. Start MySQL.
2. Create a `config.ini` from `config.ini.example`.
3. Build the desktop app with either qmake or CMake.
4. Launch the app.
5. Register a user or sign in with a seeded account from `Database/schema/test_accounts.sql`.

## Seed Accounts

The repository includes `Database/schema/test_accounts.sql` with demo accounts:

- `admin` / `Admin1234!`
- `radiologist` / `Radiologist123!`

## Notes

- Passwords are hashed with SHA-256 using `QCryptographicHash`.
- Prepared statements are used for database writes and lookups.
- The MRI inference pipeline was not modified.
- The history dock is scoped to the current user unless the user role is `Admin`.
