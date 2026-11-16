#!/usr/bin/env python3
"""Build the multi-branch documentation site.

Every branch listed in docs/branches.json is checked out in a temporary git
worktree and built with Sphinx into <out>/<branch>/. The script also writes
<out>/branches.json (read by the sidebar branch switcher) and an
<out>/index.html redirecting to the first listed branch.

Each branch is built with its own requirements.txt in its own virtualenv, so
branches may depend on different Sphinx extensions.

Usage:
    python3 docs/build_site.py [--out site] [--branches docs/branches.json]
                               [--remote origin] [--strict]

Branch refs are resolved as <remote>/<branch> when that ref exists, otherwise
as the local branch. Run `git fetch` first to build up-to-date remote branches.
"""

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run(cmd, check=True, **kw)


def ref_exists(repo, ref):
    return subprocess.run(
        ["git", "-C", repo, "rev-parse", "--verify", "--quiet", ref + "^{commit}"],
        stdout=subprocess.DEVNULL,
    ).returncode == 0


def resolve_ref(repo, remote, branch):
    for ref in (f"{remote}/{branch}", branch):
        if ref_exists(repo, ref):
            return ref
    return None


def build_branch(repo, ref, dest, workdir, strict):
    wt = workdir / "wt"
    env_dir = workdir / "venv"
    run(["git", "-C", repo, "worktree", "add", "--detach", str(wt), ref])
    try:
        venv.create(env_dir, with_pip=True)
        py = env_dir / ("Scripts" if os.name == "nt" else "bin") / "python"
        req = wt / "docs" / "source" / "requirements.txt"
        run([py, "-m", "pip", "install", "-q", "--upgrade", "pip"])
        run([py, "-m", "pip", "install", "-q", "sphinx", *(["-r", req] if req.exists() else [])])
        cmd = [py, "-m", "sphinx", "-b", "html", wt / "docs" / "source", dest]
        if strict:
            cmd[3:3] = ["-W", "--keep-going"]
        run(cmd)
    finally:
        run(["git", "-C", repo, "worktree", "remove", "--force", str(wt)])


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="site", help="output directory (default: site)")
    ap.add_argument("--branches", default=str(here / "branches.json"))
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--strict", action="store_true", help="turn Sphinx warnings into errors")
    args = ap.parse_args()

    repo = subprocess.check_output(
        ["git", "-C", str(here), "rev-parse", "--show-toplevel"], text=True).strip()
    branches = json.loads(Path(args.branches).read_text())
    out = Path(args.out).resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    published = []
    for entry in branches:
        name = entry["branch"]
        ref = resolve_ref(repo, args.remote, name)
        if ref is None:
            print(f"warning: branch '{name}' not found, skipped", file=sys.stderr)
            continue
        with tempfile.TemporaryDirectory(prefix="docbuild-") as tmp:
            build_branch(repo, ref, out / name, Path(tmp), args.strict)
        published.append(entry)

    if not published:
        sys.exit("error: no branch could be built")

    (out / "branches.json").write_text(json.dumps(published, indent=2) + "\n")
    default = html.escape(published[0]["branch"])
    (out / "index.html").write_text(
        "<!doctype html>\n<meta charset=\"utf-8\">\n"
        "<title>Onika documentation</title>\n"
        f"<meta http-equiv=\"refresh\" content=\"0; url={default}/\">\n"
        f"<link rel=\"canonical\" href=\"{default}/\">\n"
        f"<p>Redirecting to <a href=\"{default}/\">{default}/</a>...</p>\n")
    (out / ".nojekyll").write_text("")
    print(f"site written to {out}: " + ", ".join(e["branch"] for e in published))


if __name__ == "__main__":
    main()
