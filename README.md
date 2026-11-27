# Onika documentation

Sources of the documentation of [Onika](https://github.com/Collab4exaNBody/onika),
published at https://collab4exanbody.github.io/doc_onika/.

The documentation is written in Markdown (`docs/`) and built with
[Zensical](https://zensical.org/), configured in `zensical.toml`.

## Build locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install zensical
zensical serve            # live preview on http://localhost:8000
zensical build --strict   # static site in site/
```

## Published versions

Only `main` is published for now (`DOC_BRANCHES` in
`.github/workflows/docs.yml`). More branches can be added there to publish
previews side by side, with a version selector in the header. See
`docs/project/contributing-docs.md`.

Build the published site locally:

```bash
bash scripts/build_versions.sh public main
python3 -m http.server -d public 8000
```
