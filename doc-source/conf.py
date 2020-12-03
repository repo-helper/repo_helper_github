#!/usr/bin/env python3

# This file is managed by 'repo_helper'. Don't edit it directly.

# stdlib
import os
import re
import sys

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath(".."))

# this package
from __pkginfo__ import __version__

github_username = "repo-helper"
github_repository = "repo_helper_github"
github_url = f"https://github.com/{github_username}/{github_repository}"

rst_prolog = f""".. |pkgname| replace:: repo_helper_github
.. |pkgname2| replace:: ``repo_helper_github``
.. |browse_github| replace:: `Browse the GitHub Repository <{github_url}>`__
"""

author = "Dominic Davis-Foster"
project = "repo_helper_github"
slug = re.sub(r'\W+', '-', project.lower())
release = version = __version__
copyright = "2020 Dominic Davis-Foster"  # pylint: disable=redefined-builtin
language = "en"
package_root = "repo_helper_github"

extensions = [
		"sphinx_toolbox",
		"sphinx_toolbox.more_autodoc",
		"sphinx_toolbox.more_autosummary",
		"sphinx_toolbox.tweaks.param_dash",
		"sphinx.ext.intersphinx",
		"sphinx.ext.mathjax",
		"sphinxcontrib.httpdomain",
		"sphinxcontrib.extras_require",
		"sphinx.ext.todo",
		"sphinxemoji.sphinxemoji",
		"notfound.extension",
		"sphinx_copybutton",
		"sphinxcontrib.default_values",
		"sphinxcontrib.toctree_plus",
		"seed_intersphinx_mapping",
		"sphinx_click",
		]

sphinxemoji_style = "twemoji"
todo_include_todos = bool(os.environ.get("SHOW_TODOS", 0))
gitstamp_fmt = "%d %b %Y"

templates_path = ["_templates"]
html_static_path = ["_static"]
source_suffix = ".rst"
master_doc = "index"
suppress_warnings = ["image.nonlocal_uri"]
pygments_style = "default"

intersphinx_mapping = {
		"python": ("https://docs.python.org/3/", None),
		"sphinx": ("https://www.sphinx-doc.org/en/stable/", None),
		"pygithub": ("https://pygithub.readthedocs.io/en/latest", None),
		"click": ("https://click.palletsprojects.com/en/7.x/", None),
		}

html_theme = "furo"
html_theme_options = {
		"light_css_variables": {
				"toc-title-font-size": "12pt",
				"toc-font-size": "12pt",
				"admonition-font-size": "12pt",
				},
		"dark_css_variables": {
				"toc-title-font-size": "12pt",
				"toc-font-size": "12pt",
				"admonition-font-size": "12pt",
				},
		}
html_theme_path = ["../.."]
html_show_sourcelink = True  # True will show link to source

html_context = {}
htmlhelp_basename = slug

latex_documents = [("index", f'{slug}.tex', project, author, "manual")]
man_pages = [("index", slug, project, [author], 1)]
texinfo_documents = [("index", slug, project, author, slug, project, "Miscellaneous")]

toctree_plus_types = {
		"class",
		"function",
		"method",
		"data",
		"enum",
		"flag",
		"confval",
		"directive",
		"role",
		"confval",
		"protocol",
		"typeddict",
		"namedtuple",
		"exception",
		}

add_module_names = False
hide_none_rtype = True
all_typevars = True
overloads_location = "bottom"


autodoc_exclude_members = [   # Exclude "standard" methods.
		"__dict__",
		"__class__",
		"__dir__",
		"__weakref__",
		"__module__",
		"__annotations__",
		"__orig_bases__",
		"__parameters__",
		"__subclasshook__",
		"__init_subclass__",
		"__attrs_attrs__",
		"__init__",
		"__new__",
		"__getnewargs__",
		"__abstractmethods__",
		"__hash__",
		]
autodoc_default_options = {
		"members": None,  # Include all members (methods).
		"special-members": None,
		"autosummary": None,
		"show-inheritance": None,
		"exclude-members": ','.join(autodoc_exclude_members),
		}
