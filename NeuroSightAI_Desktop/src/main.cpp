#include <QApplication>
#include "mainwindow.h"

/**
 * NeuroSight AI - Desktop Application
 * Early Alzheimer Detection using MRI Images and Deep Learning
 * 
 * This is the entry point for the application.
 * It creates the main window and starts the event loop.
 */
int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    
    // Set application properties
    QApplication::setApplicationName("NeuroSight AI");
    QApplication::setApplicationVersion("1.0.0");
    QApplication::setApplicationDisplayName("NeuroSight AI - Alzheimer Detection");
    
    // Create and show main window
    MainWindow window;
    window.show();
    
    return app.exec();
}
