""".. _ref_tips_01:

3D visualization
----------------

Visualize 3D imported geometry
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~


from ansys.mechanical.core import App
from ansys.mechanical.core.examples import delete_downloads, download_file

# %%
# Create an instance of the Mechanical embedded application

app = App(globals=globals())
print(app)

# %%
# Download and import geometry file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Download the geometry file
geometry_path = download_file("Valve.pmdb", "pymechanical", "embedding")

# Define the model
model = app.Model

# Import the geometry file
geometry_import = model.GeometryImportGroup.AddGeometryImport()
geometry_import.Import(geometry_path)

# %%
# Visualize the model in 3D
# ~~~~~~~~~~~~~~~~~~~~~~~~~

app.plot()

# %%
# .. note::
#     This visualization is currently available only for geometry and on version 24R2 or later

# %%
# Clean up the files and app
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

# Delete the downloaded files
delete_downloads()

# Refresh the app
app.new()
