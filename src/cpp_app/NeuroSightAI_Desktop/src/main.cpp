#include <QApplication>
#include <QCoreApplication>
#include <QFile>
#include <QMessageBox>

#include "db/databasemanager.h"
#include "loginwindow.h"
#include "mainwindow.h"

int main(int argc, char *argv[])
{
    int currentExitCode = 0;

    do {
        QApplication app(argc, argv);
        QApplication::setApplicationName("NeuroSight AI");
        QApplication::setApplicationVersion("1.0.0");
        QApplication::setApplicationDisplayName("NeuroSight AI - Alzheimer Detection");

        DatabaseManager *db = DatabaseManager::instance();
        if (!db->connectToDatabase()) {
            QMessageBox::critical(nullptr, "Erreur Base de Donnees",
                                  "Impossible d initialiser la base SQLite locale.");
            return 1;
        }

        const QString schemaPath = QCoreApplication::applicationDirPath()
                                   + "/../../../../Database/schema/script.sql";
        if (QFile::exists(schemaPath)) {
            db->initializeSchema(schemaPath);
        } else {
            db->ensureSchemaObjects(nullptr);
        }

        LoginWindow login;
        if (login.exec() != QDialog::Accepted) {
            return 0;
        }

        MainWindow window;
        window.show();

        currentExitCode = app.exec();

    } while (currentExitCode == 42);

    return currentExitCode;
}