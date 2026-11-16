# Sphinx configuration for the Onika documentation.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = 'Onika'
copyright = '2023-2026, Thierry Carrard, Raphaël Prat, Jean-Philippe Perlat, Paul Lafourcade'
author = 'Thierry Carrard, Raphaël Prat, Jean-Philippe Perlat, Paul Lafourcade'

# Onika version documented here (keep in sync with project() in onika/CMakeLists.txt)
release = '1.0.4'
version = '1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.mathjax',
    'sphinxcontrib.bibtex',
    'sphinxcontrib.mermaid',
    'sphinx_tabs.tabs',
    'sphinx_copybutton',
    'sphinx_design',
]

mathjax3_config = {
    "tex": {
        "macros": {
            "AA": "\\unicode{197}"  # Unicode for Å
        }
    }
}

bibtex_bibfiles = ["bibliography.bib"]
bibtex_default_style = "plain"

templates_path = ['_templates']
exclude_patterns = ['requirements.txt', '*~']

# Do not copy shell prompts with the copy button
copybutton_prompt_text = r"\$ "
copybutton_prompt_is_regexp = True

# Operator graphs are drawn client-side with Mermaid (no Graphviz binary needed)
mermaid_version = "11.4.1"

# Reader paths, shown as badges at the top of each page.
# Use them as |user|, |opdev| and |core| in any page.
rst_prolog = """
.. |user| replace:: :bdg-info:`Simulation user`
.. |opdev| replace:: :bdg-success:`Operator developer`
.. |core| replace:: :bdg-warning:`Framework developer`
"""

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_title = f'Onika {release}'
html_logo = "_static/onika_logo.png"
html_theme_options = {
    'logo_only': False,
    'navigation_depth': 3,
    'collapse_navigation': False,
}
html_static_path = ['_static']


def setup(app):
    app.add_css_file('css/custom.css')
    app.add_js_file('js/branch-switcher.js')
