# VISION: Standalone-module convention + PyPI release cut

**Project slug:** `standalone-scripts-and-pypi-release`
**Date:** 2026-07-11
**Repo:** `ppsyOps/psse_utils` (`C:\Users\Chris\PycharmProjects\psse_utils`)

## Origin

While reviewing the just-built `filter-taralog-notcnv` script (originally
scaffolded in the wrong repo, `psse_model_util`, then rebuilt in `psse_utils`
per its per-script convention), two follow-up questions came up:

1. Is there CI to publish `psse_utils` to PyPI, matching `psse_model_util`?
2. Do `psse_utils`'s docs make clear that each script module is meant to
   avoid depending on its sibling script modules?

## Investigation findings (pre-gate)

**PyPI publishing already works — not a gap.** `.github/workflows/publish.yml`
(Trusted Publishing/OIDC, triggers on GitHub Release `published` or manual
`workflow_dispatch`) was carried over intact from the `psse_model_util`
pattern during the June 2026 repo repurpose. GitHub environments `pypi`
(reviewer-gated) and `testpypi` are configured. `psse-utils 2026.6.0b1` is
already live on PyPI containing `flowgate-key-facilities`. No new CI is
needed — only a routine release cut for the new script.

**Standalone-module convention is undocumented — real gap.** The user's
intent, clarified: each `.py` file under `src/psse_utils/` should not import
any *sibling* module from the `psse_utils` package itself (no
`psse_utils.<other_script>` imports). Third-party dependencies (`pandas`,
`psse_model_util`, stdlib) are explicitly fine — the constraint is about
**intra-package coupling between script modules**, not about avoiding
external dependencies. This lets a user copy a single script `.py` file out
of the repo, `pip install` its declared third-party deps, and run it
standalone without the rest of `psse_utils`.

Checked both existing scripts against this definition:
- `flowgate_key_facilities.py` — imports only `psse_model_util` (3rd party). Compliant.
- `filter_taralog_notcnv.py` — stdlib only. Compliant.
- Neither imports the other, or any other `psse_utils.*` module (only
  `__init__.py` imports `psse_utils.__about__`, which is metadata, not a
  script).

So **no code changes are needed for compliance today** — both scripts
already satisfy the constraint. The gap is purely that this constraint is
not written down anywhere (not in `README.md`'s "Adding a script" section,
not in `docs/superpowers/specs/2026-06-23-psse-utils-design.md`), so nothing
stops a future script from violating it.

## Scope (confirmed with user)

1. **Document the standalone-module convention.** Add it as an explicit,
   named rule to the repo's docs (README "Adding a script" section is the
   most likely home; the design spec may also want an update) — a concise,
   standard-parlance description (e.g. "no intra-package imports between
   script modules — each script may depend on stdlib and third-party
   packages, but not on another `psse_utils.<script>` module") plus the
   rationale (a user can `pip install` the third-party deps and copy a
   single `.py` file out of the repo to run it standalone).
2. **Cut a PyPI release** for the pending `filter-taralog-notcnv` work:
   commit + push the currently-uncommitted changes (script, tests, fixtures,
   README/pyproject/conftest updates already reviewed), bump the CalVer
   version in `src/psse_utils/__about__.py` (current: `2026.6.0b1`; today is
   2026-07-11, so `2026.7.0b1` under the existing `YYYY.M.micro` scheme,
   pending confirmation at the design gate), and publish via a GitHub
   Release to trigger the existing `publish.yml`.

## Out of scope

- Building any new CI/CD (publish.yml + environments already exist and work).
- Retrofitting `flowgate_key_facilities.py` or `filter_taralog_notcnv.py` for
  compliance — both already comply; nothing to change there.
- An automated linter/CI check enforcing the no-sibling-import rule (may be
  proposed as an option at the design gate, but is not assumed in scope).
