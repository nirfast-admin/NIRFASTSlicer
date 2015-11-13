#include "Mesh2ImageCLP.h"

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

  std::map<std::string,const char*> outputMap;
  if(region.c_str()) outputMap["region"] = region.c_str();
  if(mus.c_str()) outputMap["mus"] = mus.c_str();
  if(mua.c_str()) outputMap["mua"] = mua.c_str();
  if(kappa.c_str()) outputMap["kappa"] = kappa.c_str();
  if(! (region.c_str() || mus.c_str() || mua.c_str() || kappa.c_str()))
    {
    std::cerr << "Mesh2Image : No output volumes specified." << std::endl;
    return EXIT_FAILURE;
    }

  // read VTK dataset
  cout << "-- Reading VTK Mesh" <<endl;
  vtkNew<vtkUnstructuredGridReader> datasetReader;
  datasetReader->SetFileName(source.c_str());
  datasetReader->ReadAllScalarsOn();
  datasetReader->Update();

  vtkUnstructuredGrid* inputMesh = datasetReader->GetOutput();
  if(!inputMesh)
    {
    std::cerr << "Mesh2Image : Reading VTK mesh source failed" << std::endl;
    return EXIT_FAILURE;
    }

  // read volumeNode
  std::cout << "-- Read Input Volume" << std::endl;
  vtkNew<vtkMRMLScalarVolumeNode> volumeNode;
  vtkNew<vtkMRMLVolumeArchetypeStorageNode> volumeReader;
  volumeReader->SetFileName(input.c_str());
  if( !volumeReader->ReadData(volumeNode.GetPointer()) )
    {
     std::cerr << "Mesh2Image : Reading input volume failed" << std::endl;
     return EXIT_FAILURE;
    }

  // get input image data from volumeNode
  std::cout << "-- Set imageData space information using volume information" << std::endl;
  vtkImageData* inputImageData = volumeNode->GetImageData();
  inputImageData->SetOrigin(volumeNode->GetOrigin());
  inputImageData->SetSpacing(volumeNode->GetSpacing());

  // apply probe filter
  std::cout << "-- Resample Mesh in ImageData space" << std::endl;
  vtkNew<vtkProbeFilter> probeFilter;
  probeFilter->SetInputData(inputImageData);
  probeFilter->SetSourceData(inputMesh);
  probeFilter->PassPointArraysOn();
  probeFilter->Update();

  vtkImageData* outputImageData = probeFilter->GetImageDataOutput();
  if(!outputImageData)
  {
    std::cerr << "Mesh2Image : Resampled failed, no output image data" << std::endl;
    return EXIT_FAILURE;
  }

  // reset origin and spacing for imageData
  std::cout << "-- Reset imageData space information" << std::endl;
  inputImageData->SetOrigin(0,0,0);
  inputImageData->SetSpacing(1,1,1);
  outputImageData->SetOrigin(0,0,0);
  outputImageData->SetSpacing(1,1,1);

  // extract scalars, update volume, and write
  vtkNew<vtkMRMLVolumeArchetypeStorageNode> volumeWriter;
  typedef std::map<std::string,const char*>::iterator it_type;
  for(it_type iterator = outputMap.begin(); iterator != outputMap.end(); iterator++)
    {
    std::string arrayName = iterator->first;
    const char* outputPath = iterator->second;

    vtkNew<vtkPassArrays> passArray;
    std::cout << "-- Extract scalar : " << arrayName << std::endl;
    passArray->SetInputData(outputImageData);
    passArray->AddPointDataArray(arrayName.c_str());
    passArray->Update();

    vtkImageData* extractedImageData = vtkImageData::SafeDownCast(passArray->GetOutput());
    if(!extractedImageData)
    {
      std::cerr << "Mesh2Image : Scalar extraction failed" << std::endl;
      continue;
    }
    vtkDataArray* scalars = extractedImageData->GetPointData()->GetScalars();
    if(!(scalars ? scalars->GetNumberOfComponents() : 0))
    {
      std::cerr << "Mesh2Image : Extracted image has no scalars (1 component)" << std::endl;
      continue;
    }

    std::cout << "Update VolumeNode ImageData" << std::endl;
    volumeNode->SetImageDataConnection(passArray->GetOutputPort());

    std::cout << "Write Output Volume" << std::endl;
    volumeWriter->SetFileName(outputPath);
    volumeWriter->WriteData(volumeNode.GetPointer());
    }

  return EXIT_SUCCESS;
}
