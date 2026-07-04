clc;clear all;close all;

img=imread('ratatouille.png');

% 彩色图转为灰度图
img=rgb2gray(img);

%OTSU阈值检测，需编程实现
OTSU_result = MyOTSU(img);

figure;
imshow(OTSU_result);
title('OTSUResult');