#include "loginwindow.h"

#include "db/databasemanager.h"
#include "registerwindow.h"
#include "sessionmanager.h"

#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QFormLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QSettings>
#include <QVBoxLayout>
#include <QDebug>
#include <QMessageBox>
#include <QRegularExpression>
#include <QSettings>
#include <QVBoxLayout>

LoginWindow::LoginWindow(QWidget *parent)
    : QDialog(parent)
    , m_login(new QLineEdit(this))
    , m_password(new QLineEdit(this))
    , m_showPassword(new QCheckBox("Show password", this))
    , m_rememberMe(new QCheckBox("Remember me", this))
    , m_loginButton(new QPushButton("Login", this))
    , m_registerButton(new QPushButton("Register", this))
    , m_statusLabel(new QLabel(this))
{
    setWindowTitle("NeuroSight AI - Login");
    setModal(true);
    m_password->setEchoMode(QLineEdit::Password);

    auto *form = new QFormLayout();
    form->addRow("Username / Email", m_login);
    form->addRow("Password", m_password);
    form->addRow(QString(), m_showPassword);
    form->addRow(QString(), m_rememberMe);

    auto *buttons = new QHBoxLayout();
    buttons->addWidget(m_loginButton);
    buttons->addWidget(m_registerButton);

    auto *layout = new QVBoxLayout(this);
    layout->addLayout(form);
    layout->addWidget(m_statusLabel);
    layout->addLayout(buttons);

    connect(m_loginButton, &QPushButton::clicked, this, &LoginWindow::onLoginClicked);
    connect(m_registerButton, &QPushButton::clicked, this, &LoginWindow::onRegisterClicked);
    connect(m_showPassword, &QCheckBox::toggled, this, &LoginWindow::onTogglePassword);

    QSettings *settings = DatabaseManager::instance()->settings();
    m_login->setText(settings->value("remember/username", QString()).toString());
    m_rememberMe->setChecked(settings->value("remember/enabled", false).toBool());
}

bool LoginWindow::validateInputs(QString *errorMessage) const
{
    if (m_login->text().trimmed().isEmpty()) {
        if (errorMessage) *errorMessage = "Enter your username or email.";
        return false;
    }
    if (m_password->text().isEmpty()) {
        if (errorMessage) *errorMessage = "Enter your password.";
        return false;
    }
    return true;
}

void LoginWindow::onTogglePassword(bool checked)
{
    m_password->setEchoMode(checked ? QLineEdit::Normal : QLineEdit::Password);
}

void LoginWindow::onRegisterClicked()
{
    RegisterWindow dlg(this);
    dlg.exec();
}

void LoginWindow::onLoginClicked()
{
    QString error;
    if (!validateInputs(&error)) {
        QMessageBox::warning(this, "Validation", error);
        return;
    }

    const QString usernameOrEmail = m_login->text().trimmed();
    const QString password = m_password->text();

    if (!DatabaseManager::instance()->connectToDatabase()) {
        QMessageBox::critical(this, "Database", "Unable to connect to the database.");
        return;
    }

    if (!DatabaseManager::instance()->authenticateUser(usernameOrEmail, password, &error)) {
        qDebug() << "Login failed:" << error;
        QMessageBox::critical(this, "Login failed", error);
        return;
    }

    const CurrentUser user = DatabaseManager::instance()->currentUser();
    SessionManager::instance()->login(user.id, user.username, user.role);

    QSettings *settings = DatabaseManager::instance()->settings();
    if (m_rememberMe->isChecked()) {
        settings->setValue("remember/username", usernameOrEmail);
        settings->setValue("remember/enabled", true);
    } else {
        settings->remove("remember/username");
        settings->setValue("remember/enabled", false);
    }

    accept();
}
