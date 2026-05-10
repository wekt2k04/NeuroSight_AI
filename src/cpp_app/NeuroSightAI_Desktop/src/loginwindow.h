#ifndef LOGINWINDOW_H
#define LOGINWINDOW_H

#include <QDialog>
#include <QString>
#include <QLineEdit>
#include <QCheckBox>
#include <QPushButton>
#include <QLabel>

class LoginWindow : public QDialog
{
    Q_OBJECT
public:
    explicit LoginWindow(QWidget *parent = nullptr);

private slots:
    void onLoginClicked();
    void onRegisterClicked();
    void onTogglePassword(bool checked);

private:
    bool validateInputs(QString *errorMessage) const;

    QLineEdit *m_login;
    QLineEdit *m_password;
    QCheckBox *m_showPassword;
    QCheckBox *m_rememberMe;
    QPushButton *m_loginButton;
    QPushButton *m_registerButton;
    QLabel *m_statusLabel;
};

#endif // LOGINWINDOW_H
