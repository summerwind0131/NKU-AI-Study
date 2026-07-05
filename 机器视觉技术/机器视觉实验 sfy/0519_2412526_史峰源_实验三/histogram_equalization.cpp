#include <iostream>
#include <fstream>
#include "opencv2/opencv.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <stdio.h>
#include<cmath>
using namespace cv;
using namespace std;

Mat myEqualizeHist(Mat img)
{
	//确保输入单通道灰度图片
	CV_Assert(img.type()==CV_8UC1);
	Mat EqualizedImg;
	/*
	
	完善直方图均衡化的计算过程
	
	*/
	EqualizedImg.create(img.rows,img.cols,img.type());
	int k=256;
	int H[256]={0};
	int M=img.rows;
	int N=img.cols;
	int MN=M*N;

	//形成直方图
	for(int i=0;i<M;i++){
		for(int j=0;j<N;j++){
			int pixcelValue=img.at<uchar>(i,j);
			H[pixcelValue]++;
		}
	}

	//形成累计直方图
	int Hc[256]={0};
	Hc[0]=H[0];
	for(int p=1;p<k;p++){
		Hc[p]=Hc[p-1]+H[p];
	}

	//设置查找表
	uchar T[256]={0};
	double factor=(double)(k-1)/MN;
	for(int p=0;p<k;p++){
		T[p]=(uchar)cvRound(factor*Hc[p]);
	}

	for(int i=0;i<M;i++){
		for(int j=0;j<N;j++){
			int originalPixel=img.at<char>(i,j);
			EqualizedImg.at<char>(i,j)=T[originalPixel];
		}
	}
	//返回原图像经过直方图均衡化后的变换结果
	return EqualizedImg;
}

void main()
{
	Mat input = imread("testimg.jpg");

	Mat gray;
	//彩色图转为灰度图
	cvtColor(input, gray, COLOR_BGR2GRAY);

	//直方图均衡化，需编程实现
	Mat EqualizedImg = myEqualizeHist(gray);
	
	imshow("input", input);
	imshow("EqualizedImg", EqualizedImg);
	waitKey(0);
}