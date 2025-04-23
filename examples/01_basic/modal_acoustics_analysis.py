""".. _ref_modal_acoustics_analysis:

Modal acoustics analysis
------------------------

This example demonstrate modal acoustic analysis that involves
modeling both a structure and the surrounding
fluid to analyze frequencies and standing wave patterns within the structure.
This type of analysis is essential for applications such as Sonar, concert hall design,
noise reduction in various settings, audio speaker design, and geophysical exploration.

Mechanical enables you to model pure acoustic problems and fluid-structure
interaction (FSI) problems. A coupled acoustic analysis accounts for FSI.
An uncoupled acoustic analysis simulates
the fluid only and ignores any fluid-structure interaction.
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

app = App(globals=globals())
print(app)

cwd = Path.cwd() / "out"


def display_image(image_name):
    plt.figure(figsize=(16, 9))
    image_path = cwd / image_name
    plt.imshow(mpimg.imread(str(image_path)))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.show()


# %%
# Configure graphics for image export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

# %%
# Download geometry and materials files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

geometry_path = download_file("sloshing_geometry.agdb", "pymechanical", "embedding")
mat_path = download_file("Water_material_explicit.xml", "pymechanical", "embedding")


# %%
# Import the geometry
# ~~~~~~~~~~~~~~~~~~~

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

camera.SetFit()
geometry_image = cwd / "geometry.png"
graphics.ExportImage(str(geometry_image), image_export_format, settings_720p)
display_image(geometry_image.name)

# %%
# Store all variables necessary for analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

geometry = model.Geometry
mesh = model.Mesh
named_selections = model.NamedSelections
connections = model.Connections
materials = model.Materials

# %%
# Import material setup analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

model.AddModalAcousticAnalysis()
app.ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS
materials.Import(mat_path)
print("Material Import Done !")

# %%
# Get all required named selections and assign materials
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

acst_bodies = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Acoustic_bodies"
][0]
struct_bodies = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Structural_bodies"
][0]
top_bodies = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "top_bodies"
][0]
cont_bodies = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "container_bodies"
][0]
cont_V1 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Cont_V1"
][0]
cont_V2 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Cont_V2"
][0]
cont_V3 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Cont_V3"
][0]
cont_face1 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Cont_face1"
][0]
cont_face2 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Cont_face2"
][0]
cont_face3 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Cont_face3"
][0]
cont_face4 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Cont_face4"
][0]
free_faces = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Free_faces"
][0]
fsi_faces = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "FSI_faces"
][0]

solid1 = [
    i
    for i in geometry.GetChildren[Ansys.ACT.Automation.Mechanical.Body](True)
    if i.Name == "Solid1"
][0]
solid2 = [
    i
    for i in geometry.GetChildren[Ansys.ACT.Automation.Mechanical.Body](True)
    if i.Name == "Solid2"
][0]
solid3 = [
    i
    for i in geometry.GetChildren[Ansys.ACT.Automation.Mechanical.Body](True)
    if i.Name == "Solid3"
][0]
solid4 = [
    i
    for i in geometry.GetChildren[Ansys.ACT.Automation.Mechanical.Body](True)
    if i.Name == "Solid4"
][0]


# %%
# Assign material water to acoustic parts

solid1.Material = "WATER"
solid2.Material = "WATER"
solid3.Material = "WATER"
solid4.Material = "WATER"

# %%
# Mesh
# ~~~~

mesh.ElementOrder = ElementOrder.Quadratic

method1 = mesh.AddAutomaticMethod()
method1.Location = acst_bodies
method1.Method = MethodType.AllTriAllTet

method2 = mesh.AddAutomaticMethod()
method2.Location = top_bodies
method2.Method = MethodType.Automatic

# Add mesh sizing

sizing1 = mesh.AddSizing()
sizing1.Location = top_bodies
sizing1.ElementSize = Quantity("0.2 [m]")
sizing1.Behavior = SizingBehavior.Hard

# Add mesh sizing

sizing2 = mesh.AddSizing()
sizing2.Location = acst_bodies
sizing2.ElementSize = Quantity("0.2 [m]")
sizing2.Behavior = SizingBehavior.Hard

# Add mesh method

method3 = mesh.AddAutomaticMethod()
method3.Location = cont_bodies
method3.Method = MethodType.Sweep
method3.SourceTargetSelection = 4

mesh.GenerateMesh()

mesh_image = cwd / "mesh.png"
graphics.ExportImage(str(mesh_image), image_export_format, settings_720p)
display_image(mesh_image.name)

# %%
# Insert contacts
# ~~~~~~~~~~~~~~~
# Contact 1
connection_group = connections.AddConnectionGroup()
contact_region_1 = connection_group.AddContactRegion()
contact_region_1.SourceLocation = cont_V1
contact_region_1.TargetLocation = cont_face1
contact_region_1.ContactFormulation = ContactFormulation.MPC
contact_region_1.Behavior = ContactBehavior.Asymmetric
contact_region_1.PinballRegion = ContactPinballType.Radius
contact_region_1.PinballRadius = Quantity("0.25 [m]")

# %%
# Contact 2

contact_region_2 = connection_group.AddContactRegion()
contact_region_2.SourceLocation = cont_V2
contact_region_2.TargetLocation = cont_face2
contact_region_2.ContactFormulation = ContactFormulation.MPC
contact_region_2.Behavior = ContactBehavior.Asymmetric
contact_region_2.PinballRegion = ContactPinballType.Radius
contact_region_2.PinballRadius = Quantity("0.25 [m]")

# %%
# Contact 3

contact_region_3 = connection_group.AddContactRegion()
contact_region_3.SourceLocation = cont_V3
contact_region_3.TargetLocation = cont_face3
contact_region_3.ContactFormulation = ContactFormulation.MPC
contact_region_3.Behavior = ContactBehavior.Asymmetric
contact_region_3.PinballRegion = ContactPinballType.Radius
contact_region_3.PinballRadius = Quantity("0.25 [m]")

# %%
# Contact 3

sel_manager = app.ExtAPI.SelectionManager
cnv4 = DataModel.GeoData.Assemblies[0].Parts[1].Bodies[0].Vertices[3]
cont_V4 = sel_manager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
cont_V4.Entities = [cnv4]

# %%
# Contact 4

contact_region_4 = connection_group.AddContactRegion()
contact_region_4.TargetLocation = cont_face4
contact_region_4.SourceLocation = cont_V4
contact_region_4.ContactFormulation = ContactFormulation.MPC
contact_region_4.Behavior = ContactBehavior.Asymmetric
contact_region_4.PinballRegion = ContactPinballType.Radius
contact_region_4.PinballRadius = Quantity("0.25 [m]")

# %%
# Fully define Modal Multiphysics region with two physics regions

modal_acst = DataModel.Project.Model.Analyses[0]
acoustic_region = modal_acst.Children[2]
acoustic_region.Location = acst_bodies


structural_region = modal_acst.AddPhysicsRegion()
structural_region.Structural = True
structural_region.RenameBasedOnDefinition()
structural_region.Location = struct_bodies


# %%
# Analysis settings
# ~~~~~~~~~~~~~~~~~

analysis_settings = modal_acst.Children[1]
analysis_settings.MaximumModesToFind = 12
analysis_settings.SearchRangeMinimum = Quantity("0.1 [Hz]")
analysis_settings.SolverType = SolverType.Unsymmetric
analysis_settings.GeneralMiscellaneous = True
analysis_settings.CalculateReactions = True

# %%
# Boundary conditions and load
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Free surface

free_surface = modal_acst.AddAcousticFreeSurface()
free_surface.Location = free_faces

# %%
# Solid fluid interface

fsi_object = modal_acst.AddFluidSolidInterface()
fsi_object.Location = fsi_faces

# %%
# Gravity

acceleration = modal_acst.AddAcceleration()
acceleration.DefineBy = LoadDefineBy.Components
acceleration.YComponent.Output.DiscreteValues = [Quantity("9.81 [m sec^-1 sec^-1]")]

# %%
# Fixed Support

fv1 = DataModel.GeoData.Assemblies[0].Parts[1].Bodies[0].Vertices[0]
fv2 = DataModel.GeoData.Assemblies[0].Parts[1].Bodies[1].Vertices[0]
fv3 = DataModel.GeoData.Assemblies[0].Parts[1].Bodies[2].Vertices[0]
fv4 = DataModel.GeoData.Assemblies[0].Parts[1].Bodies[3].Vertices[0]

fvert = sel_manager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
fvert.Entities = [fv1, fv2, fv3, fv4]
fixed_support = modal_acst.AddFixedSupport()
fixed_support.Location = fvert

modal_acst.Activate()

graphics.ExportImage(str(geometry_image), image_export_format, settings_720p)
display_image(geometry_image.name)

# %%
# Add results
# ~~~~~~~~~~~
# Add 10 modes

soln = model.Analyses[0].Solution
total_deformation_1 = soln.AddTotalDeformation()
total_deformation_2 = soln.AddTotalDeformation()
total_deformation_2.Mode = 2
total_deformation_3 = soln.AddTotalDeformation()
total_deformation_3.Mode = 3
total_deformation_4 = soln.AddTotalDeformation()
total_deformation_4.Mode = 4
total_deformation_5 = soln.AddTotalDeformation()
total_deformation_5.Mode = 5
total_deformation_6 = soln.AddTotalDeformation()
total_deformation_6.Mode = 6
total_deformation_7 = soln.AddTotalDeformation()
total_deformation_7.Mode = 7
total_deformation_8 = soln.AddTotalDeformation()
total_deformation_8.Mode = 8
total_deformation_9 = soln.AddTotalDeformation()
total_deformation_9.Mode = 9
total_deformation_10 = soln.AddTotalDeformation()
total_deformation_10.Mode = 10

# %%
# Add acoustic pressure

acoustic_pressure_result = soln.AddAcousticPressureResult()

# %%
# Add force reaction scoped to fixed Support

force_reaction_1 = soln.AddForceReaction()
force_reaction_1.BoundaryConditionSelection = fixed_support

# %%
# Solve
# ~~~~~

soln.Solve(True)

# sphinx_gallery_start_ignore
assert soln.Status == SolutionStatusType.Done, "Solution status is not 'Done'"
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


# %%
# Results
# ~~~~~~~
# Total deformation - mode 1

app.Tree.Activate([total_deformation_1])
camera.SetFit()
total_deformation_image = cwd / "total_deformation_1.png"
graphics.ExportImage(str(total_deformation_image), image_export_format, settings_720p)
display_image(total_deformation_image.name)


# %%
# Acoustic pressure

app.Tree.Activate([acoustic_pressure_result])
acoustic_pressure_image = cwd / "acoustic_pressure.png"
graphics.ExportImage(str(acoustic_pressure_image), image_export_format, settings_720p)
display_image(acoustic_pressure_image.name)


# %%
# Display all modal frequency, force reaction
# and acoustic pressure values

frequency_1 = total_deformation_1.ReportedFrequency.Value
frequency_2 = total_deformation_2.ReportedFrequency.Value
frequency_3 = total_deformation_3.ReportedFrequency.Value
frequency_4 = total_deformation_4.ReportedFrequency.Value
frequency_5 = total_deformation_5.ReportedFrequency.Value
frequency_6 = total_deformation_6.ReportedFrequency.Value
frequency_7 = total_deformation_7.ReportedFrequency.Value
frequency_8 = total_deformation_8.ReportedFrequency.Value
frequency_9 = total_deformation_9.ReportedFrequency.Value
frequency_10 = total_deformation_10.ReportedFrequency.Value

pressure_result_max = acoustic_pressure_result.Maximum.Value
pressure_result_min = acoustic_pressure_result.Minimum.Value

force_reaction_1_x = force_reaction_1.XAxis.Value
force_reaction_1_z = force_reaction_1.ZAxis.Value

print("Modal Acoustic Results")
print("----------------------")
print("Frequency for mode 1 : ", frequency_1)
print("Frequency for mode 2 : ", frequency_2)
print("Frequency for mode 3 : ", frequency_3)
print("Frequency for mode 4 : ", frequency_4)
print("Frequency for mode 5 : ", frequency_5)
print("Frequency for mode 6 : ", frequency_6)
print("Frequency for mode 7 : ", frequency_7)
print("Frequency for mode 8 : ", frequency_8)
print("Frequency for mode 9 : ", frequency_9)
print("Frequency for mode 10 : ", frequency_10)
print("Acoustic pressure minimum : ", pressure_result_min)
print("Acoustic pressure Maximum : ", pressure_result_max)
print("Force reaction x-axis : ", force_reaction_1_x)
print("Force reaction z-axis : ", force_reaction_1_z)

# %%
# Total deformation animation for mode 10

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

deformation_gif = cwd / "deformation_10.gif"
total_deformation_10.ExportAnimation(
    str(deformation_gif), animation_export_format, settings_720p
)
gif = Image.open(deformation_gif)
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
# Project tree
# ~~~~~~~~~~~~

app.print_tree()

# %%
# Cleanup
# ~~~~~~~
# Save project

mechdat_file = cwd / "modal_acoustics.mechdat"
app.save(str(mechdat_file))
app.new()

# %%
# Delete example file

delete_downloads()
