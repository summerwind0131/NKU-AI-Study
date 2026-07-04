function DisTrans_result=MyDisTrans(bw)
%完善距离变换的计算过程
[M, N] = size(bw);
F = inf(M, N);
F(bw == 0) = 0; 
    % 第一遍扫描：左上 -> 右下
    for i = 1:M
        for j = 1:N
            if i > 1
                F(i,j) = min(F(i,j), 1 + F(i-1, j));
            end
            if j > 1
                F(i,j) = min(F(i,j), 1 + F(i, j-1));
            end
        end
    end
    % 第二遍扫描：右下 -> 左上
    for i = M:-1:1
        for j = N:-1:1
            if i < M
                F(i,j) = min(F(i,j), 1 + F(i+1, j));
            end
            if j < N
                F(i,j) = min(F(i,j), 1 + F(i, j+1));
            end
        end
    end
%返回原二值图像经过距离变换后的结果DisTrans_result
DisTrans_result=F;
end