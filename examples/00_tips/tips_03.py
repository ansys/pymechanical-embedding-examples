""" .. _ref_tips_03:

Project tree
--------------------

Display the heirarchial Mechanical project structure.
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
# Download mechdb file
# ~~~~~~~~~~~~~~~~~~~~

mechdb_path = download_file("graphics_test.mechdb", "pymechanical", "test_files")

# %%
# Load the mechdb inside Mechanical

app.open(mechdb_path)

# %%
# Display the project tree
# ~~~~~~~~~~~~~~~~~~~~~~~~

app.print_tree()

# %%
# Display tree only under first analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

app.print_tree(Model.Analyses[0])


# %%
# Cleanup
# ~~~~~~~

delete_downloads()
app.new()
