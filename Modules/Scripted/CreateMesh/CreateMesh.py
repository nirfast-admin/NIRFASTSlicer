import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

userSettings = slicer.app.userSettings()

class CreateMesh(ScriptedLoadableModule):
  '''Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  '''

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = 'Create Mesh'
    self.parent.categories = ['NIRFAST']
    self.parent.dependencies = ['Image2Mesh', 'Segmentations']
    self.parent.contributors = ['Alexis Girault (Kitware Inc.)']
    self.parent.helpText = '''
Create Mesh first creates a tetrahedral mesh using an Input Segmentation node.
It then launches a Matlab GUI allowing the user to generate the locations of the light Sources and Detectors, based on the initial positions of the Sources/Detectors fiducials input.
The output mesh files are written in Output Mesh Directory with the prefix Output Mesh Name.
They are computed using the parameters set in the Mesh Parameters section.
'''
    self.parent.acknowledgementText = '''
This work is part of the NIRFASTSlicer application developed at Kitware, Inc. to allow the use of the NIRFASTMatlab application developped by Dartmouth University and the University of Birmingham, funded by the National Institutes of Health, Grant R01 CA184354
'''


class CreateMeshWidget(ScriptedLoadableModuleWidget):
  '''Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  '''

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    self.logic = CreateMeshLogic()

    # Inputs
    inputsCollapsibleButton = ctk.ctkCollapsibleButton()
    inputsCollapsibleButton.text = 'Inputs'
    self.layout.addWidget(inputsCollapsibleButton)
    inputsFormLayout = qt.QFormLayout(inputsCollapsibleButton)

    # Segmentation selector
    self.segmentationSelector = slicer.qMRMLNodeComboBox()
    self.segmentationSelector.nodeTypes = ['vtkMRMLSegmentationNode']
    self.segmentationSelector.addEnabled = False
    self.segmentationSelector.removeEnabled = False
    self.segmentationSelector.renameEnabled = False
    self.segmentationSelector.setMRMLScene( slicer.mrmlScene )
    self.segmentationSelector.setToolTip( 'Pick the segmentation to compute a mesh from' )
    inputsFormLayout.addRow('Segmentation:', self.segmentationSelector)
    # Fiducials selector
    self.fiducialsSelector = slicer.qMRMLNodeComboBox()
    self.fiducialsSelector.nodeTypes = ['vtkMRMLMarkupsFiducialNode']
    self.fiducialsSelector.addEnabled = False
    self.fiducialsSelector.removeEnabled = False
    self.fiducialsSelector.renameEnabled = False
    self.fiducialsSelector.setMRMLScene( slicer.mrmlScene )
    self.fiducialsSelector.setToolTip( 'Select the fiducials that will define the light sources and detectors position')
    inputsFormLayout.addRow('Fiducials:', self.fiducialsSelector)

    # Outputs
    outputsCollapsibleButton = ctk.ctkCollapsibleButton()
    outputsCollapsibleButton.text = 'Outputs'
    self.layout.addWidget(outputsCollapsibleButton)
    outputsFormLayout = qt.QFormLayout(outputsCollapsibleButton)

    # Mesh directory
    self.meshPathLineEdit = ctk.ctkPathLineEdit()
    self.meshPathLineEdit.filters = ctk.ctkPathLineEdit.Dirs
    self.meshPathLineEdit.currentPath = self.cachedPathFor('CreateMeshOutputPath')
    outputsFormLayout.addRow('Mesh directory:', self.meshPathLineEdit)
    # Mesh name
    self.meshNameField = qt.QLineEdit()
    outputsFormLayout.addRow('Mesh name:', self.meshNameField)

    # Meshing
    meshingCollapsibleButton = ctk.ctkCollapsibleButton()
    meshingCollapsibleButton.text = 'Meshing'
    self.layout.addWidget(meshingCollapsibleButton)
    meshingFormLayout = qt.QFormLayout(meshingCollapsibleButton)

    # Mesh type
    self.meshTypeComboBox = ctk.ctkComboBox()
    for meshType in self.logic.meshTypes:
      self.meshTypeComboBox.addItem(meshType)
    meshingFormLayout.addRow('Mesh type:', self.meshTypeComboBox)
    # Cell size
    self.cellSizeSpinBox = slicer.qMRMLSpinBox()
    self.cellSizeSpinBox.setValue(1.5)
    self.cellSizeSpinBox.setMRMLScene( slicer.mrmlScene )
    meshingFormLayout.addRow('Cell size:', self.cellSizeSpinBox)
    # Cell radius edge
    self.cellRadiusSpinBox = slicer.qMRMLSpinBox()
    self.cellRadiusSpinBox.setValue(3.0)
    self.cellRadiusSpinBox.setMRMLScene( slicer.mrmlScene )
    meshingFormLayout.addRow('Cell radius edge:', self.cellRadiusSpinBox)
    # Facet size
    self.facetSizeSpinBox = slicer.qMRMLSpinBox()
    self.facetSizeSpinBox.setValue(1.5)
    self.facetSizeSpinBox.setMRMLScene( slicer.mrmlScene )
    meshingFormLayout.addRow('Facet size:', self.facetSizeSpinBox)
    # Facet angle
    self.facetAngleSpinBox = slicer.qMRMLSpinBox()
    self.facetAngleSpinBox.setValue(25.0)
    self.facetAngleSpinBox.setMRMLScene( slicer.mrmlScene )
    meshingFormLayout.addRow('Facet angle:', self.facetAngleSpinBox)
    # Facet distance
    self.facetDistanceSpinBox = slicer.qMRMLSpinBox()
    self.facetDistanceSpinBox.setValue(3.0)
    self.facetDistanceSpinBox.setMRMLScene( slicer.mrmlScene )
    meshingFormLayout.addRow('Facet distance:', self.facetDistanceSpinBox)
    # Optimize mesh
    self.optimizeCheckBox = qt.QCheckBox()
    meshingFormLayout.addRow('Optimize mesh:', self.optimizeCheckBox)

    # NIRFAST
    nirfastCollapsibleButton = ctk.ctkCollapsibleButton()
    nirfastCollapsibleButton.text = 'NIRFAST Matlab'
    self.layout.addWidget(nirfastCollapsibleButton)
    nirfastFormLayout = qt.QFormLayout(nirfastCollapsibleButton)

    # NIRFAST-Matlab
    self.nirfastMatlabPathLineEdit = ctk.ctkPathLineEdit()
    self.nirfastMatlabPathLineEdit.filters = ctk.ctkPathLineEdit.Dirs
    self.nirfastMatlabPathLineEdit.currentPath = self.cachedPathFor('NIRFASTMatlabPath')
    nirfastFormLayout.addRow('NIRFAST Matlab:', self.nirfastMatlabPathLineEdit)

    # Run
    self.runButton = qt.QPushButton()
    self.runButton.setCheckable(True);
    self.setRunning(False)
    self.layout.addWidget(self.runButton)

    # Progress
    self.progressBar = slicer.qSlicerCLIProgressBar()
    self.logic.setProgressBar(self.progressBar);
    self.layout.addWidget(self.progressBar)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Connections
    self.segmentationSelector.connect(
      'currentNodeChanged(vtkMRMLNode*)',
      self.onSegmentationNodeChanged
    )
    self.onSegmentationNodeChanged(self.segmentationSelector.currentNode())
    self.meshPathLineEdit.connect(
      'currentPathChanged(QString)',
      self.logic.cacheOutputMeshDir
    )
    self.nirfastMatlabPathLineEdit.connect(
      'currentPathChanged(QString)',
      self.logic.cacheNirfastMatlabDir
    )
    self.runButton.connect(
      'clicked()',
      self.onRun
    )
    self.logic.setBusy = self.setRunning
    self.logic.setError = self.showError

  def cachedPathFor(self, key):
    value = userSettings.value(key)
    if value is None:
      return userSettings.value('DefaultScenePath')
    else:
      return value

  def setRunning(self, running):
    title = 'Run'
    if running:
      title = 'Cancel'
    self.runButton.setText(title)
    self.runButton.setChecked(running)
    self.running = running
    slicer.app.processEvents()

  def showError(self, errorMessage):
    self.setRunning(False)
    qt.QMessageBox.critical(
      slicer.util.mainWindow(),
      'Create Mesh Error',
      errorMessage
    )

  def onSegmentationNodeChanged(self, node):
    if node is None:
      self.meshNameField.setText("nirfast_mesh")
    else:
      self.meshNameField.setText(node.GetName())

  def onRun(self):
    if not self.running:
      self.setRunning(True)

      self.logic.setParameters(
        self.segmentationSelector.currentNode(),
        self.fiducialsSelector.currentNode(),
        self.meshPathLineEdit.currentPath,
        self.meshNameField.text,
        self.meshTypeComboBox.currentIndex,
        self.cellSizeSpinBox.value,
        self.cellRadiusSpinBox.value,
        self.facetSizeSpinBox.value,
        self.facetAngleSpinBox.value,
        self.facetDistanceSpinBox.value,
        self.optimizeCheckBox.checked,
        self.nirfastMatlabPathLineEdit.currentPath
      )
      self.logic.run()
    else:
      self.logic.cancel()


class CreateMeshLogic(ScriptedLoadableModuleLogic):
  '''Implement the logic to calculate label statistics.
  Nodes are passed in as arguments.
  Results are stored as 'statistics' instance variable.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  '''

  def __init__(self):
    # Segmentation module (Loadable) to export segmentation to label map
    self.segmentationModuleLogic = slicer.modules.segmentations.logic()
    self.segmentationNode = None
    self.labelMapNode = slicer.vtkMRMLLabelMapVolumeNode()
    self.labelMapNode.SetHideFromEditors(1)
    slicer.mrmlScene.AddNode(self.labelMapNode)

    # Matlab module (CLI) to create a mesh from the label map
    self.image2MeshModule = slicer.modules.image2mesh
    self.image2MeshCLINode = slicer.cli.createNode(self.image2MeshModule)
    self.image2MeshCLINode.AddObserver(
      self.image2MeshCLINode.StatusModifiedEvent,
      self.onImage2MeshModified
    )
    self.image2MeshParameters = {}

    self.meshTypes = [
      'Standard',
      'Fluorescence',
      'Spectral',
      'BEM',
      'BEM Fluorescence',
      'BEM Spectral',
      'SPN'
    ]

  def setProgressBar(self, progressBar):
    self.progressBar = progressBar
    self.progressBar.setCommandLineModuleNode(self.image2MeshCLINode)

  def cacheOutputMeshDir(self, path):
    userSettings.setValue('CreateMeshOutputPath', path)

  def cacheNirfastMatlabDir(self, path):
    userSettings.setValue('NIRFASTMatlabPath', path)

  def setParameters(self, segmentationNode, fiducialsNode, meshDir, meshName, meshTypeId, cellSize, cellRadius, facetSize, facetAngle, facetDistance, optimize, nirfastDir):
    self.segmentationNode = segmentationNode
    self.image2MeshParameters['fiducials'] = fiducialsNode
    self.image2MeshParameters['meshdir'] = meshDir
    self.image2MeshParameters['meshname'] = meshName
    self.image2MeshParameters['meshtype'] = self.meshTypes[meshTypeId]
    self.image2MeshParameters['cell_size'] = cellSize
    self.image2MeshParameters['cellradiusedge'] = cellRadius
    self.image2MeshParameters['facet_size'] = facetSize
    self.image2MeshParameters['facetangle'] = facetAngle
    self.image2MeshParameters['facetdistance'] = facetDistance
    self.image2MeshParameters['optimizemesh'] = optimize
    self.image2MeshParameters['nirfastDir'] = nirfastDir

  def cancel(self):
    self.image2MeshCLINode.Cancel()

  def runSegmentToImage(self):
    self.segmentationModuleLogic.ExportAllSegmentsToLabelmapNode(
      self.segmentationNode,
      self.labelMapNode
    )
    self.image2MeshParameters['labelmap'] = self.labelMapNode

  def runImageToMesh(self):
    slicer.cli.run(
      self.image2MeshModule,
      self.image2MeshCLINode,
      self.image2MeshParameters,
      False # do not wait for completion
    )

  def onImage2MeshModified(self, cliNode, event):
    self.setBusy(cliNode.IsBusy())

  def run(self):
    if self.segmentationNode is None:
      self.setError('I/O Error: invalid segmentation node')
      return;
    if self.image2MeshParameters['fiducials'] is None:
      self.setError('I/O Error: invalid fiducials node')
      return;

    self.runSegmentToImage()
    self.runImageToMesh()
