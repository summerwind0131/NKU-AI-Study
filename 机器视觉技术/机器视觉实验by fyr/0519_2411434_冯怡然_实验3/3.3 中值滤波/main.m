clc;clear all;close all;

img=imread('ratatouille.png');

% 彩色图转为灰度图
img=rgb2gray(img);
noisy_img = imnoise(img, 'salt & pepper', 0.05);
%中值滤波，需编程实现
Medfilt2_result = MyMedfilt2(noisy_img);
figure; % 开启新窗口
imshow(img); 
title('Original Gray Image'); 
figure;
imshow(noisy_img); 
title('Salt & Pepper Noise');
figure;
imshow(Medfilt2_result); 
title('Median Filter Result');