""" .. _ref_steady_state_thermal:

Steady state thermal analysis
-----------------------------

This example problem demonstrates the use of a
simple steady-state thermal analysis to determine the temperatures,
thermal gradients, heat flow rates, and heat fluxes that are caused
by thermal loads that do not vary over time.  A steady-state thermal
analysis calculates the effects of steady thermal loads on a system
or component, in this example, a long bar model.
"""

import os

from PIL import Image
import ansys.mechanical.core as mech
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

# Embed Mechanical and set global variables
app = mech.App(version=241)
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

ExtAPI.Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Iso)
ExtAPI.Graphics.Camera.SetFit()
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

geometry_import_group = Model.GeometryImportGroup
geometry_import = geometry_import_group.AddGeometryImport()
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
# Add steady state thermal analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Model.AddSteadyStateThermalAnalysis()
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS
STAT_THERM = DataModel.Project.Model.Analyses[0]
MODEL = DataModel.Project.Model
CS = MODEL.CoordinateSystems
LCS1 = CS.AddCoordinateSystem()
LCS1.OriginX = Quantity("0 [m]")

LCS2 = CS.AddCoordinateSystem()
LCS2.OriginX = Quantity("0 [m]")
LCS2.PrimaryAxisDefineBy = CoordinateSystemAlignmentType.GlobalY

# %%
# Create named selections and construction geometry
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create named selections

FACE1 = DataModel.Project.Model.AddNamedSelection()
FACE1.ScopingMethod = GeometryDefineByType.Worksheet
FACE1.Name = "Face1"
GEN_CRT1 = FACE1.GenerationCriteria
CRT1 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
CRT1.Active = True
CRT1.Action = SelectionActionType.Add
CRT1.EntityType = SelectionType.GeoFace
CRT1.Criterion = SelectionCriterionType.LocationZ
CRT1.Operator = SelectionOperatorType.Equal
CRT1.Value = Quantity("20 [m]")
GEN_CRT1.Add(CRT1)
FACE1.Activate()
FACE1.Generate()

FACE2 = DataModel.Project.Model.AddNamedSelection()
FACE2.ScopingMethod = GeometryDefineByType.Worksheet
FACE2.Name = "Face2"
GEN_CRT2 = FACE2.GenerationCriteria
CRT1 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
CRT1.Active = True
CRT1.Action = SelectionActionType.Add
CRT1.EntityType = SelectionType.GeoFace
CRT1.Criterion = SelectionCriterionType.LocationZ
CRT1.Operator = SelectionOperatorType.Equal
CRT1.Value = Quantity("0 [m]")
GEN_CRT2.Add(CRT1)
FACE2.Activate()
FACE2.Generate()

FACE3 = DataModel.Project.Model.AddNamedSelection()
FACE3.ScopingMethod = GeometryDefineByType.Worksheet
FACE3.Name = "Face3"
GEN_CRT3 = FACE3.GenerationCriteria
CRT1 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
CRT1.Active = True
CRT1.Action = SelectionActionType.Add
CRT1.EntityType = SelectionType.GeoFace
CRT1.Criterion = SelectionCriterionType.LocationX
CRT1.Operator = SelectionOperatorType.Equal
CRT1.Value = Quantity("1 [m]")
GEN_CRT3.Add(CRT1)
CRT2 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
CRT2.Active = True
CRT2.Action = SelectionActionType.Filter
CRT2.EntityType = SelectionType.GeoFace
CRT2.Criterion = SelectionCriterionType.LocationY
CRT2.Operator = SelectionOperatorType.Equal
CRT2.Value = Quantity("2 [m]")
GEN_CRT3.Add(CRT2)
CRT3 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
CRT3.Active = True
CRT3.Action = SelectionActionType.Filter
CRT3.EntityType = SelectionType.GeoFace
CRT3.Criterion = SelectionCriterionType.LocationZ
CRT3.Operator = SelectionOperatorType.Equal
CRT3.Value = Quantity("12 [m]")
GEN_CRT3.Add(CRT3)
CRT4 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
CRT4.Active = True
CRT4.Action = SelectionActionType.Add
CRT4.EntityType = SelectionType.GeoFace
CRT4.Criterion = SelectionCriterionType.LocationZ
CRT4.Operator = SelectionOperatorType.Equal
CRT4.Value = Quantity("4.5 [m]")
GEN_CRT3.Add(CRT4)
CRT5 = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
CRT5.Active = True
CRT5.Action = SelectionActionType.Filter
CRT5.EntityType = SelectionType.GeoFace
CRT5.Criterion = SelectionCriterionType.LocationY
CRT5.Operator = SelectionOperatorType.Equal
CRT5.Value = Quantity("2 [m]")
GEN_CRT3.Add(CRT5)
FACE3.Activate()
FACE3.Generate()

BODY1 = DataModel.Project.Model.AddNamedSelection()
BODY1.ScopingMethod = GeometryDefineByType.Worksheet
BODY1.Name = "Body1"
BODY1.GenerationCriteria.Add(None)
BODY1.GenerationCriteria[0].EntityType = SelectionType.GeoFace
BODY1.GenerationCriteria[0].Criterion = SelectionCriterionType.LocationZ
BODY1.GenerationCriteria[0].Operator = SelectionOperatorType.Equal
BODY1.GenerationCriteria[0].Value = Quantity("1 [m]")
BODY1.GenerationCriteria.Add(None)
BODY1.GenerationCriteria[1].EntityType = SelectionType.GeoFace
BODY1.GenerationCriteria[1].Criterion = SelectionCriterionType.LocationZ
BODY1.GenerationCriteria[1].Operator = SelectionOperatorType.Equal
BODY1.GenerationCriteria[1].Value = Quantity("1 [m]")
BODY1.Generate()

# %%
# Create construction geometry

CONST_GEOM = MODEL.AddConstructionGeometry()
Path = CONST_GEOM.AddPath()
Path.StartYCoordinate = Quantity(2, "m")
Path.StartZCoordinate = Quantity(20, "m")
Path.StartZCoordinate = Quantity(20, "m")
Path.EndXCoordinate = Quantity(2, "m")
SURF = CONST_GEOM.AddSurface()
SURF.CoordinateSystem = LCS2
CONST_GEOM.UpdateAllSolids()

# %%
# Define boundary condition and add results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Add temperature boundary conditions

TEMP = STAT_THERM.AddTemperature()
TEMP.Location = FACE1
TEMP.Magnitude.Output.DiscreteValues = [Quantity("22[C]"), Quantity("30[C]")]

TEMP2 = STAT_THERM.AddTemperature()
TEMP2.Location = FACE2
TEMP2.Magnitude.Output.DiscreteValues = [Quantity("22[C]"), Quantity("60[C]")]

TEMP.Magnitude.Inputs[0].DiscreteValues = [
    Quantity("0 [sec]"),
    Quantity("1 [sec]"),
    Quantity("2 [sec]"),
]
TEMP.Magnitude.Output.DiscreteValues = [
    Quantity("22[C]"),
    Quantity("30[C]"),
    Quantity("40[C]"),
]

TEMP2.Magnitude.Inputs[0].DiscreteValues = [
    Quantity("0 [sec]"),
    Quantity("1 [sec]"),
    Quantity("2 [sec]"),
]
TEMP2.Magnitude.Output.DiscreteValues = [
    Quantity("22[C]"),
    Quantity("50[C]"),
    Quantity("80[C]"),
]

# Radiation probe
RAD = STAT_THERM.AddRadiation()
RAD.Location = FACE3
RAD.AmbientTemperature.Inputs[0].DiscreteValues = [
    Quantity("0 [sec]"),
    Quantity("1 [sec]"),
    Quantity("2 [sec]"),
]
RAD.AmbientTemperature.Output.DiscreteValues = [
    Quantity("22[C]"),
    Quantity("30[C]"),
    Quantity("40[C]"),
]
RAD.Correlation = RadiationType.SurfaceToSurface

ANLYS_SET = STAT_THERM.AnalysisSettings
ANLYS_SET.NumberOfSteps = 2
ANLYS_SET.CalculateVolumeEnergy = True

STAT_THERM.Activate()
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "BoundaryConditions.png"), image_export_format, settings_720p
)
display_image("BoundaryConditions.png")

# %%
# Add results
# ~~~~~~~~~~~

STAT_THERM_SOLN = DataModel.Project.Model.Analyses[0].Solution
TEMP_RST = STAT_THERM_SOLN.AddTemperature()
TEMP_RST.By = SetDriverStyle.MaximumOverTime


TEMP_RST2 = STAT_THERM_SOLN.AddTemperature()
TEMP_RST2.Location = BODY1

TEMP_RST3 = STAT_THERM_SOLN.AddTemperature()
TEMP_RST3.Location = Path

TEMP_RST4 = STAT_THERM_SOLN.AddTemperature()
TEMP_RST4.Location = SURF


# Total  and directional Heat Flux

TOT_HFLUX = STAT_THERM_SOLN.AddTotalHeatFlux()
DIR_HFLUX = STAT_THERM_SOLN.AddTotalHeatFlux()
DIR_HFLUX.ThermalResultType = TotalOrDirectional.Directional
DIR_HFLUX.NormalOrientation = NormalOrientationType.ZAxis

LCS2.PrimaryAxisDefineBy = CoordinateSystemAlignmentType.GlobalZ
DIR_HFLUX.CoordinateSystem = LCS2
DIR_HFLUX.DisplayOption = ResultAveragingType.Averaged

# Thermal error

THERM_ERROR = STAT_THERM_SOLN.AddThermalError()

# Temperature probe

TEMP_PROBE = STAT_THERM_SOLN.AddTemperatureProbe()
TEMP_PROBE.GeometryLocation = FACE1
TEMP_PROBE.LocationMethod = LocationDefinitionMethod.CoordinateSystem
TEMP_PROBE.CoordinateSystemSelection = LCS2

# Heat flux probe

HFLUX_PROBE = STAT_THERM_SOLN.AddHeatFluxProbe()
HFLUX_PROBE.LocationMethod = LocationDefinitionMethod.CoordinateSystem
HFLUX_PROBE.CoordinateSystemSelection = LCS2
HFLUX_PROBE.ResultSelection = ProbeDisplayFilter.ZAxis


# Reaction probe

ANLYS_SET.NodalForces = OutputControlsNodalForcesType.Yes
REAC_PROBE = STAT_THERM_SOLN.AddReactionProbe()
REAC_PROBE.LocationMethod = LocationDefinitionMethod.GeometrySelection
REAC_PROBE.GeometryLocation = FACE1

# Radiation probe

Rad_Probe = STAT_THERM_SOLN.AddRadiationProbe()
Rad_Probe.BoundaryConditionSelection = RAD
Rad_Probe.ResultSelection = ProbeDisplayFilter.All


# %%
# Solve
# ~~~~~

STAT_THERM_SOLN.Solve(True)

# sphinx_gallery_start_ignore
assert str(STAT_THERM_SOLN.Status) == "Done", "Solution status is not 'Done'"
# sphinx_gallery_end_ignore


# %%
# Display results
# ~~~~~~~~~~~~~~~
# Total body temperature

Tree.Activate([TEMP_RST])
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "temp.png"), image_export_format, settings_720p
)
display_image("temp.png")

# %%
# Temperature on part of the body

Tree.Activate([TEMP_RST2])
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "temp2.png"), image_export_format, settings_720p
)
display_image("temp2.png")

# %%
# Temperature distribution along the specific path

Tree.Activate([TEMP_RST3])
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "temp3.png"), image_export_format, settings_720p
)
display_image("temp3.png")

# %%
# Temperature of bottom surface

Tree.Activate([TEMP_RST4])
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "temp4.png"), image_export_format, settings_720p
)
display_image("temp4.png")

# %%
# Export directional heat flux animation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tree.Activate([DIR_HFLUX])
animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

DIR_HFLUX.Activate()

DIR_HFLUX.ExportAnimation(
    os.path.join(cwd, "DirectionalHeatFlux.gif"), animation_export_format, settings_720p
)
gif = Image.open(os.path.join(cwd, "DirectionalHeatFlux.gif"))
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
# Cleanup
# ~~~~~~~
# Save project

app.save(os.path.join(cwd, "Steady_State_Thermal.mechdat"))
app.new()

# %%
# Delete example file

delete_downloads()
