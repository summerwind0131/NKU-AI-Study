#include <iostream>
#include <fstream>
#include "opencv2/opencv.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <stdio.h>
using namespace cv;
using namespace std;

Mat myHist(Mat img)
{
	Mat Hist;

    int H[256]={0};
    for(int m=0;m<img.rows;m++){
        for(int n=0;n<img.cols;n++){
            int val = img.at<uchar>(m, n);
            H[val] = H[val] + 1;
        }
    }
    int max_val = 0;
    for (int i = 0; i < 256; i++)
    {
        if (H[i] > max_val)
        {
            max_val = H[i];
        }
    }

    int hist_w = 512;
    int hist_h = 400;
    int bin_w = cvRound((double)hist_w / 256); 
    Hist=Mat(hist_h, hist_w, CV_8UC3, Scalar(255, 255, 255));

    for (int i = 0; i < 256; i++)
    {
        int intensity = cvRound((double)H[i] / max_val * hist_h);
        
        line(Hist, 
             Point(bin_w * i, hist_h), 
             Point(bin_w * i, hist_h - intensity), 
             Scalar(0, 0, 0),
             2, 8, 0);
    }
    return Hist;
	
}

void main()
{
	Mat input = imread("../testimg.jpg");

	Mat gray;
	//彩色图转为灰度图
	cvtColor(input, gray, COLOR_BGR2GRAY);

	//直方图绘制，需编程实现
	Mat Hist = myHist(gray);

	imshow("Hist", Hist);
	waitKey(0);
}