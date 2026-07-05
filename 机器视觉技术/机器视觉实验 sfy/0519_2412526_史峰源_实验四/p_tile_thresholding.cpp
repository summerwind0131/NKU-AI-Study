#include <iostream>
#include <fstream>
#include "opencv2/opencv.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <stdio.h>
using namespace cv;
using namespace std;

Mat myThresholdP(Mat img)
{
	// 初始化与原图同等大小和类型的全黑图像
	Mat ThresholdPImg = Mat::zeros(img.size(), CV_8UC1);
	
	/*
	p率阈值化代码实现
	*/
	
	// 1. 统计图像的灰度直方图
	int hist[256] = {0};
	int total_pixels = img.rows * img.cols;
	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			hist[img.at<uchar>(i, j)]++;
		}
	}
	
	// 2. 设定目标物体的面积占比 p 率 
	double p = 0.4; 
	int target_pixels = total_pixels * p;
	
	// 3. 根据p率寻找阈值
	int sum = 0;
	int threshold_value = 0;
	for (int i = 255; i >= 0; i--) {
		sum += hist[i];
		if (sum >= target_pixels) {
			threshold_value = i;
			break;
		}
	}
	
	// 4. 应用求得的阈值进行二值化
	for (int i = 0; i < img.rows; i++) {
		for (int j = 0; j < img.cols; j++) {
			if (img.at<uchar>(i, j) >= threshold_value) {
				ThresholdPImg.at<uchar>(i, j) = 255; 
			} else {
				ThresholdPImg.at<uchar>(i, j) = 0;   
			}
		}
	}

	return ThresholdPImg;
}

void main()
{
	Mat input = imread("testimg.jpg");
	if (input.empty()) {
		cout << "无法读取图像，请确认相对路径下存在 testimg.jpg 文件！" << endl;
		return;
	}

	Mat gray;
	//彩色图转为灰度图
	cvtColor(input, gray, COLOR_BGR2GRAY);

	//灰度图p率阈值化代码的实现
	Mat ThresholdPImg = myThresholdP(gray);
	
	imshow("input", input);
	imshow("gray", gray);
	imshow("ThresholdPImg", ThresholdPImg);
	waitKey(0);
}