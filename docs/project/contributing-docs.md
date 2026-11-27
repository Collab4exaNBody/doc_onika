# Contributing to this documentation

<span class="badge badge-user">Simulation user</span> <span class="badge badge-opdev">Operator developer</span> <span class="badge badge-core">Framework developer</span>

The sources are in <https://github.com/Collab4exaNBody/doc_onika>, in
Markdown under `docs/`, built with [Zensical](https://zensical.org/).
The navigation is defined in `zensical.toml` (`nav` entry).

## Build locally

``` bash
$ python3 -m venv .venv && source .venv/bin/activate
$ pip install zensical
$ zensical serve                  # live preview on http://localhost:8000
$ zensical build --strict         # static site in site/, warnings are errors
```

`--strict` turns warnings (broken links, missing pages) into errors, as in the CI: fix them before pushing.

## Page conventions

- One section per directory: `discover`, `getting-started`, `inputs`,
  `operators`, `coupling`, `python`, `libraries`, `running`, `reference`, `project`. Each new page must
  also be added to `nav` in `zensical.toml`.
- Link to other pages with relative paths to the `.md` file, e.g.
  `[operator anatomy](../operators/anatomy.md)`. Give important sections an
  explicit anchor, `## Batches { #msp-batches }`, and link to it with
  `../inputs/msp-language.md#msp-batches`, so that titles can change without
  breaking links.
- Under the title, badges tell who the page is for:

    ``` html
    <span class="badge badge-user">Simulation user</span>
    <span class="badge badge-opdev">Operator developer</span>
    <span class="badge badge-core">Framework developer</span>
    ```

- Examples must be run against a real Onika build before being documented.
  Copy the real output.
- Diagrams use Mermaid (a `mermaid` fenced code block), no image files needed.
  Images go in `docs/img/`.
- Notes and warnings are admonitions (`!!! note`, `!!! warning`), alternatives
  are content tabs (`=== "Spack"`), see the
  [Zensical authoring guide](https://zensical.org/docs/authoring/markdown/).

## Published versions and previews

The website currently publishes **only the `main` branch**. It is built by
`scripts/build_versions.sh` into `/main/`, and the site root redirects to it.

The same setup can publish other branches side by side, with a version
selector in the header. This is optional and not used today. The list of
published branches is `DOC_BRANCHES` in `.github/workflows/docs.yml`; the
first one is the default version.

To publish a preview of a branch for colleagues:

1. Push your branch.
2. Add it to `DOC_BRANCHES` in `.github/workflows/docs.yml`, on `main`
   and on your branch.
3. The `Documentation` workflow rebuilds and deploys the whole site.

To check a multi-branch site locally (optional):

``` bash
$ git fetch origin
$ bash scripts/build_versions.sh public main my-branch
$ python3 -m http.server -d public 8000      # then open http://localhost:8000
```
