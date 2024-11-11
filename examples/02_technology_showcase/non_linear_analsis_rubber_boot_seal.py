""" .. _ref_non_linear_analysis_rubber_boot_seal:

Nonlinear Analysis of a Rubber Boot Seal Model
----------------------------------------------

This example demonstrates a nonlinear 3D analysis of a rubber boot seal to:

- Create a rigid-flexible contact pair between a rigid shaft and a
  rubber boot part.
- Specify ramped effects using the On Gauss Point Detection Method
  to update contact stiffness at each iteration.
- Specify contact pairs at the inner and outer surfaces of the rubber boot.
- Specify non-ramped effects using the Nodal-Projected Normal From Contact
  Detection Method to update contact stiffness at each iteration.
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

import os

from PIL import Image
from ansys.mechanical.core import App
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

# %%
# Embed mechanical and set global variables

app = App()
app.update_globals(globals())
print(app)

cwd = os.path.join(os.getcwd(), "out")


def display_image(image_name):
    plt.figure(figsize=(16, 9))
    plt.imshow(mpimg.imread(os.path.join(cwd, image_name)))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.show()


# %%
# Configure graphics for image export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Iso)
Graphics.Camera.SetFit()
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False

# %%
# Download geometry and materials files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

geometry_path = download_file(
    "example_05_td26_Rubber_Boot_Seal.agdb", "pymechanical", "00_basic"
)
mat_path = download_file("example_05_Boot_Mat.xml", "pymechanical", "00_basic")

# %%
# Import geometry and material
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import material

materials = Model.Materials
materials.Import(mat_path)
print("Material import done !")
# %%
# Import geometry

geometry_import = Model.GeometryImportGroup.AddGeometryImport()
geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import_preferences.ProcessCoordinateSystems = True
geometry_import.Import(
    geometry_path, geometry_import_format, geometry_import_preferences
)

app.plot()

# %%
# Setup the Analysis
# ~~~~~~~~~~~~~~~~~~
# Set up the unit system

ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM
ExtAPI.Application.ActiveAngleUnit = AngleUnitType.Radian

# %%
# Store all main tree nodes as variables

GEOM = Model.Geometry
PRT1 = [x for x in Tree.AllObjects if x.Name == "Part"][0]
PRT2 = [x for x in Tree.AllObjects if x.Name == "Solid"][1]
CS_GRP = Model.CoordinateSystems
GCS = CS_GRP.Children[0]

# %%
# Add static structural analysis

Model.AddStaticStructuralAnalysis()
STAT_STRUC = Model.Analyses[0]
ANA_SETTING = STAT_STRUC.Children[0]
STAT_STRUC_SOLN = STAT_STRUC.Solution
SOLN_INFO = STAT_STRUC_SOLN.SolutionInformation

# %%
# Define named selection and coordinate system

NS_GRP = ExtAPI.DataModel.Project.Model.NamedSelections
TOP_FACE = [
    i
    for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Top_Face"
][0]
BOTTOM_FACE = [
    i
    for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Bottom_Face"
][0]
SYMM_FACES30 = [
    i
    for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Symm_Faces30"
][0]
FACES2 = [
    i
    for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Faces2"
][0]
CYL_FACES2 = [
    i
    for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Cyl_Faces2"
][0]
RUBBER_BODIES30 = [
    i
    for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Rubber_Bodies30"
][0]
INNER_FACES30 = [
    i
    for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Inner_Faces30"
][0]
OUTER_FACES30 = [
    i
    for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Outer_Faces30"
][0]
SHAFT_FACE = [
    i
    for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Shaft_Face"
][0]
SYMM_FACES15 = [
    i
    for i in NS_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Symm_Faces15"
][0]

LCS1 = CS_GRP.AddCoordinateSystem()
LCS1.OriginY = Quantity("97[mm]")

# %%
# Assign material

PRT1.Material = "Boot"
PRT2.StiffnessBehavior = StiffnessBehavior.Rigid

# %%
# Define connections

CONN_GRP = Model.Connections
CONT_REG1 = CONN_GRP.AddContactRegion()
CONT_REG1.TargetLocation = SHAFT_FACE
CONT_REG1.SourceLocation = INNER_FACES30
CONT_REG1.ContactType = ContactType.Frictional
CONT_REG1.FrictionCoefficient = 0.2
CONT_REG1.Behavior = ContactBehavior.Asymmetric
CONT_REG1.SmallSliding = ContactSmallSlidingType.Off
CONT_REG1.DetectionMethod = ContactDetectionPoint.OnGaussPoint
CONT_REG1.UpdateStiffness = UpdateContactStiffness.EachIteration
CONT_REG1.InterfaceTreatment = ContactInitialEffect.AddOffsetRampedEffects
CONT_REG1.TargetGeometryCorrection = TargetCorrection.Smoothing
CONT_REG1.TargetOrientation = TargetOrientation.Cylinder
CONT_REG1.TargetStartingPoint = GCS
CONT_REG1.TargetEndingPoint = LCS1

CONTS = CONN_GRP.Children[0]
CONT_REG2 = CONTS.AddContactRegion()
CONT_REG2.SourceLocation = INNER_FACES30
CONT_REG2.TargetLocation = INNER_FACES30
CONT_REG2.ContactType = ContactType.Frictional
CONT_REG2.FrictionCoefficient = 0.2
CONT_REG2.Behavior = ContactBehavior.Asymmetric
CONT_REG2.SmallSliding = ContactSmallSlidingType.Off
CONT_REG2.DetectionMethod = ContactDetectionPoint.NodalProjectedNormalFromContact
CONT_REG2.UpdateStiffness = UpdateContactStiffness.EachIteration
CONT_REG2.NormalStiffnessValueType = ElementControlsNormalStiffnessType.Factor
CONT_REG2.NormalStiffnessFactor = 1

CONT_REG3 = CONTS.AddContactRegion()
CONT_REG3.SourceLocation = OUTER_FACES30
CONT_REG3.TargetLocation = OUTER_FACES30
CONT_REG3.ContactType = ContactType.Frictional
CONT_REG3.FrictionCoefficient = 0.2
CONT_REG3.Behavior = ContactBehavior.Asymmetric
CONT_REG3.SmallSliding = ContactSmallSlidingType.Off
CONT_REG3.DetectionMethod = ContactDetectionPoint.NodalProjectedNormalFromContact
CONT_REG3.UpdateStiffness = UpdateContactStiffness.EachIteration
CONT_REG3.NormalStiffnessValueType = ElementControlsNormalStiffnessType.Factor
CONT_REG3.NormalStiffnessFactor = 1

# %%
# Mesh
# ~~~~

MSH = Model.Mesh
FACE_MSH = MSH.AddFaceMeshing()
FACE_MSH.Location = SHAFT_FACE
FACE_MSH.InternalNumberOfDivisions = 1

MSH_SIZE = MSH.AddSizing()
MSH_SIZE.Location = SYMM_FACES15
MSH_SIZE.ElementSize = Quantity("2 [mm]")

MSH.ElementOrder = ElementOrder.Linear
MSH.Resolution = 2

MSH.GenerateMesh()

Graphics.ExportImage(os.path.join(cwd, "mesh.png"), image_export_format, settings_720p)
display_image("mesh.png")

# %%
# Define remote points
# ~~~~~~~~~~~~~~~~~~~~
# scope them to the top and bottom faces of rigid shaft

RMPT01 = Model.AddRemotePoint()
RMPT01.Location = BOTTOM_FACE
RMPT01.Behavior = LoadBehavior.Rigid

RMPT02 = Model.AddRemotePoint()
RMPT02.Location = TOP_FACE
RMPT02.Behavior = LoadBehavior.Rigid

# %%
# Analysis settings
# ~~~~~~~~~~~~~~~~~

ANA_SETTING.Activate()
ANA_SETTING.LargeDeflection = True
ANA_SETTING.Stabilization = StabilizationType.Off

ANA_SETTING.NumberOfSteps = 2
ANA_SETTING.CurrentStepNumber = 1
ANA_SETTING.AutomaticTimeStepping = AutomaticTimeStepping.On
ANA_SETTING.DefineBy = TimeStepDefineByType.Substeps
ANA_SETTING.InitialSubsteps = 5
ANA_SETTING.MinimumSubsteps = 5
ANA_SETTING.MaximumSubsteps = 1000
ANA_SETTING.StoreResultsAt = TimePointsOptions.EquallySpacedPoints
ANA_SETTING.StoreResulsAtValue = 5

ANA_SETTING.CurrentStepNumber = 2
ANA_SETTING.AutomaticTimeStepping = AutomaticTimeStepping.On
ANA_SETTING.DefineBy = TimeStepDefineByType.Substeps
ANA_SETTING.InitialSubsteps = 10
ANA_SETTING.MinimumSubsteps = 10
ANA_SETTING.MaximumSubsteps = 1000
ANA_SETTING.StoreResultsAt = TimePointsOptions.EquallySpacedPoints
ANA_SETTING.StoreResulsAtValue = 10

ANA_SETTING.CurrentStepNumber = 3
ANA_SETTING.AutomaticTimeStepping = AutomaticTimeStepping.On
ANA_SETTING.DefineBy = TimeStepDefineByType.Substeps
ANA_SETTING.InitialSubsteps = 30
ANA_SETTING.MinimumSubsteps = 30
ANA_SETTING.MaximumSubsteps = 1000
ANA_SETTING.StoreResultsAt = TimePointsOptions.EquallySpacedPoints
ANA_SETTING.StoreResulsAtValue = 20

SOLN_INFO.NewtonRaphsonResiduals = 4

# %%
# Loads and boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

REM_DISP = STAT_STRUC.AddRemoteDisplacement()
REM_DISP.Location = RMPT01
REM_DISP.XComponent.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
    Quantity("3 [s]"),
]
REM_DISP.XComponent.Output.DiscreteValues = [
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
]
REM_DISP.YComponent.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
    Quantity("3 [s]"),
]
REM_DISP.YComponent.Output.DiscreteValues = [
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
    Quantity("-10 [mm]"),
    Quantity("-10 [mm]"),
]
REM_DISP.ZComponent.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
    Quantity("3 [s]"),
]
REM_DISP.ZComponent.Output.DiscreteValues = [
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
]

REM_DISP.RotationX.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
    Quantity("3 [s]"),
]
REM_DISP.RotationX.Output.DiscreteValues = [
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
]
REM_DISP.RotationY.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
    Quantity("3 [s]"),
]
REM_DISP.RotationY.Output.DiscreteValues = [
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
]
REM_DISP.RotationZ.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
    Quantity("3 [s]"),
]
REM_DISP.RotationZ.Output.DiscreteValues = [
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
    Quantity("0.55 [rad]"),
]

FRIC_SUP01 = STAT_STRUC.AddFrictionlessSupport()
FRIC_SUP01.Location = SYMM_FACES30
FRIC_SUP01.Name = "Symmetry_BC"
FRIC_SUP02 = STAT_STRUC.AddFrictionlessSupport()
FRIC_SUP02.Location = FACES2
FRIC_SUP02.Name = "Boot_Bottom_BC"
FRIC_SUP03 = STAT_STRUC.AddFrictionlessSupport()
FRIC_SUP03.Location = CYL_FACES2
FRIC_SUP03.Name = "Boot_Radial_BC"

# %%
# Add results
# ~~~~~~~~~~~

TOT_DEF = STAT_STRUC.Solution.AddTotalDeformation()
TOT_DEF.Location = RUBBER_BODIES30

EQV_STRS = STAT_STRUC.Solution.AddEquivalentStress()
EQV_STRS.Location = RUBBER_BODIES30

# %%
# Solve
# ~~~~~

STAT_STRUC.Solution.Solve(True)

# sphinx_gallery_start_ignore
assert str(STAT_STRUC_SOLN.Status) == "Done", "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# Postprocessing
# ~~~~~~~~~~~~~~
# Total deformation


Tree.Activate([TOT_DEF])
Graphics.ExportImage(
    os.path.join(cwd, "totaldeformation.png"), image_export_format, settings_720p
)
display_image("totaldeformation.png")

# %%
# Equivalent stress

Tree.Activate([EQV_STRS])
Graphics.ExportImage(
    os.path.join(cwd, "equivalent_stress.png"), image_export_format, settings_720p
)
display_image("equivalent_stress.png")

# %%
# Total deformation animation

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

TOT_DEF.ExportAnimation(
    os.path.join(cwd, "totaldeformation.gif"), animation_export_format, settings_720p
)
gif = Image.open(os.path.join(cwd, "totaldeformation.gif"))
fig, ax = plt.subplots(figsize=(16, 9))
ax.axis("off")
img = ax.imshow(gif.convert("RGBA"))


def update(frame):
    gif.seek(frame)
    img.set_array(gif.convert("RGBA"))
    return [img]


ani = FuncAnimation(
    fig, update, frames=range(gif.n_frames), interval=200, repeat=True, blit=True
)
plt.show()


# %%
# Cleanup
# ~~~~~~~
# Save project

app.save(os.path.join(cwd, "non-linear-rubber-boot-seal.mechdat"))
app.new()

# delete example file
delete_downloads()
