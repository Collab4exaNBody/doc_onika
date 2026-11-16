.. _contributing-docs:

Contributing to this documentation
==================================

|user| |opdev| |core|

The sources are in https://github.com/Collab4exaNBody/doc_onika, in
reStructuredText under ``docs/source``.

Build locally
-------------

.. code-block:: bash

   $ python3 -m venv .venv && source .venv/bin/activate
   $ pip install -r docs/source/requirements.txt
   $ sphinx-build -W --keep-going -b html docs/source docs/build
   $ open docs/build/index.html     # or xdg-open on Linux

``-W`` turns warnings into errors, as in the CI: fix them before pushing.

Page conventions
----------------

- One section per directory: ``discover``, ``getting-started``, ``inputs``,
  ``operators``, ``running``, ``python``, ``reference``, ``project``.
- Each page starts with a label (``.. _my-page:``) and links with
  ``:ref:`my-page```, so that pages can move without breaking links.
- Under the title, badges tell who the page is for: ``|user|``, ``|opdev|``,
  ``|core|`` (defined in ``conf.py``).
- Examples must be run against a real Onika build before being documented.
  Copy the real output.
- Diagrams use Mermaid (``.. mermaid::``), no image files needed.

Several branches online: previews
---------------------------------

The website publishes several branches side by side. A selector in the
sidebar switches between them, keeping the current page when it exists.

- The list of published branches is ``docs/branches.json`` **on the main
  branch**. The first entry is the default, served at the site root.
- Each entry has a ``branch``, a ``label`` (shown in the selector) and an
  optional ``banner`` (shown at the top of every page of that branch).

.. code-block:: json

   [
     { "branch": "main",    "label": "Current documentation (main)" },
     { "branch": "new-doc", "label": "Preview: new documentation (new-doc)",
       "banner": "You are reading a PREVIEW ..." }
   ]

To preview a branch for colleagues:

1. Push your branch.
2. Add it to ``docs/branches.json`` on ``main``.
3. The ``Documentation`` workflow rebuilds the site: each branch is built with
   its own ``requirements.txt`` into ``/<branch>/``.

Pushing to a published branch later triggers a rebuild of the site
automatically. To stop publishing a branch, remove it from
``docs/branches.json``.

Build the whole site locally (all published branches):

.. code-block:: bash

   $ git fetch origin
   $ python3 docs/build_site.py --out site
   $ python3 -m http.server -d site 8000      # then open http://localhost:8000
