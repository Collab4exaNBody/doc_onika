#!/usr/bin/env bash
# Builds one documentation site per branch, with a version selector.
#
#   scripts/build_versions.sh [output_dir] [branch ...]
#
# Output (default: public/):
#   public/<branch>/      the site built from <branch>
#   public/versions.json  the branch list read by the version selector
#   public/index.html     redirect to the default (first) branch
#
# Branches default to $DOC_BRANCHES, else "main". The first one is the default
# version. Each branch is built from a temporary git worktree; local branches
# are used when they exist, otherwise origin/<branch>. The version selector
# setting is added to the branch's zensical.toml if it does not have it.
set -euo pipefail

repo=$(git rev-parse --show-toplevel)
out=$(realpath -m "${1:-public}")
shift || true
if [ $# -gt 0 ]; then branches=("$@"); else read -r -a branches <<< "${DOC_BRANCHES:-main}"; fi
default=${branches[0]}

work=$(mktemp -d)
cleanup() {
  for b in "${branches[@]}"; do git -C "$repo" worktree remove --force "$work/$b" 2>/dev/null || true; done
  rm -rf "$work"
}
trap cleanup EXIT

rm -rf "$out"
mkdir -p "$out"

for b in "${branches[@]}"; do
  if git -C "$repo" rev-parse --verify --quiet "refs/heads/$b" >/dev/null; then ref=$b
  elif git -C "$repo" rev-parse --verify --quiet "refs/remotes/origin/$b" >/dev/null; then ref=origin/$b
  else echo "error: branch '$b' not found (locally or on origin)" >&2; exit 1; fi

  echo "=== $b ($ref)"
  git -C "$repo" worktree add --detach "$work/$b" "$ref" >/dev/null
  (
    cd "$work/$b"
    if ! grep -q '^\[project\.extra\.version\]' zensical.toml; then
      python3 - "$default" <<'EOF'
import sys
p = 'zensical.toml'
s = open(p).read()
block = '[project.extra.version]\nprovider = "mike"\ndefault = "%s"\n\n' % sys.argv[1]
if '[project.theme]' not in s:
    sys.exit('zensical.toml has no [project.theme] table')
open(p, 'w').write(s.replace('[project.theme]', block + '[project.theme]', 1))
EOF
    fi
    zensical build --clean
  )
  cp -r "$work/$b/site" "$out/$b"
done

python3 - "$out" "${branches[@]}" <<'EOF'
import json, sys
out, branches = sys.argv[1], sys.argv[2:]
versions = [{"version": b, "title": b, "aliases": ["latest"] if i == 0 else []} for i, b in enumerate(branches)]
json.dump(versions, open(out + '/versions.json', 'w'), indent=2)
EOF

cat > "$out/index.html" <<EOF
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting</title>
<meta http-equiv="refresh" content="0; url=$default/index.html">
<link rel="canonical" href="$default/index.html">
</head>
<body><a href="$default/index.html">Onika documentation</a></body>
</html>
EOF
touch "$out/.nojekyll"
echo "=== done: $out (${branches[*]}, default $default)"
