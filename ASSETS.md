# Where the big files live

Large, non-deployable working files are kept **outside this repo**, in a sibling
directory:

```
~/Documents/
├── lim2026/            ← this repo: deployed site + versioned source
└── lim2026-assets/     ← sources, archives, exports, scratch (NOT in git)
```

## Why outside rather than gitignored

A `.gitignore` entry is a request. A sibling directory is a wall — `git add -A`
physically cannot reach outside the repo root, so a stray `git add -f` or a
mis-scoped rule can't drag a gigabyte into history. That matters because once a
large binary is committed, removing it means `git filter-repo`, a force-push,
and everyone re-cloning. Prevention is much cheaper than cleanup.

## What's over there now

| Path | Size | What it is |
|---|---|---|
| `archive/squarespace/images/` | 1.0 GB | Every image from the old Squarespace site (4,365 files) |
| `archive/squarespace/html/` | 375 MB | Raw HTML of all 1,459 archived pages, exactly as served |

The repo keeps the small, valuable half of the archive: `archive/squarespace/posts/`
(markdown, 9.5 MB), `index.json` (the record of every page and its images), and
`index.html` (the searchable index).

`archive/squarespace/images` and `.../html` inside this repo are **symlinks** into
the sibling, so the archive index, the markdown image links, and
`archive-squarespace.py` all still resolve locally. Both symlink paths are
gitignored — note the rules have **no trailing slash**, because a symlink is a
file to git and a directory-only rule would miss it.

## This is not a backup

The sibling sits on the same disk as the repo. Losing the drive loses both.
`lim2026-assets` must be replicated somewhere — an external drive, or a synced
folder — or the archive exists in exactly one place. **Once the Squarespace
subscription lapses, none of it can be re-downloaded.**

## Rebuilding the archive tooling

`.venv-archive/` was deleted rather than moved, because a Python venv hardcodes
its own absolute path and breaks when relocated. To run `archive-squarespace.py`
again:

```sh
python3 -m venv .venv-archive
./.venv-archive/bin/pip install beautifulsoup4 markdownify lxml requests
```

## The standard, for other projects

Worth adopting whenever a project accumulates large non-deployable artifacts.
The trigger is noticing you're writing `.gitignore` rules for big binaries.

- `<project>/` — what deploys, plus source worth versioning
- `<project>-assets/` — raw media, archives, exports, scratch, virtualenvs
- An `ASSETS.md` in the repo saying what's over there and where it's backed up,
  so it's still discoverable in a year
- Symlink back into the repo for anything tooling expects to find in place, and
  gitignore the symlink

For a small project it's overhead. Don't bother until there's something big.

## Still worth moving here

**`assets/` — 1.0 GB, only 7 files tracked, zero references from any page we
serve.** The `assets/...` strings that turn up in a grep are inside *archived
Squarespace HTML*, not our own markup. This is the largest remaining candidate;
the 7 tracked files would need to stay or move deliberately:

```
assets/about25-vo-script-bonnie-updates.md
assets/healing-groups-discussion-15-jan-2025.md
assets/healing-groups-register-concept.html
assets/speaker-1-gem-hires.png … speaker-4-gem-hires.png
```

**`generated_imgs/` — 77 MB — must stay.** It's referenced 11 times by live
pages (the blog hero images).

**`.git` is 1.6 GB.** That's history, not working files, and moving things now
won't shrink it. Only worth addressing if clone times start to hurt.
