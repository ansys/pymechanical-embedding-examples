""" .. _ref_tips_01:

3D visualization
----------------

Visualize 3D imported geometry
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~


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
# Visualize in 3D
# ~~~~~~~~~~~~~~~

app.plot()

# %%
# .. note::
#     This visualization is currently available only for geometry and on version 24R2 or later

# %%
# Cleanup
# ~~~~~~~

delete_downloads()
app.new()
