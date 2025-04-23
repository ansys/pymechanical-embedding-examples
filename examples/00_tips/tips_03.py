""".. _ref_tips_03:

Project tree
--------------------

Display the heirarchial Mechanical project structure.
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
# Download the mechdb file
# ~~~~~~~~~~~~~~~~~~~~~~~~

mechdb_path = download_file("graphics_test.mechdb", "pymechanical", "test_files")

# %%
# Load the mechdb file inside Mechanical

app.open(mechdb_path)

# %%
# Display the project tree
# ~~~~~~~~~~~~~~~~~~~~~~~~

app.print_tree()

# %%
# Display the tree only under the first analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

first_analysis = app.Model.Analyses[0]
app.print_tree(first_analysis)


# %%
# Clean up the downloaded files and app
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Delete the downloaded files
delete_downloads()

# Refresh the app
app.new()
