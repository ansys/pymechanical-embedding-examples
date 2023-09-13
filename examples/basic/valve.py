""" .. _ref_basic_valve:
Example: Basic Valve Implementation

This example demonstrates a basic implementation of a valve in Python.
"""
import os

import ansys.mechanical.core as mech
from ansys.mechanical.core.examples import delete_downloads, download_file

# Embed Mechanical and set global variables

app = mech.App(version=232)
globals().update(mech.global_variables(app))
print(app)

geometry_path = download_file("Valve.pmdb", "pymechanical", "embedding")
analysis = Model.AddStaticStructuralAnalysis()

cwd = os.path.join(os.getcwd(), "out")

# Configure graphics for image export
ExtAPI.Graphics.Camera.SetSpecificViewOrientation(
    Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Iso
)
ExtAPI.Graphics.Camera.SetFit()
image_export_format = Ansys.Mechanical.DataModel.Enums.GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = (
    Ansys.Mechanical.DataModel.Enums.GraphicsResolutionType.EnhancedResolution
)
settings_720p.Background = Ansys.Mechanical.DataModel.Enums.GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Capture = Ansys.Mechanical.DataModel.Enums.GraphicsCaptureType.ImageOnly
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False

# Import geometry
geometry_file = geometry_path
geometry_import = Model.GeometryImportGroup.AddGeometryImport()
geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import.Import(
    geometry_file, geometry_import_format, geometry_import_preferences
)

ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "geometry.png"), image_export_format, settings_720p
)
###############################################################################
# Export the geometry
# --------------
# .. image:: /_static/basic/valve/geometry.png


# Assign materials
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

# Define mesh settings,  generate mesh
mesh = Model.Mesh
mesh.ElementSize = Quantity(25, "mm")
mesh.GenerateMesh()
Tree.Activate([mesh])
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "mesh.png"), image_export_format, settings_720p
)

# Define boundary conditions

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

# Solve model
config = ExtAPI.Application.SolveConfigurations["My Computer"]
config.SolveProcessSettings.MaxNumberOfCores = 1
config.SolveProcessSettings.DistributeSolution = False
Model.Solve()

# Evaluate results, export screenshots
solution = analysis.Solution
deformation = solution.AddTotalDeformation()
stress = solution.AddEquivalentStress()
solution.EvaluateAllResults()

Tree.Activate([deformation])
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "deformation.png"), image_export_format, settings_720p
)
Tree.Activate([stress])
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "stress.png"), image_export_format, settings_720p
)

# Export stress animation
animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.MP4
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

stress.ExportAnimation(
    os.path.join(cwd, "Valve.mp4"), animation_export_format, settings_720p
)

# Save project
app.save(os.path.join(cwd, "Valve.mechdat"))
app.new()

# delete example file
delete_downloads()
