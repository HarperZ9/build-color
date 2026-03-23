# Publishing quanta-color to PyPI

## Prerequisites
- Python 3.10+
- `pip install build twine`

## Step 1: Create PyPI Account
1. Go to https://pypi.org/account/register/
2. Create account, verify email
3. Enable 2FA (required for new accounts)

## Step 2: Generate API Token
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: "quanta-color"
4. Scope: "Entire account" (or project-specific after first upload)
5. Copy the token (starts with `pypi-`)

## Step 3: Build Package
```bash
cd quanta-color
python -m build
```

This creates:
- `dist/quanta_color-1.0.0.tar.gz` (source)
- `dist/quanta_color-1.0.0-py3-none-any.whl` (wheel)

## Step 4: Verify
```bash
python -m twine check dist/quanta_color-1.0.0*
```

## Step 5: Upload
```bash
python -m twine upload dist/quanta_color-1.0.0* \
    --username __token__ \
    --password pypi-YOUR-TOKEN-HERE
```

## Step 6: Verify Installation
```bash
pip install quanta-color
python -c "from quanta_color.spaces import srgb_to_xyz; print(srgb_to_xyz(0.5, 0.3, 0.1))"
```

## After First Upload
Users can install with: `pip install quanta-color`
