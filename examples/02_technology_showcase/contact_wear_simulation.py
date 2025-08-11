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

""".. _ref_contact_wear_simulation:

Contact Surface Wear Simulation
===============================

This example problem simulates wear at a contact surface. The wear occurs at
the interface between a hemispherical ring rotating over a flat ring. Wear characteristics
demonstrated include removal of material due to wear, changes in contact pressure and
area due to wear, and a continuous decrease of the wear rate in steady-state conditions.

This example is simulated using the Ansys Mechanical application.
The following features and capabilities are highlighted:

- Contact surface wear

- Nonlinear mesh adaptivity based on a wear criterion

Overview
--------

+------------------------------+--------------------------------------------------------------+
| Analysis Type(s)             | Static Structural Analysis                                   |
+------------------------------+--------------------------------------------------------------+
| Element Type(s)              | 2-D Axisymmetric (PLANE182),                                 |
|                              | 2-D Contact (CONTA172, TARGE169)                             |
+------------------------------+--------------------------------------------------------------+
| Solver Type(s)               | Ansys Mechanical                                             |
+------------------------------+--------------------------------------------------------------+

The following topics are available:

- `1. Introduction`_
- `2. Problem Description`_
- `3. Material Properties`_
- `4. Modeling and Meshing`_
- `5. Load and Boundary Conditions`_
- `6. Analysis and Solution Controls`_
- `7. Recommendations`_
- `8. Code`_

1. Introduction
---------------

Wear is the progressive loss of material from the surface of a solid body when in contact with another body.
The program approximates this loss of material by repositioning the contact nodes at the contacting surface.
The new node locations are determined by a wear model which calculates how much and in what direction a contact node
is to be moved to simulate wear based on the contact results. This example shows how to use the Archard wear model.
Since wear involves material removal, the element quality of solid elements underlying the contact
elements becomes progressively worse with increasing wear. Remeshing is required to successfully
simulate large amounts of wear. This example demonstrates how nonlinear mesh adaptivity can be
used to improve mesh quality when a model undergoes large amounts of wear.

As an alternative to the generalized form of the Archard wear mode, you can define your own wear model
via the userwear subroutine. The userwear subroutine is not covered in this example.

2. Problem description
------------------------

A hemispherical ring of copper with radius = 30 mm rotates on a flat ring of steel with
inner radius = 50 mm and outer radius = 150 mm.
The hemispherical ring touches the flat ring at the center from the axis of rotation (at 100 mm).

The hemispherical ring is subjected to a pressure load of 4000 N/mm2 and is rotating with
a frequency of 100,000 revolutions/sec. Sliding of the hemispherical ring on the flat ring causes
wear in the rings.

.. figure:: ../../_static/technology_showcase/problem_contact_wear.png
    :align: center
    :alt: 2d_asymmetric_model
    :figclass: align-center

    **2D Axisymmetric Model of a Hemispherical Ring Rotating on a flat Ring**

3. Material properties
----------------------

Linear elastic material behavior is assumed for both the copper ring and the steel ring.

+-----------------------+--------+-------+
| Property              | Copper | Steel |
+=======================+========+=======+
| Young’s Modulus (GPa) | 130    | 210   |
+-----------------------+--------+-------+
| Poisson’s Ratio       | 0.3    | 0.3   |
+-----------------------+--------+-------+

4. Modeling and meshing
----------------------


4.1 Geometry Details
~~~~~~~~~~~~~~~~~~~~

The rings are meshed with 2D axisymmetric elements (PLANE182 with KEYOPT(3) = 1).
Frictionless contact is modeled between the two rings by overlaying the surfaces
with contact and target elements (CONTA172 and TARGE169).

4.2 Contact Region Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A global element size of 1 mm is used for meshing. Local mesh sizing is also defined.
For the steel ring, Number of Divisions = 70 on the horizontal edges and
Number of Divisions = 35 on the vertical edges. For the hemispherical copper ring,
Number of Divisions = 60 on the curved edge and Number of Divisions = 40 on the flat edge.

4.3 Modeling Wear
~~~~~~~~~~~~~~~~~

Workbench does not have an option for modeling the Archard wear model.
Therefore, a command snippet is used to incorporate this model.

In the first part of this command input, element key options are set to control certain contact behaviors.
KEYOPT(5) = 1 is set to close the gap with an auto contact surface offset (CNOF).
KEYOPT(10) = 2 is set to perform a contact stiffness update each iteration so that the actual elastic
slip never exceeds the maximum allowable limit (SLTO) during the entire solution.

Contact elements are defined on the surface undergoing wear. The Archard wear model is defined by the
TB,WEAR,MATID,,,ARCD command, and the wear model is associated with the contact elements through the MATID (cid) specified on TB,WEAR.

The Archard wear model is specified by inputting constants C1 through C4 on the TBDATA command.
These constants represent the wear coefficient (K), material hardness (H), the contact pressure
exponent (m), and the sliding velocity exponent (n).

The wear coefficient K can sometimes be scaled to simplify modeling.
As an example, consider this ring-on-ring problem in which the rings are rotating
at constant speed. The only effect of this rotation/sliding at the contact surface is
to produce wear (friction is absent). The wear coefficient K can be scaled such that the
rotation is not explicitly modeled, but its effect is included in the computation of wear.
This greatly reduces the simulation time and effort.

More specifically, if a linear dependence of wear rate on the sliding velocity is assumed,
the wear coefficient K can be scaled by the sliding velocity. In this example,
sliding velocity is 2πN*R, where N = 100,000 revolutions/sec and R is the distance from
the axis of rotation. Scaling K by 2πN*R results in the wear rate being linearly dependent
upon the sliding velocity without explicitly modeling the sliding.
The distance from the axis of rotation (R) is assumed to be constant for all points and
is taken as 100 mm (the distance of the center of the ring from the axis of rotation).

There are two approaches for modeling wear:

- Wear on One Contact Surface (Asymmetric Contact)
- Wear on Both Contact Surfaces (Symmetric Contact)

This example only considers the first approach. Asymmetric contact is used to model wear in
the hemispherical copper ring only. For this case, contact elements are defined on the copper
ring while target elements are defined on the steel ring. The Archard wear model is defined
as a material associated with the contact elements. The material data for wear is defined
using TBDATA commands. The wear properties for the copper ring are as follows:

Wear Properties for the Copper Ring
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+----------------------+-------------------+-----------------------------------------------+
| Property             | TBDATA Constant   | Value                                         |
+======================+===================+===============================================+
| Wear Coefficient (K) | C1                | kcopper = 10e-13 * 2π * 1e5 * 100 (scaled by sliding velocity 2πN*R) |
+----------------------+-------------------+-----------------------------------------------+
| Hardness (H)         | C2                | 1 MPa                                         |
+----------------------+-------------------+-----------------------------------------------+
| Pressure exponent (n)| C3                | 1                                             |
+----------------------+-------------------+-----------------------------------------------+
| Velocity Exponent (m)| C4                | 0                                             |
+----------------------+-------------------+-----------------------------------------------+

To initiate wear after a steady state has been reached with respect to loading, TB,WEAR is used
in conjunction with TBFIELD,TIME. The problem is simulated in two load steps. In the first load step,
pressure is ramped to the desired level and wear is inactive. In the second load step, the pressure
is held constant and wear is activated.

4.4 Improving Mesh Quality During the Solution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Modeling wear involves repositioning contact surface nodes to simulate the material removal process.
As a result, the element quality of the solid elements underlying the contact elements can quickly deteriorate.
This examples uses the Nonlinear Mesh Adaptivity feature to alleviate this problem when simulating large amounts of wear.

A wear-based contact criterion triggers nonlinear mesh adaptivity whenever the mesh is distorted.
The critical ratio between the amount of wear and the underlying solid element's height is user-defined.
When the criterion is reached, nonlinear mesh adaptivity is triggered.

Nonlinear mesh adaptivity requires the following steps:

- Create a component that contains the contact elements that are undergoing wear.
- Issue the NLADAPTIVE command to trigger adaptivity based on a wear criterion.

The Mechanical application does not have an option for specifying the contact criterion for
the Nonlinear Adaptive Region feature. Therefore, to implement nonlinear mesh adaptivity in this example, a command snippet is used.

Adaptivity occurs whenever wear at any contact point exceeds 50% of the average height of the solid
element underlying the contact element. Each time the criterion is reached, the analysis is stopped,
the mesh quality is improved by morphing the mesh, history-dependent variables and boundary conditions
are mapped, and the analysis is restarted with an improved mesh. This process is done automatically.

5. Load and boundary conditions
-------------------------------

The bottom of the flat steel ring is fixed. A remote point is inserted to define a rigid surface constraint
between the nodes on the top surface of the hemispherical ring and a pilot node. The pilot node is constrained
in the X direction and in rotation about the Z axis (using Remote Displacement scoped to Remote Point).
The Remote Displacement behavior is set to Rigid.

5.1 Remote Displacement Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A remote force is applied on the remote point that is equivalent to a pressure of 4000 N/mm2.
The equivalent pressure is ramped during the first load step from 0 to 4000 N/mm2 and is kept
constant at 4000 N/mm2 during the second load step. Wear is activated in the second load step.
Using the below formula, the calculated applied force is 150,796,320 N.

Fapplied = 4000 x pi x ((Uring_offset+Uring_R)2- (Uring_offset-Uring_R)2)

where: Uring_R = 30 mm & Uring_offset = 100 mm

6. Analysis and solution controls
---------------------------------

A nonlinear static analysis is performed in two load steps. Geometric nonlinearity is included in the analysis
(Large Deflection: On), and automatic time increments are used.

The repositioning of contact nodes during wear can result in changing contact status.
If the wear increment is too large, all contact elements may go from a closed status to an open status,
resulting in rigid body motion. To prevent this, a very small-time increment is used so that the wear increment
is also small and changes in contact status are minimized.

7. Recommendations
------------------

When performing wear simulations, consider the following recommendations:

- Use one of the following contact algorithms: augmented Lagrangian or penalty function (KEYOPT(2) = 0 or 1).
  Modeling wear with the pure Lagrangian contact algorithm can result in convergence problems and is not recommended.
- Use very small substeps so that the wear increment is small. A large wear increment can abruptly change
  the contact status and cause convergence difficulties.
- In general, you should use asymmetric contact to model wear on only one side of the contact interface.
  However, you can use symmetric contact if wear is desired on both sides of the interface. In this case,
  define contact elements on both sides of the interface and use the option for the nodal-stress-based wear
  calculation (C5 of Archard wear model = 1 on TBDATA) to achieve better results.
- Simulating a large amount of wear can result in severe mesh distortions. In such cases, use the wear-based
  nonlinear adaptivity criterion to improve the mesh quality via mesh morphing.

8. Code
-------

The following code demonstrates how to set up a contact wear simulation in Ansys Mechanical using PyMechanical.

"""
# %%
# Import the necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image
from ansys.mechanical.core import App
from ansys.mechanical.core.examples import delete_downloads, download_file
from matplotlib import image as mpimg
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

if TYPE_CHECKING:
    import Ansys

# %%
# Initialize the embedded application
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

app = App(globals=globals())
print(app)

# %%
# Create functions to set camera and display images
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the path for the output files (images, gifs, mechdat)
output_path = Path.cwd() / "out"


def set_camera_and_display_image(
    camera,
    graphics,
    graphics_image_export_settings,
    image_output_path: Path,
    image_name: str,
) -> None:
    """Set the camera to fit the model and display the image.

    Parameters
    ----------
    camera : Ansys.ACT.Common.Graphics.MechanicalCameraWrapper
        The camera object to set the view.
    graphics : Ansys.ACT.Common.Graphics.MechanicalGraphicsWrapper
        The graphics object to export the image.
    graphics_image_export_settings : Ansys.Mechanical.Graphics.GraphicsImageExportSettings
        The settings for exporting the image.
    image_output_path : Path
        The path to save the exported image.
    image_name : str
        The name of the exported image file.
    """
    # Set the camera to fit the mesh
    camera.SetFit()
    # Export the mesh image with the specified settings
    image_path = image_output_path / image_name
    graphics.ExportImage(
        str(image_path), image_export_format, graphics_image_export_settings
    )
    # Display the exported mesh image
    display_image(image_path)


def display_image(
    image_path: str,
    pyplot_figsize_coordinates: tuple = (16, 9),
    plot_xticks: list = [],
    plot_yticks: list = [],
    plot_axis: str = "off",
) -> None:
    """Display the image with the specified parameters.

    Parameters
    ----------
    image_path : str
        The path to the image file to display.
    pyplot_figsize_coordinates : tuple
        The size of the figure in inches (width, height).
    plot_xticks : list
        The x-ticks to display on the plot.
    plot_yticks : list
        The y-ticks to display on the plot.
    plot_axis : str
        The axis visibility setting ('on' or 'off').
    """
    # Set the figure size based on the coordinates specified
    plt.figure(figsize=pyplot_figsize_coordinates)
    # Read the image from the file into an array
    plt.imshow(mpimg.imread(image_path))
    # Get or set the current tick locations and labels of the x-axis
    plt.xticks(plot_xticks)
    # Get or set the current tick locations and labels of the y-axis
    plt.yticks(plot_yticks)
    # Turn off the axis
    plt.axis(plot_axis)
    # Display the figure
    plt.show()


# %%
# Configure graphics for image export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

graphics = app.Graphics
camera = graphics.Camera

# Set the camera orientation to the front view
camera.SetSpecificViewOrientation(ViewOrientationType.Front)

# Set the image export format and settings
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False

# Rotate the camera on the y-axis
camera.Rotate(180, CameraAxisType.ScreenY)

# %%
# Download the geometry and material files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Download the geometry and material files from the specified paths
geometry_path = download_file("example_07_td43_wear.agdb", "pymechanical", "00_basic")
mat1_path = download_file("example_07_Mat_Copper.xml", "pymechanical", "00_basic")
mat2_path = download_file("example_07_Mat_Steel.xml", "pymechanical", "00_basic")

# %%
# Import the geometry
# ~~~~~~~~~~~~~~~~~~~

# Define the model
model = app.Model

# Add a geometry import to the geometry import group
geometry_import = model.GeometryImportGroup.AddGeometryImport()

# Set the geometry import settings
geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import_preferences.ProcessCoordinateSystems = True

# Import the geometry using the specified settings
geometry_import.Import(
    geometry_path, geometry_import_format, geometry_import_preferences
)

# Visualize the model in 3D
app.plot()

# %%
# Import the materials
# ~~~~~~~~~~~~~~~~~~~~

# Define the materials for the model
materials = model.Materials

# Import the copper and steel materials
materials.Import(mat1_path)
materials.Import(mat2_path)

# %%
# Set up the analysis
# ~~~~~~~~~~~~~~~~~~~

# Set up the unit system
app.ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM

# %%
# Store all main tree nodes as variables

geometry = model.Geometry
coordinate_systems = model.CoordinateSystems
connections = model.Connections
mesh = model.Mesh
named_selections = model.NamedSelections

# %%
# Add the static structural analysis

model.AddStaticStructuralAnalysis()
static_structural_analysis = model.Analyses[0]

# Store the static structural analysis solution
stat_struct_soln = static_structural_analysis.Solution

# Get the analysis settings for the static structural analysis
analysis_settings = static_structural_analysis.Children[0]

# %%
# Store the named selections as variables


def get_named_selection(name: str):
    """Get the named selection by name."""
    return app.DataModel.GetObjectsByName(name)[0]


curve_named_selection = get_named_selection("curve")
dia_named_selection = get_named_selection("dia")
ver_edge1 = get_named_selection("v1")
ver_edge2 = get_named_selection("v2")
hor_edge1 = get_named_selection("h1")
hor_edge2 = get_named_selection("h2")
all_bodies_named_selection = get_named_selection("all_bodies")

# %%
# Assign material to the bodies

# Set the model's 2D behavior to axi-symmetric
geometry.Model2DBehavior = Model2DBehavior.AxiSymmetric


def set_material_and_dimension(
    surface_child_index, material, dimension=ShellBodyDimension.Two_D
):
    """Set the material and dimension for a given surface."""
    surface = geometry.Children[surface_child_index].Children[0]
    surface.Material = material
    surface.Dimension = dimension


# Set the material and dimensions for the surface
set_material_and_dimension(0, "Steel")
set_material_and_dimension(1, "Copper")

# %%
# Configure settings for the contact region

# Add a contact region between the hemispherical ring and the flat ring
contact_region = connections.AddContactRegion()
# Set the source and target locations for the contact region
contact_region.SourceLocation = named_selections.Children[6]
contact_region.TargetLocation = named_selections.Children[3]
# Set contact region properties
contact_region.ContactType = ContactType.Frictionless
contact_region.Behavior = ContactBehavior.Asymmetric
contact_region.ContactFormulation = ContactFormulation.AugmentedLagrange
contact_region.DetectionMethod = ContactDetectionPoint.NodalNormalToTarget

# %%
# Add a command snippet to use Archard Wear Model

archard_wear_model = """keyo,cid,5,1
keyo,cid,10,2
pi=acos(-1)
slide_velocity=1e5
Uring_offset=100
kcopper=10e-13*slide_velocity*2*pi*Uring_offset
TB,WEAR,cid,,,ARCD
TBFIELD,TIME,0
TBDATA,1,0,1,1,0,0
TBFIELD,TIME,1
TBDATA,1,0,1,1,0,0
TBFIELD,TIME,1.01
TBDATA,1,kcopper,1,1,0,0
TBFIELD,TIME,4
TBDATA,1,kcopper,1,1,0,0"""
cmd1 = contact_region.AddCommandSnippet()
cmd1.AppendText(archard_wear_model)

# %%
# Insert a remote point

# Add a remote point to the model
remote_point = model.AddRemotePoint()
# Set the remote point location to the center of the hemispherical ring
remote_point.Location = dia_named_selection
remote_point.Behavior = LoadBehavior.Rigid

# %%
# Set properties for the mesh
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the mesh element order and size
mesh.ElementOrder = ElementOrder.Linear
mesh.ElementSize = Quantity("1 [mm]")

# %%
# Create a function to add edge sizing and properties


def add_edge_sizing_and_properties(
    mesh, location, divisions, sizing_type=SizingType.NumberOfDivisions
):
    """Set the sizing properties for a given mesh.

    Parameters
    ----------
    mesh : Ansys.Mechanical.DataModel.Mesh
        The mesh object to set the properties for.
    location : Ansys.Mechanical.DataModel.NamedSelection
        The location of the edge to set the sizing for.
    divisions : int
        The number of divisions for the edge.
    sizing_type : SizingType
        The type of sizing to apply (default is NumberOfDivisions).
    """
    edge_sizing = mesh.AddSizing()
    edge_sizing.Location = location
    edge_sizing.Type = sizing_type
    edge_sizing.NumberOfDivisions = divisions


# %%
# Add edge sizing and properties to the mesh for each named selection

add_edge_sizing_and_properties(mesh, hor_edge1, 70)
add_edge_sizing_and_properties(mesh, hor_edge2, 70)
add_edge_sizing_and_properties(mesh, ver_edge1, 35)
add_edge_sizing_and_properties(mesh, ver_edge2, 35)
add_edge_sizing_and_properties(mesh, dia_named_selection, 40)
add_edge_sizing_and_properties(mesh, curve_named_selection, 60)

# %%
# Generate the mesh and display the image

mesh.GenerateMesh()
set_camera_and_display_image(camera, graphics, settings_720p, output_path, "mesh.png")

# %%
# Set the analysis settings
# ~~~~~~~~~~~~~~~~~~~~~~~~~

# %%
# Create a function to set time steps for the analysis settings


def set_time_steps(initial: str, min: str, max: str) -> None:
    """Set the time step properties for the analysis settings.

    Parameters
    ----------
    initial : str
        The initial time step value.
    min : str
        The minimum time step value.
    max : str
        The maximum time step value.
    """
    analysis_settings.InitialTimeStep = Quantity(initial)
    analysis_settings.MinimumTimeStep = Quantity(min)
    analysis_settings.MaximumTimeStep = Quantity(max)


# %%
# Set the analysis settings for the static structural analysis

analysis_settings.NumberOfSteps = 2
analysis_settings.CurrentStepNumber = 1
analysis_settings.AutomaticTimeStepping = AutomaticTimeStepping.On
analysis_settings.DefineBy = TimeStepDefineByType.Time
set_time_steps(initial="0.1 [s]", min="0.0001 [s]", max="1 [s]")
analysis_settings.CurrentStepNumber = 2
analysis_settings.Activate()
analysis_settings.StepEndTime = Quantity("4 [s]")
analysis_settings.AutomaticTimeStepping = AutomaticTimeStepping.On
analysis_settings.DefineBy = TimeStepDefineByType.Time
set_time_steps(initial="0.01 [s]", min="0.000001 [s]", max="0.02 [s]")
analysis_settings.LargeDeflection = True

# %%
# Insert loading and boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Add a fixed support to the model
fixed_support = static_structural_analysis.AddFixedSupport()
# Set the fixed support location to the first horizontal edge
fixed_support.Location = hor_edge1

# Add a remote displacement to the model
remote_displacement = static_structural_analysis.AddRemoteDisplacement()
# Set the remote displacement location to the remote point
remote_displacement.Location = remote_point
# Add the values for the x-component and rotation about the z-axis
remote_displacement.XComponent.Output.DiscreteValues = [Quantity("0[mm]")]
remote_displacement.RotationZ.Output.DiscreteValues = [Quantity("0[deg]")]

# Add a remote force to the model
remote_force = static_structural_analysis.AddRemoteForce()
# Set the remote force location to the remote point
remote_force.Location = remote_point
# Set the remote force values for the y-component
remote_force.DefineBy = LoadDefineBy.Components
remote_force.YComponent.Output.DiscreteValues = [Quantity("-150796320 [N]")]

#  Nonlinear adaptivity does not support contact criterion yet so a command snippet is used instead
nonlinear_adaptivity = """NLADAPTIVE,all,add,contact,wear,0.50
NLADAPTIVE,all,on,all,all,1,,4
NLADAPTIVE,all,list,all,all"""

# Add the nonlinear adaptivity command snippet to the static structural analysis
cmd2 = static_structural_analysis.AddCommandSnippet()
cmd2.AppendText(nonlinear_adaptivity)
cmd2.StepSelectionMode = SequenceSelectionType.All

# Activate the static structural analysis and display the mesh image
static_structural_analysis.Activate()
set_camera_and_display_image(camera, graphics, settings_720p, output_path, "mesh.png")

# %%
# Add results to the solution
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~


def set_properties_for_result(
    result,
    display_time,
    orientation_type=NormalOrientationType.YAxis,
    display_option=ResultAveragingType.Unaveraged,
):
    """Set the properties for a given result."""
    result.NormalOrientation = orientation_type
    result.DisplayTime = Quantity(display_time)
    result.DisplayOption = display_option


# Add total deformation to the solution
total_deformation = stat_struct_soln.AddTotalDeformation()

# Add normal stress to the solution
normal_stress1 = stat_struct_soln.AddNormalStress()
set_properties_for_result(normal_stress1, display_time="1 [s]")
normal_stress2 = stat_struct_soln.AddNormalStress()
set_properties_for_result(normal_stress1, display_time="4 [s]")

# Add a contact tool to the solution
contact_tool = stat_struct_soln.AddContactTool()
contact_tool.ScopingMethod = GeometryDefineByType.Geometry
# Add selections for the contact tool
selection1 = app.ExtAPI.SelectionManager.AddSelection(all_bodies_named_selection)
selection2 = app.ExtAPI.SelectionManager.CurrentSelection
# Set the contact tool location to the current selection
contact_tool.Location = selection2
# Clear the selection
app.ExtAPI.SelectionManager.ClearSelection()

# %%
# Add contact pressure to the contact tool


def add_contact_pressure(contact_tool, display_time):
    """Add a contact pressure to the contact tool."""
    contact_pressure = contact_tool.AddPressure()
    contact_pressure.DisplayTime = Quantity(display_time)


# Add pressure to the contact tool
add_contact_pressure(contact_tool, display_time="0 [s]")
add_contact_pressure(contact_tool, display_time="4 [s]")

# %%
# Solve the solution
# ~~~~~~~~~~~~~~~~~~

stat_struct_soln.Solve(True)
# sphinx_gallery_start_ignore
assert (
    stat_struct_soln.Status == SolutionStatusType.Done
), "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# Postprocessing
# ~~~~~~~~~~~~~~

# %%
# Activate the first normal stress result and display the image

app.Tree.Activate([normal_stress1])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "normal_stress.png"
)

# %%
# Create a function to update the animation frame


def update_animation(frame: int) -> list[mpimg.AxesImage]:
    """Update the animation frame for the GIF.

    Parameters
    ----------
    frame : int
        The frame number to update the animation.

    Returns
    -------
    list[mpimg.AxesImage]
        A list containing the updated image for the animation.
    """
    # Seeks to the given frame in this sequence file
    gif.seek(frame)
    # Set the image array to the current frame of the GIF
    image.set_data(gif.convert("RGBA"))
    # Return the updated image
    return [image]


# %%
# Display the total deformation animation

# Set the animation export format
animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
# Set the animation export settings
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

# Export the animation
total_deformation_gif = output_path / "total_deformation.gif"
total_deformation.ExportAnimation(
    str(total_deformation_gif), animation_export_format, settings_720p
)

# Open the GIF file and create an animation
gif = Image.open(total_deformation_gif)
# Set the subplots for the animation and turn off the axis
figure, axes = plt.subplots(figsize=(16, 9))
axes.axis("off")
# Change the color of the image
image = axes.imshow(gif.convert("RGBA"))

# Create the animation using the figure, update_animation function, and the GIF frames
# Set the interval between frames to 200 milliseconds and repeat the animation
FuncAnimation(
    figure,
    update_animation,
    frames=range(gif.n_frames),
    interval=200,
    repeat=True,
    blit=True,
)

# Show the animation
plt.show()

# %%
# Print the project tree
# ~~~~~~~~~~~~~~~~~~~~~~

app.print_tree()

# %%
# Clean up the project
# ~~~~~~~~~~~~~~~~~~~~

# Save the project file
mechdat_file = output_path / "contact_wear.mechdat"
app.save(str(mechdat_file))

# Close the app
app.close()

# Delete the downloaded files
delete_downloads()
