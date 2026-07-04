%% Main.m - Gesture recognition system entry

clear; clc; close all;
baseDir = fileparts(mfilename('fullpath'));
cd(baseDir);

fprintf('======= Gesture Recognition System =======\n');
fprintf('1. Run DataTraining\n');
fprintf('2. Run DataTesting\n');
fprintf('3. Exit\n');

while true
    userVal = input('Please choose an option (1-3): ', 's');

    switch strtrim(userVal)
        case '1'
            run('DataTraining.m');
        case '2'
            DataTesting();
        case '3'
            fprintf('System exited.\n');
            break;
        otherwise
            fprintf('Invalid input. Please choose again.\n');
    end
end
