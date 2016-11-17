import vtk, qt, ctk, slicer, PythonQt


# ICON_DIR = os.path.dirname(os.path.realpath(__file__)) + '/Resources/Icons/'

#
# Home
#

class Home:
    def __init__(self, parent):
        parent.title = "Home"
        parent.categories = ["NIRFAST"]
        parent.dependencies = []
        parent.contributors = ["Scott Davis (Darmouth College), Hamid Dehghani (University of Birmingham), Alexis Girault (Kitware Inc). "
                               "See <a href=\"http://www.nirfast.org/people.php\">here</a> for a list of current and former developers and contributors."]
        parent.helpText = """<center>
        <br>
        <b>Welcome to NIRFAST!</b><br>
        <br>
        Visit <a href="http://www.nirfast.org">nirfast.org</a> for more information about NIRFAST.<br>
        <br>
        Documentation and tutorials can be found at: <a href="http://www.dartmouth.edu/~nir/nirfast/documentation.php">nirfast.org/documentation</a><br>
        </center>
        """
        parent.acknowledgementText = """
        NIRFAST is an open source software package for multi-modal optical imaging in living tissue.  Originally developed at Dartmouth College in 2001, ongoing development, maintenance, distribution, and training is managed by Dartmouth College, University of Birmingham, and Kitware Inc.  The project is supported by NCI R01CA184354 (Davis, SC).
        """

        # parent.icon = qt.QIcon("%s/cranioIcon.png" % ICON_DIR)

        self.parent = parent


#
# qHomeWidget
#

class HomeWidget:
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

    def setup(self):

        # TEXT
        text = """
<br>
<u>Workflow quick-reference:</u><br>
<br>
The drop-down Modules are ordered to follow the basic workflow for processing DICOMS from conventional imaging modalities which are then used in optical image reconstruction.  As a quick reference, the basic steps involve:<br>
<br>
&nbsp; 1. Use the <a href="#"><b>DICOM</b></a> module to load your MRI/CT/US DICOMS<br><br>
&nbsp; 2. Use <a href="#"><b>Volume Rendering</b></a> to view a 3D rendering of your DICOM images<br><br>
&nbsp; 3. <a href="#"><b>Crop</b></a> the image volume to the tissue region of interest for which you will reconstruct optical images.<br><br>
&nbsp; 4. Use the <a href="#"><b>Segment Editor (segment tissue)</b></a> module to segment the tissue into different tissue types which can guide the optical image reconstruction routines<br><br>
&nbsp; 5. Use the <a href="#"><b>Segmentations</b></a> module to export the tissue segmentation into a label map<br><br>
&nbsp; 6. Use the <a href="#"><b>Markups</b></a> module to place optical source and detector positions.<br><br>
&nbsp; 7. Use the <a href="#"><b>Create Mesh</b></a> module to generate a NIRFAST-compatible mesh from the segmented tissue (label maps)<br><br>
&nbsp; 8. After creating the mesh, follow tutorials on reconstructing optical images in the NIRFAST Matlab window<br><br>
&nbsp; 9. Once images have been reconstructed use the <a href="#"><b>Import Optical Properties</b></a> module to view the optical parameter images overlaid on the original DICOMS<br>
"""

        # TEXTEDIT
        self.HomeTextSection = qt.QTextEdit()
        self.HomeTextSection.setReadOnly(True)
        self.HomeTextSection.setText(text)
        self.HomeTextSection.setMinimumHeight(400)
        self.HomeTextSection.connect('cursorPositionChanged()', self.slot)
        self.layout.addWidget(self.HomeTextSection)

        # SPACER
        self.layout.addStretch()

    def slot(self):
        pos = self.HomeTextSection.textCursor().position()

        if pos >= 264 and pos <= 270 :
            slicer.util.selectModule(slicer.moduleNames.DICOM)
        elif pos >= 317 and pos <= 334 :
            slicer.util.selectModule(slicer.moduleNames.VolumeRendering)
        elif pos >= 384 and pos <= 389 :
            slicer.util.selectModule(slicer.moduleNames.CropVolume)
        elif pos >= 499 and pos <= 533 :
            slicer.util.selectModule(slicer.moduleNames.SegmentEditor)
        elif pos >= 662 and pos <= 676 :
            slicer.util.selectModule(slicer.moduleNames.Segmentations)
        elif pos >= 748 and pos <= 756 :
            slicer.util.selectModule(slicer.moduleNames.Markups)
        elif pos >= 825 and pos <= 837 :
            slicer.util.selectModule(slicer.moduleNames.Image2Mesh)
	elif pos >= 1081 and pos <= 1107 :
             slicer.util.selectModule(slicer.moduleNames.Mesh2Image)
