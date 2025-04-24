""".. _ref_steady_state_thermal:

Steady state thermal analysis
-----------------------------

This example problem demonstrates the use of a
simple steady-state thermal analysis to determine the temperatures,
thermal gradients, heat flow rates, and heat fluxes that are caused
by thermal loads that do not vary over time. A steady-state thermal
analysis calculates the effects of steady thermal loads on a system
or component, in this example, a long bar model.
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

camera.SetSpecificViewOrientation(Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Iso)
camera.SetFit()
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False


# %%
# Download and import geometry
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download the geometry file.

geometry_path = download_file("LONGBAR.x_t", "pymechanical", "embedding")

# %%
# Import the geometry

model = app.Model

geometry_import_group = model.GeometryImportGroup
geometry_import = geometry_import_group.AddGeometryImport()
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
# Add steady state thermal analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

model.AddSteadyStateThermalAnalysis()
app.ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS
stat_therm = model.Analyses[0]
coordinate_systems = model.CoordinateSystems
lcs1 = coordinate_systems.AddCoordinateSystem()
lcs1.OriginX = Quantity("0 [m]")

lcs2 = coordinate_systems.AddCoordinateSystem()
lcs2.OriginX = Quantity("0 [m]")
lcs2.PrimaryAxisDefineBy = CoordinateSystemAlignmentType.GlobalY

# %%
# Create named selections and construction geometry
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create named selections

face1 = model.AddNamedSelection()
face1.ScopingMethod = GeometryDefineByType.Worksheet
face1.Name = "Face1"
gen_crt1 = face1.GenerationCriteria
crt1 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
crt1.Active = True
crt1.Action = SelectionActionType.Add
crt1.EntityType = SelectionType.GeoFace
crt1.Criterion = SelectionCriterionType.LocationZ
crt1.Operator = SelectionOperatorType.Equal
crt1.Value = Quantity("20 [m]")
gen_crt1.Add(crt1)
face1.Activate()
face1.Generate()

face2 = model.AddNamedSelection()
face2.ScopingMethod = GeometryDefineByType.Worksheet
face2.Name = "Face2"
gen_crt2 = face2.GenerationCriteria
crt1 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
crt1.Active = True
crt1.Action = SelectionActionType.Add
crt1.EntityType = SelectionType.GeoFace
crt1.Criterion = SelectionCriterionType.LocationZ
crt1.Operator = SelectionOperatorType.Equal
crt1.Value = Quantity("0 [m]")
gen_crt2.Add(crt1)
face2.Activate()
face2.Generate()

face3 = model.AddNamedSelection()
face3.ScopingMethod = GeometryDefineByType.Worksheet
face3.Name = "Face3"
gen_crt3 = face3.GenerationCriteria
crt1 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
crt1.Active = True
crt1.Action = SelectionActionType.Add
crt1.EntityType = SelectionType.GeoFace
crt1.Criterion = SelectionCriterionType.LocationX
crt1.Operator = SelectionOperatorType.Equal
crt1.Value = Quantity("1 [m]")
gen_crt3.Add(crt1)
crt2 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
crt2.Active = True
crt2.Action = SelectionActionType.Filter
crt2.EntityType = SelectionType.GeoFace
crt2.Criterion = SelectionCriterionType.LocationY
crt2.Operator = SelectionOperatorType.Equal
crt2.Value = Quantity("2 [m]")
gen_crt3.Add(crt2)
crt3 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
crt3.Active = True
crt3.Action = SelectionActionType.Filter
crt3.EntityType = SelectionType.GeoFace
crt3.Criterion = SelectionCriterionType.LocationZ
crt3.Operator = SelectionOperatorType.Equal
crt3.Value = Quantity("12 [m]")
gen_crt3.Add(crt3)
crt4 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
crt4.Active = True
crt4.Action = SelectionActionType.Add
crt4.EntityType = SelectionType.GeoFace
crt4.Criterion = SelectionCriterionType.LocationZ
crt4.Operator = SelectionOperatorType.Equal
crt4.Value = Quantity("4.5 [m]")
gen_crt3.Add(crt4)
crt5 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
crt5.Active = True
crt5.Action = SelectionActionType.Filter
crt5.EntityType = SelectionType.GeoFace
crt5.Criterion = SelectionCriterionType.LocationY
crt5.Operator = SelectionOperatorType.Equal
crt5.Value = Quantity("2 [m]")
gen_crt3.Add(crt5)
face3.Activate()
face3.Generate()

body1 = model.AddNamedSelection()
body1.ScopingMethod = GeometryDefineByType.Worksheet
body1.Name = "Body1"
body1.GenerationCriteria.Add(None)
body1.GenerationCriteria[0].EntityType = SelectionType.GeoFace
body1.GenerationCriteria[0].Criterion = SelectionCriterionType.LocationZ
body1.GenerationCriteria[0].Operator = SelectionOperatorType.Equal
body1.GenerationCriteria[0].Value = Quantity("1 [m]")
body1.GenerationCriteria.Add(None)
body1.GenerationCriteria[1].EntityType = SelectionType.GeoFace
body1.GenerationCriteria[1].Criterion = SelectionCriterionType.LocationZ
body1.GenerationCriteria[1].Operator = SelectionOperatorType.Equal
body1.GenerationCriteria[1].Value = Quantity("1 [m]")
body1.Generate()

# %%
# Create construction geometry

construction_geometry = model.AddConstructionGeometry()
Path = construction_geometry.AddPath()
Path.StartYCoordinate = Quantity(2, "m")
Path.StartZCoordinate = Quantity(20, "m")
Path.StartZCoordinate = Quantity(20, "m")
Path.EndXCoordinate = Quantity(2, "m")
surface = construction_geometry.AddSurface()
surface.CoordinateSystem = lcs2
construction_geometry.UpdateAllSolids()

# %%
# Define boundary condition and add results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Add temperature boundary conditions

temp = stat_therm.AddTemperature()
temp.Location = face1
temp.Magnitude.Output.DiscreteValues = [Quantity("22[C]"), Quantity("30[C]")]

temp2 = stat_therm.AddTemperature()
temp2.Location = face2
temp2.Magnitude.Output.DiscreteValues = [Quantity("22[C]"), Quantity("60[C]")]

temp.Magnitude.Inputs[0].DiscreteValues = [
    Quantity("0 [sec]"),
    Quantity("1 [sec]"),
    Quantity("2 [sec]"),
]
temp.Magnitude.Output.DiscreteValues = [
    Quantity("22[C]"),
    Quantity("30[C]"),
    Quantity("40[C]"),
]

temp2.Magnitude.Inputs[0].DiscreteValues = [
    Quantity("0 [sec]"),
    Quantity("1 [sec]"),
    Quantity("2 [sec]"),
]
temp2.Magnitude.Output.DiscreteValues = [
    Quantity("22[C]"),
    Quantity("50[C]"),
    Quantity("80[C]"),
]

# %%
# Add radiation

radiation = stat_therm.AddRadiation()
radiation.Location = face3
radiation.AmbientTemperature.Inputs[0].DiscreteValues = [
    Quantity("0 [sec]"),
    Quantity("1 [sec]"),
    Quantity("2 [sec]"),
]
radiation.AmbientTemperature.Output.DiscreteValues = [
    Quantity("22[C]"),
    Quantity("30[C]"),
    Quantity("40[C]"),
]
radiation.Correlation = RadiationType.SurfaceToSurface

# %%
# Analysis settings

analysis_settings = stat_therm.AnalysisSettings
analysis_settings.NumberOfSteps = 2
analysis_settings.CalculateVolumeEnergy = True

stat_therm.Activate()
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "bc_steady_state.png"
)

# %%
# Add results
# ~~~~~~~~~~~
# Temperature

stat_therm_soln = model.Analyses[0].Solution
temp_rst = stat_therm_soln.AddTemperature()
temp_rst.By = SetDriverStyle.MaximumOverTime

temp_rst2 = stat_therm_soln.AddTemperature()
temp_rst2.Location = body1

temp_rst3 = stat_therm_soln.AddTemperature()
temp_rst3.Location = Path

temp_rst4 = stat_therm_soln.AddTemperature()
temp_rst4.Location = surface

# %%
# Total  and directional heat flux

total_heat_flux = stat_therm_soln.AddTotalHeatFlux()
directional_heat_flux = stat_therm_soln.AddTotalHeatFlux()
directional_heat_flux.ThermalResultType = TotalOrDirectional.Directional
directional_heat_flux.NormalOrientation = NormalOrientationType.ZAxis

lcs2.PrimaryAxisDefineBy = CoordinateSystemAlignmentType.GlobalZ
directional_heat_flux.CoordinateSystem = lcs2
directional_heat_flux.DisplayOption = ResultAveragingType.Averaged

# %%
# Thermal error

thermal_error = stat_therm_soln.AddThermalError()

# %%
# Temperature probe

temp_probe = stat_therm_soln.AddTemperatureProbe()
temp_probe.GeometryLocation = face1
temp_probe.LocationMethod = LocationDefinitionMethod.CoordinateSystem
temp_probe.CoordinateSystemSelection = lcs2

# %%
# Heat flux probe

hflux_probe = stat_therm_soln.AddHeatFluxProbe()
hflux_probe.LocationMethod = LocationDefinitionMethod.CoordinateSystem
hflux_probe.CoordinateSystemSelection = lcs2
hflux_probe.ResultSelection = ProbeDisplayFilter.ZAxis

# %%
# Reaction probe

analysis_settings.NodalForces = OutputControlsNodalForcesType.Yes
reaction_probe = stat_therm_soln.AddReactionProbe()
reaction_probe.LocationMethod = LocationDefinitionMethod.GeometrySelection
reaction_probe.GeometryLocation = face1

# %%
# Radiation probe

radiation_probe = stat_therm_soln.AddRadiationProbe()
radiation_probe.BoundaryConditionSelection = radiation
radiation_probe.ResultSelection = ProbeDisplayFilter.All


# %%
# Solve
# ~~~~~

stat_therm_soln.Solve(True)

# sphinx_gallery_start_ignore
assert (
    stat_therm_soln.Status == SolutionStatusType.Done
), "Solution status is not 'Done'"
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

# Display results
# ~~~~~~~~~~~~~~~
# Total body temperature

app.Tree.Activate([temp_rst])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "total_body_temp.png"
)

# %%
# Temperature on part of the body

app.Tree.Activate([temp_rst2])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "part_temp_body.png"
)

# %%
# Temperature distribution along the specific path

app.Tree.Activate([temp_rst3])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "path_temp_distribution.png"
)

# %%
# Temperature of bottom surface

app.Tree.Activate([temp_rst4])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "bottom_surface_temp.png"
)

# %%
# Export directional heat flux animation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Directional heat flux

app.Tree.Activate([directional_heat_flux])
animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

directional_heat_flux_gif = output_path / "directional_heat_flux.gif"
directional_heat_flux.ExportAnimation(
    str(directional_heat_flux_gif), animation_export_format, settings_720p
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
gif = Image.open(directional_heat_flux_gif)
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


solve_path = stat_therm.WorkingDir
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

mechdat_path = output_path / "steady_state_thermal.mechdat"
app.save(str(mechdat_path))
app.new()

# %%
# Delete example files

delete_downloads()
