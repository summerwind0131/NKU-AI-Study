function img = preprocessHand(rawImg, imgSize)
% preprocessHand - Shared preprocessing for training and testing.

    if size(rawImg, 3) == 3
        img = rgb2gray(rawImg);
    else
        img = rawImg;
    end

    img = im2uint8(img);
    img = imresize(img, imgSize);
    img = medfilt2(img, [2 2]);
    img = adapthisteq(img, 'ClipLimit', 0.01);
end
