""".. _ref_example_06:

Bolt Pretension
---------------------------------------------------------------------------------

Using supplied files, this example shows how to insert a static structural
analysis into a new Mechanical session and execute a sequence of Python
scripting commands that define and solve the bolt-pretension analysis.
Deformation, equivalent sresses, contact and bolt results are then post-processed.

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
    plt.show()


cwd = os.path.join(os.getcwd(), "out")


# %%
# Configure graphics for image export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

# %%
# Import geometry
# ~~~~~~~~~~~~~~~~

geometry_path = download_file(
    "example_06_bolt_pret_geom.agdb", "pymechanical", "00_basic"
)
geometry_file = geometry_path
geometry_import = Model.GeometryImportGroup.AddGeometryImport()
geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import_preferences.ProcessCoordinateSystems = True
geometry_import.Import(
    geometry_file, geometry_import_format, geometry_import_preferences
)
# sphinx_gallery_start_ignore
assert str(geometry_import.ObjectState) == "Solved", "Geometry Import unsuccessful"
# sphinx_gallery_end_ignore

ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "geometry.png"), image_export_format, settings_720p
)
display_image("geometry.png")

# %%
# Import Material
# ~~~~~~~~~~~~~~~

# mat_Copper_file_path = download_file(
#     "example_06_Mat_Copper.xml", "pymechanical", "00_basic"
# )
# mat_Steel_file_path = download_file(
#     "example_06_Mat_Steel.xml", "pymechanical", "00_basic"
# )

# MAT = ExtAPI.DataModel.Project.Model.Materials
# MAT.Import(mat_Copper_file_path)
# MAT.Import(mat_Steel_file_path)
# # sphinx_gallery_start_ignore
# assert str(MAT.ObjectState) == "FullyDefined", "Materials are not defined"
# sphinx_gallery_end_ignore

# %%
# Define Analysis and unit system
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Add Structural analysis

Model.AddStaticStructuralAnalysis()
STAT_STRUC = Model.Analyses[0]
STAT_STRUC_SOLN = STAT_STRUC.Solution
STAT_STRUC_ANA_SETTING = STAT_STRUC.Children[0]

# %%
# Set up the unit system.

ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM

# %%
# Store all main tree nodes as variables

MODEL = ExtAPI.DataModel.Project.Model
GEOM = ExtAPI.DataModel.Project.Model.Geometry
CONN_GRP = ExtAPI.DataModel.Project.Model.Connections
CS_GRP = ExtAPI.DataModel.Project.Model.CoordinateSystems
MSH = ExtAPI.DataModel.Project.Model.Mesh
NS_GRP = ExtAPI.DataModel.Project.Model.NamedSelections

# %%
# Store name selections
block3_block2_cont_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "block3_block2_cont"
][0]
block3_block2_targ_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "block3_block2_targ"
][0]
shank_block3_targ_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "shank_block3_targ"
][0]
shank_block3_cont_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "shank_block3_cont"
][0]
block1_washer_cont_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "block1_washer_cont"
][0]
block1_washer_targ_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "block1_washer_targ"
][0]
washer_bolt_cont_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "washer_bolt_cont"
][0]
washer_bolt_targ_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "washer_bolt_targ"
][0]
shank_bolt_targ_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "shank_bolt_targ"
][0]
shank_bolt_cont_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "shank_bolt_cont"
][0]
block2_block1_cont_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "block2_block1_cont"
][0]
block2_block1_targ_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "block2_block1_targ"
][0]
all_bodies = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "all_bodies"][0]
bodies_5 = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "bodies_5"][0]
shank = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "shank"][0]
shank_face = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "shank_face"][0]
shank_face2 = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "shank_face2"][
    0
]
bottom_surface = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "bottom_surface"
][0]
block2_surface = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "block2_surface"
][0]
shank_surface = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "shank_surface"
][0]

# %%
# Assign material to bodies

# SURFACE1 = GEOM.Children[0].Children[0]
# SURFACE1.Material = "Steel"

# SURFACE2 = GEOM.Children[1].Children[0]
# SURFACE2.Material = "Copper"

# SURFACE3 = GEOM.Children[2].Children[0]
# SURFACE3.Material = "Copper"

# SURFACE4 = GEOM.Children[3].Children[0]
# SURFACE4.Material = "Steel"

# SURFACE5 = GEOM.Children[4].Children[0]
# SURFACE5.Material = "Steel"

# SURFACE6 = GEOM.Children[5].Children[0]
# SURFACE6.Material = "Steel"

# %%
# Define coordinate system
# ~~~~~~~~~~~~~~~~~~~~~~~~~

coordinate_systems_17 = Model.CoordinateSystems
coordinate_system_93 = coordinate_systems_17.AddCoordinateSystem()
coordinate_system_93.OriginDefineBy = CoordinateSystemAlignmentType.Fixed
coordinate_system_93.OriginX = Quantity(-195, "mm")
coordinate_system_93.OriginY = Quantity(100, "mm")
coordinate_system_93.OriginZ = Quantity(50, "mm")
coordinate_system_93.PrimaryAxis = CoordinateSystemAxisType.PositiveZAxis

# %%
# Define Contacts
# ~~~~~~~~~~~~~~~
# Change contact settings and add a command snippet to use the Archard Wear Model.

connections = ExtAPI.DataModel.Project.Model.Connections

# %%
# Delete existing contacts

for connection in connections.Children:
    if connection.DataModelObjectCategory == DataModelObjectCategory.ConnectionGroup:
        connection.Delete()

CONT_REG1 = CONN_GRP.AddContactRegion()
CONT_REG1.SourceLocation = NS_GRP.Children[0]
CONT_REG1.TargetLocation = NS_GRP.Children[1]
CONT_REG1.ContactType = ContactType.Frictional
CONT_REG1.FrictionCoefficient = 0.2
CONT_REG1.SmallSliding = ContactSmallSlidingType.Off
CONT_REG1.UpdateStiffness = UpdateContactStiffness.Never
CMD1 = CONT_REG1.AddCommandSnippet()

# %%
# Add missing contact keyopt and Archard Wear Model using a command snippet

AWM = """keyopt,cid,9,5
rmodif,cid,10,0.00
rmodif,cid,23,0.001"""
CMD1.AppendText(AWM)

CONTS = CONN_GRP.Children[0]
CONT_REG2 = CONTS.AddContactRegion()
CONT_REG2.SourceLocation = NS_GRP.Children[3]
CONT_REG2.TargetLocation = NS_GRP.Children[2]
CONT_REG2.ContactType = ContactType.Bonded
CONT_REG2.ContactFormulation = ContactFormulation.MPC

CONT_REG3 = CONTS.AddContactRegion()
CONT_REG3.SourceLocation = NS_GRP.Children[4]
CONT_REG3.TargetLocation = NS_GRP.Children[5]
CONT_REG3.ContactType = ContactType.Frictional
CONT_REG3.FrictionCoefficient = 0.2
CONT_REG3.SmallSliding = ContactSmallSlidingType.Off
CONT_REG3.UpdateStiffness = UpdateContactStiffness.Never
CMD3 = CONT_REG3.AddCommandSnippet()

# Add missing contact keyopt and Archard Wear Model using a command snippet
AWM3 = """keyopt,cid,9,5
rmodif,cid,10,0.00
rmodif,cid,23,0.001"""
CMD3.AppendText(AWM3)

CONT_REG4 = CONTS.AddContactRegion()
CONT_REG4.SourceLocation = NS_GRP.Children[6]
CONT_REG4.TargetLocation = NS_GRP.Children[7]
CONT_REG4.ContactType = ContactType.Bonded
CONT_REG4.ContactFormulation = ContactFormulation.MPC

CONT_REG5 = CONTS.AddContactRegion()
CONT_REG5.SourceLocation = NS_GRP.Children[9]
CONT_REG5.TargetLocation = NS_GRP.Children[8]
CONT_REG5.ContactType = ContactType.Bonded
CONT_REG5.ContactFormulation = ContactFormulation.MPC

CONT_REG6 = CONTS.AddContactRegion()
CONT_REG6.SourceLocation = NS_GRP.Children[10]
CONT_REG6.TargetLocation = NS_GRP.Children[11]
CONT_REG6.ContactType = ContactType.Frictional
CONT_REG6.FrictionCoefficient = 0.2
CONT_REG6.SmallSliding = ContactSmallSlidingType.Off
CONT_REG6.UpdateStiffness = UpdateContactStiffness.Never
CMD6 = CONT_REG6.AddCommandSnippet()
# Add missing contact keyopt and Archard Wear Model using a command snippet.
AWM6 = """keyopt,cid,9,5
rmodif,cid,10,0.00
rmodif,cid,23,0.001"""
CMD6.AppendText(AWM6)

# %%
# Generate mesh
# ~~~~~~~~~~~~~

Hex_Method = MSH.AddAutomaticMethod()
Hex_Method.Location = all_bodies
Hex_Method.Method = MethodType.HexDominant

BODY_SIZING1 = MSH.AddSizing()
BODY_SIZING1.Location = bodies_5
BODY_SIZING1.ElementSize = Quantity(15, "mm")

BODY_SIZING2 = MSH.AddSizing()
BODY_SIZING2.Location = shank
BODY_SIZING2.ElementSize = Quantity(7, "mm")

Face_Meshing = MSH.AddFaceMeshing()
Face_Meshing.Location = shank_face
Face_Meshing.MappedMesh = False

Sweep_Method = MSH.AddAutomaticMethod()
Sweep_Method.Location = shank
Sweep_Method.Method = MethodType.Sweep
Sweep_Method.SourceTargetSelection = 2
Sweep_Method.SourceLocation = shank_face
Sweep_Method.TargetLocation = shank_face2

# MSH.GenerateMesh()
# # sphinx_gallery_start_ignore
# assert str(MSH.ObjectState) == "Solved", "Mesh could not be generated"
# # sphinx_gallery_end_ignore

# ExtAPI.Graphics.Camera.SetFit()
# ExtAPI.Graphics.ExportImage(
#     os.path.join(cwd, "mesh.png"), image_export_format, settings_720p
# )
# display_image("mesh.png")

# # %%
# # Set up analysis settings
# # ~~~~~~~~~~~~~~~~~~~~~~~~

# STAT_STRUC_ANA_SETTING.NumberOfSteps = 4
# step_index_list = [1]

# with Transaction():
#     for step_index in step_index_list:
#         STAT_STRUC_ANA_SETTING.SetAutomaticTimeStepping(
#             step_index, AutomaticTimeStepping.Off
#         )

# STAT_STRUC_ANA_SETTING.Activate()
# step_index_list = [1]

# with Transaction():
#     for step_index in step_index_list:
#         STAT_STRUC_ANA_SETTING.SetNumberOfSubSteps(step_index, 2)

# STAT_STRUC_ANA_SETTING.Activate()
# STAT_STRUC_ANA_SETTING.SolverType = SolverType.Direct
# STAT_STRUC_ANA_SETTING.SolverPivotChecking = SolverPivotChecking.Off

# # %%
# # Define loads and boundary conditions
# # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# FIX_SUP = STAT_STRUC.AddFixedSupport()
# FIX_SUP.Location = block2_surface

# Tabular_Force = STAT_STRUC.AddForce()
# Tabular_Force.Location = bottom_surface
# Tabular_Force.DefineBy = LoadDefineBy.Components
# Tabular_Force.XComponent.Inputs[0].DiscreteValues = [
#     Quantity("0[s]"),
#     Quantity("1[s]"),
#     Quantity("2[s]"),
#     Quantity("3[s]"),
#     Quantity("4[s]"),
# ]
# Tabular_Force.XComponent.Output.DiscreteValues = [
#     Quantity("0[N]"),
#     Quantity("0[N]"),
#     Quantity("5.e+005[N]"),
#     Quantity("0[N]"),
#     Quantity("-5.e+005[N]"),
# ]

# Bolt_Pretension = STAT_STRUC.AddBoltPretension()
# Bolt_Pretension.Location = shank_surface
# Bolt_Pretension.Preload.Inputs[0].DiscreteValues = [
#     Quantity("1[s]"),
#     Quantity("2[s]"),
#     Quantity("3[s]"),
#     Quantity("4[s]"),
# ]
# Bolt_Pretension.Preload.Output.DiscreteValues = [
#     Quantity("6.1363e+005[N]"),
#     Quantity("0 [N]"),
#     Quantity("0 [N]"),
#     Quantity("0[N]"),
# ]
# Bolt_Pretension.SetDefineBy(2, BoltLoadDefineBy.Lock)
# Bolt_Pretension.SetDefineBy(3, BoltLoadDefineBy.Lock)
# Bolt_Pretension.SetDefineBy(4, BoltLoadDefineBy.Lock)
# Tree.Activate([Bolt_Pretension])
# ExtAPI.Graphics.ExportImage(
#     os.path.join(cwd, "bolt_pretension.png"), image_export_format, settings_720p
# )
# display_image("bolt_pretension.png")

# # %%
# # Insert results
# # ~~~~~~~~~~~~~~

# Post_Contact_Tool = STAT_STRUC_SOLN.AddContactTool()
# Post_Contact_Tool.ScopingMethod = GeometryDefineByType.Worksheet

# Bolt_Tool = STAT_STRUC_SOLN.AddBoltTool()
# Bolt_Working_Load = Bolt_Tool.AddWorkingLoad()

# Total_Deformation = STAT_STRUC_SOLN.AddTotalDeformation()
# Equivalent_stress_1 = STAT_STRUC_SOLN.AddEquivalentStress()
# Equivalent_stress_2 = STAT_STRUC_SOLN.AddEquivalentStress()
# Equivalent_stress_2.Location = shank
# Force_Reaction_1 = STAT_STRUC_SOLN.AddForceReaction()
# Force_Reaction_1.BoundaryConditionSelection = FIX_SUP
# Moment_Reaction_2 = STAT_STRUC_SOLN.AddMomentReaction()
# Moment_Reaction_2.BoundaryConditionSelection = FIX_SUP

# # %%
# # Solve
# # ~~~~~

# STAT_STRUC_SOLN.Solve(True)
# STAT_STRUC_SS = STAT_STRUC_SOLN.Status
# # sphinx_gallery_start_ignore
# assert str(STAT_STRUC_SS) == "Done", "Solution status is not 'Done'"
# # sphinx_gallery_end_ignore

# # %%
# # Results
# # ~~~~~~~

# Tree.Activate([Total_Deformation])
# ExtAPI.Graphics.Camera.SetFit()
# ExtAPI.Graphics.ExportImage(
#     os.path.join(cwd, "total_deformation.png"), image_export_format, settings_720p
# )
# display_image("total_deformation.png")
# Tree.Activate([Equivalent_stress_1])
# ExtAPI.Graphics.ExportImage(
#     os.path.join(cwd, "equivalent_stress1.png"), image_export_format, settings_720p
# )
# display_image("equivalent_stress1.png")
# Tree.Activate([Equivalent_stress_2])
# ExtAPI.Graphics.ExportImage(
#     os.path.join(cwd, "equivalent_stress2.png"), image_export_format, settings_720p
# )
# display_image("equivalent_stress2.png")

# # %%
# # Export animation

# Post_Contact_Tool.Children[0].Activate()
# animation_export_format = (
#     Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
# )
# settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
# settings_720p.Width = 1280
# settings_720p.Height = 720

# Post_Contact_Tool.Children[0].ExportAnimation(
#     os.path.join(cwd, "contact_status.gif"), animation_export_format, settings_720p
# )

# # %%
# # .. image:: /_static/basic/contact_status.gif


# %%
# Cleanup
# ~~~~~~~
# Save project

app.save(os.path.join(cwd, "bolt_pretension.mechdat"))
app.new()

# %%
# Delete the example file

delete_downloads()
