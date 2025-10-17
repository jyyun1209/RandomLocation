#pragma once

#include <QtWidgets/qmainwindow.h>
#include <QtWidgets/qfiledialog.h>
#include <QtWidgets/qplaintextedit.h>
#include <QtGui/qevent.h>
#include <qicon.h>
#include <qimage.h>
#include <qlabel.h>
#include <qpixmap.h>
#include <qmessagebox.h>

#include <iostream>
#include <Windows.h>

#include "ui_MainWindow.h"
#include "coreFunc.h"

class MainWindow : public QMainWindow
{
	Q_OBJECT

public:
	MainWindow(QWidget *parent = Q_NULLPTR);
	~MainWindow();

	static MainWindow& instance();

public slots:
	void slotButtonMapFileClicked();
	void slotButtonMaskFileClicked();
	void slotButtonRunClicked();

private:
	Ui::MainWindowClass ui;

	QPixmap *pixmap;
	QImage pixQImage;

	std::string mapFile;
	cv::Mat mapImage;

	void closeEvent(QCloseEvent* event);
	void connectSignals();
	void disconnectSignals();
	void initializeUI();
	//QTextCursor out_cursor = QTextCursor(ui.plainTextEdit_output->document());
};