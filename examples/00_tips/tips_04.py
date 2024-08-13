""" .. _ref_tips_04:

Use ``app_libraries``
---------------------

Use app libraries which comes with Mechanical
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~


import ansys.mechanical.core as mech
from ansys.mechanical.core.embedding import add_mechanical_python_libraries
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
# Print sys path

import sys

print(sys.path)
# %%
# Update path to libraries which are found under
# "Addins", "ACT", "libraries", "Mechanical"

add_mechanical_python_libraries(app)

# %%
# Import ``materials`` module and use necessary functions

import materials

body = DataModel.GeoData.Assemblies[0].Parts[0].Bodies[0]
mat = body.Material

print(materials.GetListMaterialProperties(mat))


# %%
# Cleanup
# ~~~~~~~

delete_downloads()
app.new()
