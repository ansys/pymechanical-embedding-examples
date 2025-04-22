""".. _ref_harmonic_acoustics:

Harmonic acoustic analysis
--------------------------

This example examines a harmonic acoustic analysis that uses
surface velocity to determine the steady-state response of a
structure and the surrounding fluid medium to loads and excitations
that vary sinusoidally with time.
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
image_export_format = GraphicsImageExportFormat.PNG
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False
camera.Rotate(180, CameraAxisType.ScreenY)

# %%
# Import the geometry
# ~~~~~~~~~~~~~~~~~~~

model = app.Model
geometry_import = model.GeometryImportGroup.AddGeometryImport()
geometry_import_format = (
    Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
)
geometry_import_preferences = Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
geometry_import_preferences.ProcessNamedSelections = True

geometry_path = download_file("C_GEOMETRY.agdb", "pymechanical", "embedding")
geometry_import.Import(
    geometry_path, geometry_import_format, geometry_import_preferences
)

# %%
# Set specified model geometry children to suppressed

# Define the geometry
geometry = model.Geometry
# Set which geometry children to suppress
suppressed_solids = [1, 2, 3, 4, 5, 7, 10, 11]
# Loop through the geometry children and suppress the specified ones
for child in range(geometry.Children.Count):
    solid = geometry.Children[child]
    if child in suppressed_solids:
        solid.Suppressed = True

# Plot the geometry
app.plot()

# %%
# Store all variables necessary for analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mesh = model.Mesh
named_selections = model.NamedSelections
connections = model.Connections
materials = model.Materials

# %%
# Set up the analysis
# ~~~~~~~~~~~~~~~~~~~

# Add the harmonic acoustics analysis and unit system
model.AddHarmonicAcousticAnalysis()
app.ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardMKS

# %%
# Import and assign materials

# Download and import the material
mat_path = download_file("Air-material.xml", "pymechanical", "embedding")
materials.Import(mat_path)

# Define which geometry children to assign the material to
material_solids = [6, 8, 9]
# Loop through the geometry children and assign the material to the specified ones
for child in range(geometry.Children.Count):
    solid = geometry.Children[child]
    if child in material_solids:
        solid.Material = "Air"

# %%
# Add a coordinate system

coordinate_systems = model.CoordinateSystems
coordinate_system = coordinate_systems.AddCoordinateSystem()
coordinate_system.OriginX = Quantity("0 [mm]")
coordinate_system.OriginY = Quantity("0 [mm]")
coordinate_system.OriginZ = Quantity("0 [mm]")
coordinate_system.PrimaryAxisDefineBy = CoordinateSystemAlignmentType.GlobalZ

# %%
# Set the mesh element size and generate the mesh

mesh.ElementSize = Quantity("200 [mm]")
mesh.GenerateMesh()

# %%
# Create, activate, and generate named selections
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_ns_generation_criteria(
    model: Ansys.ACT.Automation.Mechanical.Model, face_name: str
):
    """Add a named selection with the provided name and return it and the generation criteria.

    Parameters
    ----------
    model : Ansys.ACT.Automation.Mechanical.Model
        The Mechanical model to which the named selection will be added.
    face_name : str
        The name of the named selection to be created.

    Returns
    -------
    tuple
        A tuple containing the named selection and its generation criteria.
    """
    # Add a named selection to the model
    named_selection = model.AddNamedSelection()
    # Set the scoping method and name of the named selection
    named_selection.ScopingMethod = GeometryDefineByType.Worksheet
    named_selection.Name = face_name
    # Return the named selection and its generation criteria
    return named_selection, named_selection.GenerationCriteria


def add_ns_criterion(
    generation_criteria: Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion,
    value: Quantity,
    active: bool = True,
    action: SelectionActionType = SelectionActionType.Add,
    entity_type: SelectionType = SelectionType.GeoFace,
    criterion: SelectionCriterionType = SelectionCriterionType.Size,
    operator: SelectionOperatorType = SelectionOperatorType.Equal,
):
    """Add a criterion to the named selection generation criteria.

    Parameters
    ----------
    generation_criteria : Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion
        The generation criteria to which the criterion will be added.
    value : Quantity
        The value for the criterion.
    active : bool, optional
        Whether the criterion is active (default is True).
    action : SelectionActionType, optional
        The action to be performed (default is SelectionActionType.Add).
    entity_type : SelectionType, optional
        The type of entity (default is SelectionType.GeoFace).
    criterion : SelectionCriterionType, optional
        The criterion type (default is SelectionCriterionType.Size).
    operator : SelectionOperatorType, optional
        The operator to be used (default is SelectionOperatorType.Equal).
    """
    # Create a new named selection criterion and set its properties
    ns_criterion = Ansys.ACT.Automation.Mechanical.NamedSelectionCriterion()
    ns_criterion.Active = active
    ns_criterion.Action = action
    ns_criterion.EntityType = entity_type
    ns_criterion.Criterion = criterion
    ns_criterion.Operator = operator
    ns_criterion.Value = value
    # Add the criterion to the generation criteria
    generation_criteria.Add(ns_criterion)


# Create the SF_Velo named selection and add criteria
sf_velo, generation_criteria = get_ns_generation_criteria(model, "SF_Velo")
add_ns_criterion(generation_criteria, Quantity("3e6 [mm^2]"))
add_ns_criterion(
    generation_criteria,
    Quantity("15000 [mm]"),
    action=SelectionActionType.Filter,
    criterion=SelectionCriterionType.LocationZ,
)
# Activate and generate the named selection
sf_velo.Activate()
sf_velo.Generate()

# Create the ABS_Face named selection and add criteria
abs_face, generation_criteria = get_ns_generation_criteria(model, "ABS_Face")
add_ns_criterion(generation_criteria, Quantity("1.5e6 [mm^2]"))
add_ns_criterion(
    generation_criteria,
    Quantity("5000 [mm]"),
    action=SelectionActionType.Filter,
    criterion=SelectionCriterionType.LocationY,
)
# Activate and generate the named selection
abs_face.Activate()
abs_face.Generate()

# Create the PRES_Face named selection and add criteria
pres_face, generation_criteria = get_ns_generation_criteria(model, "PRES_Face")
add_ns_criterion(generation_criteria, Quantity("1.5e6 [mm^2]"))
add_ns_criterion(
    generation_criteria,
    Quantity("4500 [mm]"),
    action=SelectionActionType.Filter,
    criterion=SelectionCriterionType.LocationY,
)
# Activate and generate the named selection
pres_face.Activate()
pres_face.Generate()

# Create the ACOUSTIC_Region named selection and add criteria
acoustic_region, generation_criteria = get_ns_generation_criteria(
    model, "ACOUSTIC_Region"
)
add_ns_criterion(
    generation_criteria,
    8,
    entity_type=SelectionType.GeoBody,
    criterion=SelectionCriterionType.Size,
)
# Activate and generate the named selection
acoustic_region.Activate()
acoustic_region.Generate()

# %%
# Set the analysis settings
# ~~~~~~~~~~~~~~~~~~~~~~~~~

analysis_settings = model.Analyses[0].AnalysisSettings
analysis_settings.RangeMaximum = Quantity("100 [Hz]")
analysis_settings.SolutionIntervals = 50
analysis_settings.CalculateVelocity = True
analysis_settings.CalculateEnergy = True
analysis_settings.CalculateVolumeEnergy = True

# %%
# Boundary conditions and load
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get the harmonic acoustics analysis from the model
harmonic_acoustics = model.Analyses[0]

# %%
# Get the acoustic region from the harmonic acoustics analysis and set its location

acoustics_region = [
    child for child in harmonic_acoustics.Children if child.Name == "Acoustics Region"
][0]
acoustics_region.Location = acoustic_region

# %%
# Add acoustic surface velocity and set its location and magnitude

surface_velocity = harmonic_acoustics.AddAcousticSurfaceVelocity()
surface_velocity.Location = sf_velo
surface_velocity.Magnitude.Output.DiscreteValues = [Quantity("5000 [mm s-1]")]

# %%
# Add acoustic pressure and set its location and magnitude

acoustic_pressure = harmonic_acoustics.AddAcousticPressure()
acoustic_pressure.Location = pres_face
acoustic_pressure.Magnitude = Quantity("1.5e-7 [MPa]")

# %%
# Add acoustic absorption surface and set its location and magnitude

absorption_surface = harmonic_acoustics.AddAcousticAbsorptionSurface()
absorption_surface.Location = abs_face
absorption_surface.AbsorptionCoefficient.Output.DiscreteValues = [Quantity("0.02")]

# Activate the harmonic acoustics analysis and display the image
harmonic_acoustics.Activate()
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "boundary_conditions.png"
)

# %%
# Add results to the analysis solution
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get the analysis solution
solution = model.Analyses[0].Solution

# %%
# Add the acoustic pressure result and set its properties

acoustic_pressure_result = solution.AddAcousticPressureResult()
acoustic_pressure_result.By = SetDriverStyle.ResultSet
acoustic_pressure_result.SetNumber = 25

# %%
# Add the acoustic total velocity result and set its frequency

total_av_result = solution.AddAcousticTotalVelocityResult()
total_av_result.Frequency = Quantity("50 [Hz]")

# %%
# Add the acoustic directional velocity result and set its properties

directional_av_result = solution.AddAcousticDirectionalVelocityResult()
directional_av_result.Frequency = Quantity("50 [Hz]")
directional_av_result.CoordinateSystem = coordinate_system

directional_av_result_2 = solution.AddAcousticDirectionalVelocityResult()
directional_av_result_2.NormalOrientation = NormalOrientationType.ZAxis
directional_av_result_2.By = SetDriverStyle.ResultSet
directional_av_result_2.SetNumber = 25

# %%
# Add the acoustic sound pressure level to the solution and set its frequency

acoustic_spl = solution.AddAcousticSoundPressureLevel()
acoustic_spl.Frequency = Quantity("50 [Hz]")

# %%
# Add the acoustic A-weighted sound pressure level to the solution and set its frequency

acoustic_weighted_sound_pressure_level = (
    solution.AddAcousticAWeightedSoundPressureLevel()
)
acoustic_weighted_sound_pressure_level.Frequency = Quantity("50 [Hz]")

# %%
# Add acoustic frequency bands for sound pressure level and A-weighted sound pressure levels

solution.AddAcousticFrequencyBandSPL()
solution.AddAcousticFrequencyBandAWeightedSPL()

# %%
# Add the acoustic velocity frequency response and set its orientation and location

av_frequency_response = solution.AddAcousticVelocityFrequencyResponse()
av_frequency_response.NormalOrientation = NormalOrientationType.ZAxis
av_frequency_response.Location = pres_face

# %%
# Add the acoustic kinetic energy and potential energy frequency response and set their locations

ke_frequency_response = solution.AddAcousticKineticEnergyFrequencyResponse()
ke_frequency_response.Location = abs_face
ke_display = ke_frequency_response.TimeHistoryDisplay

pe_frequency_response = solution.AddAcousticPotentialEnergyFrequencyResponse()
pe_frequency_response.Location = abs_face
pe_display = pe_frequency_response.TimeHistoryDisplay

# %%
# Add the acoustic total velocity result and set its location, frequency, and amplitude

total_av_result_2 = solution.AddAcousticTotalVelocityResult()
total_av_result_2.Location = pres_face
total_av_result_2.Frequency = Quantity("30 [Hz]")
total_av_result_2.Amplitude = True

# %%
# Add the acoustic directional velocity result and set its orientation, location, frequency,
# and amplitude

directional_av_result_3 = solution.AddAcousticDirectionalVelocityResult()
directional_av_result_3.NormalOrientation = NormalOrientationType.ZAxis
directional_av_result_3.Location = pres_face
directional_av_result_3.Frequency = Quantity("10 [Hz]")
directional_av_result_3.Amplitude = True

# %%
# Add the acoustic kinetic energy and potential energy and set their locations, frequencies,
# and amplitudes

acoustic_ke = solution.AddAcousticKineticEnergy()
acoustic_ke.Location = abs_face
acoustic_ke.Frequency = Quantity("68 [Hz]")
acoustic_ke.Amplitude = True

acoustic_potential_energy = solution.AddAcousticPotentialEnergy()
acoustic_potential_energy.Location = abs_face
acoustic_potential_energy.Frequency = Quantity("10 [Hz]")
acoustic_potential_energy.Amplitude = True

# %%
# Solve the solution
# ~~~~~~~~~~~~~~~~~~

solution.Solve(True)

# sphinx_gallery_start_ignore
# Assert the solution is done being solved
assert str(solution.Status) == "Done", "Solution status is not 'Done'"
# sphinx_gallery_end_ignore

# %%
# Print messages
# ~~~~~~~~~~~~~~

messages = app.ExtAPI.Application.Messages
if messages:
    for message in messages:
        print(f"[{message.Severity}] {message.DisplayString}")
else:
    print("No [Info]/[Warning]/[Error] messages")


# %%
# Postprocessing
# ~~~~~~~~~~~~~~

# %%
# Activate the acoustic pressure result and display the image
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([acoustic_pressure_result])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "acoustic_pressure.png"
)

# %%
# Activate the acoustic total velocity and display the image
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([total_av_result])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "total_velocity.png"
)

# %%
# Activate the sound pressure level and display the image
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([acoustic_spl])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "sound_pressure.png"
)

# %%
# Activate the acoustic total velocity pressure and display the image
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([total_av_result_2])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "total_velocity_pressure.png"
)

# %%
# Activate the acoustic kinetic energy on the absorption face and display the image
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

app.Tree.Activate([acoustic_ke])
set_camera_and_display_image(
    camera, graphics, settings_720p, output_path, "kinetic_energy.png"
)

# %%
# Export the acoustic pressure animation to a GIF file and display it
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

animation_export_format = GraphicsAnimationExportFormat.GIF
settings_720p = Ansys.Mechanical.Graphics.AnimationExportSettings()
settings_720p.Width = 1280
settings_720p.Height = 720

# Set the path for the GIF
press_gif_path = output_path / "press.gif"

# Export the force reaction animation to a GIF file
acoustic_pressure_result.ExportAnimation(
    str(press_gif_path), animation_export_format, settings_720p
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
gif = Image.open(press_gif_path)
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
# Display the output file from the solve
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get the working directory for the solve
solve_path = harmonic_acoustics.WorkingDir
# Get the solve output file path
solve_out_path = Path(solve_path) / "solve.out"
# Check if the solve output file exists and print its contents
if solve_out_path:
    with solve_out_path.open("rt") as file:
        for line in file:
            print(line, end="")

# %%
# Print the project tree
# ~~~~~~~~~~~~~~~~~~~~~~

app.print_tree()

# %%
# Clean up the project
# ~~~~~~~~~~~~~~~~~~~~

# Save the project
mechdat_path = output_path / "harmnonic_acoustics.mechdat"
app.save(str(mechdat_path))

# Clear the project
app.new()

# Delete the example files
delete_downloads()
