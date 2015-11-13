#-----------------------------------------------------------------------------
set(MODULE_NAME Mesh2Image)

#-----------------------------------------------------------------------------

#
# SlicerExecutionModel
#
find_package(SlicerExecutionModel REQUIRED)
include(${SlicerExecutionModel_USE_FILE})

#
# VTK
#
set(${PROJECT_NAME}_VTK_COMPONENTS
  vtkCommonCore
  )
find_package(VTK 6.0 COMPONENTS ${${PROJECT_NAME}_VTK_COMPONENTS} REQUIRED)
include(${VTK_USE_FILE})

#-----------------------------------------------------------------------------
SEMMacroBuildCLI(
  NAME ${MODULE_NAME}
  TARGET_LIBRARIES
    ${VTK_LIBRARIES}
    MRMLCore
  INCLUDE_DIRECTORIES
    ${MRMLCore_INCLUDE_DIRS}
  )
