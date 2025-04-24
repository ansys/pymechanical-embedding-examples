""".. _ref_topology_optimization:

Topology optimization of a simple cantilever beam
-------------------------------------------------

This example demonstrates the structural topology optimization of a simple
cantilever beam. The structural analysis is performed with basic constraints and
load, which is then transferred to the topology optimization.
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image
from ansys.mechanical.core import App
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

if TYPE_CHECKING:
    import Ansys

# %%
# Embed Mechanical and set global variables

app = App(globals=globals())
print(app)


# %%
# Set the image output path and create functions to fit the camera and display images
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the path for the output files (images, gifs, mechdat)
output_path = Path.cwd() / "out"


def set_camera_and_display_image(
    camera,
    graphics,
    graphics_image_export_settings,
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

graphics = app.Graphics
camera = graphics.Camera

camera.SetSpecificViewOrientation(
    Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Front
)
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False

# %%
# Import structural analsys
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Download ``.mechdat`` file

structural_mechdat_file = download_file(
    "cantilever.mechdat", "pymechanical", "embedding"
)
app.open(structural_mechdat_file)
struct = model.Analyses[0]

# sphinx_gallery_start_ignore
assert struct.ObjectState == ObjectState.Solved
# sphinx_gallery_end_ignore
struct_sln = struct.Solution
struct_sln.Solve(True)
# sphinx_gallery_start_ignore
assert struct_sln.Status == SolutionStatusType.Done, "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# Display structural analsys results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Total deformation

struct_sln.Children[1].Activate()
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "total_deformation.png"
)

# %%
# Equivalent stress

struct_sln.Children[2].Activate()
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "equivalent_stress.png"
)

# %%
# Topology optimization
# ~~~~~~~~~~~~~~~~~~~~~

# Set MKS unit system

app.ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

# Get structural analysis and link to topology optimization

topology_optimization = model.AddTopologyOptimizationAnalysis()
topology_optimization.TransferDataFrom(struct)

optimization_region = DataModel.GetObjectsByType(
    DataModelObjectCategory.OptimizationRegion
)[0]
optimization_region.BoundaryCondition = BoundaryConditionType.AllLoadsAndSupports
optimization_region.OptimizationType = OptimizationType.TopologyDensity

# sphinx_gallery_start_ignore
assert topology_optimization.ObjectState == ObjectState.NotSolved
# sphinx_gallery_end_ignore

# Insert volume response constraint object for topology optimization
# Delete mass response constraint

mass_constraint = topology_optimization.Children[3]
mass_constraint.Delete()

# Add volume response constraint

volume_constraint = topology_optimization.AddVolumeConstraint()

# Insert member size manufacturing constraint

mem_size_manufacturing_constraint = (
    topology_optimization.AddMemberSizeManufacturingConstraint()
)
mem_size_manufacturing_constraint.Minimum = ManuMemberSizeControlledType.Manual
mem_size_manufacturing_constraint.MinSize = Quantity("2.4 [m]")


topology_optimization.Activate()
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "boundary_conditions.png"
)

# %%
# Solve
# ~~~~~

top_opt_sln = topology_optimization.Solution
top_opt_sln.Solve(True)
# sphinx_gallery_start_ignore
assert top_opt_sln.Status == SolutionStatusType.Done, "Solution status is not 'Done'"
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
# Display results
# ~~~~~~~~~~~~~~~

top_opt_sln.Children[1].Activate()
topology_density = top_opt_sln.Children[1]

# %%
# Add smoothing to the STL

topology_density.AddSmoothing()
topology_optimization.Solution.EvaluateAllResults()
topology_density.Children[0].Activate()
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "topo_opitimized_smooth.png"
)

# %%
# Export animation

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

topology_optimized_gif = output_path / "topology_opitimized.gif"
topology_density.ExportAnimation(
    str(topology_optimized_gif), animation_export_format, settings_720p
)


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
gif = Image.open(topology_optimized_gif)
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
# Review the results

# Print topology density results
print("Topology Density Results")
print("Minimum Density: ", topology_density.Minimum)
print("Maximum Density: ", topology_density.Maximum)
print("Iteration Number: ", topology_density.IterationNumber)
print("Original Volume: ", topology_density.OriginalVolume.Value)
print("Final Volume: ", topology_density.FinalVolume.Value)
print("Percent Volume of Original: ", topology_density.PercentVolumeOfOriginal)
print("Original Mass: ", topology_density.OriginalMass.Value)
print("Final Mass: ", topology_density.FinalMass.Value)
print("Percent Mass of Original: ", topology_density.PercentMassOfOriginal)


# %%
# Project tree
# ~~~~~~~~~~~~

app.print_tree()

# %%
# Cleanup
# ~~~~~~~
# Save project

mechdat_file = output_path / "cantilever_beam_topology_optimization.mechdat"
app.save(str(mechdat_file))
app.new()

# %%
# Delete the example files

delete_downloads()
