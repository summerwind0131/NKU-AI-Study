#include <iostream>
#include <fstream>
#include "opencv2/opencv.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <stdio.h>

using namespace cv;
using namespace std;

Mat myInnerContours(Mat img)
{
	// 初始化为与原图大小相同的全黑图像
	Mat InnerContoursImg = Mat::zeros(img.size(), CV_8UC1);
	
	/*
	编写二值图像内边界跟踪的代码实现
	*/

	Mat visited = Mat::zeros(img.size(), CV_8UC1);

	int dx[8] = { 1, 1, 0, -1, -1, -1, 0, 1 };
	int dy[8] = { 0, 1, 1, 1, 0, -1, -1, -1 };

	// 遍历图像，寻找边界的起始点
	// 为了防止越界，略过最外层一圈像素
	for (int i = 1; i < img.rows - 1; i++) {
		for (int j = 1; j < img.cols - 1; j++) {
			
			if (img.at<uchar>(i, j) == 255 && img.at<uchar>(i, j - 1) == 0 && visited.at<uchar>(i, j) == 0) {
				
				int startX = j;
				int startY = i;
				int currX = startX;
				int currY = startY;
				
				// 初始搜索方向：由于左侧是背景，故从左上方向(即索引5)开始顺时针搜索下一个前景点
				int dir = 5; 

				// 开始Moore邻域轮廓跟踪
				do {
					InnerContoursImg.at<uchar>(currY, currX) = 255;
					visited.at<uchar>(currY, currX) = 255;

					bool found = false;
					for (int k = 0; k < 8; k++) {
						int searchDir = (dir + k) % 8;
						int nx = currX + dx[searchDir];
						int ny = currY + dy[searchDir];

						if (nx >= 0 && nx < img.cols && ny >= 0 && ny < img.rows) {
							if (img.at<uchar>(ny, nx) == 255) {
								currX = nx;
								currY = ny;
							
								dir = (searchDir + 5) % 8; 
								found = true;
								break;
							}
						}
					}

					if (!found) {
						break;
					}

				} while (currX != startX || currY != startY); 
			}
		}
	}
	return InnerContoursImg;
}

void main()
{
	Mat input = imread("testimg.jpg");

	Mat gray;
	// 彩色图转为灰度图
	cvtColor(input, gray, COLOR_BGR2GRAY);

	// 灰度图转为二值图，使用大津法(OTSU)自动寻找阈值
	Mat binary;
	threshold(gray, binary, 0, 255, THRESH_OTSU);

	// 二值图像内边界跟踪的代码实现
	Mat InnerContoursImg = myInnerContours(binary);
	
	imshow("input", input);
	imshow("gray", gray);
	imshow("binary", binary);
	imshow("InnerContoursImg", InnerContoursImg);
	waitKey(0);
}