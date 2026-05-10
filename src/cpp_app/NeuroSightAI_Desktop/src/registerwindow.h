#ifndef REGISTERWINDOW_H
#define REGISTERWINDOW_H

#include <QDialog>
#include <QString>
#include <QLineEdit>
#include <QComboBox>
#include <QPushButton>
#include <QLabel>

class RegisterWindow : public QDialog
{
    Q_OBJECT
public:
    explicit RegisterWindow(QWidget *parent = nullptr);

private slots:
    void onRegisterClicked();

private:
    bool validateInputs(QString *errorMessage) const;

    QLineEdit *m_fullName;
    QLineEdit *m_email;
    QLineEdit *m_username;
    QLineEdit *m_password;
    QLineEdit *m_confirmPassword;
    QComboBox *m_role;
    QPushButton *m_registerButton;
    QLabel *m_statusLabel;
};

#endif // REGISTERWINDOW_H
