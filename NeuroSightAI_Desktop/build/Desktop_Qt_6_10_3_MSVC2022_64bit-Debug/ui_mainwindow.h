/********************************************************************************
** Form generated from reading UI file 'mainwindow.ui'
**
** Created by: Qt User Interface Compiler version 6.10.3
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MAINWINDOW_H
#define UI_MAINWINDOW_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QFrame>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QProgressBar>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QSplitter>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QWidget *centralwidget;
    QVBoxLayout *mainLayout;
    QFrame *headerFrame;
    QHBoxLayout *headerLayout;
    QLabel *titleLabel;
    QLabel *subtitleLabel;
    QSpacerItem *headerSpacer;
    QLabel *versionLabel;
    QSplitter *mainSplitter;
    QWidget *leftPanel;
    QVBoxLayout *leftPanelLayout;
    QGroupBox *uploadGroup;
    QVBoxLayout *uploadLayout;
    QFrame *dragDropFrame;
    QVBoxLayout *dragDropLayout;
    QSpacerItem *dragDropSpacer1;
    QLabel *dragDropLabel;
    QSpacerItem *dragDropSpacer2;
    QPushButton *uploadButton;
    QLabel *imagePathLabel;
    QGroupBox *previewGroup;
    QVBoxLayout *previewLayout;
    QLabel *imagePreviewLabel;
    QSpacerItem *verticalSpacer;
    QWidget *rightPanel;
    QVBoxLayout *rightPanelLayout;
    QPushButton *analyzeButton;
    QProgressBar *progressBar;
    QGroupBox *resultsGroup;
    QVBoxLayout *resultsLayout;
    QLabel *resultLabel;
    QLineEdit *diseaseStageLabel;
    QLabel *confidenceLabel;
    QLabel *heatmapLabel;
    QLabel *statusLabel;
    QFrame *footerFrame;
    QHBoxLayout *footerLayout;
    QLabel *footerLabel;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName("MainWindow");
        MainWindow->resize(1200, 800);
        centralwidget = new QWidget(MainWindow);
        centralwidget->setObjectName("centralwidget");
        mainLayout = new QVBoxLayout(centralwidget);
        mainLayout->setObjectName("mainLayout");
        headerFrame = new QFrame(centralwidget);
        headerFrame->setObjectName("headerFrame");
        headerLayout = new QHBoxLayout(headerFrame);
        headerLayout->setObjectName("headerLayout");
        titleLabel = new QLabel(headerFrame);
        titleLabel->setObjectName("titleLabel");

        headerLayout->addWidget(titleLabel);

        subtitleLabel = new QLabel(headerFrame);
        subtitleLabel->setObjectName("subtitleLabel");

        headerLayout->addWidget(subtitleLabel);

        headerSpacer = new QSpacerItem(40, 20, QSizePolicy::Policy::Expanding, QSizePolicy::Policy::Minimum);

        headerLayout->addItem(headerSpacer);

        versionLabel = new QLabel(headerFrame);
        versionLabel->setObjectName("versionLabel");

        headerLayout->addWidget(versionLabel);


        mainLayout->addWidget(headerFrame);

        mainSplitter = new QSplitter(centralwidget);
        mainSplitter->setObjectName("mainSplitter");
        mainSplitter->setOrientation(Qt::Horizontal);
        leftPanel = new QWidget(mainSplitter);
        leftPanel->setObjectName("leftPanel");
        leftPanelLayout = new QVBoxLayout(leftPanel);
        leftPanelLayout->setObjectName("leftPanelLayout");
        leftPanelLayout->setContentsMargins(0, 0, 0, 0);
        uploadGroup = new QGroupBox(leftPanel);
        uploadGroup->setObjectName("uploadGroup");
        uploadLayout = new QVBoxLayout(uploadGroup);
        uploadLayout->setObjectName("uploadLayout");
        dragDropFrame = new QFrame(uploadGroup);
        dragDropFrame->setObjectName("dragDropFrame");
        dragDropFrame->setMinimumHeight(150);
        dragDropLayout = new QVBoxLayout(dragDropFrame);
        dragDropLayout->setObjectName("dragDropLayout");
        dragDropSpacer1 = new QSpacerItem(20, 30, QSizePolicy::Policy::Minimum, QSizePolicy::Policy::Expanding);

        dragDropLayout->addItem(dragDropSpacer1);

        dragDropLabel = new QLabel(dragDropFrame);
        dragDropLabel->setObjectName("dragDropLabel");
        dragDropLabel->setAlignment(Qt::AlignCenter);

        dragDropLayout->addWidget(dragDropLabel);

        dragDropSpacer2 = new QSpacerItem(20, 30, QSizePolicy::Policy::Minimum, QSizePolicy::Policy::Expanding);

        dragDropLayout->addItem(dragDropSpacer2);


        uploadLayout->addWidget(dragDropFrame);

        uploadButton = new QPushButton(uploadGroup);
        uploadButton->setObjectName("uploadButton");
        uploadButton->setMinimumHeight(45);

        uploadLayout->addWidget(uploadButton);

        imagePathLabel = new QLabel(uploadGroup);
        imagePathLabel->setObjectName("imagePathLabel");
        imagePathLabel->setWordWrap(true);
        imagePathLabel->setMinimumHeight(25);

        uploadLayout->addWidget(imagePathLabel);


        leftPanelLayout->addWidget(uploadGroup);

        previewGroup = new QGroupBox(leftPanel);
        previewGroup->setObjectName("previewGroup");
        previewGroup->setMinimumHeight(300);
        previewLayout = new QVBoxLayout(previewGroup);
        previewLayout->setObjectName("previewLayout");
        imagePreviewLabel = new QLabel(previewGroup);
        imagePreviewLabel->setObjectName("imagePreviewLabel");
        imagePreviewLabel->setAlignment(Qt::AlignCenter);
        imagePreviewLabel->setMinimumHeight(280);

        previewLayout->addWidget(imagePreviewLabel);


        leftPanelLayout->addWidget(previewGroup);

        verticalSpacer = new QSpacerItem(20, 40, QSizePolicy::Policy::Minimum, QSizePolicy::Policy::Expanding);

        leftPanelLayout->addItem(verticalSpacer);

        mainSplitter->addWidget(leftPanel);
        rightPanel = new QWidget(mainSplitter);
        rightPanel->setObjectName("rightPanel");
        rightPanelLayout = new QVBoxLayout(rightPanel);
        rightPanelLayout->setObjectName("rightPanelLayout");
        rightPanelLayout->setContentsMargins(0, 0, 0, 0);
        analyzeButton = new QPushButton(rightPanel);
        analyzeButton->setObjectName("analyzeButton");
        analyzeButton->setMinimumHeight(60);

        rightPanelLayout->addWidget(analyzeButton);

        progressBar = new QProgressBar(rightPanel);
        progressBar->setObjectName("progressBar");
        progressBar->setValue(0);

        rightPanelLayout->addWidget(progressBar);

        resultsGroup = new QGroupBox(rightPanel);
        resultsGroup->setObjectName("resultsGroup");
        resultsLayout = new QVBoxLayout(resultsGroup);
        resultsLayout->setObjectName("resultsLayout");
        resultLabel = new QLabel(resultsGroup);
        resultLabel->setObjectName("resultLabel");
        resultLabel->setMinimumHeight(30);

        resultsLayout->addWidget(resultLabel);

        diseaseStageLabel = new QLineEdit(resultsGroup);
        diseaseStageLabel->setObjectName("diseaseStageLabel");
        diseaseStageLabel->setReadOnly(true);
        diseaseStageLabel->setMinimumHeight(40);

        resultsLayout->addWidget(diseaseStageLabel);

        confidenceLabel = new QLabel(resultsGroup);
        confidenceLabel->setObjectName("confidenceLabel");
        confidenceLabel->setMinimumHeight(25);

        resultsLayout->addWidget(confidenceLabel);

        heatmapLabel = new QLabel(resultsGroup);
        heatmapLabel->setObjectName("heatmapLabel");
        heatmapLabel->setAlignment(Qt::AlignCenter);
        heatmapLabel->setMinimumHeight(250);

        resultsLayout->addWidget(heatmapLabel);


        rightPanelLayout->addWidget(resultsGroup);

        statusLabel = new QLabel(rightPanel);
        statusLabel->setObjectName("statusLabel");
        statusLabel->setWordWrap(true);
        statusLabel->setMinimumHeight(40);

        rightPanelLayout->addWidget(statusLabel);

        mainSplitter->addWidget(rightPanel);

        mainLayout->addWidget(mainSplitter);

        footerFrame = new QFrame(centralwidget);
        footerFrame->setObjectName("footerFrame");
        footerLayout = new QHBoxLayout(footerFrame);
        footerLayout->setObjectName("footerLayout");
        footerLabel = new QLabel(footerFrame);
        footerLabel->setObjectName("footerLabel");

        footerLayout->addWidget(footerLabel);


        mainLayout->addWidget(footerFrame);

        MainWindow->setCentralWidget(centralwidget);

        retranslateUi(MainWindow);

        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QCoreApplication::translate("MainWindow", "NeuroSight AI - Alzheimer Detection", nullptr));
        headerFrame->setStyleSheet(QCoreApplication::translate("MainWindow", "QFrame { background-color: #1e3a5f; border-bottom: 2px solid #2c5aa0; }", nullptr));
        titleLabel->setText(QCoreApplication::translate("MainWindow", "NeuroSight AI", nullptr));
        titleLabel->setStyleSheet(QCoreApplication::translate("MainWindow", "QLabel { color: white; font-size: 24px; font-weight: bold; }", nullptr));
        subtitleLabel->setText(QCoreApplication::translate("MainWindow", "Intelligent Alzheimer Detection System", nullptr));
        subtitleLabel->setStyleSheet(QCoreApplication::translate("MainWindow", "QLabel { color: #a0c4f7; font-size: 12px; margin-left: 20px; }", nullptr));
        versionLabel->setText(QCoreApplication::translate("MainWindow", "v1.0.0", nullptr));
        versionLabel->setStyleSheet(QCoreApplication::translate("MainWindow", "QLabel { color: #7a98b3; font-size: 10px; }", nullptr));
        uploadGroup->setTitle(QCoreApplication::translate("MainWindow", "MRI Image Upload", nullptr));
        uploadGroup->setStyleSheet(QCoreApplication::translate("MainWindow", "QGroupBox { font-weight: bold; padding-top: 15px; border: 1px solid #ccc; }\n"
"QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }", nullptr));
        dragDropFrame->setStyleSheet(QCoreApplication::translate("MainWindow", "QFrame { border: 2px dashed #4a9eff; background-color: #f0f7ff; border-radius: 8px; }", nullptr));
        dragDropLabel->setText(QCoreApplication::translate("MainWindow", "Drag and drop MRI image here or click to browse", nullptr));
        dragDropLabel->setStyleSheet(QCoreApplication::translate("MainWindow", "QLabel { color: #4a9eff; font-size: 14px; font-weight: bold; }", nullptr));
        uploadButton->setText(QCoreApplication::translate("MainWindow", "Browse Files", nullptr));
        uploadButton->setStyleSheet(QCoreApplication::translate("MainWindow", "QPushButton { \n"
"    background-color: #4a9eff; \n"
"    color: white; \n"
"    font-weight: bold; \n"
"    border: none; \n"
"    border-radius: 5px;\n"
"    font-size: 12px;\n"
"}\n"
"QPushButton:hover { background-color: #2e7fd9; }\n"
"QPushButton:pressed { background-color: #1e5fa8; }", nullptr));
        imagePathLabel->setText(QCoreApplication::translate("MainWindow", "No file selected", nullptr));
        imagePathLabel->setStyleSheet(QCoreApplication::translate("MainWindow", "QLabel { color: #666; font-size: 10px; padding: 5px; }", nullptr));
        previewGroup->setTitle(QCoreApplication::translate("MainWindow", "Image Preview", nullptr));
        previewGroup->setStyleSheet(QCoreApplication::translate("MainWindow", "QGroupBox { font-weight: bold; padding-top: 15px; border: 1px solid #ccc; }\n"
"QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }", nullptr));
        imagePreviewLabel->setText(QCoreApplication::translate("MainWindow", "Image preview will appear here", nullptr));
        imagePreviewLabel->setStyleSheet(QCoreApplication::translate("MainWindow", "QLabel { background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 5px; color: #999; }", nullptr));
        analyzeButton->setText(QCoreApplication::translate("MainWindow", "Analyze Image", nullptr));
        analyzeButton->setStyleSheet(QCoreApplication::translate("MainWindow", "QPushButton { \n"
"    background-color: #2ecc71; \n"
"    color: white; \n"
"    font-weight: bold; \n"
"    font-size: 16px;\n"
"    border: none; \n"
"    border-radius: 5px;\n"
"}\n"
"QPushButton:hover { background-color: #27ae60; }\n"
"QPushButton:pressed { background-color: #1e8449; }\n"
"QPushButton:disabled { background-color: #bdc3c7; color: #7f8c8d; }", nullptr));
        progressBar->setStyleSheet(QCoreApplication::translate("MainWindow", "QProgressBar {\n"
"    border: 1px solid #bdc3c7;\n"
"    border-radius: 5px;\n"
"    text-align: center;\n"
"    background-color: #ecf0f1;\n"
"}\n"
"QProgressBar::chunk {\n"
"    background-color: #3498db;\n"
"    border-radius: 3px;\n"
"}", nullptr));
        resultsGroup->setTitle(QCoreApplication::translate("MainWindow", "Analysis Results", nullptr));
        resultsGroup->setStyleSheet(QCoreApplication::translate("MainWindow", "QGroupBox { font-weight: bold; padding-top: 15px; border: 1px solid #ccc; }\n"
"QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }", nullptr));
        resultLabel->setText(QCoreApplication::translate("MainWindow", "Disease Stage: -", nullptr));
        resultLabel->setStyleSheet(QCoreApplication::translate("MainWindow", "QLabel { font-size: 16px; font-weight: bold; color: #2c3e50; padding: 10px; }", nullptr));
        diseaseStageLabel->setPlaceholderText(QCoreApplication::translate("MainWindow", "Result will appear here", nullptr));
        diseaseStageLabel->setStyleSheet(QCoreApplication::translate("MainWindow", "QLineEdit { \n"
"    border: 2px solid #3498db; \n"
"    border-radius: 5px; \n"
"    padding: 10px; \n"
"    background-color: #ecf0f1;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"    color: #2980b9;\n"
"}", nullptr));
        confidenceLabel->setText(QCoreApplication::translate("MainWindow", "Confidence: -", nullptr));
        confidenceLabel->setStyleSheet(QCoreApplication::translate("MainWindow", "QLabel { font-size: 14px; color: #27ae60; padding: 10px; font-weight: bold; }", nullptr));
        heatmapLabel->setText(QCoreApplication::translate("MainWindow", "Class Activation Map (CAM) will appear here", nullptr));
        heatmapLabel->setStyleSheet(QCoreApplication::translate("MainWindow", "QLabel { background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 5px; color: #999; }", nullptr));
        statusLabel->setText(QCoreApplication::translate("MainWindow", "Ready. Upload an MRI image to begin analysis.", nullptr));
        statusLabel->setStyleSheet(QCoreApplication::translate("MainWindow", "QLabel { \n"
"    color: #27ae60; \n"
"    font-weight: bold; \n"
"    font-size: 11px;\n"
"    padding: 10px;\n"
"    background-color: #f0fff4;\n"
"    border-radius: 5px;\n"
"}", nullptr));
        footerFrame->setStyleSheet(QCoreApplication::translate("MainWindow", "QFrame { background-color: #ecf0f1; border-top: 1px solid #bdc3c7; padding: 10px; }", nullptr));
        footerLabel->setText(QCoreApplication::translate("MainWindow", "Disclaimer: NeuroSight AI is an aid-to-diagnosis tool. Final diagnosis remains the responsibility of qualified medical professionals.", nullptr));
        footerLabel->setStyleSheet(QCoreApplication::translate("MainWindow", "QLabel { color: #7f8c8d; font-size: 10px; }", nullptr));
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MAINWINDOW_H
