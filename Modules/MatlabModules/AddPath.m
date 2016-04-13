function outputParams=AddPath(inputParams)

%% NIRFAST PATH
curDir = pwd;
libDir = fileparts(curDir);
NIRFASTPath=fullfile(libDir,'NIRFASTMatlab');

%% MATLAB PATH
pn = what('MATLAB');

%% Open startup.m
startupFilePath = fullfile(pn.path,'startup.m');
startupDoesntExist = ~exist(startupFilePath, 'file');
[fid msg] = fopen(startupFilePath,'a+');

%% Populate startup.m
if startupDoesntExist
  fprintf(fid,'%%% startup.m\n');
  fprintf(fid,'%%  This script is executed everytime you start MatLab.\n\n');
end

fprintf(fid,'%%% Adding NIRFAST package to MatLab path\n');
fprintf(fid,'NIRFASTMatlabPath = ''%s'';\n', NIRFASTPath);
fprintf(fid,'disp(''Added NIRFAST-Matlab directory to the path:'');\n');
fprintf(fid,'disp(NIRFASTMatlabPath);\n');
fprintf(fid,'disp(''Edit startup.m to remove NIRFAST-Matlab from the path when starting MatLab.'');\n');
fprintf(fid,'addpath(genpath(NIRFASTMatlabPath))\n\n');
fclose(fid);