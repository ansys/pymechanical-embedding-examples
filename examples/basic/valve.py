""" .. _ref_basic_valve:

Basic Valve Implementation
--------------------------

This example demonstrates a basic implementation of a valve in Python.
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

import os

from PIL import Image
import ansys.mechanical.core as mech
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

# %%
# Embed mechanical and set global variables

app = mech.App(version=242)
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Iso)
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False


# %%
# Download geometry and import
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download geometry

geometry_path = download_file("Valve.pmdb", "pymechanical", "embedding")

# %%
# Import geometry

geometry_import = Model.GeometryImportGroup.AddGeometryImport()
geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import.Import(
    geometry_path, geometry_import_format, geometry_import_preferences
)

app.plot()

# %%
# Assign materials and mesh the geometry
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
material_assignment = Model.Materials.AddMaterialAssignment()
material_assignment.Material = "Structural Steel"
sel = ExtAPI.SelectionManager.CreateSelectionInfo(
    Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities
)
sel.Ids = [
    body.GetGeoBody().Id
    for body in Model.Geometry.GetChildren(
        Ansys.Mechanical.DataModel.Enums.DataModelObjectCategory.Body, True
    )
]
material_assignment.Location = sel

# %%
# Define mesh settings,  generate mesh

mesh = Model.Mesh
mesh.ElementSize = Quantity(25, "mm")
mesh.GenerateMesh()
Tree.Activate([mesh])
Graphics.ExportImage(os.path.join(cwd, "mesh.png"), image_export_format, settings_720p)
display_image("mesh.png")

# %%
# Define analysis and boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

analysis = Model.AddStaticStructuralAnalysis()

fixed_support = analysis.AddFixedSupport()
fixed_support.Location = ExtAPI.DataModel.GetObjectsByName("NSFixedSupportFaces")[0]

frictionless_support = analysis.AddFrictionlessSupport()
frictionless_support.Location = ExtAPI.DataModel.GetObjectsByName(
    "NSFrictionlessSupportFaces"
)[0]

pressure = analysis.AddPressure()
pressure.Location = ExtAPI.DataModel.GetObjectsByName("NSInsideFaces")[0]

pressure.Magnitude.Inputs[0].DiscreteValues = [Quantity("0 [s]"), Quantity("1 [s]")]
pressure.Magnitude.Output.DiscreteValues = [Quantity("0 [Pa]"), Quantity("15 [MPa]")]

analysis.Activate()
Graphics.Camera.SetFit()
Graphics.ExportImage(
    os.path.join(cwd, "boundary_conditions.png"), image_export_format, settings_720p
)
display_image("boundary_conditions.png")

# %%
# Solve
# ~~~~~
# Solve process settings

config = ExtAPI.Application.SolveConfigurations["My Computer"]
config.SolveProcessSettings.MaxNumberOfCores = 1
config.SolveProcessSettings.DistributeSolution = False

# %%
# Add results

solution = analysis.Solution
deformation = solution.AddTotalDeformation()
stress = solution.AddEquivalentStress()

# %%
# Solve

solution.Solve(True)

# sphinx_gallery_start_ignore
assert str(solution.Status) == "Done", "Solution status is not 'Done'"
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
# Results
# ~~~~~~~


def display_image(image_name):
    plt.figure(figsize=(16, 9))
    plt.imshow(mpimg.imread(os.path.join(cwd, image_name)))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.show()


# %%
# Total deformation

Tree.Activate([deformation])
Graphics.ExportImage(
    os.path.join(cwd, "totaldeformation_valve.png"), image_export_format, settings_720p
)
display_image("totaldeformation_valve.png")

# %%
# Stress

Tree.Activate([stress])
Graphics.ExportImage(
    os.path.join(cwd, "stress_valve.png"), image_export_format, settings_720p
)
display_image("stress_valve.png")

# %%
# Export stress animation

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

stress.ExportAnimation(
    os.path.join(cwd, "Valve.gif"), animation_export_format, settings_720p
)
gif = Image.open(os.path.join(cwd, "Valve.gif"))
fig, ax = plt.subplots(figsize=(16, 9))
ax.axis("off")
img = ax.imshow(gif.convert("RGBA"))


def update(frame):
    gif.seek(frame)
    img.set_array(gif.convert("RGBA"))
    return [img]


ani = FuncAnimation(
    fig, update, frames=range(gif.n_frames), interval=100, repeat=True, blit=True
)
plt.show()

# %%
# Display output file from solve
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def write_file_contents_to_console(path):
    """Write file contents to console."""
    with open(path, "rt") as file:
        for line in file:
            print(line, end="")


solve_path = analysis.WorkingDir
solve_out_path = os.path.join(solve_path, "solve.out")
if solve_out_path:
    write_file_contents_to_console(solve_out_path)

# %%
# Project tree
# ~~~~~~~~~~~~

app.print_tree()

# %%
# Cleanup
# ~~~~~~~
# Save project

app.save(os.path.join(cwd, "Valve.mechdat"))
app.new()

# %%
# delete example files

delete_downloads()
