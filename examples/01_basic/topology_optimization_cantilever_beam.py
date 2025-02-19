""".. _ref_topology_optimization:

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

from ansys.mechanical.core import App
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt

# %%
# Embed Mechanical and set global variables

app = App(globals=globals())
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

Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Front)
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
STRUCT = Model.Analyses[0]

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
Graphics.Camera.SetFit()
Graphics.ExportImage(
    os.path.join(cwd, "total_deformation.png"), image_export_format, settings_720p
)
display_image("total_deformation.png")

# %%
# Equivalent stress

STRUCT_SLN.Children[2].Activate()
Graphics.Camera.SetFit()
Graphics.ExportImage(
    os.path.join(cwd, "equivalent_stress.png"), image_export_format, settings_720p
)
display_image("equivalent_stress.png")

# %%
# Topology optimization
# ~~~~~~~~~~~~~~~~~~~~~

# Set MKS unit system

ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

# Get structural analysis and link to topology optimization

TOPO_OPT = Model.AddTopologyOptimizationAnalysis()
TOPO_OPT.TransferDataFrom(STRUCT)

OPT_REG = DataModel.GetObjectsByType(DataModelObjectCategory.OptimizationRegion)[0]
OPT_REG.BoundaryCondition = BoundaryConditionType.AllLoadsAndSupports
OPT_REG.OptimizationType = OptimizationType.TopologyDensity

# sphinx_gallery_start_ignore
assert str(TOPO_OPT.ObjectState) == "NotSolved"
# sphinx_gallery_end_ignore

# Insert volume response constraint object for topology optimization
# Delete mass response constraint

MASS_CONSTRN = TOPO_OPT.Children[3]
MASS_CONSTRN.Delete()

# Add volume response constraint

VOL_CONSTRN = TOPO_OPT.AddVolumeConstraint()

# Insert member size manufacturing constraint

MEM_SIZE_MFG_CONSTRN = TOPO_OPT.AddMemberSizeManufacturingConstraint()
MEM_SIZE_MFG_CONSTRN.Minimum = ManuMemberSizeControlledType.Manual
MEM_SIZE_MFG_CONSTRN.MinSize = Quantity("2.4 [m]")


TOPO_OPT.Activate()
Graphics.Camera.SetFit()
Graphics.ExportImage(
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
Graphics.Camera.SetFit()
Graphics.ExportImage(
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
# Project tree
# ~~~~~~~~~~~~

app.print_tree()

# %%
# Cleanup
# ~~~~~~~
# Save project

app.save(os.path.join(cwd, "cantilever_beam_topology_optimization.mechdat"))
app.new()

# %%
# Delete the example files

delete_downloads()
