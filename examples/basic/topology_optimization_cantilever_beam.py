""" .. _ref_topology_optimization:

Topology optimization of a simple cantilever beam
-------------------------------------------------

This example demonstrates the structural topology optimization of a simple
cantilever beam. The structural analysis is performed with basic constraints and
load, which is then transferred to the topology optimization.
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

import os

import ansys.mechanical.core as mech
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt

# %%
# Embed Mechanical and set global variables

app = mech.App(version=241)
app.update_globals(globals())
print(app)


def display_image(image_name):
    plt.figure(figsize=(16, 9))
    plt.imshow(mpimg.imread(os.path.join(cwd, image_name)))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.show()


cwd = os.path.join(os.getcwd(), "out")

# %%
# Configure graphics for image export

ExtAPI.Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Front)
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False

# %%
# Import structural analsys
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Download ``.mechdat`` file

structural_mechdat_file = download_file(
    "cantilever.mechdat", "pymechanical", "embedding"
)
app.open(structural_mechdat_file)
STRUCT = ExtAPI.DataModel.Project.Model.Analyses[0]

# sphinx_gallery_start_ignore
assert str(STRUCT.ObjectState) == "Solved"
# sphinx_gallery_end_ignore
STRUCT_SLN = STRUCT.Solution
STRUCT_SLN.Solve(True)
# sphinx_gallery_start_ignore
assert str(STRUCT_SLN.Status) == "Done", "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# Display structural analsys results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Total deformation

STRUCT_SLN.Children[1].Activate()
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "total_deformation.png"), image_export_format, settings_720p
)
display_image("total_deformation.png")

# %%
# Equivalent stress

STRUCT_SLN.Children[2].Activate()
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "equivalent_stress.png"), image_export_format, settings_720p
)
display_image("equivalent_stress.png")

# %%
# Topology optimization
# ~~~~~~~~~~~~~~~~~~~~~

# Set MKS unit system

ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

# Store all main tree nodes as variables

GEOM = ExtAPI.DataModel.Project.Model.Geometry
MSH = ExtAPI.DataModel.Project.Model.Mesh
NS_GRP = ExtAPI.DataModel.Project.Model.NamedSelections
CONN_GRP = ExtAPI.DataModel.Project.Model.Connections
MY_TOTAL_VOL = GEOM.Volume.Value
MY_TOTAL_MA = GEOM.Mass.Value

# Get structural analysis and link to topology optimization

TOPO_OPT = ExtAPI.DataModel.Project.Model.AddTopologyOptimizationAnalysis()
TOPO_OPT.TransferDataFrom(STRUCT)

# sphinx_gallery_start_ignore
assert str(TOPO_OPT.ObjectState) == "NotSolved"
# sphinx_gallery_end_ignore

# Set ``None`` for optimization region boundary condition exclusion region
# Optimization region

OPT_REG = TOPO_OPT.Children[1]
# OPT_REG.BoundaryCondition=BoundaryConditionType.None
# Using ``getattr`` because Python.Net does not support the ``None`` enum
OPT_REG.BoundaryCondition = BoundaryConditionType.AllLoadsAndSupports

# Insert volume response constraint object for topology optimization
# Delete mass response constraint

MASS_CONSTRN = TOPO_OPT.Children[3]
MASS_CONSTRN.Delete()

# Add volume response constraint

VOL_CONSTRN = TOPO_OPT.AddVolumeConstraint()
# VOL_CONSTRN.DefineBy=ResponseConstraintDefineBy.Constant
# VOL_CONSTRN.PercentageToRetain=50

# Insert member size manufacturing constraint

MEM_SIZE_MFG_CONSTRN = TOPO_OPT.AddMemberSizeManufacturingConstraint()
MEM_SIZE_MFG_CONSTRN.Minimum = ManuMemberSizeControlledType.Manual
MEM_SIZE_MFG_CONSTRN.MinSize = Quantity("2.4 [m]")

# # Store coordinate system ID for use in symmetry manufacturing constraint
# Coordinate_Systems = DataModel.Project.Model.CoordinateSystems
# coord_sys7 = Coordinate_Systems.Children[7]

# # Insert symmetry manufacturing constraint
# SYMM_MFG_CONSTRN = TOPO_OPT.AddSymmetryManufacturingConstraint()
# SYMM_MFG_CONSTRN.CoordinateSystem = coord_sys7

TOPO_OPT.Activate()
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "boundary_conditions.png"), image_export_format, settings_720p
)
display_image("boundary_conditions.png")

# %%
# Solve
# ~~~~~

TOPO_OPT_SLN = TOPO_OPT.Solution
TOPO_OPT_SLN.Solve(True)
# sphinx_gallery_start_ignore
assert str(TOPO_OPT_SLN.Status) == "Done", "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# Messages
# ~~~~~~~~

Messages = ExtAPI.Application.Messages
if Messages:
    for message in Messages:
        print(f"[{message.Severity}] {message.DisplayString}")
else:
    print("No [Info]/[Warning]/[Error] Messages")

# %%
# Display results
# ~~~~~~~~~~~~~~~

TOPO_OPT_SLN.Children[1].Activate()
TOPO_DENS = TOPO_OPT_SLN.Children[1]

# %%
# Add smoothing to the STL

TOPO_DENS.AddSmoothing()
TOPO_OPT.Solution.EvaluateAllResults()
TOPO_DENS.Children[0].Activate()
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "topo_opitimized_smooth.png"), image_export_format, settings_720p
)
display_image("topo_opitimized_smooth.png")

# %%
# Export animation

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

TOPO_DENS.ExportAnimation(
    os.path.join(cwd, "Topo_opitimized.gif"), animation_export_format, settings_720p
)

# %%
# .. image:: /_static/basic/Topo_opitimized.gif

# %%
# Review the results

# Print topology density results
print("Topology Density Results")
print("Minimum Density: ", TOPO_DENS.Minimum)
print("Maximum Density: ", TOPO_DENS.Maximum)
print("Iteration Number: ", TOPO_DENS.IterationNumber)
print("Original Volume: ", TOPO_DENS.OriginalVolume.Value)
print("Final Volume: ", TOPO_DENS.FinalVolume.Value)
print("Percent Volume of Original: ", TOPO_DENS.PercentVolumeOfOriginal)
print("Original Mass: ", TOPO_DENS.OriginalMass.Value)
print("Final Mass: ", TOPO_DENS.FinalMass.Value)
print("Percent Mass of Original: ", TOPO_DENS.PercentMassOfOriginal)

# %%
# Display output file from solve
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def write_file_contents_to_console(path):
    """Write file contents to console."""
    with open(path, "rt") as file:
        for line in file:
            print(line, end="")


solve_path = TOPO_OPT.WorkingDir
solve_out_path = os.path.join(solve_path, "solve.out")
if solve_out_path:
    write_file_contents_to_console(solve_out_path)

# %%
# Project tree
# ~~~~~~~~~~~~


def print_tree(node, indentation=""):
    print(f"{indentation}├── {node.Name}")

    if (
        hasattr(node, "Children")
        and node.Children is not None
        and node.Children.Count > 0
    ):
        for child in node.Children:
            print_tree(child, indentation + "|  ")


root_node = DataModel.Project
print_tree(root_node)

# %%
# Cleanup
# ~~~~~~~
# Save project

app.save(os.path.join(cwd, "cantilever_beam_topology_optimization.mechdat"))
app.new()

# %%
# Delete the example files

delete_downloads()
