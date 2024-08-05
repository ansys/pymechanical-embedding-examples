""" .. _ref_tips_04:

Add logging
-----------

Add logging to the workflow
"""

# %%
# Import necessary libraries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

import logging

import ansys.mechanical.core as mech
from ansys.mechanical.core.embedding.logger import Configuration, Logger

# %%
# Configure logger to display only warning to stdout

Configuration.configure(level=logging.WARNING, to_stdout=True)

# %%
# Embed mechanical and set global variables

Configuration.configure(level=logging.ERROR, to_stdout=True)
app = mech.App(version=242)
app.update_globals(globals())
print(app)

# %%
# Add a custom error message to logging

Logger.error("Test error")

# %%
# Modify logging level and create a warning log

Configuration.set_log_level(logging.INFO)
Logger.warning("Test warning")

# %%
# Cleanup
# ~~~~~~~

app.new()
