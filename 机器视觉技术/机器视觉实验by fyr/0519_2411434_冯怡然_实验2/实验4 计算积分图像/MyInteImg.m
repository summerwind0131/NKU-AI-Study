function MyInteImg_result=MyInteImg(img)
%完善积分图像的计算过程
[rows,cols]=size(img);
MyInteImg_result = zeros(rows, cols);
s = zeros(rows, cols);
for i=rows:-1:1
    for j=cols:-1:1
        if j==cols
            s(i,j)=img(i,j);
        else
            s(i,j)=s(i,j+1)+img(i,j);
        end
        if i==rows
            MyInteImg_result(i,j)=s(i,j);
        else
            MyInteImg_result(i,j)=MyInteImg_result(i+1,j)+s(i,j);
        end
    end
end
%返回原图像计算得到的积分图像MyInteImg_result
end