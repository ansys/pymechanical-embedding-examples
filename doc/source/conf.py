"""Sphinx documentation configuration file."""
from datetime import datetime
import os

import ansys.mechanical.core
from ansys_sphinx_theme import ansys_favicon
from ansys_sphinx_theme import pyansys_logo_black as logo
import numpy as np
import pyvista
from sphinx_gallery.sorting import FileNameSortKey

# Project information
project = "pymechanical-embedding-examples"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = "0.1.dev0"

# Select desired logo, theme, and declare the html title
html_logo = logo
html_favicon = ansys_favicon
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "PyMechanical Embedding Examples"

# specify the location of your github repo
html_theme_options = {
    "github_url": "https://github.com/ansys/pymechanical-embedding-examples",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
        ("PyMechanical", "https://mechanical.docs.pyansys.com/"),
    ],
    "icon_links": [
        {
            "name": "Support",
            "url": "https://github.com/ansys/pymechanical-embedding-examples/discussions",
            "icon": "fa fa-comment fa-fw",
        },
    ],
}

# Sphinx extensions
extensions = [
    "jupyter_sphinx",
    "notfound.extension",
    "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_gallery.gen_gallery",
    "sphinxemoji.sphinxemoji",
]

# -- Sphinx Gallery Options ---------------------------------------------------
sphinx_gallery_conf = {
    # convert rst to md for ipynb
    "pypandoc": True,
    # path to your examples scripts
    "examples_dirs": ["../../examples/basic"],
    # path where to save gallery generated examples
    "gallery_dirs": ["basic"],
    # Pattern to search for example files
    "filename_pattern": r"\.py",
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # Sort gallery example by file name instead of number of lines (default)
    "within_subsection_order": FileNameSortKey,
    # directory where function granular galleries are stored
    "backreferences_dir": None,
    # Modules for which function level galleries are created. In
    "doc_module": "ansys-mapdl-core",
    "image_scrapers": ("pyvista", "matplotlib"),
    "ignore_pattern": "flycheck*",
    "thumbnail_size": (350, 350),
}

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/dev", None),
}

# numpydoc configuration
numpydoc_use_plots = True
numpydoc_show_class_members = False
numpydoc_class_members_toctree = False
numpydoc_xref_param_type = True

# Image referencing
numfig = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

# pyvista is not yet used for these examples but the sphinx build fails if it isn't configured
pyvista.set_error_output_file("errors.txt")
pyvista.OFF_SCREEN = True
pyvista.BUILDING_GALLERY = True

# must be less than or equal to the XVFB window size
try:
    pyvista.global_theme.window_size = np.array([1024, 768])
except AttributeError:
    # for compatibility with pyvista < 0.40
    pyvista.rcParams["window_size"] = np.array([1024, 768])

# Save figures in specified directory
pyvista.FIGURE_PATH = os.path.join(os.path.abspath("./images/"), "auto-generated/")
if not os.path.exists(pyvista.FIGURE_PATH):
    os.makedirs(pyvista.FIGURE_PATH)

# configure pymechanical for embedding
ansys.mechanical.core.BUILDING_GALLERY = True
if "PYMECHANICAL_BUILDING_GALLERY_GITHUB" in os.environ:
    app = ansys.mechanical.core.App(version=232)
    config = app.ExtAPI.Application.SolveConfigurations["My Computer"]
    config.SolveProcessSettings.MaxNumberOfCores = 1
    config.SolveProcessSettings.DistributeSolution = False

# static path
html_static_path = ["_static"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "links.rst",
]

# make rst_epilog a variable, so you can add other epilog parts to it
rst_epilog = ""
# Read link all targets from file
with open("links.rst") as f:
    rst_epilog += f.read()
