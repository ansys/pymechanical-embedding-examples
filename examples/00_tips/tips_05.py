""" .. _ref_tips_05:

Use ``app_libraries``
---------------------

Use app libraries which comes with Mechanical
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~


import ansys.mechanical.core as mech
from ansys.mechanical.core.embedding import add_mechanical_python_libraries

# %%
# Embed mechanical and set global variables

app = mech.App(version=242)
app.update_globals(globals())
print(app)

# %%
# Update path to libraries which are found under
# "Addins", "ACT", "libraries", "Mechanical"

add_mechanical_python_libraries(app)

# %%
# Update path to libraries which are found under
# "Addins", "ACT", "libraries", "Mechanical"


# %%
# Cleanup
# ~~~~~~~

app.new()
