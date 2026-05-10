#ifndef SESSIONMANAGER_H
#define SESSIONMANAGER_H

#include <QObject>
#include <QString>

class SessionManager : public QObject
{
    Q_OBJECT
public:
    static SessionManager* instance();

    void login(int userId, const QString &username, const QString &role);
    void logout();

    bool isLoggedIn() const;
    int currentUserId() const;
    QString currentUsername() const;
    QString currentRole() const;

private:
    explicit SessionManager(QObject *parent = nullptr);

    int m_userId = -1;
    QString m_username;
    QString m_role;
    bool m_loggedIn = false;

    static SessionManager *s_instance;
};

#endif // SESSIONMANAGER_H
