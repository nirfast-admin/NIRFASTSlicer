#============================================================================
#
# Copyright (c) Kitware, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#============================================================================

# Define names of MatlabModules
set(modules
  Image2Mesh
)

# Set paths
set(MATLABMODULES_DIR "${Slicer_LIB_DIR}/matlab-modules")
set(MATLABMODULES_INSTALL_DIR "${Slicer_INSTALL_ROOT}${MATLABMODULES_DIR}")

# Configure and Install files
foreach(module ${modules})

  message(STATUS "Copying Matlab module: ${module}")

  set(moduleXMLFile ${module}.xml)
  set(moduleMFile ${module}.m)
  if(WIN32)
	set(moduleExecutable ${module}.bat)
  else()
    set(moduleExecutable ${module})
  endif()
  
  configure_file(
    ${moduleXMLFile}
    ${CMAKE_BINARY_DIR}/${MATLABMODULES_DIR}/${moduleXMLFile}
    COPYONLY
  )
  configure_file(
    ${moduleMFile}
    ${CMAKE_BINARY_DIR}/${MATLABMODULES_DIR}/${moduleMFile}
    COPYONLY
  )
  configure_file(
    ${moduleExecutable}
    ${CMAKE_BINARY_DIR}/${MATLABMODULES_DIR}/${moduleExecutable}
    COPYONLY
  )
  install(
    FILES ${moduleXMLFile} ${moduleMFile}
    DESTINATION ${MATLABMODULES_INSTALL_DIR}
    COMPONENT Runtime
  )
  install(
    PROGRAMS ${moduleExecutable}
    DESTINATION ${MATLABMODULES_INSTALL_DIR}
    COMPONENT Runtime
  )
endforeach()

# Configure file containing the variable MATLABMODULES_DIR
# readable by main.cxx to add the path to the modules additional paths
configure_file(
  NIRFASTSlicerMatlabModulesConfigure.h.in
  ${CMAKE_BINARY_DIR}/NIRFASTSlicerMatlabModulesConfigure.h
)
