function OptimalThreshold_result=MyOptimalThreshold(img)

%完善迭代最优阈值选择的计算过程
img_double=double(img);
T=(max(img_double(:))+min(img_double(:)))/2;
Thistory=[];
deltaT=15;
while true
    Thistory=[Thistory,T];
    g1=img_double(img_double>T);
    g2=img_double(img_double<=T);
    mu1=mean(g1);
    mu2=mean(g2);
    newT=(mu1+mu2)/2;
    if abs(newT-T)<deltaT
        break;
    end
    T=newT;
end
figure;
plot(Thistory, 'o-', 'LineWidth', 1.5);
grid on; title('阈值 T 的迭代变化曲线');
xlabel('迭代次数'); ylabel('阈值大小');
%返回原图像经过迭代最优阈值选择处理后的图像OptimalThreshold_result
OptimalThreshold_result = img_double > T;
end