function Medfilt2_result=MyMedfilt2(img)
img=double(img);
[rows,cols]=size(img);
res=img;
for i=2:rows-1
    for j=2:cols-1
        temp_windows = img(i-1:i+1, j-1:j+1);
        sorted_values=sort(temp_windows(:));
        res(i,j)=sorted_values(5);
    end
end
Medfilt2_result=uint8(res);
end