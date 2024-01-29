""" .. _ref_modal:

Modal acoustics
---------------
This example demonstrates a modal acoustics analysis.
"""
# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

import os

from PIL import Image
import ansys.mechanical.core as mech
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

# %%
# Embed mechanical and set global variables

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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ExtAPI.Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Front)
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False

geometry_path = download_file("sloshing_geometry.agdb", "pymechanical", "embedding")
mat_path = download_file("Water_material_explicit.xml", "pymechanical", "embedding")


# import geometry
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
Model.AddModalAcousticAnalysis()
material = DataModel.Project.Model.Materials
material.Import(mat_path)
# "Store all main tree nodes as variables")
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

GEOM = DataModel.Project.Model.Geometry
MESH = DataModel.Project.Model.Mesh
NS = DataModel.Project.Model.NamedSelections
CONN = DataModel.Project.Model.Connections

# "Get all required named selections as variables")
acst_bodies = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Acoustic_bodies"
][0]
struct_bodies = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Structural_bodies"
][0]
top_bodies = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "top_bodies"
][0]
cont_bodies = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "container_bodies"
][0]
cont_V1 = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Cont_V1"
][0]
cont_V2 = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Cont_V2"
][0]
cont_V3 = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Cont_V3"
][0]
cont_face1 = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Cont_face1"
][0]
cont_face2 = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Cont_face2"
][0]
cont_face3 = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Cont_face3"
][0]
cont_face4 = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Cont_face4"
][0]
free_faces = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "Free_faces"
][0]
fsi_faces = [
    i
    for i in NS.GetChildren[Ansys.ACT.Automation.Mechanical.NamedSelection](True)
    if i.Name == "FSI_faces"
][0]

# "Assign thickness to surface body and Water to Acoustic parts")
solid1 = [
    i
    for i in GEOM.GetChildren[Ansys.ACT.Automation.Mechanical.Body](True)
    if i.Name == "Solid1"
][0]
solid2 = [
    i
    for i in GEOM.GetChildren[Ansys.ACT.Automation.Mechanical.Body](True)
    if i.Name == "Solid2"
][0]
solid3 = [
    i
    for i in GEOM.GetChildren[Ansys.ACT.Automation.Mechanical.Body](True)
    if i.Name == "Solid3"
][0]
solid4 = [
    i
    for i in GEOM.GetChildren[Ansys.ACT.Automation.Mechanical.Body](True)
    if i.Name == "Solid4"
][0]

solid1.Assignment = "WATER"
solid2.Assignment = "WATER"
solid3.Assignment = "WATER"
solid4.Assignment = "WATER"

# "Insert mesh sizing")
# Element order
# 0-Program Controlled
# 1-Linear
# 2-Quadratic
# MESH.ElementMidsideNodes = 1
MESH.ElementOrder = ElementOrder.Quadratic

# Add MESH method
method1 = MESH.AddAutomaticMethod()
method1.Location = acst_bodies
# Use Hex Dominant method
method1.Method = MethodType.AllTriAllTet

# Add mesh method
method2 = MESH.AddAutomaticMethod()
method2.Location = top_bodies
# Use Hex Dominant method
method2.Method = MethodType.Automatic

# Add mesh sizing
sizing1 = MESH.AddSizing()
sizing1.Location = top_bodies
sizing1.ElementSize = Quantity("0.2 [m]")
sizing1.Behavior = SizingBehavior.Hard

# Add mesh sizing
sizing2 = MESH.AddSizing()
sizing2.Location = acst_bodies
sizing2.ElementSize = Quantity("0.2 [m]")
sizing2.Behavior = SizingBehavior.Hard

# Add mesh method
method3 = MESH.AddAutomaticMethod()
method3.Location = cont_bodies
# Use Hex Dominant method
method3.Method = MethodType.Sweep
# Manual source target selection
# 0-Automatic
# 1-Manual Source
# 2-Manual Source and Target
# 3-Automatic Thin
# 4-Manual Thin
method3.SourceTargetSelection = 4

MESH.GenerateMesh()

# "Insert contacts")
# Contact 1
CONN_GROUP = CONN.AddConnectionGroup()
CONT1 = CONN_GROUP.AddContactRegion()
CONT1.SourceLocation = cont_V1
CONT1.TargetLocation = cont_face1
CONT1.ContactFormulation = ContactFormulation.MPC
CONT1.Behavior = ContactBehavior.Asymmetric
CONT1.PinballRegion = ContactPinballType.Radius
CONT1.PinballRadius = Quantity("0.25 [m]")

# Contact 2
CONT2 = CONN_GROUP.AddContactRegion()
CONT2.SourceLocation = cont_V2
CONT2.TargetLocation = cont_face2
CONT2.ContactFormulation = ContactFormulation.MPC
CONT2.Behavior = ContactBehavior.Asymmetric
CONT2.PinballRegion = ContactPinballType.Radius
CONT2.PinballRadius = Quantity("0.25 [m]")

# Contact 3
CONT3 = CONN_GROUP.AddContactRegion()
CONT3.SourceLocation = cont_V3
CONT3.TargetLocation = cont_face3
CONT3.ContactFormulation = ContactFormulation.MPC
CONT3.Behavior = ContactBehavior.Asymmetric
CONT3.PinballRegion = ContactPinballType.Radius
CONT3.PinballRadius = Quantity("0.25 [m]")

# Contact 3
sel_manager = ExtAPI.SelectionManager
# cnv4 = [250]
cnv4 = DataModel.GeoData.Assemblies[0].Parts[1].Bodies[0].Vertices[3]
cont_V4 = sel_manager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
cont_V4.Entities = [cnv4]
# sel_manager.NewSelection(cont_V4)  #This command is to do the selection in

# cont_V4.Ids = cnv4
CONT4 = CONN_GROUP.AddContactRegion()
CONT4.TargetLocation = cont_face4
CONT4.SourceLocation = cont_V4
CONT4.ContactFormulation = ContactFormulation.MPC
CONT4.Behavior = ContactBehavior.Asymmetric
CONT4.PinballRegion = ContactPinballType.Radius
CONT4.PinballRadius = Quantity("0.25 [m]")

# "Fully define Modal Multiphysics region with two physics regions")
MODAL_ACST = DataModel.Project.Model.Analyses[0]
ACOUST_REG = MODAL_ACST.Children[2]
ACOUST_REG.Location = acst_bodies

# Insert new physics region for Structural
STRUCT_REG = MODAL_ACST.AddPhysicsRegion()
STRUCT_REG.Structural = True
STRUCT_REG.RenameBasedOnDefinition()
STRUCT_REG.Location = struct_bodies

# "Setup Modal acoustic for sloshing model")
ANALYSIS_SETTINGS = MODAL_ACST.Children[1]
ANALYSIS_SETTINGS.MaximumModesToFind = 12
ANALYSIS_SETTINGS.SearchRangeMinimum = Quantity("0.1 [Hz]")
ANALYSIS_SETTINGS.SolverType = SolverType.Unsymmetric
ANALYSIS_SETTINGS.GeneralMiscellaneous = True

FREE_SF = MODAL_ACST.AddAcousticFreeSurface()
FREE_SF.Location = free_faces

FSI_OBJ = MODAL_ACST.AddFluidSolidInterface()
FSI_OBJ.Location = fsi_faces

ACCELERATION = MODAL_ACST.AddAcceleration()
ACCELERATION.DefineBy = LoadDefineBy.Components
ACCELERATION.YComponent.Output.DiscreteValues = [Quantity("9.81 [m sec^-1 sec^-1]")]

# Vertices for Fixed Support
# vert = [241, 244, 238, 249]
# vobj = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
# vobj.Ids = vert
fv1 = DataModel.GeoData.Assemblies[0].Parts[1].Bodies[0].Vertices[0]
fv2 = DataModel.GeoData.Assemblies[0].Parts[1].Bodies[1].Vertices[0]
fv3 = DataModel.GeoData.Assemblies[0].Parts[1].Bodies[2].Vertices[0]
fv4 = DataModel.GeoData.Assemblies[0].Parts[1].Bodies[3].Vertices[0]

fvert = sel_manager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
fvert.Entities = [fv1, fv2, fv3, fv4]
FIXED_SUPPORT = MODAL_ACST.AddFixedSupport()
FIXED_SUPPORT.Location = fvert

# "Solve and validate frequencies")
# soln = MODAL_ACST.Children[8]
soln = DataModel.Project.Model.Analyses[0].Solution
TOT_DEF1 = soln.AddTotalDeformation()
TOT_DEF2 = soln.AddTotalDeformation()
TOT_DEF2.Mode = 2
TOT_DEF3 = soln.AddTotalDeformation()
TOT_DEF3.Mode = 3
TOT_DEF4 = soln.AddTotalDeformation()
TOT_DEF4.Mode = 4
TOT_DEF5 = soln.AddTotalDeformation()
TOT_DEF5.Mode = 5
TOT_DEF6 = soln.AddTotalDeformation()
TOT_DEF6.Mode = 6
TOT_DEF7 = soln.AddTotalDeformation()
TOT_DEF7.Mode = 7
TOT_DEF8 = soln.AddTotalDeformation()
TOT_DEF8.Mode = 8
TOT_DEF9 = soln.AddTotalDeformation()
TOT_DEF9.Mode = 9
TOT_DEF10 = soln.AddTotalDeformation()
TOT_DEF10.Mode = 10
TOT_DEF11 = soln.AddTotalDeformation()
TOT_DEF11.Mode = 11
TOT_DEF12 = soln.AddTotalDeformation()
TOT_DEF12.Mode = 12
ACOUST_PRES_RES = soln.AddAcousticPressureResult()


# "First Frequency", FREQ1, 0.46024, 5)
# "Second Frequency", FREQ2, 0.46024, 5)
# "Third Frequency", FREQ3, 0.61696, 5)
# "Fourth Frequency", FREQ4, 0.61749, 5)
# "Fifth Frequency", FREQ5, 0.69336, 5)
# "Sixth Frequency", FREQ6, 0.726, 5)
# "Seventh Frequency", FREQ7, 0.72602, 5)
# "Eighth Frequency", FREQ8, 0.81704, 5)
# "Ninth Frequency", FREQ9, 0.81743, 5)
# "Tenth Frequency", FREQ10, 0.81893, 5)
# "Eleventh Frequency", FREQ11, 0.81945, 5)
# "Twelfth Frequency", FREQ12, 0.90288, 5)

# "Max Acoustics Pressure", PRMAX, 1.4724, 5)
# "Min Acoustics Pressure", PRMIN, -1.4718, 5)


ANALYSIS_SETTINGS.CalculateReactions = True

# Add force Reaction scoped to Fixed Support
FORCE_REACT1 = soln.AddForceReaction()
FORCE_REACT1.BoundaryConditionSelection = FIXED_SUPPORT


# "Solve and validate frequencies with higher order TET elements")
soln.Solve(True)

# %%
# Temperature of bottom surface

Tree.Activate([TOT_DEF1])
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "TOT_DEF1.png"), image_export_format, settings_720p
)
display_image("TOT_DEF1.png")


FREQ1 = TOT_DEF1.ReportedFrequency.Value
FREQ2 = TOT_DEF2.ReportedFrequency.Value
FREQ3 = TOT_DEF3.ReportedFrequency.Value
FREQ4 = TOT_DEF4.ReportedFrequency.Value
FREQ5 = TOT_DEF5.ReportedFrequency.Value
FREQ6 = TOT_DEF6.ReportedFrequency.Value
FREQ7 = TOT_DEF7.ReportedFrequency.Value
FREQ8 = TOT_DEF8.ReportedFrequency.Value
FREQ9 = TOT_DEF9.ReportedFrequency.Value
FREQ10 = TOT_DEF10.ReportedFrequency.Value
FREQ11 = TOT_DEF11.ReportedFrequency.Value
FREQ12 = TOT_DEF12.ReportedFrequency.Value
PRMAX = ACOUST_PRES_RES.Maximum.Value
PRMIN = ACOUST_PRES_RES.Minimum.Value

FRC1_X = FORCE_REACT1.XAxis.Value
FRC1_Z = FORCE_REACT1.ZAxis.Value

# "First Frequency", FREQ1, 0.46024, 5)
# "Second Frequency", FREQ2, 0.46024, 5)
# "Third Frequency", FREQ3, 0.61696, 5)
# "Fourth Frequency", FREQ4, 0.61749, 5)
# "Fifth Frequency", FREQ5, 0.69336, 5)
# "Sixth Frequency", FREQ6, 0.726, 5)
# "Seventh Frequency", FREQ7, 0.72602, 5)
# "Eighth Frequency", FREQ8, 0.81704, 5)
# "Ninth Frequency", FREQ9, 0.81743, 5)
# "Tenth Frequency", FREQ10, 0.81893, 5)
# "Eleventh Frequency", FREQ11, 0.81945, 5)
# "Twelfth Frequency", FREQ12, 0.90288, 5)

# Adding coverage for Tabular Data output in Acoustics Modal case.
print(FREQ1)
print(FREQ2)
print(FREQ3)
print(FREQ4)
print(FREQ5)
print(FREQ6)
print(FREQ7)
print(FREQ8)
# "First Frequency", FREQ1, 0.46024, 5)
# "Second Frequency", FREQ2, 0.46024, 5)
# "Third Frequency", FREQ3, 0.61696, 5)
# "Fourth Frequency", FREQ4, 0.61749, 5)
# "Fifth Frequency", FREQ5, 0.69336, 5)
# "Sixth Frequency", FREQ6, 0.726, 5)
# "Seventh Frequency", FREQ7, 0.72602, 5)
# "Eighth Frequency", FREQ8, 0.81704, 5)
# "Ninth Frequency", FREQ9, 0.81743, 5)
# "Tenth Frequency", FREQ10, 0.81893, 5)
# "Eleventh Frequency", FREQ11, 0.81945, 5)
# "Twelfth Frequency", FREQ12, 0.90288, 5)

# "Validate pressure and reaction with higher order TET elements")
# "Max Acoustics Pressure", PRMAX, 1.4724, 5)
# "Min Acoustics Pressure", PRMIN, -1.4718, 5)

# %%
# Export directional heat flux animation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tree.Activate([TOT_DEF2])
animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720


TOT_DEF2.ExportAnimation(
    os.path.join(cwd, "deformation_2.gif"), animation_export_format, settings_720p
)
gif = Image.open(os.path.join(cwd, "deformation_2.gif"))
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

app.save(os.path.join(cwd, "modal_acou.mechdat"))
app.new()

# %%
# Delete example file

delete_downloads()
