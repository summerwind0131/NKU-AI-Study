function OTSU_result=MyOTSU(img)
%完善OTSU阈值检测的计算过程
counts=imhist(img);
p=counts/sum(counts);
graylevels=(0:255)';
mu=sum(graylevels.*p);
sigma2=zeros(256,1);
for t=1:256
    w0=sum(p(1:t));
    w1=1-w0;
    if w0==0||w1==0
        continue;
    end
    mu0=sum(graylevels(1:t).*p(1:t))/w0;
    mu1=(mu-w0*mu0)/w1;
    sigma2(t)=w0*w1*(mu0-mu1)^2;
end
[~, max_idx] = max(sigma2);
best_T = max_idx - 1;
%返回原图像经过OTSU最优阈值化后的二值图OTSU_result
OTSU_result=img>best_T;
end