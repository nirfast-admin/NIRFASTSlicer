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

%% If startup file did not exist, create & populate it
if startupDidntExist  
  [fid, msg] = fopen(startupFileName,'wt');
  
  if fid == -1
    outputParams.status = ['FAILURE: could not create startup.m file (', msg, ').'];
    outputParams.instructions = ['Manually add ''', NIRFASTPath,''' and its subdirectories to your MatLab path to use the NIRFAST package.'];
    outputParams.command = ['addpath(genpath(''',NIRFASTPath,'''))'];
    fprintf('\nCould not create startup.m file: %s.\nManually add the following path and its subdirectories to your MatLab path to use the NIRFAST package:\n%s', msg, NIRFASTPath)
    return
  end
  
  fprintf(fid,'%% startup.m\n');
  fprintf(fid,'%% This script is executed everytime you start MatLab.\n\n');
  fprintf(fid,'%% Adding NIRFAST package to MatLab path\n');
  fprintf(fid,'NIRFASTPath = ''%s'';\n', NIRFASTPath);
  fprintf(fid,'disp(''Added NIRFAST-Matlab directory to the path:'');\n');
  fprintf(fid,'disp(NIRFASTPath);\n');
  fprintf(fid,'disp(''Edit startup.m to remove NIRFAST-Matlab from the path when starting MatLab.'');\n');
  fprintf(fid,'addpath(genpath(NIRFASTPath))\n\n');
  fclose(fid);
  
  %% Populate output message
  outputParams.status = 'SUCCESS: NIRFAST successfully added to MatLab path.';
  outputParams.instructions = ['Edit ''', startupFileName,''' if you need to remove NIRFAST from the path when starting MatLab.'];
  outputParams.command = ['edit(''',startupFileName,''')'];
  
  return;
end

%% If file exists, replace existing NIRFASTPath or append if not found
[fid, msg] = fopen(startupFileName,'rt');

if fid == -1
    outputParams.status = ['FAILURE: could not create startup.m file (', msg, ').'];
    outputParams.instructions = ['Manually add ''', NIRFASTPath,''' and its subdirectories to your MatLab path to use the NIRFAST package.'];
    outputParams.command = ['addpath(genpath(''',NIRFASTPath,'''))'];
    fprintf('\nCould not create startup.m file: %s.\nManually add the following path and its subdirectories to your MatLab path to use the NIRFAST package:\n%s', msg, NIRFASTPath)
    return
end

tempFileName = fullfile(startupFilePath,'startup_temp.m');
[temp_fid, temp_msg] = fopen(tempFileName,'wt');

if temp_fid == -1
    outputParams.status = ['FAILURE: could not create temp file (', temp_msg, ').'];
    outputParams.instructions = ['Manually add ''', NIRFASTPath,''' and its subdirectories to your MatLab path to use the NIRFAST package.'];
    outputParams.command = ['addpath(genpath(''',NIRFASTPath,'''))'];
    fprintf('\nCould not create startup.m file: %s.\nManually add the following path and its subdirectories to your MatLab path to use the NIRFAST package:\n%s', msg, NIRFASTPath)
    return
end

NIRFASTPathFound = false;
  
while (~feof(fid))
  line = fgetl(fid);
  if strncmp(line,'NIRFASTPath',11)
    line = sprintf('NIRFASTPath = ''%s'';', NIRFASTPath);
    NIRFASTPathFound = true;
  end
  fprintf(temp_fid,'%s\n',line);
end
fclose(fid);

if ~NIRFASTPathFound
  fprintf(temp_fid,'%% Adding NIRFAST package to MatLab path\n');
  fprintf(temp_fid,'NIRFASTPath = ''%s'';\n', NIRFASTPath);
  fprintf(temp_fid,'disp(''Added NIRFAST-Matlab directory to the path:'');\n');
  fprintf(temp_fid,'disp(NIRFASTPath);\n');
  fprintf(temp_fid,'disp(''Edit startup.m to remove NIRFAST-Matlab from the path when starting MatLab.'');\n');
  fprintf(temp_fid,'addpath(genpath(NIRFASTPath))\n\n');
end

fclose(temp_fid);
movefile(tempFileName,startupFileName);

%% Populate output message
outputParams.status = 'SUCCESS: NIRFAST successfully added to MatLab path.';
outputParams.instructions = ['Edit ''', startupFileName,''' if you need to remove NIRFAST from the path when starting MatLab.'];
outputParams.command = ['edit(''',startupFileName,''')'];