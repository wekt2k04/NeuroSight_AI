#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QLabel>
#include <QPushButton>
#include <QLineEdit>
#include <QProgressBar>
#include <QPixmap>
#include <QDragEnterEvent>
#include <QDropEvent>
#include "modelhandler.h"

namespace Ui {
    class MainWindow;
}

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    // File upload and UI interactions
    void onUploadButtonClicked();
    void onAnalyzeButtonClicked();

    // Model processing callbacks
    void onPredictionReceived(const QString &diagnosis, float confidence, const QString &heatmapPath);
    void onModelError(const QString &errorMessage);
    void onProcessingStarted();
    void onProcessingFinished();

protected:
    void dragEnterEvent(QDragEnterEvent *event) override;
    void dropEvent(QDropEvent *event) override;

private:
    void setupUI();
    void connectSignalsAndSlots();
    void enableDragAndDrop();
    void displayImage(const QString &imagePath);
    void clearResults();
    void updateStatusMessage(const QString &message, bool isError = false);

    // UI Components
    Ui::MainWindow *ui;
    
    // Core components
    ModelHandler *modelHandler;
    
    // Data members
    QString selectedImagePath;
    QPixmap currentImage;
    QPixmap heatmapImage;
    
    // UI element pointers (created dynamically or from .ui file)
    QPushButton *uploadButton;
    QPushButton *analyzeButton;
    QLabel *imagePathLabel;
    QLabel *resultLabel;
    QLabel *confidenceLabel;
    QLabel *statusLabel;
    QLabel *imagePreviewLabel;
    QLabel *heatmapLabel;
    QProgressBar *progressBar;
    QLineEdit *diseaseStageLabel;
};

#endif // MAINWINDOW_H
