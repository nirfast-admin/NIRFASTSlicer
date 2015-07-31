function outputParams=Image2Mesh(inputParams)
% TODO instead of launching directly image2mesh_gui and giving those parameters path
% Parameters:
%  inputParams.inputvolume: labelmap
%  inputParams.outputmesh: output mesh
%

% Add paths to NIRFast
NIRFASTPath=fullfile('..','NIRFast');
addpath(genpath(NIRFASTPath));

% Add paths to NIRFastMeshing
MESHINGPath=fullfile('..','NIRFastMeshing');
addpath(genpath(MESHINGPath));

% Launch main function from nirfast.m in NIRFAST
image2mesh_gui();

%% Help for reading/writing parameters
%
% Reading input parameters
%
%  integer, integer-vector, float, float-vector, double, double-vector, string, string-enumeration, file:
%    value=inputParams.name;
%  string-vector:
%    value=cli_stringvectordecode(inputParams.name);
%  point-vector:
%    value=cli_pointvectordecode(inputParams.name);
%  boolean:
%    value=isfield(inputParams,'name');
%  image:
%    value=cli_imageread(inputParams.name);
%  transform:
%    value=cli_lineartransformread(inputParams.name);
%   or (for generic transforms):
%    value=cli_transformread(inputParams.name);
%  point:
%    values_LPS=cli_pointvectordecode(inputParams.name);
%    [pointDim pointCount]=size(values_LPS);
%  region:
%    values=cli_pointvectordecode(inputParams.name);
%    [regionDim regionCount]=size(values_LPS);
%    center_LPS=[values(1:3,regionIndex); 1];
%    radius_LPS=abs([values(4:6,regionIndex); 1]);
%  measurement:
%    value=cli_measurementread(inputParams.name);
%  geometry:
%    value=cli_geometryread(inputParams.name);
%    Important: in the CLI definition file the following attribute shall be added to the geometry element: fileExtensions=".ply"
%    See https://subversion.assembla.com/svn/slicerrt/trunk/MatlabBridge/src/Examples/MeshScale/ for a complete example.
%
%  Notes:
%    - Input and file (image, transform, measurement, geometry) parameter names are defined by the <longflag> element in the XML file
%    - Output parameter names are defined by the <name> element in the XML file
%    - For retrieving index-th unnamed parameter use inputParams.unnamed{index+1} instead of inputParams.name
%
%
% Writing output parameters
%
%  integer, integer-vector, float, float-vector, double, double-vector, string, string-enumeration, file:
%    outputParams.name=value;
%  image:
%    cli_imagewrite(inputParams.name, value);
%  transform:
%    cli_lineartransformwrite(inputParams.name, value);
%   or (for generic transforms):
%    cli_transformwrite(inputParams.name, value);
%  measurement:
%    cli_measurementwrite(inputParams.name, value);
%  geometry:
%    cli_geometrywrite(inputParams.name, value);
%    Important: in the CLI definition file the following attribute shall be added to the geometry element: fileExtensions=".stl"
%    See https://subversion.assembla.com/svn/slicerrt/trunk/MatlabBridge/src/Examples/MeshScale/ for a complete example.
%
