""".. _ref_non_linear_analysis_rubber_boot_seal:

Nonlinear Analysis of a Rubber Boot Seal Model
----------------------------------------------

This example demonstrates a nonlinear 3D analysis of a rubber boot seal to:

- Create a rigid-flexible contact pair between a rigid shaft and a
  rubber boot part.
- Specify ramped effects using the On Gauss Point Detection Method
  to update contact stiffness at each iteration.
- Specify contact pairs at the inner and outer surfaces of the rubber boot.
- Specify non-ramped effects using the Nodal-Projected Normal From Contact
  Detection Method to update contact stiffness at each iteration.
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

# %%
# Set the image output path and create functions to fit the camera and display images
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the path for the output files (images, gifs, mechdat)
output_path = Path.cwd() / "out"


def set_camera_and_display_image(
    camera: Ansys.ACT.Common.Graphics.MechanicalCameraWrapper,
    graphics: Ansys.ACT.Common.Graphics.MechanicalGraphicsWrapper,
    graphics_image_export_settings: Ansys.Mechanical.Graphics.GraphicsImageExportSettings,
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

camera.SetSpecificViewOrientation(ViewOrientationType.Iso)
camera.SetFit()
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

geometry_path = download_file(
    "example_05_td26_Rubber_Boot_Seal.agdb", "pymechanical", "00_basic"
)
mat_path = download_file("example_05_Boot_Mat.xml", "pymechanical", "00_basic")

# %%
# Import geometry and material
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import material

model = app.Model

materials = model.Materials
materials.Import(mat_path)
print("Material import done !")

# %%
# Import geometry

geometry_import = model.GeometryImportGroup.AddGeometryImport()
geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True
geometry_import_preferences.ProcessCoordinateSystems = True
geometry_import.Import(
    geometry_path, geometry_import_format, geometry_import_preferences
)

app.plot()

# %%
# Setup the Analysis
# ~~~~~~~~~~~~~~~~~~
# Set up the unit system

app.ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM
app.ExtAPI.Application.ActiveAngleUnit = AngleUnitType.Radian

# %%
# Store all main tree nodes as variables

geometry = model.Geometry
part1 = [x for x in app.Tree.AllObjects if x.Name == "Part"][0]
part2 = [x for x in app.Tree.AllObjects if x.Name == "Solid"][1]
coordinate_systems = model.CoordinateSystems
gcs = coordinate_systems.Children[0]

# %%
# Add static structural analysis

model.AddStaticStructuralAnalysis()
static_structural_analysis = model.Analyses[0]
analysis_settings = static_structural_analysis.Children[0]
stat_struct_soln = static_structural_analysis.Solution
soln_info = stat_struct_soln.SolutionInformation

# %%
# Define named selection and coordinate system

named_selections = app.ExtAPI.DataModel.Project.Model.NamedSelections
top_face = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Top_Face"
][0]
bottom_face = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Bottom_Face"
][0]
symm_faces30 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Symm_Faces30"
][0]
faces2 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Faces2"
][0]
cyl_faces2 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Cyl_Faces2"
][0]
rubber_bodies30 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Rubber_Bodies30"
][0]
inner_faces30 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Inner_Faces30"
][0]
outer_faces30 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Outer_Faces30"
][0]
shaft_face = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Shaft_Face"
][0]
symm_faces15 = [
    i
    for i in named_selections.GetChildren[
        Ansys.ACT.Automation.Mechanical.NamedSelection
    ](True)
    if i.Name == "Symm_Faces15"
][0]

lcs1 = coordinate_systems.AddCoordinateSystem()
lcs1.OriginY = Quantity("97[mm]")

# %%
# Assign material

part1.Material = "Boot"
part2.StiffnessBehavior = StiffnessBehavior.Rigid

# %%
# Define connections

connections = model.Connections
contact_region1 = connections.AddContactRegion()
contact_region1.TargetLocation = shaft_face
contact_region1.SourceLocation = inner_faces30
contact_region1.ContactType = ContactType.Frictional
contact_region1.FrictionCoefficient = 0.2
contact_region1.Behavior = ContactBehavior.Asymmetric
contact_region1.SmallSliding = ContactSmallSlidingType.Off
contact_region1.DetectionMethod = ContactDetectionPoint.OnGaussPoint
contact_region1.UpdateStiffness = UpdateContactStiffness.EachIteration
contact_region1.InterfaceTreatment = ContactInitialEffect.AddOffsetRampedEffects
contact_region1.TargetGeometryCorrection = TargetCorrection.Smoothing
contact_region1.TargetOrientation = TargetOrientation.Cylinder
contact_region1.TargetStartingPoint = gcs
contact_region1.TargetEndingPoint = lcs1

conts = connections.Children[0]
contact_region2 = conts.AddContactRegion()
contact_region2.SourceLocation = inner_faces30
contact_region2.TargetLocation = inner_faces30
contact_region2.ContactType = ContactType.Frictional
contact_region2.FrictionCoefficient = 0.2
contact_region2.Behavior = ContactBehavior.Asymmetric
contact_region2.SmallSliding = ContactSmallSlidingType.Off
contact_region2.DetectionMethod = ContactDetectionPoint.NodalProjectedNormalFromContact
contact_region2.UpdateStiffness = UpdateContactStiffness.EachIteration
contact_region2.NormalStiffnessValueType = ElementControlsNormalStiffnessType.Factor
contact_region2.NormalStiffnessFactor = 1

contact_region3 = conts.AddContactRegion()
contact_region3.SourceLocation = outer_faces30
contact_region3.TargetLocation = outer_faces30
contact_region3.ContactType = ContactType.Frictional
contact_region3.FrictionCoefficient = 0.2
contact_region3.Behavior = ContactBehavior.Asymmetric
contact_region3.SmallSliding = ContactSmallSlidingType.Off
contact_region3.DetectionMethod = ContactDetectionPoint.NodalProjectedNormalFromContact
contact_region3.UpdateStiffness = UpdateContactStiffness.EachIteration
contact_region3.NormalStiffnessValueType = ElementControlsNormalStiffnessType.Factor
contact_region3.NormalStiffnessFactor = 1

# %%
# Mesh
# ~~~~

mesh = model.Mesh
face_mesh = mesh.AddFaceMeshing()
face_mesh.Location = shaft_face
face_mesh.InternalNumberOfDivisions = 1

mesh_size = mesh.AddSizing()
mesh_size.Location = symm_faces15
mesh_size.ElementSize = Quantity("2 [mm]")

mesh.ElementOrder = ElementOrder.Linear
mesh.Resolution = 2

mesh.GenerateMesh()
set_camera_and_display_image(camera, graphics, settings_720p, output_path, "mesh.png")

# %%
# Define remote points
# ~~~~~~~~~~~~~~~~~~~~
# scope them to the top and bottom faces of rigid shaft

remote_point01 = model.AddRemotePoint()
remote_point01.Location = bottom_face
remote_point01.Behavior = LoadBehavior.Rigid

remote_point02 = model.AddRemotePoint()
remote_point02.Location = top_face
remote_point02.Behavior = LoadBehavior.Rigid

# %%
# Analysis settings
# ~~~~~~~~~~~~~~~~~

analysis_settings.Activate()
analysis_settings.LargeDeflection = True
analysis_settings.Stabilization = StabilizationType.Off

analysis_settings.NumberOfSteps = 2
analysis_settings.CurrentStepNumber = 1
analysis_settings.AutomaticTimeStepping = AutomaticTimeStepping.On
analysis_settings.DefineBy = TimeStepDefineByType.Substeps
analysis_settings.InitialSubsteps = 5
analysis_settings.MinimumSubsteps = 5
analysis_settings.MaximumSubsteps = 1000
analysis_settings.StoreResultsAt = TimePointsOptions.EquallySpacedPoints
analysis_settings.StoreResulsAtValue = 5

analysis_settings.CurrentStepNumber = 2
analysis_settings.AutomaticTimeStepping = AutomaticTimeStepping.On
analysis_settings.DefineBy = TimeStepDefineByType.Substeps
analysis_settings.InitialSubsteps = 10
analysis_settings.MinimumSubsteps = 10
analysis_settings.MaximumSubsteps = 1000
analysis_settings.StoreResultsAt = TimePointsOptions.EquallySpacedPoints
analysis_settings.StoreResulsAtValue = 10

analysis_settings.CurrentStepNumber = 3
analysis_settings.AutomaticTimeStepping = AutomaticTimeStepping.On
analysis_settings.DefineBy = TimeStepDefineByType.Substeps
analysis_settings.InitialSubsteps = 30
analysis_settings.MinimumSubsteps = 30
analysis_settings.MaximumSubsteps = 1000
analysis_settings.StoreResultsAt = TimePointsOptions.EquallySpacedPoints
analysis_settings.StoreResulsAtValue = 20

soln_info.NewtonRaphsonResiduals = 4

# %%
# Loads and boundary conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

remote_displacement = static_structural_analysis.AddRemoteDisplacement()
remote_displacement.Location = remote_point01
remote_displacement.XComponent.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
    Quantity("3 [s]"),
]
remote_displacement.XComponent.Output.DiscreteValues = [
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
]
remote_displacement.YComponent.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
    Quantity("3 [s]"),
]
remote_displacement.YComponent.Output.DiscreteValues = [
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
    Quantity("-10 [mm]"),
    Quantity("-10 [mm]"),
]
remote_displacement.ZComponent.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
    Quantity("3 [s]"),
]
remote_displacement.ZComponent.Output.DiscreteValues = [
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
    Quantity("0 [mm]"),
]

remote_displacement.RotationX.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
    Quantity("3 [s]"),
]
remote_displacement.RotationX.Output.DiscreteValues = [
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
]
remote_displacement.RotationY.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
    Quantity("3 [s]"),
]
remote_displacement.RotationY.Output.DiscreteValues = [
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
]
remote_displacement.RotationZ.Inputs[0].DiscreteValues = [
    Quantity("0 [s]"),
    Quantity("1 [s]"),
    Quantity("2 [s]"),
    Quantity("3 [s]"),
]
remote_displacement.RotationZ.Output.DiscreteValues = [
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
    Quantity("0 [rad]"),
    Quantity("0.55 [rad]"),
]

frictionless_support1 = static_structural_analysis.AddFrictionlessSupport()
frictionless_support1.Location = symm_faces30
frictionless_support1.Name = "Symmetry_BC"
frictionless_support2 = static_structural_analysis.AddFrictionlessSupport()
frictionless_support2.Location = faces2
frictionless_support2.Name = "Boot_Bottom_BC"
frictionless_support3 = static_structural_analysis.AddFrictionlessSupport()
frictionless_support3.Location = cyl_faces2
frictionless_support3.Name = "Boot_Radial_BC"

# %%
# Add results
# ~~~~~~~~~~~

total_deformation = static_structural_analysis.Solution.AddTotalDeformation()
total_deformation.Location = rubber_bodies30

equivalent_stress = static_structural_analysis.Solution.AddEquivalentStress()
equivalent_stress.Location = rubber_bodies30

# %%
# Solve
# ~~~~~

static_structural_analysis.Solution.Solve(True)

# sphinx_gallery_start_ignore
assert (
    stat_struct_soln.Status == SolutionStatusType.Done
), "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# Postprocessing
# ~~~~~~~~~~~~~~
# Total deformation


app.Tree.Activate([total_deformation])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "total_deformation.png"
)

# %%
# Equivalent stress

app.Tree.Activate([equivalent_stress])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "equivalent_stress.png"
)

# %%
# Total deformation animation

animation_export_format = (
    Ansys.Mechanical.DataModel.Enums.GraphicsAnimationExportFormat.GIF
)
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

total_deformation_gif = output_path / "total_deformation.gif"
total_deformation.ExportAnimation(
    str(total_deformation_gif), animation_export_format, settings_720p
)


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
# Cleanup
# ~~~~~~~
# Save project

mechdat_file = output_path / "non_linear_rubber_boot_seal.mechdat"
app.save(str(mechdat_file))
app.new()

# delete example file
delete_downloads()
