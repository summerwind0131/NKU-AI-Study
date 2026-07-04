clc;clear all;close all;

% 读入图像
img = imread('ratatouille.png');

% 将读入的彩色图像转换为二值图像
bw = imbinarize(img);
%距离变换，需编程实现
DisTrans_result = MyDisTrans(bw);
imshow(DisTrans_result);
imshow(DisTrans_result);
title('DisTrans-result');