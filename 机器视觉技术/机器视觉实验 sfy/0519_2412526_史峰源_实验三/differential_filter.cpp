#include <iostream>
#include <fstream>
#include "opencv2/opencv.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include<cmath>
#include <stdio.h>

using namespace cv;
using namespace std;

Mat myEdgeDetect(Mat img)
{
	Mat EdgeImg;
    CV_Assert(img.type()==CV_8UC1);

    //先进性平滑滤波，再使用一阶差分滤波器

    Mat blurred;
    GaussianBlur(img,blurred,Size(3,3),0,0);

    Mat grad_x,grad_y;
    Mat abs_grad_x,abs_grad_y;

    Sobel(blurred,grad_x,CV_16S,1,0,3);
    Sobel(blurred,grad_y,CV_16S,0,1,3);
    
    convertScaleAbs(grad_x,abs_grad_x);
    convertScaleAbs(grad_y,abs_grad_y);

    addWeighted(abs_grad_x,0.5,abs_grad_y,0.5,0,EdgeImg);
	/*

	完善使用差分滤波器的边缘检测计算过程（利用线性滤波）

	*/


	//返回原图像经过边缘检测的结果EdgeImg
	return EdgeImg;
}


int main()
{
	Mat input = imread("testimg.jpg");

	Mat gray;
	//彩色图转为灰度图
	cvtColor(input, gray, COLOR_BGR2GRAY);

	//使用差分滤波器的边缘检测（利用线性滤波），需编程实现
	Mat EdgeImg = myEdgeDetect(gray);

	imshow("input", input);
	imshow("EdgeImg", EdgeImg);
	waitKey(0);
	return 0;
}