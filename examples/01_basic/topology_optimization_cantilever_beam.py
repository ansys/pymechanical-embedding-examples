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

from pathlib import Path

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
    image_path = cwd / image_name
    plt.imshow(mpimg.imread(str(image_path)))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.show()


cwd = Path.cwd() / "out"

# %%
# Configure graphics for image export

graphics = app.Graphics
camera = graphics.Camera

camera.SetSpecificViewOrientation(ViewOrientationType.Front)
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
struct = model.Analyses[0]

# sphinx_gallery_start_ignore
assert struct.ObjectState == ObjectState.Solved
# sphinx_gallery_end_ignore
struct_sln = struct.Solution
struct_sln.Solve(True)
# sphinx_gallery_start_ignore
assert struct_sln.Status == SolutionStatusType.Done, "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# Display structural analsys results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Total deformation

struct_sln.Children[1].Activate()
camera.SetFit()
total_deformation_image = cwd / "total_deformation.png"
graphics.ExportImage(str(total_deformation_image), image_export_format, settings_720p)
display_image(total_deformation_image.name)

# %%
# Equivalent stress

struct_sln.Children[2].Activate()
camera.SetFit()
equivalent_stress_image = cwd / "equivalent_stress.png"
graphics.ExportImage(str(equivalent_stress_image), image_export_format, settings_720p)
display_image(equivalent_stress_image.name)

# %%
# Topology optimization
# ~~~~~~~~~~~~~~~~~~~~~

# Set MKS unit system

app.ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

# Get structural analysis and link to topology optimization

topology_optimization = model.AddTopologyOptimizationAnalysis()
topology_optimization.TransferDataFrom(struct)

optimization_region = DataModel.GetObjectsByType(
    DataModelObjectCategory.OptimizationRegion
)[0]
optimization_region.BoundaryCondition = BoundaryConditionType.AllLoadsAndSupports
optimization_region.OptimizationType = OptimizationType.TopologyDensity

# sphinx_gallery_start_ignore
assert topology_optimization.ObjectState == ObjectState.NotSolved
# sphinx_gallery_end_ignore

# Insert volume response constraint object for topology optimization
# Delete mass response constraint

mass_constraint = topology_optimization.Children[3]
mass_constraint.Delete()

# Add volume response constraint

volume_constraint = topology_optimization.AddVolumeConstraint()

# Insert member size manufacturing constraint

mem_size_manufacturing_constraint = (
    topology_optimization.AddMemberSizeManufacturingConstraint()
)
mem_size_manufacturing_constraint.Minimum = ManuMemberSizeControlledType.Manual
mem_size_manufacturing_constraint.MinSize = Quantity("2.4 [m]")


topology_optimization.Activate()
camera.SetFit()
boundary_conditions_image = cwd / "boundary_conditions.png"
graphics.ExportImage(str(boundary_conditions_image), image_export_format, settings_720p)
display_image(boundary_conditions_image.name)

# %%
# Solve
# ~~~~~

top_opt_sln = topology_optimization.Solution
top_opt_sln.Solve(True)
# sphinx_gallery_start_ignore
assert top_opt_sln.Status == SolutionStatusType.Done, "Solution status is not 'Done'"
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
# Display results
# ~~~~~~~~~~~~~~~

top_opt_sln.Children[1].Activate()
topology_density = top_opt_sln.Children[1]

# %%
# Add smoothing to the STL

topology_density.AddSmoothing()
topology_optimization.Solution.EvaluateAllResults()
topology_density.Children[0].Activate()
camera.SetFit()
smoothed_image = cwd / "topo_opitimized_smooth.png"
graphics.ExportImage(str(smoothed_image), image_export_format, settings_720p)
display_image(smoothed_image.name)

# %%
# Export animation

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

topology_optimized_gif = cwd / "topology_opitimized.gif"
topology_density.ExportAnimation(
    str(topology_optimized_gif), animation_export_format, settings_720p
)

# %%
# .. image:: /_static/basic/Topo_opitimized.gif

# %%
# Review the results

# Print topology density results
print("Topology Density Results")
print("Minimum Density: ", topology_density.Minimum)
print("Maximum Density: ", topology_density.Maximum)
print("Iteration Number: ", topology_density.IterationNumber)
print("Original Volume: ", topology_density.OriginalVolume.Value)
print("Final Volume: ", topology_density.FinalVolume.Value)
print("Percent Volume of Original: ", topology_density.PercentVolumeOfOriginal)
print("Original Mass: ", topology_density.OriginalMass.Value)
print("Final Mass: ", topology_density.FinalMass.Value)
print("Percent Mass of Original: ", topology_density.PercentMassOfOriginal)


# %%
# Project tree
# ~~~~~~~~~~~~

app.print_tree()

# %%
# Cleanup
# ~~~~~~~
# Save project

mechdat_file = cwd / "cantilever_beam_topology_optimization.mechdat"
app.save(str(mechdat_file))
app.new()

# %%
# Delete the example files

delete_downloads()
