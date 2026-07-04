function DataTesting()
% DataTesting.m - Test HOG + SVM gesture classifier

    baseDir = fileparts(mfilename('fullpath'));
    modelPath = fullfile(baseDir, 'trainedModel.mat');

    if ~exist(modelPath, 'file')
        error('trainedModel.mat was not found. Please run DataTraining.m first.');
    end

    modelData = load(modelPath, 'classifier', 'imgSize', 'cellSize');
    classifier = modelData.classifier;
    imgSize = modelData.imgSize;
    cellSize = modelData.cellSize;

    choice = questdlg('Choose testing mode:', 'Testing Mode', ...
        'Single Image', 'Folder Batch', 'Cancel', 'Single Image');

    switch choice
        case 'Single Image'
            detectSingleFile(classifier, imgSize, cellSize);
        case 'Folder Batch'
            detectFolder(classifier, imgSize, cellSize, baseDir);
        otherwise
            fprintf('Testing canceled.\n');
    end
end

function detectSingleFile(classifier, imgSize, cellSize)
    [file, path] = uigetfile( ...
        {'*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff', 'Image files'}, ...
        'Choose a gesture image');

    if isequal(file, 0)
        fprintf('No image selected.\n');
        return;
    end

    fullPath = fullfile(path, file);
    rawImg = imread(fullPath);
    label = predictLabel(rawImg, classifier, imgSize, cellSize);

    figure('Name', ['Single Image: ', file], 'NumberTitle', 'off');
    imshow(rawImg);
    title(['Prediction: ', char(label)], 'FontSize', 16, 'Color', 'r');

    fprintf('Image "%s" was classified as "%s"\n', file, char(label));
end

function detectFolder(classifier, imgSize, cellSize, baseDir)
    selPath = uigetdir(baseDir, 'Choose a folder with test images');
    if isequal(selPath, 0)
        fprintf('No folder selected.\n');
        return;
    end

    exts = {'*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tif', '*.tiff'};
    imgFiles = [];
    for i = 1:numel(exts)
        imgFiles = [imgFiles; dir(fullfile(selPath, exts{i}))]; %#ok<AGROW>
    end

    if isempty(imgFiles)
        msgbox('No image files were found in the selected folder.', 'Info');
        return;
    end

    numFiles = numel(imgFiles);
    fprintf('--- Batch testing started. %d images found. ---\n', numFiles);

    rows = ceil(sqrt(numFiles));
    cols = ceil(numFiles / rows);
    figure('Name', 'Batch Testing Results', 'NumberTitle', 'off');

    for i = 1:numFiles
        fileName = imgFiles(i).name;
        fullPath = fullfile(selPath, fileName);
        rawImg = imread(fullPath);
        label = predictLabel(rawImg, classifier, imgSize, cellSize);

        fprintf('Image "%s" was classified as "%s"\n', fileName, char(label));

        subplot(rows, cols, i);
        imshow(rawImg);
        title(sprintf('%s -> %s', fileName, char(label)), ...
            'FontSize', 8, ...
            'Interpreter', 'none');
    end

    fprintf('--- Batch testing finished. ---\n');
end

function label = predictLabel(rawImg, classifier, imgSize, cellSize)
    img = preprocessHand(rawImg, imgSize);
    features = extractHOGFeatures(img, 'CellSize', cellSize);
    label = predict(classifier, features);
end
