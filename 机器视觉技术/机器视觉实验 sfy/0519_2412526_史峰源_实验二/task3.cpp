#include <iostream>
#include <fstream>
#include "opencv2/opencv.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <stdio.h>

using namespace cv;
using namespace std;

Mat myConv(Mat img)
{
	Mat Conv_img;

	/*
	完善图像卷积处理的计算过程
	*/

    //  开始计时
    double t = (double)getTickCount();

    // 生成高斯滤波器
    int ksize = 128;
    double sigma = 20.0;
    Mat k1D = getGaussianKernel(ksize, sigma, CV_32F);
    Mat h = k1D * k1D.t();

    // 图像数据格式转换
    Mat img_float;
    img.convertTo(img_float, CV_32F);

    // 扩充图像和滤波器的尺寸
    int dft_rows = getOptimalDFTSize(img.rows + h.rows - 1);
    int dft_cols = getOptimalDFTSize(img.cols + h.cols - 1);
    Mat padded_img, padded_h;
    copyMakeBorder(img_float, padded_img, 0, dft_rows - img.rows, 0, dft_cols - img.cols, BORDER_CONSTANT, Scalar::all(0));
    copyMakeBorder(h, padded_h, 0, dft_rows - h.rows, 0, dft_cols - h.cols, BORDER_CONSTANT, Scalar::all(0));

    // 傅里叶变换 
    Mat planes_img[] = { padded_img, Mat::zeros(padded_img.size(), CV_32F) };
    Mat complex_img;
    merge(planes_img, 2, complex_img);
    dft(complex_img, complex_img);

    Mat planes_h[] = { padded_h, Mat::zeros(padded_h.size(), CV_32F) };
    Mat complex_h;
    merge(planes_h, 2, complex_h);
    dft(complex_h, complex_h);


    Mat complex_res;
    mulSpectrums(complex_img, complex_h, complex_res, 0);

    // 逆傅里叶变换
    dft(complex_res, complex_res, DFT_INVERSE | DFT_SCALE);
    Mat planes_res[2];
    split(complex_res, planes_res);
    Mat result = planes_res[0]; // 提取实部作为结果

    int start_x = (h.cols - 1) / 2;
    int start_y = (h.rows - 1) / 2;
    Rect roi(start_x, start_y, img.cols, img.rows);
    Mat same_result = result(roi);
    same_result.convertTo(Conv_img, CV_8UC1);

    t = ((double)getTickCount() - t) / getTickFrequency();
    cout << "基于FFT的图像卷积耗时: " << t << " 秒。" << endl;

	//返回卷积处理后的图像
	return Conv_img;
}

int main()
{
	Mat input = imread("../testimg.jpg");

    if (input.empty()) {
        cout << "无法读取图像 testimg.jpg，请检查图片路径" << endl;
        return -1;
    }

	Mat gray;
	//彩色图转为灰度图
	cvtColor(input, gray, COLOR_BGR2GRAY);

	//图像卷积处理，需编程实现
	Mat Conv_img = myConv(gray);

	imshow("Conv_img", Conv_img);
	waitKey(0);
    
    return 0;
}