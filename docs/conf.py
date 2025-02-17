# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
import os
import sys

import django

sys.path.insert(0, os.path.abspath("../src"))
os.environ["LOG_REQUESTS"] = "false"

import openforms  # noqa isort:skip

from openforms.setup import setup_env  # noqa isort:skip

setup_env()
django.setup()

# -- Project information -----------------------------------------------------

project = "Open Forms"
copyright = "2022, Maykin Media"
author = openforms.__author__

# The full version, including alpha/beta/rc tags
release = openforms.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.intersphinx",
    "sphinx_tabs.tabs",
    "recommonmark",
    # "sphinx_markdown_tables",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".pytest_cache", "_archive"]

source_suffix = [".rst", ".md"]

intersphinx_mapping = {
    "requests": (
        "https://docs.python-requests.org/en/latest/",
        None,
    ),
    "ape_pie": (
        "https://ape-pie.readthedocs.io/en/latest/",
        None,
    ),
    "django": (
        "http://docs.djangoproject.com/en/3.2/",
        "http://docs.djangoproject.com/en/3.2/_objects/",
    ),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_logo = "logo.svg"
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = [
    "theme_overrides.css",  # override wide tables with word wrap
]

todo_include_todos = True

linkcheck_ignore = [
    r"urn:*",
    r"https?://.*\.gemeente.nl",
    r"http://localhost:\d+/",
    r"https://.*sentry.*",
    r"https://example.com*",
    r"https://portal.azure.com*",
    r"https://.*kvk\.nl*",
    r"https://gdpr.eu*",
    r"https://www\.omg\.org/*",  # incredibly unstable domain...
    r"https://www\.jccsoftware\.nl/.*",  # looks like the requests user agent is blocked...
    r"https://hub\.docker\.com/r/.*",  # HTTP 429, presumably docker hub is blocking/limiting Github CI runners
]
