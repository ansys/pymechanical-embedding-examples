""".. _ref_basic_valve:

Basic Valve Implementation
--------------------------

This example demonstrates a basic implementation of a valve in Python.
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

from pathlib import Path

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

cwd = Path.cwd() / "out"


def display_image(image_name):
    plt.figure(figsize=(16, 9))
    image_path = cwd / image_name
    plt.imshow(mpimg.imread(str(image_path)))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.show()


# %%
# Configure graphics for image export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

graphics = app.Graphics
camera = graphics.Camera

camera.SetSpecificViewOrientation(ViewOrientationType.Iso)
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

model = app.Model

geometry_import = model.GeometryImportGroup.AddGeometryImport()
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
material_assignment = model.Materials.AddMaterialAssignment()
material_assignment.Material = "Structural Steel"
sel = app.ExtAPI.SelectionManager.CreateSelectionInfo(
    Ansys.ACT.Interfaces.Common.SelectionTypeEnum.GeometryEntities
)
sel.Ids = [
    body.GetGeoBody().Id
    for body in model.Geometry.GetChildren(
        Ansys.Mechanical.DataModel.Enums.DataModelObjectCategory.Body, True
    )
]
material_assignment.Location = sel

# %%
# Define mesh settings,  generate mesh

mesh = model.Mesh
mesh.ElementSize = Quantity(25, "mm")
mesh.GenerateMesh()
app.Tree.Activate([mesh])
mesh_image = cwd / "mesh.png"
graphics.ExportImage(str(mesh_image), image_export_format, settings_720p)
display_image(mesh_image.name)

# %%
# Define analysis and boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

analysis = model.AddStaticStructuralAnalysis()

fixed_support = analysis.AddFixedSupport()
fixed_support.Location = app.ExtAPI.DataModel.GetObjectsByName("NSFixedSupportFaces")[0]

frictionless_support = analysis.AddFrictionlessSupport()
frictionless_support.Location = app.ExtAPI.DataModel.GetObjectsByName(
    "NSFrictionlessSupportFaces"
)[0]

pressure = analysis.AddPressure()
pressure.Location = app.ExtAPI.DataModel.GetObjectsByName("NSInsideFaces")[0]

pressure.Magnitude.Inputs[0].DiscreteValues = [Quantity("0 [s]"), Quantity("1 [s]")]
pressure.Magnitude.Output.DiscreteValues = [Quantity("0 [Pa]"), Quantity("15 [MPa]")]

analysis.Activate()
camera.SetFit()
boundary_conditions_image = cwd / "boundary_conditions.png"
graphics.ExportImage(str(boundary_conditions_image), image_export_format, settings_720p)
display_image(boundary_conditions_image.name)


# %%
# Add results

solution = analysis.Solution
deformation = solution.AddTotalDeformation()
stress = solution.AddEquivalentStress()

# %%
# Solve

solution.Solve(True)

# sphinx_gallery_start_ignore
assert solution.Status == SolutionStatusType.Done, "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# Messages
# ~~~~~~~~

messages = app.ExtAPI.Application.Messages
if messages:
    for message in messages:
        print(f"[{message.Severity}] {message.DisplayString}")
else:
    print("No [Info]/[Warning]/[Error] messages")

# %%
# Results
# ~~~~~~~

# %%
# Total deformation

app.Tree.Activate([deformation])
total_deformation_valve_image = cwd / "total_deformation_valve.png"
graphics.ExportImage(
    str(total_deformation_valve_image), image_export_format, settings_720p
)
display_image(total_deformation_valve_image.name)

# %%
# Stress

app.Tree.Activate([stress])
stress_valve_image = cwd / "stress_valve.png"
graphics.ExportImage(str(stress_valve_image), image_export_format, settings_720p)
display_image(stress_valve_image.name)

# %%
# Export stress animation

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

valve_gif = cwd / "valve.gif"
stress.ExportAnimation(str(valve_gif), animation_export_format, settings_720p)
gif = Image.open(valve_gif)
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
solve_out_path = solve_path + "solve.out"
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

mechdat_file = cwd / "valve.mechdat"
app.save(str(mechdat_file))
app.new()

# %%
# delete example files

delete_downloads()
