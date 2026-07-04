clc;clear all;close all;

img=imread('ratatouille.png');

% 彩色图转为灰度图
img=rgb2gray(img);

%迭代的最优阈值选择，需编程实现
%鼓励尝试同时输出阈值t的变化曲线图
%可以稍微修改这个源程序，比如增加下面这个函数的返回值等
OptimalThreshold_result = MyOptimalThreshold(img);

figure;
imshow(OptimalThreshold_result);
title('OptimalThresholdResult');