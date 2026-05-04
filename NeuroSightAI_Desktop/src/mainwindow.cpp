#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFileDialog>
#include <QDragEnterEvent>
#include <QDropEvent>
#include <QMimeData>
#include <QPixmap>
#include <QScrollArea>
#include <QMessageBox>
#include <QSplitter>
#include <QGroupBox>
#include <QApplication>
#include <QScreen>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
    , modelHandler(nullptr)
    , uploadButton(nullptr)
    , analyzeButton(nullptr)
    , imagePathLabel(nullptr)
    , resultLabel(nullptr)
    , confidenceLabel(nullptr)
    , statusLabel(nullptr)
    , imagePreviewLabel(nullptr)
    , heatmapLabel(nullptr)
    , progressBar(nullptr)
    , diseaseStageLabel(nullptr)
{
    ui->setupUi(this);
    
    // Initialize model handler
    modelHandler = new ModelHandler(this);
    
    // Connect signals and slots
    connectSignalsAndSlots();
    
    // Enable drag and drop
    enableDragAndDrop();
    
    // Setup window properties
    this->setWindowTitle("NeuroSight AI - Alzheimer Detection System");
    this->resize(1200, 800);
    
    // Center window on screen
    QScreen *screen = QApplication::primaryScreen();
    QRect screenGeometry = screen->geometry();
    int x = (screenGeometry.width() - this->width()) / 2;
    int y = (screenGeometry.height() - this->height()) / 2;
    this->move(x, y);
    
    // Set initial status
    updateStatusMessage("Ready. Upload an MRI image to begin analysis.");
}

MainWindow::~MainWindow()
{
    delete ui;
    if (modelHandler) {
        delete modelHandler;
    }
}

/**
 * Connect UI signals to slots
 */
void MainWindow::connectSignalsAndSlots()
{
    // Get UI components from the .ui file
    uploadButton = ui->uploadButton;
    analyzeButton = ui->analyzeButton;
    imagePathLabel = ui->imagePathLabel;
    resultLabel = ui->resultLabel;
    confidenceLabel = ui->confidenceLabel;
    statusLabel = ui->statusLabel;
    imagePreviewLabel = ui->imagePreviewLabel;
    heatmapLabel = ui->heatmapLabel;
    progressBar = ui->progressBar;
    diseaseStageLabel = ui->diseaseStageLabel;
    
    // Connect button signals
    connect(uploadButton, &QPushButton::clicked, this, &MainWindow::onUploadButtonClicked);
    connect(analyzeButton, &QPushButton::clicked, this, &MainWindow::onAnalyzeButtonClicked);
    
    // Connect model handler signals
    connect(modelHandler, &ModelHandler::predictionReady, 
            this, &MainWindow::onPredictionReceived);
    connect(modelHandler, &ModelHandler::errorOccurred, 
            this, &MainWindow::onModelError);
    connect(modelHandler, &ModelHandler::processingStarted, 
            this, &MainWindow::onProcessingStarted);
    connect(modelHandler, &ModelHandler::processingFinished, 
            this, &MainWindow::onProcessingFinished);
    
    // Initially disable analyze button
    analyzeButton->setEnabled(false);
    progressBar->setValue(0);
    progressBar->setVisible(false);
}

/**
 * Enable drag and drop functionality for the window
 */
void MainWindow::enableDragAndDrop()
{
    setAcceptDrops(true);
}

/**
 * Handle upload button click - open file dialog
 */
void MainWindow::onUploadButtonClicked()
{
    QString fileName = QFileDialog::getOpenFileName(this,
        tr("Select MRI Image"), "",
        tr("Image Files (*.jpg *.jpeg *.png *.nii *.dcm);;All Files (*)"));
    
    if (!fileName.isEmpty()) {
        selectedImagePath = fileName;
        displayImage(fileName);
        imagePathLabel->setText("File: " + fileName);
        analyzeButton->setEnabled(true);
        updateStatusMessage("Image loaded. Click 'Analyze' to process.");
    }
}

/**
 * Handle analyze button click - send image to model
 */
void MainWindow::onAnalyzeButtonClicked()
{
    if (selectedImagePath.isEmpty()) {
        updateStatusMessage("Please select an image first.", true);
        return;
    }
    
    // Disable button during processing
    analyzeButton->setEnabled(false);
    uploadButton->setEnabled(false);
    
    // Show progress
    progressBar->setVisible(true);
    progressBar->setValue(50);
    
    // Send image to model
    modelHandler->predictImage(selectedImagePath);
}

/**
 * Display selected image in preview
 */
void MainWindow::displayImage(const QString &imagePath)
{
    QPixmap pixmap(imagePath);
    
    if (!pixmap.isNull()) {
        currentImage = pixmap;
        // Scale to fit label while maintaining aspect ratio
        QPixmap scaled = pixmap.scaledToWidth(300, Qt::SmoothTransformation);
        imagePreviewLabel->setPixmap(scaled);
        imagePreviewLabel->setAlignment(Qt::AlignCenter);
    } else {
        imagePreviewLabel->setText("Could not load image");
        updateStatusMessage("Failed to load image file.", true);
    }
}

/**
 * Clear all results from previous analysis
 */
void MainWindow::clearResults()
{
    resultLabel->setText("Disease Stage: -");
    confidenceLabel->setText("Confidence: -");
    diseaseStageLabel->setText("");
    heatmapLabel->setPixmap(QPixmap());
    progressBar->setValue(0);
}

/**
 * Update status message in status label
 */
void MainWindow::updateStatusMessage(const QString &message, bool isError)
{
    statusLabel->setText(message);
    if (isError) {
        statusLabel->setStyleSheet("QLabel { color: #ff4444; font-weight: bold; }");
    } else {
        statusLabel->setStyleSheet("QLabel { color: #44aa44; font-weight: bold; }");
    }
}

/**
 * Called when prediction result is received from model
 */
void MainWindow::onPredictionReceived(const QString &diagnosis, float confidence, const QString &heatmapPath)
{
    // Update diagnosis result
    resultLabel->setText(QString("Disease Stage: <b>%1</b>").arg(diagnosis));
    
    // Update confidence
    confidenceLabel->setText(QString("Confidence: <b>%1%</b>").arg(QString::number(confidence, 'f', 2)));
    
    // Display heatmap if available
    if (!heatmapPath.isEmpty()) {
        QPixmap heatmap(heatmapPath);
        if (!heatmap.isNull()) {
            heatmapImage = heatmap;
            QPixmap scaled = heatmap.scaledToWidth(300, Qt::SmoothTransformation);
            heatmapLabel->setPixmap(scaled);
            heatmapLabel->setAlignment(Qt::AlignCenter);
        }
    }
    
    // Update disease stage
    diseaseStageLabel->setText(QString("Stage: %1").arg(diagnosis));
    diseaseStageLabel->setStyleSheet("QLineEdit { font-size: 14px; font-weight: bold; }");
    
    // Update progress
    progressBar->setValue(100);
    
    // Update status
    updateStatusMessage(QString("Analysis complete. %1 detected with %2% confidence.")
                       .arg(diagnosis).arg(QString::number(confidence, 'f', 1)));
}

/**
 * Called when model reports an error
 */
void MainWindow::onModelError(const QString &errorMessage)
{
    updateStatusMessage(QString("Error: %1").arg(errorMessage), true);
    analyzeButton->setEnabled(true);
    uploadButton->setEnabled(true);
    progressBar->setVisible(false);
    
    QMessageBox::critical(this, "Model Error", 
                         "An error occurred during analysis:\n" + errorMessage);
}

/**
 * Called when processing starts
 */
void MainWindow::onProcessingStarted()
{
    updateStatusMessage("Processing image with ML model...");
    progressBar->setVisible(true);
    progressBar->setValue(25);
}

/**
 * Called when processing finishes
 */
void MainWindow::onProcessingFinished()
{
    analyzeButton->setEnabled(true);
    uploadButton->setEnabled(true);
}

/**
 * Handle drag enter event for drag and drop
 */
void MainWindow::dragEnterEvent(QDragEnterEvent *event)
{
    if (event->mimeData()->hasUrls()) {
        event->acceptProposedAction();
    }
}

/**
 * Handle drop event for drag and drop
 */
void MainWindow::dropEvent(QDropEvent *event)
{
    const QMimeData *mimeData = event->mimeData();
    
    if (mimeData->hasUrls()) {
        QList<QUrl> urls = mimeData->urls();
        if (!urls.isEmpty()) {
            QString filePath = urls.first().toLocalFile();
            selectedImagePath = filePath;
            displayImage(filePath);
            imagePathLabel->setText("File: " + filePath);
            analyzeButton->setEnabled(true);
            updateStatusMessage("Image loaded via drag & drop. Click 'Analyze' to process.");
            event->acceptProposedAction();
        }
    }
}
