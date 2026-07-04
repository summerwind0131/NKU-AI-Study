%% DataTraining.m - Train HOG + SVM gesture classifier

clear; clc; close all;
rng(1);
baseDir = fileparts(mfilename('fullpath'));

%% 1. Load dataset
datasetPath = fullfile(baseDir, 'Hand_Posture_Easy_Stu');
if ~exist(datasetPath, 'dir')
    error('Dataset folder Hand_Posture_Easy_Stu was not found in the current folder.');
end

imds = imageDatastore(datasetPath, ...
    'IncludeSubfolders', true, ...
    'LabelSource', 'foldernames');

if numel(imds.Files) == 0
    error('No images were found in the dataset folder.');
end

[trainingSet, validationSet] = splitEachLabel(imds, 0.7, 'randomize');

%% 2. Parameters
imgSize = [128, 128];
cellSize = [8, 8];

%% 3. Extract training HOG features with augmentation
fprintf('Extracting training HOG features with data augmentation...\n');
numTrainImages = numel(trainingSet.Files);

sampleImg = preprocessHand(readimage(trainingSet, 1), imgSize);
sampleFeature = extractHOGFeatures(sampleImg, 'CellSize', cellSize);
featureLength = numel(sampleFeature);

augPerImage = 4; % original, horizontal flip, -10 deg, +10 deg
trainingFeatures = zeros(numTrainImages * augPerImage, featureLength);
trainingLabels = repelem(trainingSet.Labels, augPerImage);

row = 1;
for i = 1:numTrainImages
    rawImg = readimage(trainingSet, i);

    augImgs = cell(augPerImage, 1);
    augImgs{1} = rawImg;
    augImgs{2} = flip(rawImg, 2);
    augImgs{3} = imrotate(rawImg, -10, 'bilinear', 'crop');
    augImgs{4} = imrotate(rawImg, 10, 'bilinear', 'crop');

    for j = 1:augPerImage
        img = preprocessHand(augImgs{j}, imgSize);
        trainingFeatures(row, :) = extractHOGFeatures(img, 'CellSize', cellSize);
        row = row + 1;
    end
end

%% 4. Extract validation HOG features
fprintf('Extracting validation HOG features...\n');
numValImages = numel(validationSet.Files);
valFeatures = zeros(numValImages, featureLength);

for i = 1:numValImages
    imgVal = preprocessHand(readimage(validationSet, i), imgSize);
    valFeatures(i, :) = extractHOGFeatures(imgVal, 'CellSize', cellSize);
end

%% 5. Train SVM classifier
fprintf('Training SVM classifier...\n');
t = templateSVM('KernelFunction', 'rbf', ...
                'KernelScale', 'auto', ...
                'Standardize', true, ...
                'BoxConstraint', 1);

classifier = fitcecoc(trainingFeatures, trainingLabels, ...
    'Learners', t, ...
    'Coding', 'onevsall');

%% 6. Validate model
predictedLabels = predict(classifier, valFeatures);
accuracy = mean(predictedLabels == validationSet.Labels);

fprintf('Training finished. Validation accuracy: %.2f%%\n', accuracy * 100);

%% 7. Save model
modelPath = fullfile(baseDir, 'trainedModel.mat');
save(modelPath, 'classifier', 'imgSize', 'cellSize', 'accuracy');
fprintf('Model saved as trainedModel.mat\n');

%% 8. Plot confusion matrix
figure('Name', 'Validation Confusion Matrix', 'NumberTitle', 'off');
confusionchart(validationSet.Labels, predictedLabels, ...
    'Title', sprintf('HOG + SVM Confusion Matrix, Accuracy %.2f%%', accuracy * 100), ...
    'RowSummary', 'row-normalized', ...
    'ColumnSummary', 'column-normalized');
