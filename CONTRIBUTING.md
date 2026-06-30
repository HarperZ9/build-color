# Contributing

Build Color is a public color-science package. Contributions should preserve
numerical behavior, keep optional GUI dependencies optional, and include focused
tests for color transforms, appearance models, tone mapping, gamut behavior, or
LUT/ICC output.

## Local Setup

```powershell
python -m pip install -e ".[all]"
python -m pip install pytest ruff
```

## Verification

For release-boundary and documentation changes:

```powershell
git diff --check
```

For core package changes:

```powershell
python -m pytest tests/test_spaces.py tests/test_adaptation.py tests/test_tonemap.py -q
python -m pytest tests/test_difference.py tests/test_gamut.py tests/test_lut_io.py -q
```

For broader changes, run the full test suite:

```powershell
python -m pytest tests/ -q
```

Do not commit `.env` files, generated display measurements, private device
profiles, credentials, or local-only build artifacts.
