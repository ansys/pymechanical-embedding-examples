# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

""".. _ref_shape_optimization:

Shape Optimization of a Bracket
-------------------------------

This example demonstrates how to insert a Static Structural analysis
into a new Mechanical session and execute a sequence of Python scripting
commands that define and solve a shape optimization analysis of bracket.
Scripts then evaluate the following results: deformation and
optimized shape.
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
# Embed mechanical and set global variables

app = App()
app.update_globals(globals())
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Iso)
Graphics.Camera.SetFit()
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False
Graphics.Camera.Rotate(180, CameraAxisType.ScreenY)

# %%
# Download and import geometry
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download the geometry file

geometry_path = download_file("bracket_model.agdb", "pymechanical", "embedding")
geometry_import_group_11 = Model.GeometryImportGroup
geometry_import = geometry_import_group_11.AddGeometryImport()

geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import.Import(
    geometry_path, geometry_import_format, geometry_import_preferences
)

# sphinx_gallery_start_ignore
assert str(geometry_import.ObjectState) == "Solved", "Geometry Import unsuccessful"
# sphinx_gallery_end_ignore

app.plot()

# %%
# Define Named Selections
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Specify variables for named selection objects

NS_GRP = ExtAPI.DataModel.Project.Model.NamedSelections
BOUNDARY_COND_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "boundary_cond"
][0]
LOADING_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "loading"][0]
EXCLUSON_REGION_NS = [
    x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "exclusion_region"
][0]
BRACKET_NS = [x for x in ExtAPI.DataModel.Tree.AllObjects if x.Name == "bracket"][0]

# %%
# Mesh
# ~~~~

mesh_13 = Model.Mesh
automatic_method_33 = mesh_13.AddAutomaticMethod()
automatic_method_33.ScopingMethod = GeometryDefineByType.Component

selection = NS_GRP.Children[3]
automatic_method_33.Location = selection
automatic_method_33.Method = MethodType.AllTriAllTet
automatic_method_33.ElementOrder = ElementOrder.Linear

sizing_35 = mesh_13.AddSizing()
sizing_35.ScopingMethod = GeometryDefineByType.Component
selection = NS_GRP.Children[3]
sizing_35.Location = selection
sizing_35.ElementSize = Quantity(6e-3, "m")

mesh_13.GenerateMesh()

# %%
# Define Analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Add Structural analysis

model_10 = Model
analysis_51 = model_10.AddStaticStructuralAnalysis()

# %%
# Define loads and boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

fixed_support_55 = analysis_51.AddFixedSupport()
selection = NS_GRP.Children[0]
fixed_support_55.Location = selection

force_57 = analysis_51.AddForce()
selection = NS_GRP.Children[1]
force_57.Location = selection
force_57.DefineBy = LoadDefineBy.Components
force_57.ZComponent.Output.SetDiscreteValue(0, Quantity(25000, "N"))

# %%
# Analysis settings
# ~~~~~~~~~~~~~~~~~

STAT_STRUC = Model.Analyses[0]
SOLN = STAT_STRUC.Solution

# %%
# Insert results
# ~~~~~~~~~~~~~~

Total_Deformation = SOLN.AddTotalDeformation()

# %%
# Solve
# ~~~~~

SOLN.Solve(True)
STAT_STRUC_SS = SOLN.Status
# sphinx_gallery_start_ignore
assert str(STAT_STRUC_SS) == "Done", "Solution status is not 'Done'"
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
# Results
# ~~~~~~~
# Total deformation

Tree.Activate([Total_Deformation])
Graphics.Camera.SetFit()
Graphics.ExportImage(
    os.path.join(cwd, "total_deformation.png"), image_export_format, settings_720p
)
display_image("total_deformation.png")

# %%
# Define Analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Add Topology Optimization Analysis

analysis_61 = model_10.AddTopologyOptimizationAnalysis()
analysis_61.ImportLoad(Model.Analyses[0])

# %%
# Define Optimization Settings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Specify the shape optimization region

optimization_region_64 = DataModel.GetObjectsByType(
    DataModelObjectCategory.OptimizationRegion
)[0]
selection = NS_GRP.Children[3]
optimization_region_64.DesignRegionLocation = selection
optimization_region_64.ExclusionScopingMethod = GeometryDefineByType.Component
selection = NS_GRP.Children[2]
optimization_region_64.ExclusionRegionLocation = selection

optimization_region_64.OptimizationType = OptimizationType.Shape
optimization_region_64.ShapeMoveLimitControl = TopoPropertyControlType.Manual
optimization_region_64.MorphingIterationMoveLimit = 0.002
optimization_region_64.MaxCumulatedDisplacementControl = TopoPropertyControlType.Manual
optimization_region_64.MorphingTotalMoveLimit = 0.02
optimization_region_64.MeshDeformationToleranceControl = TopoPropertyControlType.Manual

# %%
# Define Objective
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Specify objective as minimizing volume

Objective_type = DataModel.GetObjectsByType(DataModelObjectCategory.Objective)[0]
Objective_type.Worksheet.SetObjectiveType(0, ObjectiveType.MinimizeVolume)

# %%
# Define Compliance Settings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Specify compliance as response constraint

compliance_constraint_75 = analysis_61.AddComplianceConstraint()
compliance_constraint_75.ComplianceLimit.Output.SetDiscreteValue(0, Quantity(0.27, "J"))

mass_constraint_67 = DataModel.GetObjectsByName("Response Constraint")
DataModel.Remove(mass_constraint_67)

# %%
# Analysis settings
# ~~~~~~~~~~~~~~~~~
STAT_SHAPE = Model.Analyses[1]
SOLN = STAT_SHAPE.Solution

# %%
# Insert results
# ~~~~~~~~~~~~~~

# Topology_Density = SOLN.AddTopologyDensity()
Topology_Density = DataModel.GetObjectsByName("Topology Density")[0]

# %%
# Solve: shape Optimization Simulation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SOLN.Solve(True)
STAT_SHAPE_SS = SOLN.Status

# sphinx_gallery_start_ignore
assert str(STAT_STRUC_SS) == "Done", "Solution status is not 'Done'"
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
# Results
# ~~~~~~~
# Topology Density

Tree.Activate([Topology_Density])
Graphics.Camera.SetFit()
Graphics.ExportImage(
    os.path.join(cwd, "topology_density.png"), image_export_format, settings_720p
)
display_image("topology_density.png")


# %%
# Cleanup
# ~~~~~~~
# Save project

app.save(os.path.join(cwd, "shape-optimization.mechdat"))
app.new()

# delete example file
delete_downloads()
