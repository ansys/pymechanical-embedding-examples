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

cwd = Path.cwd() / "out"


def display_image(image_name):
    plt.figure(figsize=(16, 9))
    image_path = cwd / image_name
    plt.imshow(mpimg.imread(image_path))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.show()


# %%
# Configure graphics for image export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
camera.Rotate(180, CameraAxisType.ScreenY)

# %%
# Download geometry and materials files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

geometry_path = download_file("C_GEOMETRY.agdb", "pymechanical", "embedding")
mat_path = download_file("Air-material.xml", "pymechanical", "embedding")

# %%
# Import the geometry
# ~~~~~~~~~~~~~~~~~~~

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

geometry = model.Geometry

solid1 = geometry.Children[0]
solid2 = geometry.Children[1]
solid3 = geometry.Children[2]
solid4 = geometry.Children[3]
solid5 = geometry.Children[4]
solid6 = geometry.Children[5]
solid7 = geometry.Children[6]
solid8 = geometry.Children[7]
solid9 = geometry.Children[8]
solid10 = geometry.Children[9]
solid11 = geometry.Children[10]

solid1.Suppressed = True
solid2.Suppressed = True
solid3.Suppressed = True
solid4.Suppressed = True
solid5.Suppressed = True
solid7.Suppressed = True
solid10.Suppressed = True
solid11.Suppressed = True

app.plot()

# %%
# Store all Variables necessary for analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mesh = model.Mesh
named_selection = model.NamedSelections
connection = model.Connections
coordinate_systems = model.CoordinateSystems
mat = model.Materials

# %%
# Setup the Analysis
# ~~~~~~~~~~~~~~~~~~
# Add harmonic acoustics and unit system

model.AddHarmonicAcousticAnalysis()
app.ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

# %%
# Import and assign materials

mat.Import(mat_path)
solid6.Material = "Air"
solid8.Material = "Air"
solid9.Material = "Air"

# %%
# Create coordinate system
lcs1 = coordinate_systems.AddCoordinateSystem()
lcs1.OriginX = Quantity("0 [mm]")
lcs1.OriginY = Quantity("0 [mm]")
lcs1.OriginZ = Quantity("0 [mm]")
lcs1.PrimaryAxisDefineBy = CoordinateSystemAlignmentType.GlobalZ

# %%
# Generate mesh

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
camera.SetFit()
boundary_condition_image = cwd / "bounday_conditions.png"
graphics.ExportImage(str(boundary_condition_image), image_export_format, settings_720p)
display_image("bounday_conditions.png")

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
acoustic_pressure_image = cwd / "acoustic_pressure.png"
graphics.ExportImage(str(acoustic_pressure_image), image_export_format, settings_720p)
display_image("acoustic_pressure.png")

# %%
# Total acoustic velocity
# ^^^^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([acoustic_pressure_result_1])
total_velocity_image = cwd / "total_velocity.png"
graphics.ExportImage(str(total_velocity_image), image_export_format, settings_720p)
display_image("total_velocity.png")

# %%
# Sound pressure level
# ^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([acoustic_spl])
sound_pressure_image = cwd / "sound_pressure.png"
graphics.ExportImage(str(sound_pressure_image), image_export_format, settings_720p)
display_image("sound_pressure.png")

# %%
# Total velocity on pressure surface
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([acoustic_total_velocity_2])
total_velocity_pressure_image = cwd / "total_velocity_pressure.png"
graphics.ExportImage(
    str(total_velocity_pressure_image), image_export_format, settings_720p
)
display_image("total_velocity_pressure.png")

# %%
# Kinetic energy on absorption face
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([acoustic_ke])
kinetic_energy_image = cwd / "kinetic_energy.png"
graphics.ExportImage(str(kinetic_energy_image), image_export_format, settings_720p)
display_image("kinetic_energy.png")

# %%
# Total acoustic pressure animation
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

press_gif = cwd / "press.gif"
acoustic_pressure_result_1.ExportAnimation(
    str(press_gif), animation_export_format, settings_720p
)
gif = Image.open(press_gif)
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

mechdat_file = cwd / "harmonic_acoustics.mechdat"
app.save(str(mechdat_file))
app.new()

# delete example file
delete_downloads()
