""" .. _ref_topology_optimization:

Topology Optimization of a Simple Cantilever
--------------------------------------------

This example demonstrates the structural topology optimization of a simple
cantilever. The structural analysis is performed with basic constraints and
load, which is then transferred to topology optimization.
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

from Ansys.ACT.Automation.Mechanical import *
from Ansys.ACT.Interfaces.Common import *
from Ansys.ACT.Mechanical.Fields import *
from Ansys.Mechanical.DataModel.Enums import *
from Ansys.Mechanical.DataModel.MechanicalEnums import *


def display_image(image_name):
    path = os.path.join(os.path.join(cwd, image_name))
    image = mpimg.imread(path)
    plt.figure(figsize=(15, 15))
    plt.axis("off")
    plt.imshow(image)
    plt.show()


cwd = os.path.join(os.getcwd(), "out")

structural_mechdat_file = download_file(
    "cantilever.mechdat", "pymechanical", "embedding"
)
app.open(structural_mechdat_file)
STRUCT = ExtAPI.DataModel.Project.Model.Analyses[0]
assert str(STRUCT.ObjectState) == "Solved"
STRUCT_SLN = STRUCT.Solution
STRUCT_SLN.Solve(True)
assert str(STRUCT_SLN.Status) == "Done", "Solution status is not 'Done'"

##############################################
# Configure graphics for image export

ExtAPI.Graphics.Camera.SetSpecificViewOrientation(
    Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Iso
)
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

###############################
# Structural Analsys Results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~

###############################
# Total Deformation

STRUCT_SLN.Children[1].Activate()
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "total_deformation.png"), image_export_format, settings_720p
)
display_image("total_deformation.png")

###############################
# Equivalent Stress

STRUCT_SLN.Children[2].Activate()
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "equivalent_stress.png"), image_export_format, settings_720p
)
display_image("equivalent_stress.png")

##############################################################
# Topology Optimization
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set MKS Unit System
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

# Store all main tree nodes as variables
GEOM = ExtAPI.DataModel.Project.Model.Geometry
MSH = ExtAPI.DataModel.Project.Model.Mesh
NS_GRP = ExtAPI.DataModel.Project.Model.NamedSelections
CONN_GRP = ExtAPI.DataModel.Project.Model.Connections
MY_TOTAL_VOL = GEOM.Volume.Value
MY_TOTAL_MA = GEOM.Mass.Value

# Get Structural Analysis and link to Topology optimization
TOPO_OPT = ExtAPI.DataModel.Project.Model.AddTopologyOptimizationAnalysis()
TOPO_OPT.TransferDataFrom(STRUCT)
assert str(TOPO_OPT.ObjectState) == "NotSolved"

# Set None for Optimization Region Boundary Condition Exclusion Region
# Optimization Region
OPT_REG = TOPO_OPT.Children[1]
# OPT_REG.BoundaryCondition=BoundaryConditionType.None
# Using getattr since pythonnet doesn not support enum None
OPT_REG.BoundaryCondition = getattr(BoundaryConditionType, "None")

# Insert Volume Response Constraint Object for Topology Optimization"
# Delete Mass Response Constraint
MASS_CONSTRN = TOPO_OPT.Children[3]
MASS_CONSTRN.Delete()

# Add Volume Response Constraint
VOL_CONSTRN = TOPO_OPT.AddVolumeConstraint()
# VOL_CONSTRN.DefineBy=ResponseConstraintDefineBy.Constant
# VOL_CONSTRN.PercentageToRetain=50

# Insert Member Size Manufacturing Constraint
MEM_SIZE_MFG_CONSTRN = TOPO_OPT.AddMemberSizeManufacturingConstraint()
MEM_SIZE_MFG_CONSTRN.Minimum = ManuMemberSizeControlledType.Manual
MEM_SIZE_MFG_CONSTRN.MinSize = Quantity("2.4 [m]")

# Store Coordinate System ID for use in Symmetry Manufacturing Constraint
Coordinate_Systems = DataModel.Project.Model.CoordinateSystems
coord_sys7 = Coordinate_Systems.Children[7]

# Insert Symmetry Manufacturing Constraint
SYMM_MFG_CONSTRN = TOPO_OPT.AddSymmetryManufacturingConstraint()
SYMM_MFG_CONSTRN.CoordinateSystem = coord_sys7

########
# Solve

TOPO_OPT_SLN = TOPO_OPT.Solution
TOPO_OPT_SLN.Solve(True)
assert str(TOPO_OPT_SLN.Status) == "Done", "Solution status is not 'Done'"

###############################
# Results
# ~~~~~~~~

TOPO_OPT_SLN.Children[1].Activate()
TOPO_DENS = TOPO_OPT_SLN.Children[1]

###########################
# Add smoothing to the STL

TOPO_DENS.AddSmoothing()
TOPO_OPT.Solution.EvaluateAllResults()
TOPO_DENS.Children[0].Activate()
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "topo_opitimized_smooth.png"), image_export_format, settings_720p
)
display_image("topo_opitimized_smooth.png")

##########################################################################
# Compare the results


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

# Save project
app.save(os.path.join(cwd, "cantilever_topology_optimization.mechdat"))
app.new()

# Delete the example file
delete_downloads()
