#include "sessionmanager.h"

#include <QApplication>

SessionManager* SessionManager::s_instance = nullptr;

SessionManager::SessionManager(QObject *parent)
    : QObject(parent)
{
}

SessionManager* SessionManager::instance()
{
    if (!s_instance) s_instance = new SessionManager(qApp);
    return s_instance;
}

void SessionManager::login(int userId, const QString &username, const QString &role)
{
    m_userId = userId;
    m_username = username;
    m_role = role;
    m_loggedIn = true;
}

void SessionManager::logout()
{
    m_userId = -1;
    m_username.clear();
    m_role.clear();
    m_loggedIn = false;
}

bool SessionManager::isLoggedIn() const { return m_loggedIn; }
int SessionManager::currentUserId() const { return m_userId; }
QString SessionManager::currentUsername() const { return m_username; }
QString SessionManager::currentRole() const { return m_role; }
