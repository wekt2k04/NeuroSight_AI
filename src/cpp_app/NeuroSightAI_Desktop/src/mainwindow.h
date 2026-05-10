#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QPixmap>
#include <QPointer>

#include "modelhandler.h"

QT_BEGIN_NAMESPACE
namespace Ui {
class MainWindow;
}
QT_END_NAMESPACE

class QTimer;
class QDockWidget;
class QLineEdit;
class QTableView;
class QSortFilterProxyModel;
class QPushButton;

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow() override;

protected:
    void dragEnterEvent(QDragEnterEvent *event) override;
    void dropEvent(QDropEvent *event) override;

private slots:
    void onUploadButtonClicked();
    void onAnalyzeButtonClicked();

    void onPredictionReceived(const QString &diagnosis, float confidence, const QString &heatmapPath);
    void onModelError(const QString &errorMessage);
    void onProcessingStarted();
    void onProcessingFinished();
    void onLogoutRequested();
    void onHistoryFilterChanged(const QString &text);
    void onDeleteHistoryClicked();
    void onRefreshHistoryClicked();

    void onProgressPulse();

private:
    enum class WorkflowState {
        AwaitingImage,
        ImageReady,
        Analyzing,
        ResultReady,
        ErrorState
    };

    void setupWindow();
    void setupConnections();
    void setupShortcuts();
    void setupAccessibilityHints();
    void setupSessionUi();
    void setupHistoryDock();
    void refreshHistory();
    void setWorkflowState(WorkflowState state, const QString &message = QString());
    void updateWorkflowIndicators();
    void updateStatusMessage(const QString &message, bool isError = false);

    void loadImageFromPath(const QString &path);
    void displayImagePreview(const QPixmap &pixmap);
    void clearResultPanel();

    Ui::MainWindow *ui;
    ModelHandler *modelHandler;

    QDockWidget *historyDock;
    QLineEdit *historyFilterEdit;
    QTableView *historyTable;
    QSortFilterProxyModel *historyProxyModel;
    QPushButton *deleteHistoryButton;
    QPushButton *refreshHistoryButton;

    QString selectedImagePath;
    QPixmap currentImage;
    QPixmap currentHeatmap;

    WorkflowState workflowState;
    QTimer *progressPulseTimer;
};

#endif // MAINWINDOW_H
