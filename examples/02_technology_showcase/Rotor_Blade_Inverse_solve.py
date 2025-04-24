""".. _ref_example_10_td_055:

Inverse-Solving analysis of a rotor fan blade with disk
-------------------------------------------------------

This example demonstrates the inverse-solving analysis of a rotor fan blade with disk.
The NASA Rotor 67 fan bladed disk is a subsystem of a turbo fan's compressor set used
in aerospace engine applications. This sector model, representing a challenging industrial
example for which the detailed geometry and flow information is available in the public
domain, consists of a disk and a fan blade with a sector angle of 16.364 degrees.
The sector model represents the running condition or hot geometry of the blade. It is
already optimized at the running condition under loading. The primary objective is to
obtain the cold geometry (for manufacturing) from the given hot geometry using inverse solving.

- ELEMENTS: SOLID186
- MATERIAL: Elastic Material
- CONTACT:  MPC bonded contact pair

To highlight Mechanical APDL inverse-solving technology, this example problem does not
involve a cyclic symmetry analysis.

**Material Properties:**

+------------+--------+----------------+----------------+---------------------------+
| Temperature| Density| Young's Modulus| Poisson's Ratio| Coeff of Thermal Expansion|
+============+========+================+================+===========================+
| 22 deg C   | 7840   | 2.2e11 Pa      | 0.27           | 1.2e-5                    |
+------------+--------+----------------+----------------+---------------------------+
| 200 deg C  | 7740   | 2e11 Pa        | 0.28           | 1.3e-5                    |
+------------+--------+----------------+----------------+---------------------------+
| 300 deg C  | 7640   | 1.9e11 Pa      | 0.29           | 1.4e-5                    |
+------------+--------+----------------+----------------+---------------------------+
| 600 deg C  | 7540   | 1.8e11 Pa      | 0.30           | 1.5e-5                    |
+------------+--------+----------------+----------------+---------------------------+


**Following loads are considered:**

The rotational velocity (CGOMGA,0,0,1680) is applied along the global Z axis. The reference
temperature is maintained at 22°C, and the temperature loading is applied on the blade (BF)

**Expected results:**

Inverse-Solving Analysis: A nonlinear static analysis using inverse solving
(INVOPT,ON) is performed on the hot geometry of the model to obtain the cold geometry
(for manufacturing) and the stress/strain results on the hot geometry.

"""

from pathlib import Path

from ansys.mechanical.core import App
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt

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
# Download required files
# ~~~~~~~~~~~~~~~~~~~~~~~
# Download the geometry file

geometry_path = download_file(
    "example_10_td_055_Rotor_Blade_Geom.pmdb", "pymechanical", "embedding"
)

# %%
# Download the material file

mat_path = download_file(
    "example_10_td_055_Rotor_Blade_Mat_File.xml", "pymechanical", "embedding"
)

# %%
# Download the CFX pressure data

cfx_data_path = download_file(
    "example_10_CFX_ExportResults_FT_10P_EO2.csv", "pymechanical", "embedding"
)


# %%
# Download required Temperature file

temp_data_path = download_file(
    "example_10_Temperature_Data.txt", "pymechanical", "embedding"
)

# %%
# Configure graphics for image export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

graphics = app.Graphics
camera = graphics.Camera

camera.SetSpecificViewOrientation(
    Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Iso
)
camera.SetFit()
image_export_format = Ansys.Mechanical.DataModel.Enums.GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = (
    Ansys.Mechanical.DataModel.Enums.GraphicsResolutionType.EnhancedResolution
)
settings_720p.Background = Ansys.Mechanical.DataModel.Enums.GraphicsBackgroundType.White
settings_720p.Width = 1280
# settings_720p.Capture = Ansys.Mechanical.DataModel.Enums.GraphicsCaptureType.ImageOnly
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False

# %%
# Import geometry
# ~~~~~~~~~~~~~~~
# Reads geometry file and display

model = app.Model

geometry_import_group = model.GeometryImportGroup
geometry_import = geometry_import_group.AddGeometryImport()
geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import_preferences.NamedSelectionKey = ""
geometry_import_preferences.ProcessMaterialProperties = True
geometry_import_preferences.ProcessCoordinateSystems = True
geometry_import.Import(
    geometry_path, geometry_import_format, geometry_import_preferences
)

app.plot()

# %%
# Assign materials
# ~~~~~~~~~~~~~~~~
# Import material from xml file and assign it to bodies

materials = model.Materials
materials.Import(mat_path)

part1 = [x for x in app.Tree.AllObjects if x.Name == "Component2\Rotor11"][0]
part2 = [x for x in app.Tree.AllObjects if x.Name == "Component3"][0]
part2_blade1 = part2.Children[0]
part2_blade2 = part2.Children[1]
part2_blade3 = part2.Children[2]
part1.Material = "MAT1 (Setup, File1)"
part2_blade1.Material = "MAT1 (Setup, File1)"
part2_blade2.Material = "MAT1 (Setup, File1)"
part2_blade3.Material = "MAT1 (Setup, File1)"

# %%
# Define units system and store variables
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Select MKS units
app.ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

# Store all main tree nodes as variables
geometry = model.Geometry
mesh = model.Mesh
materials = model.Materials
coordinate_systems = model.CoordinateSystems
named_selections = model.NamedSelections

# %%
# Define named selection
# ~~~~~~~~~~~~~~~~~~~~~~
# Create NS for named selection

blade_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade"][0]
blade_surface_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade_Surf"][0]
fix_support_ns = [x for x in app.Tree.AllObjects if x.Name == "Fix_Support"][0]
blade_hub_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade_Hub"][0]
hub_contact_ns = [x for x in app.Tree.AllObjects if x.Name == "Hub_Contact"][0]
blade_target_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade_Target"][0]
hub_low_ns = [x for x in app.Tree.AllObjects if x.Name == "Hub_Low"][0]
hub_high_ns = [x for x in app.Tree.AllObjects if x.Name == "Hub_High"][0]
blade1_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade1"][0]
blade1_source_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade1_Source"][0]
blade1_target_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade1_Target"][0]
blade2_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade2"][0]
blade2_source_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade2_Source"][0]
blade2_target_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade2_Target"][0]
blade3_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade3"][0]
blade3_source_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade3_Source"][0]
blade3_target_ns = [x for x in app.Tree.AllObjects if x.Name == "Blade3_Target"][0]

# %%
# Define coordinate system
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Create cylindrical coordinate system

coordinate_systems = model.CoordinateSystems
coord_system = coordinate_systems.AddCoordinateSystem()
coord_system.CoordinateSystemType = (
    Ansys.ACT.Interfaces.Analysis.CoordinateSystemTypeEnum.Cylindrical
)
coord_system.OriginDefineBy = CoordinateSystemAlignmentType.Component
coord_system.OriginDefineBy = CoordinateSystemAlignmentType.Fixed

# %%
# Define contacts
# ~~~~~~~~~~~~~~~

# Define connections

connections = model.Connections
contact_region1 = connections.AddContactRegion()
contact_region1.SourceLocation = named_selections.Children[6]
contact_region1.TargetLocation = named_selections.Children[5]
contact_region1.Behavior = ContactBehavior.AutoAsymmetric
contact_region1.ContactFormulation = ContactFormulation.MPC

# %%
# Define mesh settings and generate mesh
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mesh = model.Mesh
mesh.ElementSize = Quantity(0.004, "m")
mesh.UseAdaptiveSizing = False
mesh.MaximumSize = Quantity(0.004, "m")
mesh.ShapeChecking = 0
automatic_method_Hub = mesh.AddAutomaticMethod()
automatic_method_Hub.Location = named_selections.Children[0]
automatic_method_Hub.Method = MethodType.Sweep
automatic_method_Hub.SweepNumberDivisions = 6

match_control_Hub = mesh.AddMatchControl()
match_control_Hub.LowNamedSelection = named_selections.Children[7]
match_control_Hub.HighNamedSelection = named_selections.Children[8]
cyc_coordinate_system = coordinate_systems.Children[1]
match_control_Hub.RotationAxis = cyc_coordinate_system

sizing_Blade = mesh.AddSizing()
selection = named_selections.Children[5]
sizing_Blade.Location = selection
# sizing_Blade.ElementSize = Quantity(1e-3, "m")
sizing_Blade.ElementSize = Quantity(1e-2, "m")
sizing_Blade.CaptureCurvature = True
sizing_Blade.CurvatureNormalAngle = Quantity(0.31, "rad")
# sizing_Blade.LocalMinimumSize = Quantity(0.00025, "m")
sizing_Blade.LocalMinimumSize = Quantity(0.0005, "m")

automatic_method_Blade1 = mesh.AddAutomaticMethod()
selection = named_selections.Children[9]
automatic_method_Blade1.Location = selection
automatic_method_Blade1.Method = MethodType.Sweep
automatic_method_Blade1.SourceTargetSelection = 2
selection = named_selections.Children[10]
automatic_method_Blade1.SourceLocation = selection
selection = named_selections.Children[11]
automatic_method_Blade1.TargetLocation = selection
automatic_method_Blade1.SweepNumberDivisions = 5

automatic_method_Blade2 = mesh.AddAutomaticMethod()
selection = named_selections.Children[12]
automatic_method_Blade2.Location = selection
automatic_method_Blade2.Method = MethodType.Sweep
automatic_method_Blade2.SourceTargetSelection = 2
selection = named_selections.Children[13]
automatic_method_Blade2.SourceLocation = selection
selection = named_selections.Children[14]
automatic_method_Blade2.TargetLocation = selection
automatic_method_Blade2.SweepNumberDivisions = 5

automatic_method_Blade3 = mesh.AddAutomaticMethod()
selection = named_selections.Children[15]
automatic_method_Blade3.Location = selection
automatic_method_Blade3.Method = MethodType.Sweep
automatic_method_Blade3.SourceTargetSelection = 2
selection = named_selections.Children[16]
automatic_method_Blade3.SourceLocation = selection
selection = named_selections.Children[17]
automatic_method_Blade3.TargetLocation = selection
automatic_method_Blade3.SweepNumberDivisions = 5

mesh.GenerateMesh()
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "blade_mesh.png"
)

# %%
# Define analysis settings
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Setup static structural settings with inverse solve

model.AddStaticStructuralAnalysis()
static_structural_analysis = model.Analyses[0]
analysis_settings = app.ExtAPI.DataModel.Project.Model.Analyses[0].AnalysisSettings
analysis_settings.AutomaticTimeStepping = AutomaticTimeStepping.On
analysis_settings.NumberOfSubSteps = 10

analysis_settings.Activate()

cmd1 = static_structural_analysis.AddCommandSnippet()
# Add convergence criterion using command snippet.
archard_wear_model = """CNVTOL,U,1.0,5e-5,1,,"""
cmd1.AppendText(archard_wear_model)

analysis_settings.InverseOption = True
analysis_settings.LargeDeflection = True

# %%
# Define boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Apply rotational velocity

rotational_velocity = static_structural_analysis.AddRotationalVelocity()
rotational_velocity.DefineBy = LoadDefineBy.Components
rotational_velocity.ZComponent.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
]
rotational_velocity.ZComponent.Output.DiscreteValues = [
    Quantity("0 [rad/s]"),
    Quantity("1680 [rad/s]"),
    Quantity("1680 [rad/s]"),
]

# Apply Fixed Support Condition

fixed_support = static_structural_analysis.AddFixedSupport()
selection = named_selections.Children[3]
fixed_support.Location = selection


# %%
# Import CFX pressure
# ~~~~~~~~~~~~~~~~~~~
# Import CFX pressure data and apply it to structural blade surface

imported_load_group = static_structural_analysis.AddImportedLoadExternalData()

external_data_files = Ansys.Mechanical.ExternalData.ExternalDataFileCollection()
external_data_files.SaveFilesWithProject = False
external_data_file_1 = Ansys.Mechanical.ExternalData.ExternalDataFile()
external_data_files.Add(external_data_file_1)
external_data_file_1.Identifier = "File1"
external_data_file_1.Description = ""
external_data_file_1.IsMainFile = False
external_data_file_1.FilePath = cfx_data_path
external_data_file_1.ImportSettings = (
    Ansys.Mechanical.ExternalData.ImportSettingsFactory.GetSettingsForFormat(
        Ansys.Mechanical.DataModel.MechanicalEnums.ExternalData.ImportFormat.Delimited
    )
)
import_settings = external_data_file_1.ImportSettings
import_settings.SkipRows = 17
import_settings.SkipFooter = 0
import_settings.Delimiter = ","
import_settings.AverageCornerNodesToMidsideNodes = False
import_settings.UseColumn(
    0,
    Ansys.Mechanical.DataModel.MechanicalEnums.ExternalData.VariableType.XCoordinate,
    "m",
    "X Coordinate@A",
)
import_settings.UseColumn(
    1,
    Ansys.Mechanical.DataModel.MechanicalEnums.ExternalData.VariableType.YCoordinate,
    "m",
    "Y Coordinate@B",
)
import_settings.UseColumn(
    2,
    Ansys.Mechanical.DataModel.MechanicalEnums.ExternalData.VariableType.ZCoordinate,
    "m",
    "Z Coordinate@C",
)
import_settings.UseColumn(
    3,
    Ansys.Mechanical.DataModel.MechanicalEnums.ExternalData.VariableType.Pressure,
    "Pa",
    "Pressure@D",
)

imported_load_group.ImportExternalDataFiles(external_data_files)
imported_pressure = imported_load_group.AddImportedPressure()
selection = named_selections.Children[2]
imported_pressure.Location = selection
imported_pressure.AppliedBy = LoadAppliedBy.Direct
imported_pressure.ImportLoad()

app.Tree.Activate([imported_pressure])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "imported_pressure.png"
)

###################################################################################
# Import Temperature
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import temperature data and apply it to structural blade

imported_load_group = static_structural_analysis.AddImportedLoadExternalData()

external_data_files = Ansys.Mechanical.ExternalData.ExternalDataFileCollection()
external_data_files.SaveFilesWithProject = False
external_data_file_1 = Ansys.Mechanical.ExternalData.ExternalDataFile()
external_data_files.Add(external_data_file_1)
external_data_file_1.Identifier = "File1"
external_data_file_1.Description = ""
external_data_file_1.IsMainFile = False
external_data_file_1.FilePath = temp_data_path

external_data_file_1.ImportSettings = (
    Ansys.Mechanical.ExternalData.ImportSettingsFactory.GetSettingsForFormat(
        Ansys.Mechanical.DataModel.MechanicalEnums.ExternalData.ImportFormat.Delimited
    )
)
import_settings = external_data_file_1.ImportSettings
import_settings.SkipRows = 0
import_settings.SkipFooter = 0
import_settings.Delimiter = ","
import_settings.AverageCornerNodesToMidsideNodes = False
import_settings.UseColumn(
    0,
    Ansys.Mechanical.DataModel.MechanicalEnums.ExternalData.VariableType.XCoordinate,
    "m",
    "X Coordinate@A",
)
import_settings.UseColumn(
    1,
    Ansys.Mechanical.DataModel.MechanicalEnums.ExternalData.VariableType.YCoordinate,
    "m",
    "Y Coordinate@B",
)
import_settings.UseColumn(
    2,
    Ansys.Mechanical.DataModel.MechanicalEnums.ExternalData.VariableType.ZCoordinate,
    "m",
    "Z Coordinate@C",
)
import_settings.UseColumn(
    3,
    Ansys.Mechanical.DataModel.MechanicalEnums.ExternalData.VariableType.Temperature,
    "C",
    "Temperature@D",
)

imported_load_group.ImportExternalDataFiles(external_data_files)
imported_body_temperature = imported_load_group.AddImportedBodyTemperature()

selection = named_selections.Children[1]
imported_body_temperature.Location = selection
imported_body_temperature.ImportLoad()

app.Tree.Activate([imported_body_temperature])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "imported_temperature.png"
)

# %%
# Postprocessing
# ~~~~~~~~~~~~~~
# Insert results

solution = static_structural_analysis.Solution

total_deformation1 = solution.AddTotalDeformation()
total_deformation1.DisplayTime = Quantity("1 [s]")

equivalent_stress1 = solution.AddEquivalentStress()
equivalent_stress1.DisplayTime = Quantity("1 [s]")

equivalent_total_strain1 = solution.AddEquivalentTotalStrain()
equivalent_total_strain1.DisplayTime = Quantity("1 [s]")

thermal_strain1 = solution.AddThermalStrain()
thermal_strain1.DisplayTime = Quantity("1 [s]")


# %%
# Run Solution
# ~~~~~~~~~~~~
# Solve inverse analysis on blade model

solution.Solve(True)
soln_status = solution.Status

# %%
# Postprocessing
# ~~~~~~~~~~~~~~
# Evaluate results and export screenshots

# %%
# Total deformation

app.Tree.Activate([total_deformation1])
graphics.ViewOptions.ResultPreference.ExtraModelDisplay = (
    Ansys.Mechanical.DataModel.MechanicalEnums.Graphics.ExtraModelDisplay.NoWireframe
)
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "total_deformation.png"
)

# %%
# Equivalent stress

app.Tree.Activate([thermal_strain1])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "thermal_strain.png"
)

# %%
# Cleanup
# ~~~~~~~
# Save project

mechdat_file = output_path / "blade_inverse.mechdat"
app.save(str(mechdat_file))
app.new()

# %%
# Delete example file

delete_downloads()
