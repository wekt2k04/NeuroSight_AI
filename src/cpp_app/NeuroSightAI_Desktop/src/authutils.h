#ifndef AUTHUTILS_H
#define AUTHUTILS_H

#include <QString>

QString hashPassword(const QString &password);
bool verifyPassword(const QString &password, const QString &storedHash);

#endif // AUTHUTILS_H
