#include "registerwindow.h"

#include "db/databasemanager.h"

#include <QApplication>
#include <QComboBox>
#include <QFormLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QRegularExpression>
#include <QDebug>
#include <QMessageBox>
#include <QVBoxLayout>
#include <QRegularExpression>
#include <QVBoxLayout>

RegisterWindow::RegisterWindow(QWidget *parent)
    : QDialog(parent)
    , m_fullName(new QLineEdit(this))
    , m_email(new QLineEdit(this))
    , m_username(new QLineEdit(this))
    , m_password(new QLineEdit(this))
    , m_confirmPassword(new QLineEdit(this))
    , m_role(new QComboBox(this))
    , m_registerButton(new QPushButton("Create account", this))
    , m_statusLabel(new QLabel(this))
{
    setWindowTitle("NeuroSight AI - Registration");
    m_password->setEchoMode(QLineEdit::Password);
    m_confirmPassword->setEchoMode(QLineEdit::Password);
    m_role->addItems({"Radiologist", "Admin", "DataScientist"});

    auto *form = new QFormLayout();
    form->addRow("Full name", m_fullName);
    form->addRow("Email", m_email);
    form->addRow("Username", m_username);
    form->addRow("Password", m_password);
    form->addRow("Confirm password", m_confirmPassword);
    form->addRow("Role", m_role);

    auto *layout = new QVBoxLayout(this);
    layout->addLayout(form);
    layout->addWidget(m_statusLabel);
    layout->addWidget(m_registerButton);

    connect(m_registerButton, &QPushButton::clicked, this, &RegisterWindow::onRegisterClicked);
}

static bool isValidEmail(const QString &email)
{
    static const QRegularExpression rx(R"(^[\w\.\-]+@[\w\-]+(\.[\w\-]+)+$)");
    return rx.match(email).hasMatch();
}

bool RegisterWindow::validateInputs(QString *errorMessage) const
{
    if (m_fullName->text().trimmed().isEmpty()) {
        if (errorMessage) *errorMessage = "Full name is required.";
        return false;
    }
    if (!isValidEmail(m_email->text().trimmed())) {
        if (errorMessage) *errorMessage = "Enter a valid email address.";
        return false;
    }
    if (m_username->text().trimmed().isEmpty()) {
        if (errorMessage) *errorMessage = "Username is required.";
        return false;
    }
    if (m_password->text().length() < 8) {
        if (errorMessage) *errorMessage = "Password must be at least 8 characters.";
        return false;
    }
    if (m_password->text() != m_confirmPassword->text()) {
        if (errorMessage) *errorMessage = "Passwords do not match.";
        return false;
    }
    return true;
}

void RegisterWindow::onRegisterClicked()
{
    QString error;
    if (!validateInputs(&error)) {
        qDebug() << "Registration validation failed:" << error;
        QMessageBox::warning(this, "Validation", error);
        return;
    }

    if (!DatabaseManager::instance()->connectToDatabase()) {
        QMessageBox::critical(this, "Database", "Unable to connect to the database.");
        return;
    }

    if (!DatabaseManager::instance()->ensureSchemaObjects(&error)) {
        QMessageBox::critical(this, "Schema", error);
        return;
    }

    if (!DatabaseManager::instance()->createUser(m_fullName->text().trimmed(),
                                                 m_email->text().trimmed(),
                                                 m_username->text().trimmed(),
                                                 m_password->text(),
                                                 m_role->currentText(),
                                                 &error)) {
        qDebug() << "Registration failed:" << error;
        QMessageBox::critical(this, "Registration failed", error);
        return;
    }

    QMessageBox::information(this, "Success", "Account created successfully.");
    accept();
}
