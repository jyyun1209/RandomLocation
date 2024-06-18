#pragma once
#include <iostream>
#include <cstdlib>
#include <time.h>
#include <chrono>
#include <opencv2/opencv.hpp>

cv::Mat loadImage(std::string fileName);
void pickRandomCoord(std::vector<int>& randomCoord, std::vector<int> rangeX, std::vector<int> rangeY);
void pickRandomCoord_float(double& randomCoord, std::vector<double> rangeX);
std::vector<double> pixelToReal(int imgW, int imgH, std::vector<int> randomCoord);