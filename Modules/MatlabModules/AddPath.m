function outputParams=AddPath(inputParams)

%% NIRFAST PATH
curDir = pwd;
libDir = fileparts(curDir);
NIRFASTPath=fullfile(libDir,'NIRFASTMatlab');

%% MATLAB PATH
pn = what('MATLAB');
startupFilePath = pn.path;

%% Open startup.m
startupFileName = fullfile(startupFilePath,'startup.m');
startupDidntExist = ~exist(startupFileName, 'file');
fid = fopen(startupFileName,'a+t');

%% Make sure a startup file exists
if fid == -1
  disp('Generating new startup.m file since none was present.');
  cd(startupFilePath)
  fidm = fopen('startup.m','w');
  fclose(fidm);
  cd(curDir)
  fid = fopen(startupFileName,'a+t');
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