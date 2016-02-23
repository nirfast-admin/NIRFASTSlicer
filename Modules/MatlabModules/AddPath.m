function outputParams=AddPath(inputParams)

%% NIRFAST PATH
curDir = pwd;
libDir = fileparts(curDir);
NIRFASTPath=fullfile(libDir,'NIRFASTMatlab');

%% MATLAB PATH
pn = what('MATLAB');

%% POPULATE startup.m
[fid msg] = fopen(fullfile(pn.path,'startup.m'),'a+t');
st = 'addpath(genpath(';
fprintf(fid,'%% startup.m\n');
fprintf(fid,'%%\n');
fprintf(fid,'%% Adds top folder and subfolders of newdir to path at start of each MatLab instance.\n');
fprintf(fid,'%%\n\n');
fprintf(fid,'%s''%s''))\n\n',st,NIRFASTPath);
fclose(fid);