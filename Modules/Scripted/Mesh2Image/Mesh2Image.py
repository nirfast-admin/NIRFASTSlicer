###########################################################################
#  Library: iCSPlan
#
# Copyright 2015 Kitware Inc. 28 Corporate Drive,
# Clifton Park, NY, 12065, USA.
# All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###########################################################################
import vtk, qt, ctk, slicer, PythonQt
import os
import sys


# ICON_DIR = os.path.dirname(os.path.realpath(__file__)) + '/Resources/Icons/'

#
# Mesh2Image
#

class Mesh2Image:
    def __init__(self, parent):
        parent.title = "Import Optical Properties"
        parent.categories = ["NIRFAST"]
        parent.dependencies = []
        parent.contributors = ["Alexis Girault (Kitware Inc)"]
        parent.helpText = """
        This module acts like a probe filter : it resamples the VTK mesh holding the point attributes (optical information) into the image space of the Input Volume, which can be the grayscale image or the label map, previously used to set the boundaries of the mesh in Image2Mesh.
        This module will dynamically create a scalar volume for each point attribute of the VTK mesh. Those volumes can then be overlayed over the Input Volume.
        """
        parent.acknowledgementText = """
        This work is part of the NIRFASTSlicer application developped at Kitware, Inc. to allow the use of the NIRFASTMatlab application developped by Dartmouth University and the University of Birmingham, funded by the National Institutes of Health, Grant R01 CA184354.
        """

        # parent.icon = qt.QIcon("%s/cranioIcon.png" % ICON_DIR)

        self.parent = parent


#
# Mesh2ImageLogic
#

class Mesh2ImageLogic:
    def __init__(self):
        print "logic init"

        # Progress
        self.Observations = []
        self.Node = slicer.vtkMRMLCommandLineModuleNode()
        self.Node.SetStatus(self.Node.Idle)

        # Output
        self.OutputVolumes = {}

    def progressFunction(self, caller, event):
        probeFilter = vtk.vtkProbeFilter.SafeDownCast(caller)
        if not probeFilter:
            print "COULD NOT OBSERVE PROBEFILTER"
            return
        text = " Progress: " + str(round(probeFilter.GetProgress() * 100)) + "%"
        print text
        self.Node.SetName(text)
        slicer.app.processEvents()

    def resample(self, sourceMeshPath, volumeNode, imageSpacing):

        self.Node.SetStatus(self.Node.Running)

        # Read VTK Dataset
        print "-- Reading VTK Dataset"
        datasetReader = vtk.vtkUnstructuredGridReader()
        datasetReader.SetFileName(sourceMeshPath)
        datasetReader.ReadAllScalarsOn()
        datasetReader.Update()

        inputMesh = datasetReader.GetOutput()
        if inputMesh is None:
            print >> sys.stderr, "Mesh2Image : Reading VTK mesh source failed"
            self.Node.SetStatus(self.Node.CompletedWithErrors)
            return 0

        # Get input image data from volumeNode
        if volumeNode:
            print "-- Setting imageData space information using volume information"
            inputImageData = volumeNode.GetImageData()
            inputImageData.SetOrigin(volumeNode.GetOrigin())
            inputImageData.SetSpacing(volumeNode.GetSpacing())
            volumesLogic = slicer.modules.volumes.logic()

        # Create input image data based on mesh bounds
        else:
            bd = inputMesh.GetBounds()
            imgSpacing = [imageSpacing] * 3
            imgOrigin = bd[0],bd[2],bd[4]
            dimX = int(round(abs(bd[0]-bd[1])/imageSpacing))
            dimY = int(round(abs(bd[2]-bd[3])/imageSpacing))
            dimZ = int(round(abs(bd[4]-bd[5])/imageSpacing))
            inputImageData = vtk.vtkImageData()
            inputImageData.SetSpacing(imgSpacing)
            inputImageData.SetOrigin(imgOrigin)
            inputImageData.SetDimensions(dimX, dimY, dimZ)

        # Apply probe filter
        print "-- Resampling Mesh in ImageData space"
        probeFilter = vtk.vtkProbeFilter()
        probeFilter.SetInputData(inputImageData)
        probeFilter.SetSourceData(inputMesh)
        probeFilter.PassPointArraysOn()
        probeFilter.AddObserver(vtk.vtkCommand.ProgressEvent, self.progressFunction)
        # probeFilter.AddObserver(vtk.vtkCommand.StartEvent, self.startFunction)
        # probeFilter.AddObserver(vtk.vtkCommand.EndEvent, self.endFunction)
        probeFilter.Update()

        outputImageData = probeFilter.GetImageDataOutput()
        if outputImageData is None:
            print >> sys.stderr, "Mesh2Image : Resampled failed, no output image data"
            self.Node.SetStatus(self.Node.CompletedWithErrors)
            return 0

        # Reset Origin and Spacing for imageData
        print "-- Resetting imageData space information"
        inputImageData.SetOrigin(0, 0, 0)
        inputImageData.SetSpacing(1, 1, 1)
        outputImageData.SetOrigin(0, 0, 0)
        outputImageData.SetSpacing(1, 1, 1)

        # Remove useless array(s)
        print "-- Removing unneeded arrays"
        removeArrayFilter = vtk.vtkPassArrays()
        removeArrayFilter.SetInputData(outputImageData)
        removeArrayFilter.RemoveArraysOn()
        removeArrayFilter.AddPointDataArray("vtkValidPointMask")
        if volumeNode: removeArrayFilter.AddPointDataArray("ImageScalars")
        removeArrayFilter.Update()

        outputImageData = removeArrayFilter.GetOutput()

        self.OutputVolumes = {}
        ptData = outputImageData.GetPointData()
        for i in range(ptData.GetNumberOfArrays()):
            arrayName = ptData.GetArrayName(i)

            # Extract array
            print "-- Extracting array", arrayName
            passArrayFilter = vtk.vtkPassArrays()
            passArrayFilter.SetInputData(outputImageData)
            passArrayFilter.AddPointDataArray(arrayName)
            passArrayFilter.Update()

            extractedImageData = vtk.vtkImageData.SafeDownCast(passArrayFilter.GetOutput())
            if extractedImageData is None:
                print "Array extraction failed"
                continue
            extractedImageData.GetPointData().SetActiveScalars(arrayName)
            scalars = extractedImageData.GetPointData().GetScalars()
            if scalars is None:
                print "No scalar values for this array"
                continue
            if scalars.GetNumberOfComponents == 0:
                print "This array components are not scalar values"
                continue

            # Update volumeNode ImageData
            print "Creating Output Node"
            outputNode = slicer.vtkMRMLScalarVolumeNode()
            if volumeNode:
                outputNode = volumesLogic.CloneVolume(volumeNode,
                                                      volumeNode.GetName() + "_" + arrayName)
            else:
                outputNode.SetSpacing(imgSpacing)
                outputNode.SetOrigin(imgOrigin)
                outputNode.SetName("data_" + arrayName)
            outputNode.SetImageDataConnection(passArrayFilter.GetOutputPort())

            # Add to scene and handle display
            slicer.mrmlScene.AddNode(outputNode)
            SetSliceViewerLayers(slicer.mrmlScene,
                                 foreground=outputNode,
                                 foregroundOpacity=0.8)
            displayNode = outputNode.GetDisplayNode()
            displayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeIron")
            displayNode.AutoWindowLevelOn()
            displayNode.ApplyThresholdOn()
            displayNode.SetLowerThreshold(0.000001)
            displayNode.SetInterpolate(0)

            # Add to list for the module GUI
            self.OutputVolumes[arrayName] = outputNode

        # FINISH
        self.Node.SetStatus(self.Node.Completed)
        return 1

#
# qMesh2ImageWidget
#

class Mesh2ImageWidget:
    def __init__(self, parent=None):
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        self.layout = self.parent.layout()
        if not parent:
            self.setup()
            self.parent.show()

        # Logic
        self.Logic = Mesh2ImageLogic()

    def setup(self):

        # 1) INPUTS
        self.InputsSection = ctk.ctkCollapsibleButton()
        self.InputsSection.text = "Inputs"
        self.InputsSection.collapsed = 0
        self.InputsLayout = qt.QGridLayout(self.InputsSection)
        self.layout.addWidget(self.InputsSection)

        # 2) OUTPUTS
        self.OutputsSection = ctk.ctkCollapsibleButton()
        self.OutputsSection.text = "Outputs"
        self.OutputsSection.collapsed = 0
        self.OutputsLayout = qt.QFormLayout(self.OutputsSection)
        self.layout.addWidget(self.OutputsSection)

        # 3) SPACER
        self.layout.addStretch(1)

        # 4) PROGRESS
        self.ProgressBar = slicer.qSlicerCLIProgressBar()
        self.ProgressBar.setCommandLineModuleNode(self.Logic.Node)
        self.layout.addWidget(self.ProgressBar)

        # 1.1) Inputs Values
        label = qt.QLabel("VTK Mesh: ")
        self.SourceMeshPathLine = ctk.ctkPathLineEdit()
        self.SourceMeshPathLine.toolTip = 'VTK unstructured grid mesh holding the data to be interpolated into a Volume.'
        self.InputsLayout.addWidget(label, 0, 0)
        self.InputsLayout.addWidget(self.SourceMeshPathLine, 0, 1)

        label = qt.QLabel("Bounding Volume: ")
        self.InputVolumeComboBox = slicer.qMRMLNodeComboBox()
        self.InputVolumeComboBox.nodeTypes = (("vtkMRMLScalarVolumeNode"), "")
        self.InputVolumeComboBox.showChildNodeTypes = False
        self.InputVolumeComboBox.setMRMLScene(slicer.mrmlScene)
        self.InputVolumeComboBox.addEnabled = False
        self.InputVolumeComboBox.renameEnabled = True
        self.InputVolumeComboBox.toolTip = 'Volume defining the output geometric structure where the point data of the source mesh is resampled.'
        self.InputsLayout.addWidget(label, 1, 0)
        self.InputsLayout.addWidget(self.InputVolumeComboBox, 1, 1)

        self.ResamplePushButton = qt.QPushButton("Resample Mesh")
        self.ResamplePushButton.toolTip = "Resample Mesh"
        self.ResamplePushButton.connect('clicked()', self.onResamplePressed)
        self.InputsLayout.addWidget(self.ResamplePushButton, 2, 1)

        self.OutputWidgets = []

    def onResamplePressed(self):

        self.ResamplePushButton.setEnabled(False)
        self.ProgressBar.setNameVisibility(True)

        input_volume = self.InputVolumeComboBox.currentNode()
        source_mesh = self.SourceMeshPathLine.currentPath
        img_spacing = 0.0
        ok = True

        # no mesh
        if not source_mesh:
            print >> sys.stderr, "Mesh2Image : VTK mesh file missing"
            qt.QMessageBox.critical(
                slicer.util.mainWindow(),
                "Mesh2Image", "VTK mesh file missing")
            ok = False

        # no volume
        elif input_volume is None:
            s = ("No bounding volume was selected to resample your mesh. You will get\n"
                 "better results by using the original image used to create your mesh.\n"
                 "You can still extract the mesh optical parameters without it by\n"
                 "resampling your VTK mesh in its own bounding box space. To do so,\n"
                 "select your image spacing (in mm) and press 'OK':")

            boolResult = PythonQt.BoolResult()
            img_spacing = qt.QInputDialog.getDouble(
                slicer.util.mainWindow(),
                "Mesh2Image", s, 1, 0, 10, 3, boolResult)
            ok = boolResult

        # put volume in background
        else:
            SetSliceViewerLayers(slicer.mrmlScene, background=input_volume, labelOpacity=0.0)

        if ok:
            # empty output list
            while len(self.OutputWidgets):
                widget = self.OutputWidgets[0]
                widget.deleteLater()
                self.OutputWidgets.remove(widget)

            # resample
            if self.Logic.resample(source_mesh, input_volume, img_spacing):
                # display outputs
                i = len(self.OutputWidgets)  # should be 0
                for name, node in self.Logic.OutputVolumes.items():
                    label = qt.QLabel(name + " volume:")
                    comboBox = slicer.qMRMLNodeComboBox()
                    comboBox.nodeTypes = (("vtkMRMLScalarVolumeNode"), "")
                    comboBox.setMRMLScene(slicer.mrmlScene)
                    comboBox.addEnabled = False
                    comboBox.renameEnabled = True
                    comboBox.setCurrentNode(node)
                    self.OutputsLayout.addRow(label, comboBox)
                    self.OutputWidgets.append(label)
                    self.OutputWidgets.append(comboBox)

                    i += 1

                centerSlices(slicer.mrmlScene)

        # update GUI
        self.ResamplePushButton.setEnabled(True)
        self.ProgressBar.setNameVisibility(False)
        return



#
# Utilities
#

def clearLayout(layout):
    if layout is not None:
        for i in reversed(range(layout.count())):
            item = layout.takeAt(i)
            widget = item.widget()
            if widget is not None:
                label = layout.labelForField(widget)
                if label is not None:
                    label.setParent(None)
                widget.setParent(None)
            else:
                clearLayout(item.layout())

def SetSliceViewerLayers(scene, label=None, labelOpacity=None, background=None,
                         foreground=None, foregroundOpacity=None):
    if isinstance(label, slicer.vtkMRMLNode):
        label = label.GetID()
    if isinstance(background, slicer.vtkMRMLNode):
        background = background.GetID()
    if isinstance(foreground, slicer.vtkMRMLNode):
        foreground = foreground.GetID()
    num = scene.GetNumberOfNodesByClass('vtkMRMLSliceCompositeNode')
    for i in range(num):
        sliceViewer = scene.GetNthNodeByClass(i, 'vtkMRMLSliceCompositeNode')
        if foreground is not None:
            sliceViewer.SetForegroundVolumeID(foreground)
        if background is not None:
            sliceViewer.SetBackgroundVolumeID(background)
        if label is not None:
            sliceViewer.SetLabelVolumeID(label)
        if foregroundOpacity is not None:
            sliceViewer.SetForegroundOpacity(foregroundOpacity)
        if labelOpacity is not None:
            sliceViewer.SetLabelOpacity(labelOpacity)

def centerSlices(scene):
    sliceViewer = scene.GetNthNodeByClass(0, 'vtkMRMLSliceCompositeNode')
    sliceViewer.LinkedControlOn()
    sliceNames = ["Red","Yellow","Green"]
    for sliceName in sliceNames:
        slicer.app.layoutManager().sliceWidget(sliceName).sliceLogic().FitSliceToAll()
