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

from pathlib import Path

from PIL import Image
from ansys.mechanical.core import App
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import Ansys

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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

graphics = app.Graphics
camera = graphics.Camera

camera.SetSpecificViewOrientation(Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Front)
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False
camera.Rotate(180, CameraAxisType.ScreenY)

# %%
# Download geometry and materials files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

geometry_path = download_file("example_07_td43_wear.agdb", "pymechanical", "00_basic")
mat1_path = download_file("example_07_Mat_Copper.xml", "pymechanical", "00_basic")
mat2_path = download_file("example_07_Mat_Steel.xml", "pymechanical", "00_basic")

# %%
# Import geometry
# ~~~~~~~~~~~~~~~

model = app.Model

geometry_import = model.GeometryImportGroup.AddGeometryImport()
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

materials = model.Materials
materials.Import(mat1_path)
materials.Import(mat2_path)

print("Material import done !")

# %%
# Setup the Analysis
# ~~~~~~~~~~~~~~~~~~
# Set up the unit system

app.ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM

# %%
# Store all main tree nodes as variables

geometry = model.Geometry
coordinate_systems = model.CoordinateSystems
connections = model.Connections
mesh = model.Mesh
named_selections = model.NamedSelections

# %%
# Add static structural analysis

model.AddStaticStructuralAnalysis()
static_structural_analysis = model.Analyses[0]
stat_struct_soln = static_structural_analysis.Solution
stat_struct_analysis_settings = static_structural_analysis.Children[0]

# %%
# Store name selection

curve_named_selection = [x for x in app.Tree.AllObjects if x.Name == "curve"][0]
dia_named_selection = [x for x in app.Tree.AllObjects if x.Name == "dia"][0]
ver_edge1 = [x for x in app.Tree.AllObjects if x.Name == "v1"][0]
ver_edge2 = [x for x in app.Tree.AllObjects if x.Name == "v2"][0]
hor_edge1 = [x for x in app.Tree.AllObjects if x.Name == "h1"][0]
hor_edge2 = [x for x in app.Tree.AllObjects if x.Name == "h2"][0]
all_bodies_named_selection = [x for x in app.Tree.AllObjects if x.Name == "all_bodies"][
    0
]

# %%
# Assign material to bodies and change behavior to axisymmetric

geometry.Model2DBehavior = Model2DBehavior.AxiSymmetric

surface1 = geometry.Children[0].Children[0]
surface1.Material = "Steel"
surface1.Dimension = ShellBodyDimension.Two_D

surface2 = geometry.Children[1].Children[0]
surface2.Material = "Copper"
surface2.Dimension = ShellBodyDimension.Two_D

# %%
# Change contact settings

contact_region = connections.AddContactRegion()
contact_region.SourceLocation = named_selections.Children[6]
contact_region.TargetLocation = named_selections.Children[3]
# contact_region.FlipContactTarget()
contact_region.ContactType = ContactType.Frictionless
contact_region.Behavior = ContactBehavior.Asymmetric
contact_region.ContactFormulation = ContactFormulation.AugmentedLagrange
contact_region.DetectionMethod = ContactDetectionPoint.NodalNormalToTarget

# %%
# Add a command snippet to use Archard Wear Model

archard_wear_model = """keyo,cid,5,1
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
cmd1 = contact_region.AddCommandSnippet()
cmd1.AppendText(archard_wear_model)

# %%
# Insert remote point

remote_point = model.AddRemotePoint()
remote_point.Location = dia_named_selection
remote_point.Behavior = LoadBehavior.Rigid

# %%
# Mesh
# ~~~~

mesh.ElementOrder = ElementOrder.Linear
mesh.ElementSize = Quantity("1 [mm]")

edge_sizing1 = mesh.AddSizing()
edge_sizing1.Location = hor_edge1
edge_sizing1.Type = SizingType.NumberOfDivisions
edge_sizing1.NumberOfDivisions = 70

edge_sizing2 = mesh.AddSizing()
edge_sizing2.Location = hor_edge2
edge_sizing2.Type = SizingType.NumberOfDivisions
edge_sizing2.NumberOfDivisions = 70

edge_sizing3 = mesh.AddSizing()
edge_sizing3.Location = ver_edge1
edge_sizing3.Type = SizingType.NumberOfDivisions
edge_sizing3.NumberOfDivisions = 35

edge_sizing4 = mesh.AddSizing()
edge_sizing4.Location = ver_edge2
edge_sizing4.Type = SizingType.NumberOfDivisions
edge_sizing4.NumberOfDivisions = 35

edge_sizing5 = mesh.AddSizing()
edge_sizing5.Location = dia_named_selection
edge_sizing5.Type = SizingType.NumberOfDivisions
edge_sizing5.NumberOfDivisions = 40

edge_sizing6 = mesh.AddSizing()
edge_sizing6.Location = curve_named_selection
edge_sizing6.Type = SizingType.NumberOfDivisions
edge_sizing6.NumberOfDivisions = 60

mesh.GenerateMesh()
set_camera_and_display_image(camera, graphics, settings_720p, output_path, "mesh.png")

# %%
# Analysis settings
# ~~~~~~~~~~~~~~~~~

stat_struct_analysis_settings.NumberOfSteps = 2
stat_struct_analysis_settings.CurrentStepNumber = 1
stat_struct_analysis_settings.AutomaticTimeStepping = AutomaticTimeStepping.On
stat_struct_analysis_settings.DefineBy = TimeStepDefineByType.Time
stat_struct_analysis_settings.InitialTimeStep = Quantity("0.1 [s]")
stat_struct_analysis_settings.MinimumTimeStep = Quantity("0.0001 [s]")
stat_struct_analysis_settings.MaximumTimeStep = Quantity("1 [s]")
stat_struct_analysis_settings.CurrentStepNumber = 2
stat_struct_analysis_settings.Activate()
stat_struct_analysis_settings.StepEndTime = Quantity("4 [s]")
stat_struct_analysis_settings.AutomaticTimeStepping = AutomaticTimeStepping.On
stat_struct_analysis_settings.DefineBy = TimeStepDefineByType.Time
stat_struct_analysis_settings.InitialTimeStep = Quantity("0.01 [s]")
stat_struct_analysis_settings.MinimumTimeStep = Quantity("0.000001 [s]")
stat_struct_analysis_settings.MaximumTimeStep = Quantity("0.02 [s]")

stat_struct_analysis_settings.LargeDeflection = True

# %%
# Insert loading and boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

fixed_support = static_structural_analysis.AddFixedSupport()
fixed_support.Location = hor_edge1

remote_displacement = static_structural_analysis.AddRemoteDisplacement()
remote_displacement.Location = remote_point
remote_displacement.XComponent.Output.DiscreteValues = [Quantity("0[mm]")]
remote_displacement.RotationZ.Output.DiscreteValues = [Quantity("0[deg]")]

remote_force = static_structural_analysis.AddRemoteForce()
remote_force.Location = remote_point
remote_force.DefineBy = LoadDefineBy.Components
remote_force.YComponent.Output.DiscreteValues = [Quantity("-150796320 [N]")]

# Nonlinear Adaptivity does not support contact criterion yet hence command snippet used

nonlinear_adaptivity = """NLADAPTIVE,all,add,contact,wear,0.50
NLADAPTIVE,all,on,all,all,1,,4
NLADAPTIVE,all,list,all,all"""
cmd2 = static_structural_analysis.AddCommandSnippet()
cmd2.AppendText(nonlinear_adaptivity)
cmd2.StepSelectionMode = SequenceSelectionType.All

static_structural_analysis.Activate()
set_camera_and_display_image(camera, graphics, settings_720p, output_path, "mesh.png")

# %%
# Insert results
# ~~~~~~~~~~~~~~

total_deformation = stat_struct_soln.AddTotalDeformation()

normal_stress1 = stat_struct_soln.AddNormalStress()
normal_stress1.NormalOrientation = NormalOrientationType.YAxis
normal_stress1.DisplayTime = Quantity("1 [s]")
normal_stress1.DisplayOption = ResultAveragingType.Unaveraged

normal_stress2 = stat_struct_soln.AddNormalStress()
normal_stress2.NormalOrientation = NormalOrientationType.YAxis
normal_stress2.DisplayTime = Quantity("4 [s]")
normal_stress2.DisplayOption = ResultAveragingType.Unaveraged

contact_tool = stat_struct_soln.AddContactTool()
contact_tool.ScopingMethod = GeometryDefineByType.Geometry
selection1 = app.ExtAPI.SelectionManager.AddSelection(all_bodies_named_selection)
selection2 = app.ExtAPI.SelectionManager.CurrentSelection
contact_tool.Location = selection2
app.ExtAPI.SelectionManager.ClearSelection()
contact_pressure1 = contact_tool.AddPressure()
contact_pressure1.DisplayTime = Quantity("1 [s]")

contact_pressure2 = contact_tool.AddPressure()
contact_pressure2.DisplayTime = Quantity("4 [s]")

# %%
# Solve
# ~~~~~

stat_struct_soln.Solve(True)
# sphinx_gallery_start_ignore
assert (
    stat_struct_soln.Status == SolutionStatusType.Done
), "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# Postprocessing
# ~~~~~~~~~~~~~~
# Normal stress

app.Tree.Activate([normal_stress1])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "normal_stress.png"
)

# %%
# Total deformation animation

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

total_deformation_gif = output_path / "total_deformation.gif"
total_deformation.ExportAnimation(
    str(total_deformation_gif), animation_export_format, settings_720p
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
gif = Image.open(total_deformation_gif)
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
    interval=200,
    repeat=True,
    blit=True,
)

# Show the animation
plt.show()

# %%
# Project tree
# ~~~~~~~~~~~~

app.print_tree()

# %%
# Cleanup
# ~~~~~~~
# Save project

mechdat_file = output_path / "contact_wear.mechdat"
app.save(str(mechdat_file))
app.new()

# delete example file
delete_downloads()
