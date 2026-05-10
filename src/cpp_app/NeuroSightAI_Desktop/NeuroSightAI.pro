QT += core gui sql

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++17

INCLUDEPATH += src
INCLUDEPATH += third_party/onnxruntime/include

LIBS += -L$$PWD/third_party/onnxruntime/lib -lonnxruntime

# Specify Qt version (Qt 6.x)
lessThan(QT_MAJOR_VERSION, 6) {
    error("This project requires Qt 6.0 or later. Found Qt" $$QT_VERSION)
}

TARGET = NeuroSightAI
TEMPLATE = app

# Source files
SOURCES += \
    src/main.cpp \
    src/mainwindow.cpp \
    src/modelhandler.cpp \
    src/authutils.cpp \
    src/sessionmanager.cpp \
    src/loginwindow.cpp \
    src/registerwindow.cpp \
    src/db/databasemanager.cpp

# Header files
HEADERS += \
    src/mainwindow.h \
    src/modelhandler.h \
    src/authutils.h \
    src/sessionmanager.h \
    src/loginwindow.h \
    src/registerwindow.h \
    src/db/databasemanager.h

# UI files
FORMS += \
    ui/mainwindow.ui

# Resource files
RESOURCES += \
    resources/resources.qrc

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

# Python scripting support (for calling the ML model)
QT += network
