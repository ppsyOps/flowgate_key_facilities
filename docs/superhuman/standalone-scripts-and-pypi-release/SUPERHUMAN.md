# SUPERHUMAN.md — standalone-scripts-and-pypi-release

Superhuman-version: 0.4.0
Slug: standalone-scripts-and-pypi-release
Repo: ppsyOps/psse_utils (C:\Users\Chris\PycharmProjects\psse_utils)
Environment: dev (laptop Claude Code)

## Preferences (G1)

- Cadence: on-divergence (single combined gate for requirements+design+test-plan;
  G5 fires as one-liner notifications thereafter unless drift occurs)
- Value-vs-foundation: n/a (doc + release project, no feature tradeoff)
- Git/remote: origin already configured (ppsyOps/psse_utils); work directly on
  master, no feature branch/PR
- Parallelism: not applicable (2 small sequential chunks)
- Autonomous mode: not requested (off)

## Decisions log

[2026-07-11] G0: VISION approved; user decision: approve
  - Scope: (1) document the no-sibling-import "standalone module" convention;
    (2) cut a version-bumped PyPI release including filter-taralog-notcnv.
  - No code compliance work needed — both existing scripts already comply.

[2026-07-11] G1: Workflow preferences approved; user decision: approve
  - Cadence: on-divergence. Git: direct on master.

[2026-07-11] G2+G3+G4 (combined, on-divergence cadence): REQUIREMENTS/DESIGN/TEST approved; user decision: approve
  - Option A README wording + design-spec echo; 2 chunks (docs, release);
    version bump to 2026.7.0b1; PM creates+publishes the GitHub Release
    (user still separately approves the pypi-environment reviewer gate).

## Retuning notes

(none yet)

## Chunk log

- Chunk 1 (R1 — docs): pending
- Chunk 2 (R2 — release): pending
