#include "MainWindow.h"

MainWindow::MainWindow(QWidget* parent)
	: QMainWindow(parent)
{
	QGuiApplication::setWindowIcon(QIcon("icon/Main.png"));
	ui.setupUi(this);
	pixmap = new QPixmap();

	initializeUI();
	connectSignals();

	srand(time(0));
}

MainWindow::~MainWindow()
{
	disconnectSignals();
}

MainWindow& MainWindow::instance()
{
	static MainWindow instance;
	return instance;
}

void MainWindow::closeEvent(QCloseEvent* event)
{
	QWidget::closeEvent(event);
	cv::destroyAllWindows();
}

void MainWindow::initializeUI()
{
	ui.lineEdit_mapFile->setText("Map\\Map_ROK_Crop.jpg");
	ui.lineEdit_maskFile->setText("Map\\Map_ROK_Crop_Mask.jpg");

	mapFile = ui.lineEdit_mapFile->text().toStdString();
	mapImage = loadImage(mapFile);
	if (mapImage.empty() == false)
	{
		cv::resize(mapImage, mapImage, cv::Size(0, 0), 0.1, 0.1);

		pixQImage = QImage(mapImage.data, mapImage.cols, mapImage.rows, mapImage.step, QImage::Format_BGR888);
		ui.label_mapImage->setPixmap(pixmap->fromImage(pixQImage));
		ui.label_mapImage->show();
	}
}

void MainWindow::connectSignals()
{
	connect(ui.pushButton_mapFile, &QPushButton::clicked, this, &MainWindow::slotButtonMapFileClicked);
	connect(ui.pushButton_maskFile, &QPushButton::clicked, this, &MainWindow::slotButtonMaskFileClicked);
	connect(ui.pushButton_run, &QPushButton::clicked, this, &MainWindow::slotButtonRunClicked);
}

void MainWindow::disconnectSignals()
{
	disconnect(ui.pushButton_mapFile, &QPushButton::clicked, this, &MainWindow::slotButtonMapFileClicked);
	disconnect(ui.pushButton_maskFile, &QPushButton::clicked, this, &MainWindow::slotButtonMaskFileClicked);
	disconnect(ui.pushButton_run, &QPushButton::clicked, this, &MainWindow::slotButtonRunClicked);
}

void MainWindow::slotButtonMapFileClicked()
{
	const QString filter = "image files (*.png *.jpg *.bmp)";
	const QString strFolder = QFileDialog::getOpenFileName(this, "Select Map File");
	if (strFolder.isEmpty() == true)
		return;

	ui.lineEdit_mapFile->setText(strFolder);

	mapFile = ui.lineEdit_mapFile->text().toStdString();
	mapImage = loadImage(mapFile);
	if (mapImage.empty() == true)
	{
		std::cerr << "Error: Map not loaded" << std::endl;
		return;
	}
	cv::resize(mapImage, mapImage, cv::Size(0, 0), 0.1, 0.1);

	pixQImage = QImage(mapImage.data, mapImage.cols, mapImage.rows, mapImage.step, QImage::Format_BGR888);
	ui.label_mapImage->setPixmap(pixmap->fromImage(pixQImage));
	ui.label_mapImage->show();
}

void MainWindow::slotButtonMaskFileClicked()
{
	const QString filter = "image files (*.png *.jpg *.bmp)";
	const QString strFolder = QFileDialog::getOpenFileName(this, "Select Mask File");
	if (strFolder.isEmpty() == true)
		return;

	ui.lineEdit_maskFile->setText(strFolder);
}

void MainWindow::slotButtonRunClicked()
{
	//updatesEnabled();
	ui.plainTextEdit_output->clear();

	/* Load A Map */
	std::string maskFile = ui.lineEdit_maskFile->text().toStdString();
	cv::Mat maskImage;

	maskImage = loadImage(maskFile);
	if (maskImage.empty() == true)
	{
		std::cerr << "Error: Mask not loaded" << std::endl;
		return;
	}
	cv::cvtColor(maskImage, maskImage, cv::COLOR_BGR2GRAY);
	cv::resize(maskImage, maskImage, cv::Size(0, 0), 0.1, 0.1);
	//cv::imshow("Map Image", mapImage);


	/* Map Mask */
	cv::Mat mapMask;
	mapMask = cv::Mat::zeros(maskImage.size(), CV_8UC1);
	maskImage.copyTo(mapMask, maskImage == 255);
	cv::medianBlur(mapMask, mapMask, 5);
	//cv::imwrite("Map Mask.jpg", mapMask);
	//cv::imshow("Map Mask", mapMask);
	mapMask.copyTo(maskImage);

	cv::Mat maskImage_C3;
	maskImage_C3 = cv::Mat::zeros(maskImage.size(), CV_8UC3);
	cv::cvtColor(maskImage, maskImage_C3, cv::COLOR_GRAY2BGR);

	int imgW, imgH;
	imgW = maskImage.cols;
	imgH = maskImage.rows;
	char c_randomCoord[64];
	std::vector<int> randomCoord = { 0, 0 };	// (width, height) -> (col, row)
	int max_iter = 20;
	int game_iter = 1;
	while (game_iter)
	{
		qApp->processEvents();
		game_iter = rand() % 5;
		for (int rep = 0; rep < max_iter; rep++)
		{
			Sleep(250);

			cv::Mat showImage;
			mapImage.copyTo(showImage);
			/* Edge Detection */
			//cv::Mat mapEdgeImage;
			//cv::Canny(mapImage, mapEdgeImage, 100, 200); // 모든 선을 검출함
			//cv::Canny(mapImage, mapEdgeImage, 550, 600); // 옅은 색상의 선을 검출하지 못함

			//cv::imshow("Map Edge Image", mapEdgeImage);


			/* Find Contour */
			//cv::Mat mapContourImage = cv::Mat::zeros(mapImage.size(), CV_8UC1);
			//std::vector<std::vector<cv::Point>> contours;
			//cv::findContours(mapEdgeImage, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_NONE); // 외곽선을 찾음
			//cv::findContours(mapEdgeImage, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE); // 외곽선을 찾음
			//cv::findContours(mapImage, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE); // 외곽선을 찾음
			//cv::drawContours(mapContourImage, contours, -1, 255, 1); // 외곽선을 그림

			//cv::imshow("Map Contour Image", mapContourImage);


			/* Fill Inside the Edge */
			//cv::Mat mapFilledImage;
			//cv::erode(mapContourImage, mapFilledImage, cv::Mat(), cv::Point(-1, -1), 3);
			//cv::dilate(mapContourImage, mapFilledImage, cv::Mat(), cv::Point(-1, -1), 3);
			//cv::dilate(mapEdgeImage, mapFilledImage, cv::Mat(), cv::Point(-1, -1), 3);
			//cv::morphologyEx(mapEdgeImage, mapFilledImage, cv::MORPH_CLOSE, cv::Mat(), cv::Point(-1, -1), 3);
			//cv::dilate(mapFilledImage, mapFilledImage, cv::Mat(), cv::Point(-1, -1), 3);

			//cv::imshow("Map Filled Image", mapFilledImage);

			while (1)
			{
				pickRandomCoord(randomCoord, { 0, imgW }, { 0, imgH });
				if (mapMask.at<uchar>(randomCoord[1], randomCoord[0]) == 255)
				{
					break;
				}
			}

			//sprintf(c_randomCoord, "%d, %d\n", randomCoord[0], randomCoord[1]);
			//ui.plainTextEdit_output->setPlainText(c_randomCoord);

			cv::circle(showImage, cv::Point(randomCoord[0], randomCoord[1]), 5, cv::Scalar(0, 0, 255), -1);

			pixQImage = QImage(showImage.data, showImage.cols, showImage.rows, showImage.step, QImage::Format_BGR888);
			ui.label_mapImage->setPixmap(pixmap->fromImage(pixQImage));
			ui.label_mapImage->show();
			repaint();
		}
		//out_cursor.movePosition(QTextCursor::End);
		//out_cursor.insertText(c_randomCoord);
		//ui.plainTextEdit_output->appendPlainText(c_randomCoord);
		//repaint();
		Sleep(3000);
	}
	std::vector<double> realCoord = pixelToReal(imgW, imgH, randomCoord);
	std::cout << "random pixel: " << randomCoord[0] << ", " << randomCoord[1] << std::endl;
	std::cout << "random real: " << realCoord[0] << ", " << realCoord[1] << std::endl;

	sprintf(c_randomCoord, "%f, %f\n", realCoord[1], realCoord[0]);
	ui.plainTextEdit_output->appendPlainText(c_randomCoord);
	char message[64];
	sprintf(message, "Your GPS Coordinate is: \n\n%s", c_randomCoord);
	QMessageBox::information(this, "Finished", message);
	//ui.plainTextEdit_output->appendPlainText("Finish!");
	//repaint();
	//cv::imshow("Random Point in Map", showImage);
	//cv::waitKey(0);
}