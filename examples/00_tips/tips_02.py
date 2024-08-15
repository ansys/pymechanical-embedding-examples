""" .. _ref_tips_02:

Export image
------------

Export image and display
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

import os

import ansys.mechanical.core as mech
from ansys.mechanical.core.examples import delete_downloads, download_file

# %%
# Embed mechanical and set global variables

app = mech.App(version=242)
app.update_globals(globals())
print(app)


# %%
# Download geometry and import
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Download geometry

geometry_path = download_file("Valve.pmdb", "pymechanical", "embedding")

# %%
# Import geometry

geometry_import = Model.GeometryImportGroup.AddGeometryImport()
geometry_import.Import(geometry_path)

# %%
# Configure graphics for image export
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Orientation
Graphics.Camera.SetSpecificViewOrientation(ViewOrientationType.Iso)

# Export format
image_export_format = GraphicsImageExportFormat.PNG

# Resolution and background
settings_720p = Ansys.Mechanical.Graphics.GraphicsImageExportSettings()
settings_720p.Resolution = GraphicsResolutionType.EnhancedResolution
settings_720p.Background = GraphicsBackgroundType.White
settings_720p.Width = 1280
settings_720p.Height = 720
settings_720p.CurrentGraphicsDisplay = False

# Rotate the geometry if needed
ExtAPI.Graphics.Camera.Rotate(180, CameraAxisType.ScreenY)


# %%
# custom function for displaying the image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from matplotlib import image as mpimg
from matplotlib import pyplot as plt

# Temporary directory to save image
cwd = os.path.join(os.getcwd(), "out")


def display_image(image_name):
    plt.figure(figsize=(16, 9))
    plt.imshow(mpimg.imread(os.path.join(cwd, image_name)))
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.show()


# %%
# Export Image and display
# ~~~~~~~~~~~~~~~~~~~~~~~~

# Fits the geometry in viewing area
Graphics.Camera.SetFit()

Graphics.ExportImage(
    os.path.join(cwd, "geometry.png"), image_export_format, settings_720p
)

# Display image using matplotlib
display_image("geometry.png")

# %%
# Cleanup
# ~~~~~~~

delete_downloads()
app.new()
