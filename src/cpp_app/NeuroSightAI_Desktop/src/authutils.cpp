#include "authutils.h"

#include <QCryptographicHash>

QString hashPassword(const QString &password)
{
    return QString::fromUtf8(QCryptographicHash::hash(password.toUtf8(), QCryptographicHash::Sha256).toHex());
}

bool verifyPassword(const QString &password, const QString &storedHash)
{
    return hashPassword(password) == storedHash;
}
