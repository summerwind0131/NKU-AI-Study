#include <iostream>
#include <fstream>
#include "opencv2/opencv.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <stdio.h>
#include<Windows.h>
using namespace cv;
using namespace std;

Mat myEqualizeHist(Mat img)
{
	Mat EqualizedImg;
	//形成图像直方图
	int hist[256] = { 0 }; //灰度级为256
	int pixelNum = img.rows * img.cols; //图像像素总数
	//统计每个灰度级的像素数
	for (int r = 0; r < img.rows; r++) {
		for (int c = 0; c < img.cols; c++) {
			uchar intensity = img.at<uchar>(r, c);
			hist[intensity]++;
		}
	}
	//计算累计分布函数
	int Hc[256] = { 0 };
	Hc[0] = hist[0];
	for (int i = 1; i < 256; i++) {
		Hc[i] = Hc[i - 1] + hist[i];
	}
	//计算变换函数
	uchar T[256] = { 0 };
	for (int i = 0; i < 256; i++) {
		T[i] = (uchar)cvRound((double)Hc[i] * 255.0 / pixelNum);
	}
	//重新扫描图像，根据查找表获得变换结果
	EqualizedImg = img.clone();
	for (int r = 0; r < img.rows; r++) {
		for (int c = 0; c < img.cols; c++) {
			uchar intensity = img.at<uchar>(r, c);
			EqualizedImg.at<uchar>(r, c) = T[intensity];
		}
	}

	
	//返回原图像经过直方图均衡化后的变换结果
	return EqualizedImg;
}

void main()
{
	SetProcessDPIAware();
	Mat input = imread(R"(C:\Users\AliceJFeng\Desktop\ratatouille.png)");

	Mat gray;
	//彩色图转为灰度图
	cvtColor(input, gray, COLOR_BGR2GRAY);

	//直方图均衡化，需编程实现
	Mat EqualizedImg = myEqualizeHist(gray);

	int displayWidth = 600;
	double scale = (double)displayWidth / input.cols;
	int displayHeight = (int)(input.rows * scale);

	double zoom = 0.7;
	Mat showInput, showGray, showEqual;

	resize(input, showInput, Size(), zoom, zoom);
	resize(gray, showGray, Size(), zoom, zoom);
	resize(EqualizedImg, showEqual, Size(), zoom, zoom);

	// 4. 直接显示（因为已经 resize 过了，默认窗口就能看全）
	imshow("1.Original", showInput);
	imshow("2.Gray", showGray);
	imshow("3.Equalized", showEqual);
	Ptr<CLAHE> clahe = createCLAHE();
	clahe->setClipLimit(2.0);      // 限制对比度系数，数值越大对比度越强
	clahe->setTilesGridSize(Size(8, 8)); // 分块大小

	Mat claheImg;
	clahe->apply(gray, claheImg);

	imshow("CLAHE Result (More Natural)", claheImg);
	waitKey(0);
}