# Onika documentation

Sources of the documentation of [Onika](https://github.com/Collab4exaNBody/onika),
published at https://collab4exanbody.github.io/doc_onika/.

## Build locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r docs/source/requirements.txt
sphinx-build -W --keep-going -b html docs/source docs/build
```

Then open `docs/build/index.html`.

## Several branches online

The site publishes every branch listed in `docs/branches.json` (on `main`),
each under `/<branch>/`, with a branch selector in the sidebar. This is used to
preview a documentation branch for review while keeping the current one.
See `docs/source/project/contributing-docs.rst` for details.

Build the whole multi-branch site locally:

```bash
git fetch origin
python3 docs/build_site.py --out site
python3 -m http.server -d site 8000
```
