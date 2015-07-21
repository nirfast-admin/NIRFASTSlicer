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

set(modules NIRFast Threshold)

set(NIRView_MATLABMODULES_DIR "${Slicer_LIB_DIR}/MatlabModules")
set(NIRView_INSTALL_MATLABMODULES_DIR "${Slicer_INSTALL_ROOT}${NIRView_MATLABMODULES_DIR}")

foreach(module ${modules})

  message(STATUS "Configuring Matlab module: ${module}")
  configure_file(
    ${module}.xml 
    ${CMAKE_BINARY_DIR}/${NIRView_MATLABMODULES_DIR}/${module}.xml
  )
  configure_file(
    ${module}.m
    ${CMAKE_BINARY_DIR}/${NIRView_MATLABMODULES_DIR}/${module}.m
  )
  configure_file(
    ${module}
    ${CMAKE_BINARY_DIR}/${NIRView_MATLABMODULES_DIR}/${module}
  )
  install(
    FILES ${module}.xml ${module}.m ${module}
    DESTINATION ${NIRView_INSTALL_MATLABMODULES_DIR}
    COMPONENT Runtime
  )
endforeach()

configure_file(
  NIRViewMatLabModulesConfigure.h.in
  ${CMAKE_BINARY_DIR}/NIRViewMatLabModulesConfigure.h
  )
