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

# %%
# Set the image output path and create functions to fit the camera and display images
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the path for the output files (images, gifs, mechdat)
output_path = Path.cwd() / "out"


def set_camera_and_display_image(
    camera: Ansys.ACT.Common.Graphics.MechanicalCameraWrapper,
    graphics: Ansys.ACT.Common.Graphics.MechanicalGraphicsWrapper,
    graphics_image_export_settings: Ansys.Mechanical.Graphics.GraphicsImageExportSettings,
    image_output_path: Path,
    image_name: str,
) -> None:
    """Set the camera to fit the model and display the image.

    Parameters
    ----------
    camera : Ansys.ACT.Common.Graphics.MechanicalCameraWrapper
        The camera object to set the view.
    graphics : Ansys.ACT.Common.Graphics.MechanicalGraphicsWrapper
        The graphics object to export the image.
    graphics_image_export_settings : Ansys.Mechanical.Graphics.GraphicsImageExportSettings
        The settings for exporting the image.
    image_output_path : Path
        The path to save the exported image.
    image_name : str
        The name of the exported image file.
    """
    # Set the camera to fit the mesh
    camera.SetFit()
    # Export the mesh image with the specified settings
    image_path = image_output_path / image_name
    graphics.ExportImage(
        str(image_path), image_export_format, graphics_image_export_settings
    )
    # Display the exported mesh image
    display_image(image_path)


def display_image(
    image_path: str,
    pyplot_figsize_coordinates: tuple = (16, 9),
    plot_xticks: list = [],
    plot_yticks: list = [],
    plot_axis: str = "off",
) -> None:
    """Display the image with the specified parameters.

    Parameters
    ----------
    image_path : str
        The path to the image file to display.
    pyplot_figsize_coordinates : tuple
        The size of the figure in inches (width, height).
    plot_xticks : list
        The x-ticks to display on the plot.
    plot_yticks : list
        The y-ticks to display on the plot.
    plot_axis : str
        The axis visibility setting ('on' or 'off').
    """
    # Set the figure size based on the coordinates specified
    plt.figure(figsize=pyplot_figsize_coordinates)
    # Read the image from the file into an array
    plt.imshow(mpimg.imread(image_path))
    # Get or set the current tick locations and labels of the x-axis
    plt.xticks(plot_xticks)
    # Get or set the current tick locations and labels of the y-axis
    plt.yticks(plot_yticks)
    # Turn off the axis
    plt.axis(plot_axis)
    # Display the figure
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
set_camera_and_display_image(camera, graphics, settings_720p, output_path, "mesh.png")

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
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "boundary_conditions.png"
)

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
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "total_deformation_valve.png"
)

# %%
# Stress

app.Tree.Activate([stress])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "stress_valve.png"
)

# %%
# Export stress animation

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

valve_gif = output_path / "valve.gif"
stress.ExportAnimation(str(valve_gif), animation_export_format, settings_720p)


def update_animation(frame: int) -> list[mpimg.AxesImage]:
    """Update the animation frame for the GIF.

    Parameters
    ----------
    frame : int
        The frame number to update the animation.

    Returns
    -------
    list[mpimg.AxesImage]
        A list containing the updated image for the animation.
    """
    # Seeks to the given frame in this sequence file
    gif.seek(frame)
    # Set the image array to the current frame of the GIF
    image.set_data(gif.convert("RGBA"))
    # Return the updated image
    return [image]


# Open the GIF file and create an animation
gif = Image.open(valve_gif)
# Set the subplots for the animation and turn off the axis
figure, axes = plt.subplots(figsize=(16, 9))
axes.axis("off")
# Change the color of the image
image = axes.imshow(gif.convert("RGBA"))

# Create the animation using the figure, update_animation function, and the GIF frames
# Set the interval between frames to 200 milliseconds and repeat the animation
FuncAnimation(
    figure,
    update_animation,
    frames=range(gif.n_frames),
    interval=100,
    repeat=True,
    blit=True,
)

# Show the animation
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

mechdat_file = output_path / "valve.mechdat"
app.save(str(mechdat_file))
app.new()

# %%
# delete example files

delete_downloads()
