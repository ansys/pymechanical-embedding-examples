""".. _ref_contact_wear_simulation:

Contact Surface Wear Simulation
-------------------------------

Using a Archard wear model, this example demonstrates contact sliding
of a hemispherical ring on a flat ring to produce wear.

The model includes:

- Hemispherical ring with a radius of 30 mm made of copper.
- Flat ring with an inner radius of 50 mm and an outer radius of 150 mm made of steel.

The hemispherical ring is in contact with the flat ring at the center
from the axis of rotation at 100 mm and is subjected to a
1) pressure of 4000 N/mm2 and 2) a rotation with a frequency
of 100,000 revolutions/sec.

The application evaluates total deformation and normal stress results,
in loading direction, prior to and following wear. In addition,
contact pressure prior to wear is evaluated.
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

app = App(globals=globals())
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

Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Front)
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False
Graphics.Camera.Rotate(180, CameraAxisType.ScreenY)

# %%
# Download geometry and materials files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

geometry_path = download_file("example_07_td43_wear.agdb", "pymechanical", "00_basic")
mat1_path = download_file("example_07_Mat_Copper.xml", "pymechanical", "00_basic")
mat2_path = download_file("example_07_Mat_Steel.xml", "pymechanical", "00_basic")

# %%
# Import geometry
# ~~~~~~~~~~~~~~~

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
# Import materials
# ~~~~~~~~~~~~~~~~

MAT = Model.Materials
MAT.Import(mat1_path)
MAT.Import(mat2_path)

print("Material import done !")

# %%
# Setup the Analysis
# ~~~~~~~~~~~~~~~~~~
# Set up the unit system

ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM

# %%
# Store all main tree nodes as variables

MODEL = Model
GEOM = Model.Geometry
CS_GRP = Model.CoordinateSystems
CONN_GRP = Model.Connections
MSH = Model.Mesh
NS_GRP = Model.NamedSelections

# %%
# Add static structural analysis

Model.AddStaticStructuralAnalysis()
STAT_STRUC = Model.Analyses[0]
STAT_STRUC_SOLN = STAT_STRUC.Solution
STAT_STRUC_ANA_SETTING = STAT_STRUC.Children[0]

# %%
# Store name selection

CURVE_NS = [x for x in Tree.AllObjects if x.Name == "curve"][0]
DIA_NS = [x for x in Tree.AllObjects if x.Name == "dia"][0]
VER_EDGE1 = [x for x in Tree.AllObjects if x.Name == "v1"][0]
VER_EDGE2 = [x for x in Tree.AllObjects if x.Name == "v2"][0]
HOR_EDGE1 = [x for x in Tree.AllObjects if x.Name == "h1"][0]
HOR_EDGE2 = [x for x in Tree.AllObjects if x.Name == "h2"][0]
ALL_BODIES_NS = [x for x in Tree.AllObjects if x.Name == "all_bodies"][0]

# %%
# Assign material to bodies and change behavior to axisymmetric

GEOM.Model2DBehavior = Model2DBehavior.AxiSymmetric

SURFACE1 = GEOM.Children[0].Children[0]
SURFACE1.Material = "Steel"
SURFACE1.Dimension = ShellBodyDimension.Two_D

SURFACE2 = GEOM.Children[1].Children[0]
SURFACE2.Material = "Copper"
SURFACE2.Dimension = ShellBodyDimension.Two_D

# %%
# Change contact settings

CONT_REG = CONN_GRP.AddContactRegion()
CONT_REG.SourceLocation = NS_GRP.Children[6]
CONT_REG.TargetLocation = NS_GRP.Children[3]
# CONT_REG.FlipContactTarget()
CONT_REG.ContactType = ContactType.Frictionless
CONT_REG.Behavior = ContactBehavior.Asymmetric
CONT_REG.ContactFormulation = ContactFormulation.AugmentedLagrange
CONT_REG.DetectionMethod = ContactDetectionPoint.NodalNormalToTarget

# %%
# Add a command snippet to use Archard Wear Model

AWM = """keyo,cid,5,1
keyo,cid,10,2
pi=acos(-1)
slide_velocity=1e5
Uring_offset=100
kcopper=10e-13*slide_velocity*2*pi*Uring_offset
TB,WEAR,cid,,,ARCD
TBFIELD,TIME,0
TBDATA,1,0,1,1,0,0
TBFIELD,TIME,1
TBDATA,1,0,1,1,0,0
TBFIELD,TIME,1.01
TBDATA,1,kcopper,1,1,0,0
TBFIELD,TIME,4
TBDATA,1,kcopper,1,1,0,0"""
CMD1 = CONT_REG.AddCommandSnippet()
CMD1.AppendText(AWM)

# %%
# Insert remote point

REM_PT = MODEL.AddRemotePoint()
REM_PT.Location = DIA_NS
REM_PT.Behavior = LoadBehavior.Rigid

# %%
# Mesh
# ~~~~

MSH.ElementOrder = ElementOrder.Linear
MSH.ElementSize = Quantity("1 [mm]")

EDGE_SIZING1 = MSH.AddSizing()
EDGE_SIZING1.Location = HOR_EDGE1
EDGE_SIZING1.Type = SizingType.NumberOfDivisions
EDGE_SIZING1.NumberOfDivisions = 70

EDGE_SIZING2 = MSH.AddSizing()
EDGE_SIZING2.Location = HOR_EDGE2
EDGE_SIZING2.Type = SizingType.NumberOfDivisions
EDGE_SIZING2.NumberOfDivisions = 70

EDGE_SIZING3 = MSH.AddSizing()
EDGE_SIZING3.Location = VER_EDGE1
EDGE_SIZING3.Type = SizingType.NumberOfDivisions
EDGE_SIZING3.NumberOfDivisions = 35

EDGE_SIZING4 = MSH.AddSizing()
EDGE_SIZING4.Location = VER_EDGE2
EDGE_SIZING4.Type = SizingType.NumberOfDivisions
EDGE_SIZING4.NumberOfDivisions = 35

EDGE_SIZING5 = MSH.AddSizing()
EDGE_SIZING5.Location = DIA_NS
EDGE_SIZING5.Type = SizingType.NumberOfDivisions
EDGE_SIZING5.NumberOfDivisions = 40

EDGE_SIZING6 = MSH.AddSizing()
EDGE_SIZING6.Location = CURVE_NS
EDGE_SIZING6.Type = SizingType.NumberOfDivisions
EDGE_SIZING6.NumberOfDivisions = 60

MSH.GenerateMesh()

Graphics.Camera.SetFit()
Graphics.ExportImage(os.path.join(cwd, "mesh.png"), image_export_format, settings_720p)
display_image("mesh.png")

# %%
# Analysis settings
# ~~~~~~~~~~~~~~~~~

STAT_STRUC_ANA_SETTING.NumberOfSteps = 2
STAT_STRUC_ANA_SETTING.CurrentStepNumber = 1
STAT_STRUC_ANA_SETTING.AutomaticTimeStepping = AutomaticTimeStepping.On
STAT_STRUC_ANA_SETTING.DefineBy = TimeStepDefineByType.Time
STAT_STRUC_ANA_SETTING.InitialTimeStep = Quantity("0.1 [s]")
STAT_STRUC_ANA_SETTING.MinimumTimeStep = Quantity("0.0001 [s]")
STAT_STRUC_ANA_SETTING.MaximumTimeStep = Quantity("1 [s]")
STAT_STRUC_ANA_SETTING.CurrentStepNumber = 2
STAT_STRUC_ANA_SETTING.Activate()
STAT_STRUC_ANA_SETTING.StepEndTime = Quantity("4 [s]")
STAT_STRUC_ANA_SETTING.AutomaticTimeStepping = AutomaticTimeStepping.On
STAT_STRUC_ANA_SETTING.DefineBy = TimeStepDefineByType.Time
STAT_STRUC_ANA_SETTING.InitialTimeStep = Quantity("0.01 [s]")
STAT_STRUC_ANA_SETTING.MinimumTimeStep = Quantity("0.000001 [s]")
STAT_STRUC_ANA_SETTING.MaximumTimeStep = Quantity("0.02 [s]")

STAT_STRUC_ANA_SETTING.LargeDeflection = True

# %%
# Insert loading and boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FIX_SUP = STAT_STRUC.AddFixedSupport()
FIX_SUP.Location = HOR_EDGE1

REM_DISP = STAT_STRUC.AddRemoteDisplacement()
REM_DISP.Location = REM_PT
REM_DISP.XComponent.Output.DiscreteValues = [Quantity("0[mm]")]
REM_DISP.RotationZ.Output.DiscreteValues = [Quantity("0[deg]")]

REM_FRC = STAT_STRUC.AddRemoteForce()
REM_FRC.Location = REM_PT
REM_FRC.DefineBy = LoadDefineBy.Components
REM_FRC.YComponent.Output.DiscreteValues = [Quantity("-150796320 [N]")]

# Nonlinear Adaptivity does not support contact criterion yet hence command snippet used

NLAD = """NLADAPTIVE,all,add,contact,wear,0.50
NLADAPTIVE,all,on,all,all,1,,4
NLADAPTIVE,all,list,all,all"""
CMD2 = STAT_STRUC.AddCommandSnippet()
CMD2.AppendText(NLAD)
CMD2.StepSelectionMode = SequenceSelectionType.All

STAT_STRUC.Activate()
Graphics.Camera.SetFit()
Graphics.ExportImage(os.path.join(cwd, "mesh.png"), image_export_format, settings_720p)
display_image("mesh.png")

# %%
# Insert results
# ~~~~~~~~~~~~~~

TOT_DEF = STAT_STRUC_SOLN.AddTotalDeformation()

NORM_STRS1 = STAT_STRUC_SOLN.AddNormalStress()
NORM_STRS1.NormalOrientation = NormalOrientationType.YAxis
NORM_STRS1.DisplayTime = Quantity("1 [s]")
NORM_STRS1.DisplayOption = ResultAveragingType.Unaveraged

NORM_STRS2 = STAT_STRUC_SOLN.AddNormalStress()
NORM_STRS2.NormalOrientation = NormalOrientationType.YAxis
NORM_STRS2.DisplayTime = Quantity("4 [s]")
NORM_STRS2.DisplayOption = ResultAveragingType.Unaveraged

CONT_TOOL = STAT_STRUC_SOLN.AddContactTool()
CONT_TOOL.ScopingMethod = GeometryDefineByType.Geometry
SEL1 = ExtAPI.SelectionManager.AddSelection(ALL_BODIES_NS)
SEL2 = ExtAPI.SelectionManager.CurrentSelection
CONT_TOOL.Location = SEL2
ExtAPI.SelectionManager.ClearSelection()
CONT_PRES1 = CONT_TOOL.AddPressure()
CONT_PRES1.DisplayTime = Quantity("1 [s]")

CONT_PRES2 = CONT_TOOL.AddPressure()
CONT_PRES2.DisplayTime = Quantity("4 [s]")

# %%
# Solve
# ~~~~~

STAT_STRUC_SOLN.Solve(True)
STAT_STRUC_SS = STAT_STRUC_SOLN.Status
# sphinx_gallery_start_ignore
assert str(STAT_STRUC_SS) == "Done", "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# Postprocessing
# ~~~~~~~~~~~~~~
# Normal stress

Tree.Activate([NORM_STRS1])
Graphics.ExportImage(
    os.path.join(cwd, "normal_stresss.png"), image_export_format, settings_720p
)
display_image("normal_stresss.png")

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
# Project tree
# ~~~~~~~~~~~~

app.print_tree()

# %%
# Cleanup
# ~~~~~~~
# Save project

app.save(os.path.join(cwd, "contact_wear.mechdat"))
app.new()

# delete example file
delete_downloads()
