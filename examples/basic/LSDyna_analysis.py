""" .. _ref_ls_dyna:

LS-Dyna analysis
----------------

Using supplied files, this example shows how to insert an LS-Dyna analysis
into a new Mechanical session and execute a sequence of Python scripting
commands that define and solve the analysis. Deformation results are then reported
and plastic strain (EPS) animation is exported in the project directory.

"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

import logging
import os

from PIL import Image
import ansys.mechanical.core as mech
from ansys.mechanical.core.embedding.logger import Configuration
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

Configuration.configure(level=logging.DEBUG, to_stdout=True)

app = mech.App(version=242)
globals().update(mech.global_variables(app, True))
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
import clr

clr.AddReference("Ansys.ACT.WB1")
clr.AddReference("Ansys.ACT.Interfaces")
clr.AddReference("Ansys.Mechanical.DataModel")
from Ansys.ACT.Math import Vector3D
import Ansys.Mechanical.DataModel.MechanicalEnums as MechanicalEnums
from Ansys.Mechanical.Graphics import Point

ExtAPI.Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Iso)
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False

# Set camera
ExtAPI.Graphics.Camera.FocalPoint = Point(
    [9.0521184381880495, 2.9680547361873595, -11.52925245328758], "mm"
)
ExtAPI.Graphics.Camera.ViewVector = Vector3D(
    0.5358281613965048, -0.45245539014067604, 0.71286204933850261
)
ExtAPI.Graphics.Camera.UpVector = Vector3D(
    -0.59927496479653264, 0.39095266724498329, 0.69858823962485084
)
ExtAPI.Graphics.Camera.SceneHeight = Quantity(14.66592829617538, "mm")
ExtAPI.Graphics.Camera.SceneWidth = Quantity(8.4673776497126063, "mm")

# Set scale factor
true_scale = getattr(MechanicalEnums.Graphics.DeformationScaling, "True")
ExtAPI.Graphics.ViewOptions.ResultPreference.DeformationScaling = true_scale
ExtAPI.Graphics.ViewOptions.ResultPreference.DeformationScaleMultiplier = 1

# %%
# Download geometry and materials files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

geometry_path = download_file("example_08_Taylor_Bar.agdb", "pymechanical", "00_basic")
mat_path = download_file("example_08_Taylor_Bar_Mat.xml", "pymechanical", "00_basic")

# %%
# Import the geometry
# ~~~~~~~~~~~~~~~~~~~

geometry_import = Model.GeometryImportGroup.AddGeometryImport()
geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import.Import(
    geometry_path, geometry_import_format, geometry_import_preferences
)

ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "geometry.png"), image_export_format, settings_720p
)
display_image("geometry.png")

# %%
# Store all Variables necessary for analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MESH = Model.Mesh
NS = Model.NamedSelections
CONN = Model.Connections
CS = Model.CoordinateSystems
MAT = Model.Materials

# %%
# Setup the Analysis
# ~~~~~~~~~~~~~~~~~~
# Add ls dyna analysis and unit system

LSD_Analysis = Model.AddLSDynaAnalysis()
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMMton
ExtAPI.Application.ActiveAngleUnit = AngleUnitType.Radian

# %%
# Import and assign materials

MAT = ExtAPI.DataModel.Project.Model.Materials
MAT.Import(mat_path)

# Assign the material
ExtAPI.DataModel.Project.Model.Geometry.Children[0].Children[0].Material = "Bullet"

# %%
# Create coordinate system

cs = Model.CoordinateSystems
lcs = cs.AddCoordinateSystem()
lcs.Origin = [10.0, 1.5, -10.0]
lcs.PrimaryAxis = CoordinateSystemAxisType.PositiveZAxis
lcs.PrimaryAxisDefineBy = CoordinateSystemAlignmentType.GlobalY
lcs.OriginDefineBy = CoordinateSystemAlignmentType.Fixed

# %%
# Generate mesh
# By default quadratic element order in Mechanical - LSDyna supports only Linear

MESH.ElementOrder = ElementOrder.Linear
MESH.ElementSize = Quantity(0.5, "mm")
MESH.GenerateMesh()

ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "mesh.png"), image_export_format, settings_720p
)
display_image("mesh.png")

# %%
# Solver settings

LSD_Analysis.Solver.Properties["Step Controls/Endtime"].Value = 3.0e-5

# %%
# Boundary conditions and load
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

LSD_Analysis.Activate()

# Add Rigid Wall
rigid_wall = LSD_Analysis.CreateLoadObject("Rigid Wall", "LSDYNA")
rigid_wall.Properties["Coordinate System"].Value = lcs.ObjectId
ExtAPI.DataModel.Tree.Refresh()

# Adding initial velocity
ic = ExtAPI.DataModel.GetObjectsByName("Initial Conditions")[0]
vel = ic.InsertVelocity()
selection = ExtAPI.SelectionManager.CreateSelectionInfo(
    SelectionTypeEnum.GeometryEntities
)
selection.Ids = [ExtAPI.DataModel.GeoData.Assemblies[0].Parts[0].Bodies[0].Id]
vel.Location = selection
vel.DefineBy = LoadDefineBy.Components
vel.YComponent = Quantity(
    -280000, ExtAPI.DataModel.CurrentUnitFromQuantityName("Velocity")
)

# %%
# Add results
# ~~~~~~~~~~~

SOLN = LSD_Analysis.Solution

# %%
# Total deformation

TOT_DEFO = SOLN.AddTotalDeformation()

# %%
# User defined results

EPS = SOLN.AddUserDefinedResult()
EPS.Expression = "EPS"

# %%
# Solve
# ~~~~~

SOLN.Solve(True)

# sphinx_gallery_start_ignore
assert str(SOLN.Status) == "Done", "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# Messages
# ~~~~~~~~

Messages = ExtAPI.Application.Messages
if Messages:
    for message in Messages:
        print(f"[{message.Severity}] {message.DisplayString}")
else:
    print("No [Info]/[Warning]/[Error] Messages")


# %%
# Postprocessing
# ~~~~~~~~~~~~~~

# %%
# Total deformation
# ^^^^^^^^^^^^^^^^^

Tree.Activate([TOT_DEFO])
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "total_deformation.png"), image_export_format, settings_720p
)
display_image("total_deformation.png")

# %%
# User defined result animation - EPS
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

EPS.ExportAnimation(
    os.path.join(cwd, "eps.gif"), animation_export_format, settings_720p
)
gif = Image.open(os.path.join(cwd, "eps.gif"))
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


def print_tree(node, indentation=""):
    if hasattr(node, "Suppressed") and node.Suppressed is True:
        print(f"{indentation}├── {node.Name} (Suppressed)")
    else:
        print(f"{indentation}├── {node.Name}")

    if (
        hasattr(node, "Children")
        and node.Children is not None
        and node.Children.Count > 0
    ):
        for child in node.Children:
            print_tree(child, indentation + "|  ")


root_node = DataModel.Project
print_tree(root_node)

# %%
# Cleanup
# ~~~~~~~
# Save project

app.save(os.path.join(cwd, "lsdyna_analysis.mechdat"))
app.new()

# delete example file
delete_downloads()
