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
&nbsp; 4. Use the <a href="#"><b>Segment Editor</b></a> module to segment the tissue into different tissue types which can guide the optical image reconstruction routines<br><br>
&nbsp; 5. Use the <a href="#"><b>Markups</b></a> module to place optical source and detector positions.<br><br>
&nbsp; 6. Use the <a href="#"><b>Create Mesh</b></a> module to generate a NIRFAST-compatible mesh from the segmented tissue (label maps)<br><br>
&nbsp; 7. After creating the mesh, follow tutorials on reconstructing optical images in the NIRFAST Matlab window<br><br>
&nbsp; 8. Once optical properties have been reconstructed, open the resulting volumetric mesh in NIRFAST-Slicer and use the <a href="#"><b>Models</b></a> module to visualize the data overlaid on the original DICOM: in the Display menu, check 'Slice Intersections Visible' from the Visibility submenu, and select the parameters to display in the Scalars submenu.<br>
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
        elif pos >= 645 and pos <= 653 :
            slicer.util.selectModule(slicer.moduleNames.Markups)
        elif pos >= 722 and pos <= 734 :
            slicer.util.selectModule(slicer.moduleNames.CreateMesh)
        elif pos >= 1047 and pos <= 1053 :
             slicer.util.selectModule(slicer.moduleNames.Models)
