#include "mainwindow.h"
#include "ui_mainwindow.h"

#include "db/databasemanager.h"
#include "sessionmanager.h"

#include <QAction>
#include <QDragEnterEvent>
#include <QDockWidget>
#include <QFileDialog>
#include <QFileInfo>
#include <QKeySequence>
#include <QMenuBar>
#include <QMessageBox>
#include <QMimeData>
#include <QPixmap>
#include <QScreen>
#include <QLineEdit>
#include <QPushButton>
#include <QSortFilterProxyModel>
#include <QTableView>
#include <QHeaderView>
#include <QAbstractItemView>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QShortcut>
#include <QTimer>
#include <QCoreApplication>
#include <QGuiApplication>
#include <QSqlQueryModel>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
    , modelHandler(new ModelHandler(this))
    , historyDock(nullptr)
    , historyFilterEdit(nullptr)
    , historyTable(nullptr)
    , historyProxyModel(nullptr)
    , deleteHistoryButton(nullptr)
    , refreshHistoryButton(nullptr)
    , workflowState(WorkflowState::AwaitingImage)
    , progressPulseTimer(new QTimer(this))
{
    ui->setupUi(this);
    setupWindow();
    setupConnections();
    setupShortcuts();
    setupAccessibilityHints();
    setupSessionUi();
    setupHistoryDock();

    progressPulseTimer->setInterval(120);
    connect(progressPulseTimer, &QTimer::timeout, this, &MainWindow::onProgressPulse);

    setWorkflowState(WorkflowState::AwaitingImage,
                     "Drop an MRI scan or use Browse to start the clinical workflow.");
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::setupWindow()
{
    setWindowTitle("NeuroSight AI - Neuro-Cognitive Diagnostic Workspace");
    resize(1360, 860);
    setAcceptDrops(true);

    const QRect screenGeometry = QGuiApplication::primaryScreen()->availableGeometry();
    move(screenGeometry.center() - rect().center());

    ui->progressBar->setVisible(false);
    ui->progressBar->setRange(0, 0);  // ✅ mode indéterminé Qt natif
    ui->analyzeButton->setEnabled(false);
    clearResultPanel();
}

void MainWindow::setupConnections()
{
    connect(ui->uploadButton, &QPushButton::clicked, this, &MainWindow::onUploadButtonClicked);
    connect(ui->analyzeButton, &QPushButton::clicked, this, &MainWindow::onAnalyzeButtonClicked);

    connect(modelHandler, &ModelHandler::predictionReady, this, &MainWindow::onPredictionReceived);
    connect(modelHandler, &ModelHandler::errorOccurred, this, &MainWindow::onModelError);
    connect(modelHandler, &ModelHandler::processingStarted, this, &MainWindow::onProcessingStarted);
    connect(modelHandler, &ModelHandler::processingFinished, this, &MainWindow::onProcessingFinished);
}

void MainWindow::setupShortcuts()
{
    auto *openShortcut = new QShortcut(QKeySequence::Open, this);
    connect(openShortcut, &QShortcut::activated, this, &MainWindow::onUploadButtonClicked);

    auto *analyzeShortcut = new QShortcut(QKeySequence(Qt::CTRL | Qt::Key_Return), this);
    connect(analyzeShortcut, &QShortcut::activated, [this]() {
        if (ui->analyzeButton->isEnabled()) {
            onAnalyzeButtonClicked();
        }
    });
}

void MainWindow::setupAccessibilityHints()
{
    ui->uploadButton->setToolTip("Step 1: Select a patient scan");
    ui->analyzeButton->setToolTip("Step 2: Launch AI inference");
    ui->imagePreviewLabel->setToolTip("Visual confirmation area");
    ui->heatmapLabel->setToolTip("Explainability map area");
}

void MainWindow::setupSessionUi()
{
    if (!SessionManager::instance()->isLoggedIn()) {
        return;
    }

    const QString userText = QString("Signed in as %1 (%2)")
                                 .arg(SessionManager::instance()->currentUsername(),
                                      SessionManager::instance()->currentRole());
    updateStatusMessage(userText, false);

    auto *logoutAction = new QAction("Logout", this);
    connect(logoutAction, &QAction::triggered, this, &MainWindow::onLogoutRequested);
    menuBar()->addAction(logoutAction);
}

void MainWindow::setupHistoryDock()
{
    historyDock = new QDockWidget("Prediction History", this);
    historyDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea | Qt::BottomDockWidgetArea);

    auto *container = new QWidget(historyDock);
    auto *layout = new QVBoxLayout(container);

    historyFilterEdit = new QLineEdit(container);
    historyFilterEdit->setPlaceholderText("Search patient or class...");

    historyTable = new QTableView(container);
    historyTable->setSelectionBehavior(QAbstractItemView::SelectRows);
    historyTable->setSelectionMode(QAbstractItemView::SingleSelection);
    historyTable->setSortingEnabled(true);
    historyTable->horizontalHeader()->setStretchLastSection(true);

    historyProxyModel = new QSortFilterProxyModel(this);
    historyProxyModel->setFilterCaseSensitivity(Qt::CaseInsensitive);
    historyProxyModel->setFilterKeyColumn(-1);

    deleteHistoryButton = new QPushButton("Delete Selected", container);
    refreshHistoryButton = new QPushButton("Refresh", container);

    auto *buttonRow = new QHBoxLayout();
    buttonRow->addWidget(deleteHistoryButton);
    buttonRow->addWidget(refreshHistoryButton);

    layout->addWidget(historyFilterEdit);
    layout->addWidget(historyTable);
    layout->addLayout(buttonRow);
    container->setLayout(layout);
    historyDock->setWidget(container);
    addDockWidget(Qt::BottomDockWidgetArea, historyDock);

    connect(historyFilterEdit, &QLineEdit::textChanged, this, &MainWindow::onHistoryFilterChanged);
    connect(deleteHistoryButton, &QPushButton::clicked, this, &MainWindow::onDeleteHistoryClicked);
    connect(refreshHistoryButton, &QPushButton::clicked, this, &MainWindow::onRefreshHistoryClicked);

    refreshHistory();
}

void MainWindow::refreshHistory()
{
    if (!historyTable || !historyProxyModel) return;

    QSqlQueryModel *model = DatabaseManager::instance()->predictionHistoryModel(
        historyFilterEdit ? historyFilterEdit->text() : QString());
    if (!model) {
        QMessageBox::warning(this, "History", "Unable to load prediction history.");
        return;
    }

    if (historyProxyModel->sourceModel()) {
        historyProxyModel->sourceModel()->deleteLater();
    }

    model->setParent(this);
    historyProxyModel->setSourceModel(model);
    historyTable->setModel(historyProxyModel);
    historyTable->hideColumn(0);
    historyTable->hideColumn(1);
}

void MainWindow::setWorkflowState(WorkflowState state, const QString &message)
{
    workflowState = state;

    switch (workflowState) {
    case WorkflowState::AwaitingImage:
        ui->uploadButton->setEnabled(true);
        ui->analyzeButton->setEnabled(false);
        ui->progressBar->setVisible(false);
        break;
    case WorkflowState::ImageReady:
        ui->uploadButton->setEnabled(true);
        ui->analyzeButton->setEnabled(true);
        ui->progressBar->setVisible(false);
        break;
    case WorkflowState::Analyzing:
        ui->uploadButton->setEnabled(false);
        ui->analyzeButton->setEnabled(false);
        ui->progressBar->setVisible(true);
        break;
    case WorkflowState::ResultReady:
        ui->uploadButton->setEnabled(true);
        ui->analyzeButton->setEnabled(true);
        ui->progressBar->setVisible(true);
        ui->progressBar->setValue(100);
        break;
    case WorkflowState::ErrorState:
        ui->uploadButton->setEnabled(true);
        ui->analyzeButton->setEnabled(!selectedImagePath.isEmpty());
        ui->progressBar->setVisible(false);
        break;
    }

    updateWorkflowIndicators();
    if (!message.isEmpty()) {
        updateStatusMessage(message, workflowState == WorkflowState::ErrorState);
    }
}

void MainWindow::updateWorkflowIndicators()
{
    const auto accentFor = [this](int step) -> QString {
        const int activeStep =
            (workflowState == WorkflowState::AwaitingImage) ? 1 :
            (workflowState == WorkflowState::ImageReady)    ? 2 :
            (workflowState == WorkflowState::Analyzing)     ? 3 : 4;

        if (step < activeStep)
            return "background:#1f7a5a;color:#e9fff5;border:1px solid #2bbf8a;";
        if (step == activeStep)
            return "background:#1a3b61;color:#d8ebff;border:1px solid #3f7fc4;";
        return "background:#1b2330;color:#7f90a8;border:1px solid #2f3a4a;";
    };

    ui->step1Badge->setStyleSheet("QLabel{" + accentFor(1) + "border-radius:10px;padding:6px 10px;}");
    ui->step2Badge->setStyleSheet("QLabel{" + accentFor(2) + "border-radius:10px;padding:6px 10px;}");
    ui->step3Badge->setStyleSheet("QLabel{" + accentFor(3) + "border-radius:10px;padding:6px 10px;}");
    ui->step4Badge->setStyleSheet("QLabel{" + accentFor(4) + "border-radius:10px;padding:6px 10px;}");
}

void MainWindow::updateStatusMessage(const QString &message, bool isError)
{
    ui->statusLabel->setText(message);
    if (isError) {
        ui->statusLabel->setStyleSheet("QLabel { background:#4b1f26; color:#ffdbe0; border:1px solid #8e3d4c; border-radius:8px; padding:10px; }");
    } else {
        ui->statusLabel->setStyleSheet("QLabel { background:#142c23; color:#d8ffef; border:1px solid #2d6b54; border-radius:8px; padding:10px; }");
    }
}

void MainWindow::loadImageFromPath(const QString &path)
{
    QPixmap pixmap(path);
    if (pixmap.isNull()) {
        setWorkflowState(WorkflowState::ErrorState, "Unable to decode image. Please provide a valid MRI image.");
        return;
    }

    selectedImagePath = path;
    currentImage = pixmap;

    ui->imagePathLabel->setText("Selected scan: " + QFileInfo(path).fileName());
    ui->scanMetaLabel->setText("Source path: " + path);

    displayImagePreview(pixmap);
    clearResultPanel();
    setWorkflowState(WorkflowState::ImageReady,
                     "Image validated. You can now run AI analysis (Ctrl+Enter).");
}

void MainWindow::displayImagePreview(const QPixmap &pixmap)
{
    const QPixmap scaled = pixmap.scaled(ui->imagePreviewLabel->size(), Qt::KeepAspectRatio, Qt::SmoothTransformation);
    ui->imagePreviewLabel->setPixmap(scaled);
    ui->imagePreviewLabel->setAlignment(Qt::AlignCenter);
}

void MainWindow::clearResultPanel()
{
    ui->resultLabel->setText("Disease Stage: -");
    ui->diseaseStageLabel->setText("");
    ui->confidenceLabel->setText("Confidence: -");
    ui->heatmapLabel->setPixmap(QPixmap());
    ui->heatmapLabel->setText("Explainability map will appear here after inference.");
}

void MainWindow::onUploadButtonClicked()
{
    const QString fileName = QFileDialog::getOpenFileName(
        this,
        tr("Select MRI Image"),
        QString(),
        tr("Image Files (*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.nii *.dcm);;All Files (*)"));

    if (!fileName.isEmpty()) {
        loadImageFromPath(fileName);
    }
}

void MainWindow::onAnalyzeButtonClicked()
{
    if (selectedImagePath.isEmpty()) {
        setWorkflowState(WorkflowState::ErrorState, "Please select an image first.");
        return;
    }

    // ✅ pas de setValue(5) en mode indéterminé
    setWorkflowState(WorkflowState::Analyzing,
                     "Inference running... cognitive markers and visual saliency are being extracted.");
    modelHandler->predictImage(selectedImagePath);
}

void MainWindow::onPredictionReceived(const QString &diagnosis, float confidence, const QString &heatmapPath)
{
    ui->resultLabel->setText(QString("Disease Stage: %1").arg(diagnosis));
    ui->diseaseStageLabel->setText(diagnosis);
    ui->confidenceLabel->setText(QString("Confidence: %1%").arg(QString::number(confidence, 'f', 2)));

    if (!heatmapPath.isEmpty()) {
        QPixmap heatmap(heatmapPath);
        if (!heatmap.isNull()) {
            currentHeatmap = heatmap;
            QSize targetSize = ui->heatmapLabel->size();
            if (targetSize.width() < 10 || targetSize.height() < 10)
                targetSize = QSize(300, 300);
            ui->heatmapLabel->setPixmap(
                heatmap.scaled(targetSize, Qt::KeepAspectRatio, Qt::SmoothTransformation));
            ui->heatmapLabel->setAlignment(Qt::AlignCenter);
            ui->heatmapLabel->setText("");
        }
    }

    const QString patientName = QFileInfo(selectedImagePath).completeBaseName();
    QString dbError;
    if (!DatabaseManager::instance()->savePrediction(patientName, diagnosis, confidence, selectedImagePath, heatmapPath, &dbError)) {
        qWarning() << "Prediction save failed:" << dbError;
        QMessageBox::warning(this, "Database", "Prediction completed but could not be saved to the history database.");
    } else {
        refreshHistory();
    }

    setWorkflowState(WorkflowState::ResultReady,
                     QString("Analysis complete: %1 detected with %2% confidence.")
                         .arg(diagnosis)
                         .arg(QString::number(confidence, 'f', 2)));
}

void MainWindow::onModelError(const QString &errorMessage)
{
    setWorkflowState(WorkflowState::ErrorState, "Inference error: " + errorMessage);
    QMessageBox::critical(this, "Inference Error", errorMessage);
}

void MainWindow::onProcessingStarted()
{
    if (!progressPulseTimer->isActive()) {
        progressPulseTimer->start();
    }
}

void MainWindow::onProcessingFinished()
{
    progressPulseTimer->stop();
    ui->progressBar->setRange(0, 100);  // ✅ repasse en déterminé pour afficher 100%
    ui->progressBar->setValue(100);
}

void MainWindow::onLogoutRequested()
{
    if (SessionManager::instance()->isLoggedIn()) {
        DatabaseManager::instance()->logLogout(SessionManager::instance()->currentUserId(), nullptr);
    }
    SessionManager::instance()->logout();
    DatabaseManager::instance()->closeDatabase();
    QCoreApplication::exit(42);
}

void MainWindow::onHistoryFilterChanged(const QString &text)
{
    if (!historyProxyModel) return;
    historyProxyModel->setFilterFixedString(text);
}

void MainWindow::onDeleteHistoryClicked()
{
    if (!historyTable || !historyTable->selectionModel() || !historyTable->selectionModel()->hasSelection()) {
        QMessageBox::information(this, "Delete prediction", "Select a prediction row first.");
        return;
    }

    const QModelIndex proxyIndex = historyTable->selectionModel()->selectedRows().first();
    const QModelIndex sourceIndex = historyProxyModel->mapToSource(proxyIndex);
    const int predictionId = sourceIndex.sibling(sourceIndex.row(), 0).data().toInt();

    if (QMessageBox::question(this, "Delete prediction", "Delete the selected prediction history row?") != QMessageBox::Yes) {
        return;
    }

    QString error;
    if (!DatabaseManager::instance()->deletePrediction(predictionId, &error)) {
        qWarning() << "Delete prediction failed:" << error;
        QMessageBox::critical(this, "Delete failed", error);
        return;
    }
    refreshHistory();
}

void MainWindow::onRefreshHistoryClicked()
{
    refreshHistory();
}

void MainWindow::onProgressPulse()
{
    // ✅ Plus utilisé en mode indéterminé — conservé pour compatibilité .h
    if (workflowState != WorkflowState::Analyzing) {
        progressPulseTimer->stop();
    }
}

void MainWindow::dragEnterEvent(QDragEnterEvent *event)
{
    if (event->mimeData()->hasUrls()) {
        event->acceptProposedAction();
    }
}

void MainWindow::dropEvent(QDropEvent *event)
{
    if (!event->mimeData()->hasUrls() || event->mimeData()->urls().isEmpty()) {
        return;
    }

    const QString path = event->mimeData()->urls().first().toLocalFile();
    if (!path.isEmpty()) {
        loadImageFromPath(path);
        event->acceptProposedAction();
    }
}