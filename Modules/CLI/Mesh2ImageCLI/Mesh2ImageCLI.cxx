#include "Mesh2ImageCLICLP.h"

// VTK includes
#include <vtkNew.h>
#include <vtkUnstructuredGridReader.h>
#include <vtkUnstructuredGrid.h>
#include <vtkImageData.h>
#include <vtkPointData.h>
#include <vtkDataArray.h>
#include <vtkProbeFilter.h>
#include <vtkPassArrays.h>

// MRML
#include <vtkMRMLScalarVolumeNode.h>
#include <vtkMRMLVolumeArchetypeStorageNode.h>

// System includes
#include <iostream>
#include <fstream>
#include <string>
#include <map>

int main( int argc, char *argv[] )
{
  PARSE_ARGS;

  // read VTK dataset
  cout << "-- Reading VTK Mesh" <<endl;
  vtkNew<vtkUnstructuredGridReader> datasetReader;
  datasetReader->SetFileName(source.c_str());
  datasetReader->ReadAllScalarsOn();
  datasetReader->Update();

  vtkUnstructuredGrid* inputMesh = datasetReader->GetOutput();
  if(!inputMesh)
    {
    std::cerr << "Mesh2ImageCLI : Reading VTK mesh source failed" << std::endl;
    return EXIT_FAILURE;
    }

  // read volumeNode
  std::cout << "-- Reading Input Volume" << std::endl;
  vtkNew<vtkMRMLScalarVolumeNode> volumeNode;
  vtkNew<vtkMRMLVolumeArchetypeStorageNode> volumeReader;
  volumeReader->SetFileName(input.c_str());
  if( !volumeReader->ReadData(volumeNode.GetPointer()) )
    {
     std::cerr << "Mesh2ImageCLI : Reading input volume failed" << std::endl;
     return EXIT_FAILURE;
    }

  // get input image data from volumeNode
  std::cout << "-- Setting imageData space information using volume information" << std::endl;
  vtkImageData* inputImageData = volumeNode->GetImageData();
  inputImageData->SetOrigin(volumeNode->GetOrigin());
  inputImageData->SetSpacing(volumeNode->GetSpacing());

  // apply probe filter
  std::cout << "-- Resampling Mesh in ImageData space" << std::endl;
  vtkNew<vtkProbeFilter> probeFilter;
  probeFilter->SetInputData(inputImageData);
  probeFilter->SetSourceData(inputMesh);
  probeFilter->PassPointArraysOn();
  probeFilter->Update();

  vtkImageData* outputImageData = probeFilter->GetImageDataOutput();
  if(!outputImageData)
  {
    std::cerr << "Mesh2ImageCLI : Resampled failed, no output image data" << std::endl;
    return EXIT_FAILURE;
  }

  // reset origin and spacing for imageData
  std::cout << "-- Resetting imageData space information" << std::endl;
  inputImageData->SetOrigin(0,0,0);
  inputImageData->SetSpacing(1,1,1);
  outputImageData->SetOrigin(0,0,0);
  outputImageData->SetSpacing(1,1,1);

  // removing unneeded arrays
  vtkNew<vtkPassArrays> removeArrayFilter;
  removeArrayFilter->SetInputData(outputImageData);
  removeArrayFilter->RemoveArraysOn();
  removeArrayFilter->AddPointDataArray("vtkValidPointMask");
  removeArrayFilter->AddPointDataArray("ImageScalars");
  removeArrayFilter->Update();

  // update output volume node
  std::cout << "-- Updating VolumeNode ImageData" << std::endl;
  volumeNode->SetImageDataConnection(removeArrayFilter->GetOutputPort());

  // write
  vtkNew<vtkMRMLVolumeArchetypeStorageNode> volumeWriter;
  std::cout << "-- Write Output Volume" << std::endl;
  volumeWriter->SetFileName(output.c_str());
  volumeWriter->WriteData(volumeNode.GetPointer());

  return EXIT_SUCCESS;
}
