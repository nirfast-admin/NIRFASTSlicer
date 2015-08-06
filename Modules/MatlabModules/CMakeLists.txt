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

# The following call will include the NIRViewConfig.cmake
# defining the variable NIRFast_SOURCE_DIR
find_package(NIRView REQUIRED)

### NIRFast ###

# Set paths
set(NIRView_NIRFAST_DIR "${Slicer_LIB_DIR}")
set(NIRView_INSTALL_NIRFAST_DIR "${Slicer_INSTALL_ROOT}${NIRView_NIRFAST_DIR}")

# Copy NIRFast
message(STATUS "Copying project sources: NIRFast")
file(
  COPY ${NIRFast_SOURCE_DIR}
  DESTINATION ${CMAKE_BINARY_DIR}/${NIRView_NIRFAST_DIR}
)

# Install NIRFast
install(
  DIRECTORY ${NIRFast_SOURCE_DIR}
  DESTINATION ${NIRView_INSTALL_NIRFAST_DIR}
  COMPONENT Runtime
)

### NIRFastMeshing ###

# Set paths
set(NIRView_NIRFASTMESHING_DIR "${Slicer_LIB_DIR}")
set(NIRView_INSTALL_NIRFASTMESHING_DIR "${Slicer_INSTALL_ROOT}${NIRView_NIRFASTMESHING_DIR}")

# Copy NIRFast
message(STATUS "Copying project sources: NIRFastMeshing")
file(
  COPY ${NIRFastMeshing_SOURCE_DIR}
  DESTINATION ${CMAKE_BINARY_DIR}/${NIRView_NIRFASTMESHING_DIR}
)

# Install NIRFast
install(
  DIRECTORY ${NIRFastMeshing_SOURCE_DIR}
  DESTINATION ${NIRView_INSTALL_NIRFASTMESHING_DIR}
  COMPONENT Runtime
)

### MatlabModules ###

# Define names of MatlabModules
set(modules Image2Mesh)

# Set paths
set(NIRView_MATLABMODULES_DIR "${Slicer_LIB_DIR}/MatlabModules")
set(NIRView_INSTALL_MATLABMODULES_DIR "${Slicer_INSTALL_ROOT}${NIRView_MATLABMODULES_DIR}")

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
    ${CMAKE_BINARY_DIR}/${NIRView_MATLABMODULES_DIR}/${moduleXMLFile}
    COPY_ONLY
  )
  configure_file(
    ${moduleMFile}
    ${CMAKE_BINARY_DIR}/${NIRView_MATLABMODULES_DIR}/${moduleMFile}
    COPY_ONLY
  )
  configure_file(
    ${moduleExecutable}
    ${CMAKE_BINARY_DIR}/${NIRView_MATLABMODULES_DIR}/${moduleExecutable}
    COPY_ONLY
  )
  install(
    FILES ${moduleXMLFile} ${moduleMFile}
    DESTINATION ${NIRView_INSTALL_MATLABMODULES_DIR}
    COMPONENT Runtime
  )
  install(
    PROGRAMS ${moduleExecutable}
    DESTINATION ${NIRView_INSTALL_MATLABMODULES_DIR}
    COMPONENT Runtime
  )
endforeach()

# Configure file containing the variable NIRView_MATLABMODULES_DIR
# readable by main.cxx to add the path to the modules additional paths
configure_file(
  NIRViewMatLabModulesConfigure.h.in
  ${CMAKE_BINARY_DIR}/NIRViewMatLabModulesConfigure.h
)
