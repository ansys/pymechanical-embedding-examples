# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

""".. _ref_harmonic_acoustics:

Harmonic acoustic analysis
--------------------------

This example examines a harmonic acoustic analysis that uses
surface velocity to determine the steady-state response of a
structure and the surrounding fluid medium to loads and excitations
that vary sinusoidally with time.
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
# Embed mechanical and set global variables

app = App()
app.update_globals(globals())
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
camera.SetSpecificViewOrientation(
    Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Iso
)
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

# Download the geometry file from the ansys/example-data repository
geometry_path = download_file("C_GEOMETRY.agdb", "pymechanical", "embedding")
# Download the material file from the ansys/example-data repository
mat_path = download_file("Air-material.xml", "pymechanical", "embedding")

# %%
# Import the geometry
# ~~~~~~~~~~~~~~~~~~~

# Define the model
model = app.Model

# Add the geometry import group and set its preferences
geometry_import = model.GeometryImportGroup.AddGeometryImport()
geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import.Import(
    geometry_path, geometry_import_format, geometry_import_preferences
)

# Define the geometry in the model
geometry = model.Geometry

# Suppress the bodies at the specified geometry.Children indices
suppressed_indices = [0, 1, 2, 3, 4, 6, 9, 10]
for child in range(geometry.Children.Count):
    if child in suppressed_indices:
        geometry.Children[child].Suppressed = True

# Visualize the model in 3D
app.plot()

# %%
# Store all variables necessary for analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mesh = model.Mesh
named_selection = model.NamedSelections
connection = model.Connections
coordinate_systems = model.CoordinateSystems
mat = model.Materials

# %%
# Set up the analysis
# ~~~~~~~~~~~~~~~~~~~

# Add the harmonic acoustics analysis and unit system
model.AddHarmonicAcousticAnalysis()
app.ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

# %%
# Import and assign materials

# Import the material file
mat.Import(mat_path)

# Assign the material to geometry.Children bodies that are not suppressed
for child in range(geometry.Children.Count):
    if child not in suppressed_indices:
        geometry.Children[child].Material = "Air"

# %%
# Create coordinate system

# Add a coordinate system and set its properties
lcs1 = coordinate_systems.AddCoordinateSystem()
lcs1.OriginX = Quantity("0 [mm]")
lcs1.OriginY = Quantity("0 [mm]")
lcs1.OriginZ = Quantity("0 [mm]")
lcs1.PrimaryAxisDefineBy = CoordinateSystemAlignmentType.GlobalZ

# %%
# Generate the mesh

mesh.ElementSize = Quantity("200 [mm]")
mesh.GenerateMesh()

# %%
# Create named selections
# ~~~~~~~~~~~~~~~~~~~~~~~~

sf_velo = model.AddNamedSelection()
sf_velo.ScopingMethod = GeometryDefineByType.Worksheet
sf_velo.Name = "sf_velo"

generation_criteria_1 = sf_velo.GenerationCriteria
criteria_1 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
criteria_1.Active = True
criteria_1.Action = SelectionActionType.Add
criteria_1.EntityType = SelectionType.GeoFace
criteria_1.Criterion = SelectionCriterionType.Size
criteria_1.Operator = SelectionOperatorType.Equal
criteria_1.Value = Quantity("3e6 [mm^2]")
generation_criteria_1.Add(criteria_1)

criteria_2 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
criteria_2.Active = True
criteria_2.Action = SelectionActionType.Filter
criteria_2.EntityType = SelectionType.GeoFace
criteria_2.Criterion = SelectionCriterionType.LocationZ
criteria_2.Operator = SelectionOperatorType.Equal
criteria_2.Value = Quantity("15000 [mm]")
generation_criteria_1.Add(criteria_2)

sf_velo.Activate()
sf_velo.Generate()


abs_face = model.AddNamedSelection()
abs_face.ScopingMethod = GeometryDefineByType.Worksheet
abs_face.Name = "abs_face"

generation_criteria_2 = abs_face.GenerationCriteria
criteria_1 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
criteria_1.Active = True
criteria_1.Action = SelectionActionType.Add
criteria_1.EntityType = SelectionType.GeoFace
criteria_1.Criterion = SelectionCriterionType.Size
criteria_1.Operator = SelectionOperatorType.Equal
criteria_1.Value = Quantity("1.5e6 [mm^2]")
generation_criteria_2.Add(criteria_1)

criteria_2 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
criteria_2.Active = True
criteria_2.Action = SelectionActionType.Filter
criteria_2.EntityType = SelectionType.GeoFace
criteria_2.Criterion = SelectionCriterionType.LocationY
criteria_2.Operator = SelectionOperatorType.Equal
criteria_2.Value = Quantity("500 [mm]")
generation_criteria_2.Add(criteria_2)

abs_face.Activate()
abs_face.Generate()


pres_face = model.AddNamedSelection()
pres_face.ScopingMethod = GeometryDefineByType.Worksheet
pres_face.Name = "pres_face"

generation_criteria_3 = pres_face.GenerationCriteria
criteria_1 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
criteria_1.Active = True
criteria_1.Action = SelectionActionType.Add
criteria_1.EntityType = SelectionType.GeoFace
criteria_1.Criterion = SelectionCriterionType.Size
criteria_1.Operator = SelectionOperatorType.Equal
criteria_1.Value = Quantity("1.5e6 [mm^2]")
generation_criteria_3.Add(criteria_1)

criteria_2 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
criteria_2.Active = True
criteria_2.Action = SelectionActionType.Filter
criteria_2.EntityType = SelectionType.GeoFace
criteria_2.Criterion = SelectionCriterionType.LocationY
criteria_2.Operator = SelectionOperatorType.Equal
criteria_2.Value = Quantity("4500 [mm]")
generation_criteria_3.Add(criteria_2)

pres_face.Activate()
pres_face.Generate()


acoustic_region = model.AddNamedSelection()
acoustic_region.ScopingMethod = GeometryDefineByType.Worksheet
acoustic_region.Name = "acoustic_region"

generation_criteria_4 = acoustic_region.GenerationCriteria
criteria_1 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
criteria_1.Active = True
criteria_1.Action = SelectionActionType.Add
criteria_1.EntityType = SelectionType.GeoBody
criteria_1.Criterion = SelectionCriterionType.Type
criteria_1.Operator = SelectionOperatorType.Equal
criteria_1.Value = 8
generation_criteria_4.Add(criteria_1)

acoustic_region.Activate()
acoustic_region.Generate()

# %%
# Analysis settings
# ~~~~~~~~~~~~~~~~~

analysis_settings = model.Analyses[0].AnalysisSettings
analysis_settings.RangeMaximum = Quantity("100 [Hz]")
analysis_settings.SolutionIntervals = 50
analysis_settings.CalculateVelocity = True
analysis_settings.CalculateEnergy = True
analysis_settings.CalculateVolumeEnergy = True

# %%
# Boundary conditions and load
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

harmonic_acoustics = model.Analyses[0]

# %%
# Acoustic region

acoustics_region = [
    x for x in harmonic_acoustics.Children if x.Name == "Acoustics Region"
][0]
acoustics_region.Location = acoustic_region

# %%
# Surface velocity

surface_velocity = harmonic_acoustics.AddAcousticSurfaceVelocity()
surface_velocity.Location = sf_velo
surface_velocity.Magnitude.Output.DiscreteValues = [Quantity("5000 [mm s-1]")]

# %%
# Acoustic pressure

acoustic_pressure = harmonic_acoustics.AddAcousticPressure()
acoustic_pressure.Location = pres_face
acoustic_pressure.Magnitude = Quantity("1.5e-7 [MPa]")

# %%
# Acoustic absoption surface

absorption_surface = harmonic_acoustics.AddAcousticAbsorptionSurface()
absorption_surface.Location = abs_face
absorption_surface.AbsorptionCoefficient.Output.DiscreteValues = [Quantity("0.02")]

harmonic_acoustics.Activate()
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "bounday_conditions.png"
)

# %%
# Add results
# ~~~~~~~~~~~

solution = model.Analyses[0].Solution

# %%
# Acoustic pressure

acoustic_pressure_result_1 = solution.AddAcousticPressureResult()
acoustic_pressure_result_1.By = SetDriverStyle.ResultSet
acoustic_pressure_result_1.SetNumber = 25

# %%
# Acoustic velocity - total and directional

acoustic_total_velocity_1 = solution.AddAcousticTotalVelocityResult()
acoustic_total_velocity_1.Frequency = Quantity("50 [Hz]")

acoustic_directional_velocity_1 = solution.AddAcousticDirectionalVelocityResult()
acoustic_directional_velocity_1.Frequency = Quantity("50 [Hz]")
acoustic_directional_velocity_1.CoordinateSystem = lcs1

acoustic_directional_velocity_2 = solution.AddAcousticDirectionalVelocityResult()
acoustic_directional_velocity_2.NormalOrientation = NormalOrientationType.ZAxis
acoustic_directional_velocity_2.By = SetDriverStyle.ResultSet
acoustic_directional_velocity_2.SetNumber = 25

# %%
# Acoustic sound pressure and frequency bands

acoustic_spl = solution.AddAcousticSoundPressureLevel()
acoustic_spl.Frequency = Quantity("50 [Hz]")

acoustic_a_spl = solution.AddAcousticAWeightedSoundPressureLevel()
acoustic_a_spl.Frequency = Quantity("50 [Hz]")

acoustic_frq_band_spl = solution.AddAcousticFrequencyBandSPL()

a_freq_band_spl = solution.AddAcousticFrequencyBandAWeightedSPL()

z_velocity_response = solution.AddAcousticVelocityFrequencyResponse()
z_velocity_response.NormalOrientation = NormalOrientationType.ZAxis
z_velocity_response.Location = pres_face
z_velocity_response.NormalOrientation = NormalOrientationType.ZAxis

# %%
# Acoustic kinetic  and potentional energy frequency response

ke_response = solution.AddAcousticKineticEnergyFrequencyResponse()
ke_response.Location = abs_face
KE_display = ke_response.TimeHistoryDisplay

pe_response = solution.AddAcousticPotentialEnergyFrequencyResponse()
pe_response.Location = abs_face
PE_display = pe_response.TimeHistoryDisplay

# %%
# Acoustic total and directional velocity

acoustic_total_velocity_2 = solution.AddAcousticTotalVelocityResult()
acoustic_total_velocity_2.Location = pres_face
acoustic_total_velocity_2.Frequency = Quantity("30 [Hz]")
acoustic_total_velocity_2.Amplitude = True

acoustic_directional_velocity_3 = solution.AddAcousticDirectionalVelocityResult()
acoustic_directional_velocity_3.NormalOrientation = NormalOrientationType.ZAxis
acoustic_directional_velocity_3.Location = pres_face
acoustic_directional_velocity_3.Frequency = Quantity("10 [Hz]")
acoustic_directional_velocity_3.Amplitude = True

acoustic_ke = solution.AddAcousticKineticEnergy()
acoustic_ke.Location = abs_face
acoustic_ke.Frequency = Quantity("68 [Hz]")
acoustic_ke.Amplitude = True

acoustic_pe = solution.AddAcousticPotentialEnergy()
acoustic_pe.Location = abs_face
acoustic_pe.Frequency = Quantity("10 [Hz]")
acoustic_pe.Amplitude = True

# %%
# Solve
# ~~~~~

solution.Solve(True)

# sphinx_gallery_start_ignore
assert solution.Status == SolutionStatusType.Done, "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# messages
# ~~~~~~~~

messages = app.ExtAPI.Application.Messages
if messages:
    for message in messages:
        print(f"[{message.Severity}] {message.DisplayString}")
else:
    print("No [Info]/[Warning]/[Error] messages")


# %%
# Postprocessing
# ~~~~~~~~~~~~~~

# %%
# Total acoustic pressure
# ^^^^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([acoustic_pressure_result_1])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "acoustic_pressure.png"
)

# %%
# Total acoustic velocity
# ^^^^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([acoustic_pressure_result_1])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "total_velocity.png"
)

# %%
# Sound pressure level
# ^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([acoustic_spl])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "sound_pressure.png"
)

# %%
# Total velocity on pressure surface
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([acoustic_total_velocity_2])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "total_velocity_pressure.png"
)

# %%
# Kinetic energy on absorption face
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([acoustic_ke])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "kinetic_energy.png"
)

# %%
# Total acoustic pressure animation
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

press_gif = output_path / "press.gif"
acoustic_pressure_result_1.ExportAnimation(
    str(press_gif), animation_export_format, settings_720p
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
gif = Image.open(press_gif)
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


solve_path = harmonic_acoustics.WorkingDir
solve_out_path = Path(solve_path) / "solve.out"
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

mechdat_file = output_path / "harmonic_acoustics.mechdat"
app.save(str(mechdat_file))
app.new()

# delete example file
delete_downloads()
