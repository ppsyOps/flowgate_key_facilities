# TEST PLAN: Standalone-module convention + PyPI release cut

**Slug:** `standalone-scripts-and-pypi-release`
**Date:** 2026-07-11

## Backup strategy

Existing-file edits are all additive/small (README section, one design-spec
bullet, one version string) on files already tracked by git on a clean
`origin/master`-synced branch — git history is the backup; no separate
snapshot needed. No destructive operations planned.

## R1 verification (docs — inference-driven, human-readable check)

- Manual read-through: does the new README paragraph state (a) the rule
  (no `psse_utils.<script>` importing another `psse_utils.<script>`) and
  (b) the rationale (copy-one-file portability), in one place, without
  requiring the design spec to understand it? (R1.5)
- Confirm the design-spec echo doesn't contradict the README wording.
- No automated test — this is documentation content, not executable
  behavior.

## R2 verification (release — code-driven)

1. `pdm run pytest` (or `.venv\Scripts\python -m pytest`) green after the
   version bump, before pushing. Re-confirms the 34/34 passing, 100%
   coverage result from the prior session still holds.
2. `python -m build` + `twine check dist/*` locally (or trust CI's `build`
   job) — sdist/wheel build cleanly, metadata valid.
3. After the Release triggers `publish.yml`: confirm the `publish-testpypi`
   job succeeds (GitHub Actions run green).
4. After PyPI-environment reviewer approval: confirm `publish-pypi` job
   succeeds.
5. Clean-venv install check: `python -m venv` a throwaway venv,
   `pip install --pre psse-utils==2026.7.0b1`, run
   `flowgate-key-facilities --help` and `filter-taralog-notcnv --help`,
   confirm both exit 0 and print usage.

## Out of scope for testing

- No new unit tests required — `filter-taralog-notcnv`'s own test suite
  (34 tests) was already written and verified in the prior session; this
  project only bumps its version and ships it.
