function outputParams=SavePath(inputParams)

if strcmp(inputParams.savingDir,'/')
    errordlg('Select a directory to save the files', 'I/O Error')
    error('I/O Error: missing directory')
end

%% NIRFAST PATH
NIRFASTPath=fullfile('..','NIRFASTMatlab');
addpath(genpath(NIRFASTPath));
status = savepath(fullfile(inputParams.savingDir,'pathdef.m'));
if status == 1
  errordlg('Could not save pathdef.m', 'Writing Error')
  error('Writing Error: Could not save pathdef.m)')
end
