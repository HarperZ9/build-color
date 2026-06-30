# Build Color v1.0.1

## Release Type

Patch release for current public package state and release-artifact
normalization.

## Verification

- `python -m pytest -q`
- `python -m build`
- `python -m twine check dist/*`
- `PYTHONPATH=C:\dev\public\public-surface-sweeper\src python -m public_surface_sweeper . --summary`
- `git diff --check`

## Artifacts

- `build_color-1.0.1-py3-none-any.whl`
- `build_color-1.0.1.tar.gz`

## Publishing Notes

GitHub Release artifacts are in scope. PyPI publication remains separate and
requires registry credentials.
