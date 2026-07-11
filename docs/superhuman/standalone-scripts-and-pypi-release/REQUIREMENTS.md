# REQUIREMENTS: Standalone-module convention + PyPI release cut

**Slug:** `standalone-scripts-and-pypi-release`
**Date:** 2026-07-11

## R1 — Document the standalone-module convention

**R1.1.** The repo's docs must state, in standard developer parlance, that
each script module under `src/psse_utils/` must have **no intra-package
imports** — i.e. no `psse_utils.<script>` script module may import another
`psse_utils.<script>` script module. Third-party packages (`pandas`,
`psse_model_util`, etc.) and stdlib are unrestricted. `__init__.py` /
`__about__.py` (package metadata, not scripts) are exempt from this rule.

**R1.2.** The doc must state the rationale: this lets someone copy a single
`.py` file out of the repo, `pip install` its declared third-party
dependencies, and run it standalone without the rest of `psse_utils`.

**R1.3.** Primary home: README.md's "Adding a script" section (the existing
per-script-convention checklist), since that's what a contributor reads
before adding a script. Secondary: note the same constraint in
`docs/superpowers/specs/2026-06-23-psse-utils-design.md` under "Per-script
convention" so the design record and the contributor-facing doc agree.

**R1.4.** Non-goal: no CI/lint enforcement of this rule in this project
(may be proposed as a future option, not required now).

**R1.5.** Acceptance: a reader of README.md's "Adding a script" section can,
without consulting any other doc, state the no-sibling-import rule and why
it exists.

## R2 — Cut a PyPI release including filter-taralog-notcnv

**R2.1.** All currently-uncommitted `filter-taralog-notcnv` work (already
reviewed against `git diff`/`git status` earlier this session — see prior
conversation turns) is committed and pushed to `master`.

**R2.2.** `src/psse_utils/__about__.py`'s `__version__` is bumped from the
currently-published `2026.6.0b1` to a new CalVer value (`YYYY.M.micro`
scheme). Given today is 2026-07-11, that's `2026.7.0b1` (still beta —
`psse-model-util`, the base dependency, is itself still pre-release, so
`psse-utils` stays `b1` per the existing convention noted in README/spec).

**R2.3.** A GitHub Release is created (human-in-the-loop: PM will prepare
the tag/release, but per Trapezia-adjacent discipline the release action
itself is a "visible to others" action — PM confirms with user immediately
before publishing) which triggers the existing `.github/workflows/publish.yml`
Trusted Publishing workflow: TestPyPI publish automatically, then PyPI
publish gated by the `pypi` environment's required reviewer (`cadvena`).

**R2.4.** Acceptance: `pip install --pre psse-utils==2026.7.0b1` (or
whatever version is actually cut) succeeds from PyPI and exposes both
`flowgate-key-facilities` and `filter-taralog-notcnv` console commands.

## Out of scope

- Any change to `flowgate_key_facilities.py` or `filter_taralog_notcnv.py`
  source (both already comply with R1).
- Automated enforcement (linter/CI check) of the no-sibling-import rule.
- Yanking or modifying the existing `2026.6.0b1` release.
