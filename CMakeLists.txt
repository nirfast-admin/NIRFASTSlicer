cmake_minimum_required(VERSION 3.11)

# Enable C++11
if(NOT DEFINED CMAKE_CXX_STANDARD)
  if(DEFINED Qt5_DIR)
    set(CMAKE_CXX_STANDARD 11)
  else()
    set(CMAKE_CXX_STANDARD 98)
  endif()
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Slicer sources
include(FetchContent)
if(NOT DEFINED slicersources_SOURCE_DIR)
  # Download Slicer sources and set variables slicersources_SOURCE_DIR and slicersources_BINARY_DIR
  FetchContent_Populate(slicersources
	  GIT_REPOSITORY git://github.com/Slicer/Slicer
	  GIT_TAG        e6878b0065778a56d2e7f182f4c9abba20f4ca88 # 2018-03-22
	  GIT_PROGRESS   1
	  )
else()
  set(slicersources_BINARY_DIR ${CMAKE_CURRENT_BINARY_DIR}/slicersources-subbuild)
endif()

set(CMAKE_MODULE_PATH ${slicersources_SOURCE_DIR}/CMake ${CMAKE_MODULE_PATH})
include(SlicerInitializeOSXVariables)

# Set application metadata
set(APPLICATION_NAME           "NIRFASTSlicer")
set(Slicer_VERSION_MAJOR       "1")
set(Slicer_VERSION_MINOR       "1")
set(Slicer_VERSION_PATCH       "0")
project(${APPLICATION_NAME} VERSION "${Slicer_VERSION_MAJOR}.${Slicer_VERSION_MINOR}.${Slicer_VERSION_PATCH}")

# Set organization
set(Slicer_ORGANIZATION_DOMAIN "nirfast.org")
set(Slicer_ORGANIZATION_NAME   "Dartmouth College NIRFAST Group")

# Configure Application
set(Slicer_APPLICATIONS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/Applications)
set(Slicer_MAIN_PROJECT ${APPLICATION_NAME}App)
set(${Slicer_MAIN_PROJECT}_APPLICATION_NAME ${APPLICATION_NAME})

# Default home and favorite modules
set(Slicer_DEFAULT_HOME_MODULE "Home")
set(Slicer_DEFAULT_FAVORITE_MODULES "Data, Volumes, Models, Transforms, Markups, SegmentEditor")

# Configure SuperBuild
set(SUPERBUILD_TOPLEVEL_PROJECT Slicer)
set(EXTERNAL_PROJECT_ADDITIONAL_DIR "${CMAKE_CURRENT_SOURCE_DIR}/SuperBuild")
include(ExternalProjectDependency)

if(NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_DEFAULT_BUILD_TYPE "Release")
endif()
include(SlicerInitializeBuildType)
include(SlicerInitializeReleaseType)

# Slicer options
option(BUILD_TESTING                            "Build application test suite"                        OFF)
option(Slicer_BUILD_DOCUMENTATION               "Build documentation (Doxygen, sphinx, ...)"          OFF)
if(WIN32)
  option(Slicer_BUILD_WIN32_CONSOLE             "Build application executable as a console app"       OFF)
endif()

option(Slicer_BUILD_QT_DESIGNER_PLUGINS         "Build Qt designer plugins"                           OFF)
option(Slicer_BUILD_DICOM_SUPPORT               "Build application with DICOM support"                ON)
option(Slicer_BUILD_DIFFUSION_SUPPORT           "Build application with Diffusion support"            OFF)
option(Slicer_BUILD_EXTENSIONMANAGER_SUPPORT    "Build application with ExtensionManager support"     OFF)
option(Slicer_BUILD_MULTIVOLUME_SUPPORT         "Build application with MultiVolume support"          OFF)
option(Slicer_BUILD_PARAMETERSERIALIZER_SUPPORT "Build application with parameter serializer support" OFF)
option(Slicer_USE_PYTHONQT                      "Build application with Python support"               ON)
option(Slicer_USE_PYTHONQT_WITH_TCL             "Build application with Python Tcl adapter layer"     OFF)
option(Slicer_USE_QtTesting                     "Build application with QtTesting support"            OFF)
option(Slicer_USE_SimpleITK                     "Build application with SimpleITK support"            OFF)

option(Slicer_BUILD_BRAINSTOOLS                 "Build application with BRAINSTools module"           OFF)
option(Slicer_BUILD_DataStore                   "Build application with DataStore module"             OFF)
option(Slicer_BUILD_CompareVolumes              "Build application with ChangeTrackerPy module"       OFF)
option(Slicer_BUILD_LandmarkRegistration        "Build application with LandmarkRegistration module"  OFF)

# Enable Slicer built-in modules
set(Slicer_CLIMODULES_ENABLED
  LabelMapSmoothing
  ModelMaker
  ResampleScalarVectorDWIVolume # Needed by 'CropVolume' module
  )
set(Slicer_QTLOADABLEMODULES_ENABLED
  )
set(Slicer_QTSCRIPTEDMODULES_ENABLED
  )

# Disable Slicer built-in modules
set(Slicer_CLIMODULES_DISABLED
  )
set(Slicer_QTLOADABLEMODULES_DISABLED
  #Cameras
  #Units
  #Terminologies
  #Colors
  #SubjectHierarchy
  #Annotations
  #Markups
  #Transforms
  #Data
  #DoubleArrays
  #Models
  #SceneViews # Needed to avoid warning when loading scene
  #Segmentations
  SlicerWelcome
  #Tables
  #Reformat
  #ViewControllers
  #Volumes
  #VolumeRendering
  )
set(Slicer_QTSCRIPTEDMODULES_DISABLED
  #DataProbe
  DMRIInstall
  Editor
  EditorLib
  Endoscopy
  LabelStatistics
  PerformanceTests
  SampleData
  #ScreenCapture
  #SegmentEditor
  #SegmentStatistics
  SelfTests
  SurfaceToolbox
  VectorToScalarVolume
  )

# Enable/Disable Slicer custom modules: To create a new module, use the SlicerExtensionWizard.
set(Slicer_EXTENSION_SOURCE_DIRS
  ${${APPLICATION_NAME}_SOURCE_DIR}/Modules/MatlabModules
  ${${APPLICATION_NAME}_SOURCE_DIR}/Modules/Scripted/Home
  )

# Add remote extension source directories
include(ExternalProjectAddSource)

# Remote modules (added in topological order)
Slicer_Remote_Add(OpenIGTLink
  GIT_REPOSITORY ${EP_GIT_PROTOCOL}://github.com/Slicer/OpenIGTLink.git
  GIT_TAG 18db20552ac5cd48afdb94555d11a2f4f2c5417f # version 3.0 from 2017-06-28 + few Slicer patches
  LABELS REMOTE_MODULE
  )
list(APPEND Slicer_REMOTE_DEPENDENCIES OpenIGTLink)

Slicer_Remote_Add(OpenIGTLinkIF
  GIT_REPOSITORY ${EP_GIT_PROTOCOL}://github.com/Slicer/OpenIGTLinkIF.git
  GIT_TAG 0266aa27ad19a00f8d2b1c04736b9f3d3fb25aee # slicer-2017.05.17-bd4d34f
  LABELS REMOTE_MODULE
  )
list(APPEND Slicer_REMOTE_DEPENDENCIES OpenIGTLinkIF)

Slicer_Remote_Add(MatlabBridge
  GIT_REPOSITORY ${EP_GIT_PROTOCOL}://github.com/PerkLab/SlicerMatlabBridge.git
  GIT_TAG 934a1eff4db11b16af7d3de31357d08515dd05cd # 2018-02-21
  LABELS REMOTE_MODULE
  )
list(APPEND Slicer_REMOTE_DEPENDENCIES MatlabBridge)

# OpenIGTLink options
set(OpenIGTLink_BUILD_TESTING OFF)
set(OpenIGTLink_INSTALL_NO_DEVELOPMENT ON)

mark_as_superbuild(VARS
  OpenIGTLink_BUILD_TESTING:BOOL
  OpenIGTLink_INSTALL_NO_DEVELOPMENT:BOOL
  )

# Add Slicer sources
add_subdirectory(${slicersources_SOURCE_DIR} ${slicersources_BINARY_DIR})
