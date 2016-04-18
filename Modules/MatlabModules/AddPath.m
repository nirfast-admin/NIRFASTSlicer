function outputParams=AddPath(inputParams)

%% NIRFAST PATH
curDir = pwd;
libDir = fileparts(curDir);
NIRFASTPath=fullfile(libDir,'NIRFASTMatlab');

%% MATLAB PATH
startupFilePath = userpath;
startupFilePath = startupFilePath(1:end-1);

%% Open startup.m
startupFileName = fullfile(startupFilePath,'startup.m');
startupDidntExist = ~exist(startupFileName, 'file');
[fid, msg] = fopen(startupFileName,'a+t');

%% Make sure a startup file exists
if fid == -1
  error('\nCould not create startup.m file: %s.\nManually add the following path and its subdirectories to your MatLab path to use the NIRFAST package:\n%s', msg, NIRFASTPath)
end

%% If startup file did not exist
if startupDidntExist
  fprintf(fid,'%% startup.m\n');
  fprintf(fid,'%% This script is executed everytime you start MatLab.\n\n');
end

%% Populate startup file
fprintf(fid,'%% Adding NIRFAST package to MatLab path\n');
fprintf(fid,'NIRFASTPath = ''%s'';\n', NIRFASTPath);
fprintf(fid,'disp(''Added NIRFAST-Matlab directory to the path:'');\n');
fprintf(fid,'disp(NIRFASTPath);\n');
fprintf(fid,'disp(''Edit startup.m to remove NIRFAST-Matlab from the path when starting MatLab.'');\n');
fprintf(fid,'addpath(genpath(NIRFASTPath))\n\n');
fclose(fid);