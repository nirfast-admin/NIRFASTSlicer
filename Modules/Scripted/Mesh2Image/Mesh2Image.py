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
import vtk, qt, ctk, slicer
import os
import sys


# ICON_DIR = os.path.dirname(os.path.realpath(__file__)) + '/Resources/Icons/'

#
# Mesh2Image
#

class Mesh2Image:
    def __init__(self, parent):
        parent.title = "Mesh2Image"
        parent.categories = ["NIRFAST"]
        parent.dependencies = []
        parent.contributors = ["Alexis Girault (Kitware)"]
        parent.helpText = """
        """
        parent.acknowledgementText = """
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

    def resample(self, volumeNode, sourceMeshPath):

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

        # Read volumeNode
        if volumeNode is None:
            print >> sys.stderr, "Mesh2Image : Reading input volume failed"
            self.Node.SetStatus(self.Node.CompletedWithErrors)
            return 0

        # Get input image data from volumeNode
        print "-- Setting imageData space information using volume information"
        inputImageData = volumeNode.GetImageData()
        inputImageData.SetOrigin(volumeNode.GetOrigin())
        inputImageData.SetSpacing(volumeNode.GetSpacing())

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

        # Remove useless array
        print "-- Removing unneeded arrays"
        removeArrayFilter = vtk.vtkPassArrays()
        removeArrayFilter.SetInputData(outputImageData)
        removeArrayFilter.RemoveArraysOn()
        removeArrayFilter.AddPointDataArray("vtkValidPointMask")
        removeArrayFilter.AddPointDataArray("ImageScalars")
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
            outputNode.Copy(volumeNode)
            outputNode.SetName(outputNode.GetName() + "_" + arrayName)
            outputNode.SetAndObserveStorageNodeID(None)
            outputNode.SetAndObserveDisplayNodeID(None)
            outputNode.SetImageDataConnection(passArrayFilter.GetOutputPort())
            slicer.mrmlScene.AddNode(outputNode)
            outputNode.SetAndObserveStorageNodeID(None)

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
        label = qt.QLabel("Cropped Volume: ")
        self.InputVolumeComboBox = slicer.qMRMLNodeComboBox()
        self.InputVolumeComboBox.nodeTypes = (("vtkMRMLVolumeNode"), "")
        self.InputVolumeComboBox.setMRMLScene(slicer.mrmlScene)
        self.InputVolumeComboBox.addEnabled = False
        self.InputVolumeComboBox.renameEnabled = True
        self.InputVolumeComboBox.toolTip = 'Cropped Volume defining the ROI to resample the point data of the input mesh.'
        self.InputsLayout.addWidget(label, 0, 0)
        self.InputsLayout.addWidget(self.InputVolumeComboBox, 0, 1)

        label = qt.QLabel("VTK Dataset: ")
        self.SourceMeshPathLine = ctk.ctkPathLineEdit()
        self.SourceMeshPathLine.toolTip = 'VTK unstructured grid mesh'
        self.InputsLayout.addWidget(label, 1, 0)
        self.InputsLayout.addWidget(self.SourceMeshPathLine, 1, 1)

        self.ResamplePushButton = qt.QPushButton("Resample Dataset")
        self.ResamplePushButton.toolTip = "Resample Dataset"
        self.ResamplePushButton.connect('clicked()', self.onResamplePressed)
        self.InputsLayout.addWidget(self.ResamplePushButton, 2, 1)

        self.OutputWidgets = []

    def onResamplePressed(self):

        self.ResamplePushButton.setEnabled(False)
        self.ProgressBar.setNameVisibility(True)

        input_volume = self.InputVolumeComboBox.currentNode()
        source_mesh = self.SourceMeshPathLine.currentPath

        # no good inputs
        if (input_volume is None) or (source_mesh is None):
            print >> sys.stderr, "Mesh2Image : Input missing"
            qt.QMessageBox.critical(
                slicer.util.mainWindow(),
                "Mesh2Image", "Input missing")


        else:

            # empty output list
            while len(self.OutputWidgets):
                widget = self.OutputWidgets[0]
                widget.deleteLater()
                self.OutputWidgets.remove(widget)

            # resample
            if self.Logic.resample(input_volume, source_mesh):
                # display outputs
                i = len(self.OutputWidgets) # should be 0
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

                    node.SetAndObserveDisplayNodeID(None)

                    i += 1

        self.ResamplePushButton.setEnabled(True)
        self.ProgressBar.setNameVisibility(False)
        return


    def clearLayout(self, layout):
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
                    self.clearLayout(item.layout())
