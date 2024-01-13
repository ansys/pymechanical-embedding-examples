""" .. _ref_contact:

Contact debonding
--------------------------

This example demonstrates a basic implementation contact debonding in Python.
"""
import os

import ansys.mechanical.core as mech
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt

# Embed Mechanical and set global variables
app = mech.App(version=232)
globals().update(mech.global_variables(app, True))
print(app)


def display_image(image_name):
    path = os.path.join(os.path.join(cwd, image_name))
    image = mpimg.imread(path)
    plt.figure(figsize=(15, 15))
    plt.axis("off")
    plt.imshow(image)
    # plt.show()


cwd = os.path.join(os.getcwd(), "out")

# IMPORT GEOMETRY AND Materials
# Add geom from cloud

geometry_path = download_file(
    "Contact_Debonding_Example.agdb", "pymechanical", "embedding"
)
mat1_path = download_file(
    "Contact_Debonding_Example_Mat1.xml", "pymechanical", "embedding"
)
mat2_path = download_file(
    "Contact_Debonding_Example_Mat2.xml", "pymechanical", "embedding"
)
# setup  graphics

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
# settings_720p.Capture = Ansys.Mechanical.DataModel.Enums.GraphicsCaptureType.ImageOnly
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False

# import geometry
geometry_import_group = Model.GeometryImportGroup
geometry_import = geometry_import_group.AddGeometryImport()
geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import_preferences.AnalysisType = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.AnalysisType.Type2D
)
geometry_import.Import(
    geometry_path, geometry_import_format, geometry_import_preferences
)

ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "geometry.png"), image_export_format, settings_720p
)
display_image("geometry.png")
# Scenario 1 Store main Tree Object items

MODEL = Model
GEOMETRY = Model.Geometry
PART = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "Part 2"][0]

MAT_GRP = MODEL.Materials
MAT_GRP.Import(mat1_path)
MAT_GRP.Import(mat2_path)
MAT_BODY = [
    i
    for i in MAT_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.Material](True)
    if i.Name == "Interface Body Material"
][0]
MAT_CZM = [
    i
    for i in MAT_GRP.GetChildren[Ansys.ACT.Automation.Mechanical.Material](True)
    if i.Name == "CZM Crack Material"
][0]

connections = MODEL.AddConnections()
CONNECTIONS_GRP = connections.AddConnectionGroup()
MODEL.Connections.CreateAutomaticConnections()
CONNECTIONS_GRP = ExtAPI.DataModel.Project.Model.Connections
CONTACTS = [
    i
    for i in CONNECTIONS_GRP.GetChildren[
        Ansys.ACT.Automation.Mechanical.Connections.ConnectionGroup
    ](True)
    if i.Name == "Contacts"
][0]
CONTACT_REGION = [
    i
    for i in CONTACTS.GetChildren[
        Ansys.ACT.Automation.Mechanical.Connections.ContactRegion
    ](True)
    if i.Name == "Contact Region"
][0]

MESH = Model.Mesh

NAMED_SELECTIONS = ExtAPI.DataModel.Project.Model.NamedSelections
NS_EDGE_HIGH = [
    i
    for i in NAMED_SELECTIONS.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "High_Edge"
][0]
NS_EDGE_LOW = [
    i
    for i in NAMED_SELECTIONS.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Low_Edge"
][0]
NS_EDGES_SHORT = [
    i
    for i in NAMED_SELECTIONS.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Short_Edges"
][0]
NS_EDGES_LONG = [
    i
    for i in NAMED_SELECTIONS.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Long_Edges"
][0]
NS_EDGES_FIXED = [
    i
    for i in NAMED_SELECTIONS.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Fixed_Edges"
][0]
NS_VERTEX_DISP1 = [
    i
    for i in NAMED_SELECTIONS.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Disp1_Vertex"
][0]
NS_VERTEX_DISP2 = [
    i
    for i in NAMED_SELECTIONS.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Disp2_Vertex"
][0]
NS_FACES_BOTH = [
    i
    for i in NAMED_SELECTIONS.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Both_Faces"
][0]

MODEL.AddStaticStructuralAnalysis()
STATIC_STRUCTURAL = ExtAPI.DataModel.AnalysisByName("Static Structural")
ANALYSIS_SETTINGS = STATIC_STRUCTURAL.AnalysisSettings
SOLUTION = STATIC_STRUCTURAL.Solution

# Scenario 2 Set Display Unit
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM

# Scenario 3 Set 2D Behavior
GEOMETRY.Activate()
GEOMETRY.Model2DBehavior = Model2DBehavior.PlaneStrain

# Scenario 4 Assign Material
PART.Activate()
PART.Material = MAT_BODY.Name

# Scenario 5 Define Contact Region
CONTACT_REGION.Activate()
CONTACT_REGION.SourceLocation = NS_EDGE_HIGH
CONTACT_REGION.TargetLocation = NS_EDGE_LOW
CONTACT_REGION.ContactType = ContactType.Bonded
CONTACT_REGION.ContactFormulation = ContactFormulation.PurePenalty

# Scenario 6 Define Mesh controls and generate mesh
MESH.Activate()
MESH.ElementOrder = ElementOrder.Quadratic
MESH.UseAdaptiveSizing = False
MESH.ElementSize = Quantity("0.75 [mm]")

SIZING_MESH = MESH.AddSizing()
SIZING_MESH.Location = NS_EDGES_SHORT
SIZING_MESH.ElementSize = Quantity("0.75 [mm]")
SIZING_MESH.Behavior = SizingBehavior.Hard

SIZING_MESH2 = MESH.AddSizing()
SIZING_MESH2.Location = NS_EDGES_LONG
SIZING_MESH2.ElementSize = Quantity("0.5 [mm]")
SIZING_MESH2.Behavior = SizingBehavior.Hard

FACE_MESHING = MESH.AddFaceMeshing()
FACE_MESHING.Location = NS_FACES_BOTH
FACE_MESHING.Method = FaceMeshingMethod.Quadrilaterals

MESH.Activate()
MESH.GenerateMesh()
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "mesh.png"), image_export_format, settings_720p
)
display_image("mesh.png")
# Scenario 7 Add Contact Debonding object
MODEL.Activate()
FRACTURE = MODEL.AddFracture()

CONTACT_DEBONDING = FRACTURE.AddContactDebonding()
CONTACT_DEBONDING.Material = MAT_CZM.Name
CONTACT_DEBONDING.ContactRegion = CONTACT_REGION

# Scenario 8 Define Analysis Settings
ANALYSIS_SETTINGS.Activate()
ANALYSIS_SETTINGS.AutomaticTimeStepping = AutomaticTimeStepping.On
ANALYSIS_SETTINGS.DefineBy = TimeStepDefineByType.Substeps
ANALYSIS_SETTINGS.MaximumSubsteps = 100
ANALYSIS_SETTINGS.InitialSubsteps = 100
ANALYSIS_SETTINGS.MinimumSubsteps = 100
ANALYSIS_SETTINGS.LargeDeflection = True

# Scenario 9 Define boundary conditions
STATIC_STRUCTURAL.Activate()
FIXED_SUPPORT = STATIC_STRUCTURAL.AddFixedSupport()
FIXED_SUPPORT.Location = NS_EDGES_FIXED

STATIC_STRUCTURAL.Activate()
DISPLACEMENT = STATIC_STRUCTURAL.AddDisplacement()
DISPLACEMENT.Location = NS_VERTEX_DISP1
DISPLACEMENT.DefineBy = LoadDefineBy.Components
DISPLACEMENT.YComponent.Output.DiscreteValues = [Quantity("10 [mm]")]

STATIC_STRUCTURAL.Activate()
DISPLACEMENT2 = STATIC_STRUCTURAL.AddDisplacement()
DISPLACEMENT2.Location = NS_VERTEX_DISP2
DISPLACEMENT2.DefineBy = LoadDefineBy.Components
DISPLACEMENT2.YComponent.Output.DiscreteValues = [Quantity("-10 [mm]")]

# Scenario 10 Add results
SOLUTION.Activate()
DIRECTIONAL_DEFORMATION = SOLUTION.AddDirectionalDeformation()
DIRECTIONAL_DEFORMATION.NormalOrientation = NormalOrientationType.YAxis

FORCE_REACTION = SOLUTION.AddForceReaction()
FORCE_REACTION.BoundaryConditionSelection = DISPLACEMENT

# Scenario 11 Solve and review results
STATIC_STRUCTURAL.Activate()
STATIC_STRUCTURAL.Solve(True)

DIRECTIONAL_DEFORMATION.Activate()
MIN_DIRECTIONAL_DEFORMATION = DIRECTIONAL_DEFORMATION.Minimum.Value
MAX_DIRECTIONAL_DEFORMATION = DIRECTIONAL_DEFORMATION.Maximum.Value

FORCE_REACTION.Activate()
Y_AXIS_FORCE_REACTION = FORCE_REACTION.YAxis.Value
MOT_Y_AXIS_FORCE_REACTION = FORCE_REACTION.MaximumYAxis.Value
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "contact_force.png"), image_export_format, settings_720p
)
display_image("contact_force.png")

# %%
# Export animation
animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

FORCE_REACTION.ExportAnimation(
    os.path.join(cwd, "force.gif"), animation_export_format, settings_720p
)

## add messages in between

app.save(os.path.join(cwd, "debonding.mechdat"))
app.new()

# delete example file
delete_downloads()
