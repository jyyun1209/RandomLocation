#include "coreFunc.h"

cv::Mat loadImage(std::string fileName)
{
	cv::Mat image = cv::imread(fileName);
	if (image.empty() == true)
	{
		std::cerr << "Error: Image not loaded" << std::endl;
		return cv::Mat();
	}

	return image;
}

void pickRandomCoord(std::vector<int>& randomCoord, std::vector<int> rangeX, std::vector<int> rangeY)
{
	//srand(time(0));
	//auto now = std::chrono::system_clock::now();
	//auto duration = now.time_since_epoch();
	//srand(std::chrono::duration_cast<std::chrono::milliseconds>(duration).count());
	randomCoord[0] = (rand() % (rangeX[1] - rangeX[0] + 1)) + rangeX[0];
	randomCoord[1] = (rand() % (rangeY[1] - rangeY[0] + 1)) + rangeY[0];
}

void pickRandomCoord_float(double& randomCoord, std::vector<double> rangeX)
{
	
	randomCoord = (double)rand() / RAND_MAX;
	randomCoord = randomCoord * (rangeX[1] - rangeX[0]) + rangeX[0];
}

std::vector<double> pixelToReal(int imgW, int imgH, std::vector<int> randomCoord)
{
	double realX_min = 125;
	double realX_max = 130;
	double realY_min = 34;
	double realY_max = 39;
	double pixX_min = 0;
	double pixX_max = imgW;
	double pixY_min = 0;
	double pixY_max = imgH;

	double realW = realX_max - realX_min;
	double realH = realY_max - realY_min;

	std::vector<double> pix_unit;
	pix_unit.push_back(realW / imgW);
	pix_unit.push_back(realH / imgH);

	double realX, realY;
	realX = realX_min + pix_unit[0] * (randomCoord[0] - 1);
	realY = realY_max - pix_unit[1] * (randomCoord[1] - 1);

	std::cout << "pixel unit: " << pix_unit[0] << ", " << pix_unit[1] << std::endl;
	std::cout << "real coord - remain: " << realX << ", " << realY << std::endl;

	double remain = 0;
	if (pix_unit[0] > 0.00001)
	{
		pickRandomCoord_float(remain, { 0, pix_unit[0] });
		realX = realX + remain;
	}
	if (pix_unit[1] > 0.00001)
	{
		pickRandomCoord_float(remain, { 0, pix_unit[1] });
		realY = realY + remain;
	}

	return { realX, realY };
}