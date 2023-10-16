
import os
import ansys.mechanical.core as mech
from ansys.mechanical.core.examples import delete_downloads, download_file

from matplotlib import image as mpimg
from matplotlib import pyplot as plt
#Embed Mechanical and set global variables
app = mech.App(version=232)
globals().update(mech.global_variables(app))
print(app)
from Ansys.ACT.Interfaces.Common import *
from Ansys.ACT.Mechanical.Fields import *
from Ansys.Mechanical.DataModel.Enums import *
from Ansys.Mechanical.DataModel.MechanicalEnums import *
from Ansys.ACT.Automation.Mechanical import *

cwd = os.path.join(os.getcwd(), "out")
def display_image(image_name):
    path = os.path.join(os.path.join(cwd, image_name))
    image = mpimg.imread(path)
    plt.figure(figsize=(15, 15))
    plt.axis("off")
    plt.imshow(image)
    plt.show()

structural_mechdat_file = download_file("cantilever.mechdat", "pymechanical", "embedding")
app.open(structural_mechdat_file)
structural_analysis = ExtAPI.DataModel.Project.Model.Analyses[0]
STRUCT_ID = structural_analysis.Id
structural_analysis.Solve()

##############################################
# Configure graphics for image export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
###################################################################################
# Structural Analsys Results
structural_solution = structural_analysis.Solution
# Total Deformation
structural_solution.Children[1].Activate()
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "total_deformation.png"), image_export_format, settings_720p
)
# Equivalent Stress
structural_solution.Children[2].Activate()
ExtAPI.Graphics.Camera.SetFit()
ExtAPI.Graphics.ExportImage(
    os.path.join(cwd, "equivalent_stress.png"), image_export_format, settings_720p
)
display_image("equivalent_stress.png")
##############################################################
# Topology Optimization

# Set MKS Unit System
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

# Store all main tree nodes as variables"
GEOM = ExtAPI.DataModel.Project.Model.Geometry
MSH = ExtAPI.DataModel.Project.Model.Mesh
NS_GRP = ExtAPI.DataModel.Project.Model.NamedSelections
CONN_GRP = ExtAPI.DataModel.Project.Model.Connections


MY_TOTAL_VOL = GEOM.Volume.Value
MY_TOTAL_MA = GEOM.Mass.Value
#Get Sturctural Analysis and link to Topo
TOPO_OPT = ExtAPI.DataModel.Project.Model.AddTopologyOptimizationAnalysis()
TOPO_OPT.TransferDataFrom(structural_analysis)

# Set None for Optimization Region Boundary Condition Exclusion Region
#Optimization Region
OPT_REG=TOPO_OPT.Children[1]
# OPT_REG.BoundaryCondition=BoundaryConditionType.None
# Using getattr since pythonnet doesn not support enum None
OPT_REG.BoundaryCondition=getattr(BoundaryConditionType,'None')

# Insert Volume Response Constraint Object for Topology Optimization" 
#Delete Mass Response Constraint
MASS_CONSTRN=TOPO_OPT.Children[3]
MASS_CONSTRN.Delete()
#Add Volume Response Constraint
VOL_CONSTRN=TOPO_OPT.AddVolumeConstraint()
#VOL_CONSTRN.DefineBy=ResponseConstraintDefineBy.Constant
#VOL_CONSTRN.PercentageToRetain=50

#Insert Member Size Manufacturing Constraint
MEM_SIZE_MFG_CONSTRN=TOPO_OPT.AddMemberSizeManufacturingConstraint()
MEM_SIZE_MFG_CONSTRN.Minimum=ManuMemberSizeControlledType.Manual
MEM_SIZE_MFG_CONSTRN.MinSize=Quantity("2.4 [m]")

# Store Coordinate System ID for use in Symmetry Manufacturing Constraint
Coordinate_Systems=DataModel.Project.Model.CoordinateSystems
coord_sys7=Coordinate_Systems.Children[7]

#Insert Symmetry Manufacturing Constraint
SYMM_MFG_CONSTRN=TOPO_OPT.AddSymmetryManufacturingConstraint()
SYMM_MFG_CONSTRN.CoordinateSystem=coord_sys7

# Setting different Coordinate System Axis for Symmetry Manufacturing Constraint
SYMM_MFG_CONSTRN_axis = str(SYMM_MFG_CONSTRN.Axis)
# Verify default Axis for Symmetry Manufacturing Constraint", SYMM_MFG_CONSTRN_axis, "PositiveXAxis
SYMM_MFG_CONSTRN.Axis=CoordinateSystemAxisType.PositiveYAxis
SYMM_MFG_CONSTRN_axis = str(SYMM_MFG_CONSTRN.Axis)
SYMM_MFG_CONSTRN.Axis=CoordinateSystemAxisType.PositiveXAxis


TOPO_OPT.Solution.Solve(True)

#Go to first Topology Density Result
TOPO_OPT.Solution.Children[1].Activate()
TOPO_DENS = TOPO_OPT.Solution.Children[1]
# Adding smoothing the STL
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
TOPO_DENS_min = TOPO_DENS.Minimum
TOPO_DENS_max = TOPO_DENS.Maximum
TOPO_DENS_ov = TOPO_DENS.OriginalVolume.Value
TOPO_DENS_fv = TOPO_DENS.FinalVolume.Value
TOPO_DENS_pvo = TOPO_DENS.PercentVolumeOfOriginal
TOPO_DENS_om = TOPO_DENS.OriginalMass.Value
TOPO_DENS_fm = TOPO_DENS.FinalMass.Value
TOPO_DENS_pmo = TOPO_DENS.PercentMassOfOriginal
TOPO_DENS_itrn = TOPO_DENS.IterationNumber
print("Original Volume for Topology Density Result", TOPO_DENS_ov)
print("Final Volume for Topology Density Result", TOPO_DENS_fv)
print("Percent Volume of Original for Topology Density Result", TOPO_DENS_pvo)
print("Original Mass for Topology Density Result", TOPO_DENS_om)
print("Final Mass for Topology Density Result", TOPO_DENS_fm)
print("Percent Mass of Original for Topology Density Result", TOPO_DENS_pmo)

# Save project
app.save(os.path.join(os.getcwd(), "cantilever_topology_optimization.mechdat"))
app.new()

# delete example file
delete_downloads()