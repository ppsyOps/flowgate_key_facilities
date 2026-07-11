# DESIGN: Standalone-module convention + PyPI release cut

**Slug:** `standalone-scripts-and-pypi-release`
**Date:** 2026-07-11

## Chunking

Two independent, sequential chunks:

- **Chunk 1 — Docs (R1):** edit `README.md` "Adding a script" section (+
  optionally the design spec) to state the no-sibling-import rule and
  rationale.
- **Chunk 2 — Release (R2):** commit pending work, bump version, push,
  create GitHub Release, verify PyPI install.

No parallelism needed/possible — Chunk 2's commit should include Chunk 1's
doc edit (one clean commit that both documents the convention and ships the
release it documents), so Chunk 1 runs first.

## R1 — Wording approach (3 options)

**Option A — Named rule, one paragraph (Recommended).** Add a labeled
subsection or bullet to README's "Adding a script" list, e.g.:

> **No intra-package imports.** A script module may depend on stdlib and
> third-party packages (e.g. `pandas`, `psse_model_util`) but must never
> import another `psse_utils.<script>` module. This keeps every script
> copy-paste portable: install its declared third-party dependencies and
> the single `.py` file runs standalone, without the rest of this repo.

Pro: matches the existing README style (short, numbered/bulleted
constraints under "Adding a script"). Con: none significant.

**Option B — Separate "Design principles" section.** Pull this rule (and
the existing logic/CLI-separation rule) out of the numbered "Adding a
script" checklist into a new top-level "Design principles" section.

Pro: gives room to grow more principles later. Con: larger doc restructure
than the ask calls for; existing spec already treats "separate logic from
CLI" as a per-script convention inline, so splitting now is inconsistent
with that.

**Option C — Design-spec-only.** Only update
`docs/superpowers/specs/2026-06-23-psse-utils-design.md`, not README.

Pro: keeps README terse. Con: fails R1.3/R1.5 — a contributor reading just
the README (the more likely entry point) wouldn't see the rule.

**Recommendation: Option A**, plus a one-line echo in the design spec's
"Per-script convention" bullet list so the two documents agree (satisfies
R1.3's "secondary" home without a restructure).

## R2 — Release mechanics

1. `git add` the reviewed pending files (`src/psse_utils/filter_taralog_notcnv.py`,
   the three test files, three data fixtures, `tests/e2e/`, plus modified
   `README.md` (incl. R1 doc edit), `pyproject.toml`, `tests/conftest.py`).
2. Bump `src/psse_utils/__about__.py` `__version__` → `2026.7.0b1`.
3. One commit on `master`, pushed to `origin` (`gh auth switch --user OrionAIDev`
   first per repo access convention).
4. `pdm run pytest` green before pushing (already verified 34 passed/100%
   coverage in the prior session — re-run once more after the version bump
   to catch any regression from the bump itself, e.g. a version-string test).
5. Create a GitHub Release (tag `v2026.7.0b1` or `2026.7.0b1` — match
   whatever tag scheme `psse_model_util`/the runbook uses) — **PM confirms
   the exact tag and release trigger with the user immediately before
   publishing**, since a Release is a visible/external action.
6. `publish.yml` fires: build → TestPyPI (auto) → PyPI (gated on the
   `pypi` environment's required reviewer, `cadvena`, who must approve the
   deployment in the GitHub Actions UI).
7. Verify: `pip install --pre psse-utils==2026.7.0b1` in a clean venv,
   confirm both console scripts (`flowgate-key-facilities --help`,
   `filter-taralog-notcnv --help`) work.

## Declared artifact set

- `README.md` (updated)
- `docs/superpowers/specs/2026-06-23-psse-utils-design.md` (updated,
  one-line echo)
- `src/psse_utils/__about__.py` (version bump)
- No new source/test files beyond what's already staged from the prior
  session (`filter_taralog_notcnv.py` + its tests/fixtures) — those are
  reused as-is, already reviewed.
