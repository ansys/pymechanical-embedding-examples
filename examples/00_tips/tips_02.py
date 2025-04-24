""".. _ref_tips_02:

Export image
------------

Export image and display
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

from pathlib import Path

from ansys.mechanical.core import App
from ansys.mechanical.core.examples import delete_downloads, download_file

# %%
# Create an instance of the Mechanical embedded application

# Create an instance of the App class
app = App()

# Update the global variables
app.update_globals(globals())

# Print the app to ensure it is working
print(app)

# %%
# Download and import the geometry file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Download the geometry file
geometry_path = download_file("Valve.pmdb", "pymechanical", "embedding")

# %%
# Import the geometry file

geometry_import = Model.GeometryImportGroup.AddGeometryImport()
geometry_import.Import(geometry_path)

# %%
# Configure graphics for image export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Set the orientation of the camera
ExtAPI.Graphics.Camera.SetSpecificViewOrientation(Ansys.Mechanical.DataModel.Enums.ViewOrientationType.Iso)

# Set the image export format
image_export_format = GraphicsImageExportFormat.PNG

# Configure the export settings for the image
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False

# Rotate the geometry on the Y-axis
Graphics.Camera.Rotate(180, CameraAxisType.ScreenY)

# %%
# Create a function to display the image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from matplotlib import image as mpimg
from matplotlib import pyplot as plt

# Directory to save the image
output_path = Path.cwd() / "out"


def display_image(image_name) -> None:
    """Display the image using matplotlib.

    Parameters
    ----------
    image_name : str
        The name of the image file to display.
    """
    # Create the full path to the image
    image_path = output_path / image_name

    # Plot the figure and display the image
    plt.figure(figsize=(16, 9))
    plt.imshow(mpimg.imread(str(image_path)))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.show()


# %%
# Export and display the image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Fit the geometry in the viewing area
Graphics.Camera.SetFit()

# Export the image
geometry_image = output_path / "geometry.png"
Graphics.ExportImage(str(geometry_image), image_export_format, settings_720p)

# Display the image
display_image(geometry_image.name)

# %%
# Clean up the downloaded files and app
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Delete the downloaded files
delete_downloads()

# Refresh the app
app.new()
