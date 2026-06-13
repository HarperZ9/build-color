# AGENTS.md - Quanta Color

## Scope

This file applies to the `quanta-color` repository. Root workspace instructions
still apply; this repo is a public Python color-science library and a dependency
surface for Calibrate Pro.

## Product Boundary

Quanta Color is a reusable color-science package. Keep the public repo focused
on deterministic color transforms, color appearance models, tone mapping,
spectral utilities, gamut mapping, LUT/ICC helpers, CLI behavior, and optional
GUI workbench surfaces.

Publishable surfaces:

- `quanta_color/` - package code.
- `tests/` - regression coverage for spaces, adaptation, tone mapping,
  spectral math, gamut, harmony, difference metrics, CVD simulation, and LUT IO.
- `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `docs/`, and `pyproject.toml` -
  package and product posture.

Keep local-only unless deliberately scrubbed:

- `.env`, `.env.*`, `.warden-safe-cache/`, local settings, generated logs, and
  build artifacts.
- Generated ICC/LUT/profile files, screenshots, private display measurements,
  and customer or device-identifying calibration data.

## Editing Rules

- Preserve numerical behavior with focused tests; color math regressions are
  easy to make and hard to see by inspection alone.
- Keep optional GUI dependencies optional. Core package tests should not require
  PyQt6.
- Keep CLI examples aligned with `pyproject.toml` entry points.
- When adding a new color model, tone mapper, or difference metric, document the
  source model and add at least one roundtrip, invariant, or known-value test.

## Verification

For documentation or release-boundary changes:

```powershell
git diff --check
```

For package behavior changes, run the focused core suite:

```powershell
python -m pytest tests/test_spaces.py tests/test_adaptation.py tests/test_tonemap.py -q
python -m pytest tests/test_difference.py tests/test_gamut.py tests/test_lut_io.py -q
```

Before committing or pushing, scan changed files for credential-shaped content
and confirm `.env` remains ignored.
