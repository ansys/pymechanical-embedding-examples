""" .. _ref_basic_valve:

Basic Valve Implementation
--------------------------
**Author**:
`Pernelle Marone Hitz <https://github.com/pmaroneh>`_

This example demonstrates a basic implementation of a valve in Python.
"""
import os

import ansys.mechanical.core as mech
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt

# Embed Mechanical and set global variables
app = mech.App(version=232)
globals().update(mech.global_variables(app))
print(app)

geometry_path = download_file("Valve.pmdb", "pymechanical", "embedding")
analysis = Model.AddStaticStructuralAnalysis()

cwd = os.path.join(os.getcwd(), "out")


def display_image(image_name):
    path = os.path.join(os.path.join(cwd, image_name))
    image = mpimg.imread(path)
    plt.figure(figsize=(15, 15))
    plt.axis("off")
    plt.imshow(image)
    plt.show()


# %%
# Configure graphics for image export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "geometry.png"), image_export_format, settings_720p
)
display_image("geometry.png")

# %%
# Assign materials and mesh the geometry
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
display_image("mesh.png")

# %%
# Define boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
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

# %%
# Postprocessing
# ~~~~~~~~~~~~~~
# Evaluate results, export screenshots
solution = analysis.Solution
deformation = solution.AddTotalDeformation()
stress = solution.AddEquivalentStress()
solution.EvaluateAllResults()

# %%
# Deformation
Tree.Activate([deformation])
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "deformation.png"), image_export_format, settings_720p
)
display_image("deformation.png")

# %%
# Stress
Tree.Activate([stress])
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "stress.png"), image_export_format, settings_720p
)
display_image("stress.png")

# %%
# Export stress animation
animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

stress.ExportAnimation(
    os.path.join(cwd, "Valve.gif"), animation_export_format, settings_720p
)

# %%
# .. image:: /_static/basic/Valve.gif


# Save project
app.save(os.path.join(cwd, "Valve.mechdat"))
app.new()

# delete example file
delete_downloads()
