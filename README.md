<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/HarperZ9/build-color/main/docs/art/hero-dark.svg">
  <img src="https://raw.githubusercontent.com/HarperZ9/build-color/main/docs/art/hero-light.svg" alt="build-color: Python color-science workbench: convert, adapt, appear, map, measure. Parallel rays pass through a lens drawn in fine lines, gather at a bright core and spread out past it." width="100%">
</picture>


# build-color

Color math for Python, with a command line and an optional desktop workbench.
Convert between sRGB, Oklab, CIELAB, JzAzBz, ICtCp and the wide-gamut RGB
spaces. Tone map HDR values with twelve operators, encode and decode PQ and HLG,
and compute CIECAM02 and CAM16 appearance. Grade differences with seven Delta E
metrics, adapt white points with nine methods, and write ICC display profiles
and `.cube` or CLF LUT files. The core needs only NumPy.

It is for graphics and game developers, colorists and tool builders who want
these formulas as plain NumPy functions they can read, test and call from a
script.

[![PyPI: 1.0.2](https://img.shields.io/badge/pypi-1.0.2-e6e1d6?style=flat-square&labelColor=1a1712)](https://pypi.org/project/build-color/)
[![CI](https://github.com/HarperZ9/build-color/actions/workflows/ci.yml/badge.svg)](https://github.com/HarperZ9/build-color/actions/workflows/ci.yml)
[![license](https://img.shields.io/badge/license-FSL--1.1--MIT-e6e1d6?style=flat-square&labelColor=1a1712)](https://github.com/HarperZ9/build-color/blob/main/LICENSE)
![python 3.10+](https://img.shields.io/badge/python-3.10%2B-e6e1d6?style=flat-square&labelColor=1a1712)

## Quick start

```bash
pip install build-color
build-color info ff6030
build-color convert ff6030 --to oklab
build-color difference ff0000 00ff00 --metric all
build-color harmony ff6030 --scheme triadic
build-color adapt 0.4596,0.2985,0.0614 --from D65 --to D50
build-color spectrum --temp 6500
build-color icc --gamma 2.2 --output display.icc
```

`convert ff6030 --to oklab` prints `(0.6904, 0.1627, 0.1214)`. The `icc`
command writes a 2088-byte ICC v4.4 matrix and curve profile.

From Python:

```python
import numpy as np
from build_color.spaces import srgb_to_oklab
from build_color.tonemap import aces_filmic
from build_color.appearance import ciecam02_forward, ViewingConditions

srgb_to_oklab(np.array([0.8, 0.2, 0.1]))  # [0.557, 0.164, 0.102]
aces_filmic(np.array([0.18, 1.0, 4.0]))  # [0.267, 0.804, 0.973]

# CIECAM02 takes XYZ and the white on a 0 to 100 scale.
vc = ViewingConditions(white_point=np.array([95.05, 100.0, 108.88]), L_A=318.31, Y_b=20.0)
c = ciecam02_forward(np.array([19.01, 20.00, 21.78]), vc)
print(round(c.J, 2), round(c.C, 2), round(c.h, 1))  # 41.73 0.1 219.0
```

The desktop workbench is an optional extra:

```bash
pip install "build-color[gui]"
build-color gui
```

Limits to know before you rely on it:

- The `difference` command prints five metrics. The JzAzBz and Oklab Delta E
  functions are in the Python API only.
- The dominant wavelength that `info` prints is wrong in 1.0.2. It reports
  775 nm for `#ff6030`, where the right answer is near 600 nm. Ignore that line.
- ICC output is a display profile built from primaries, white point and a gamma
  curve. It does not measure a display.
- The workbench's Image Analyzer needs Pillow, which the `gui` extra does not
  install. Add it with `pip install Pillow`.
- The Gran Turismo (Uchimura) curve is not monotone. The other eleven tone
  mapping operators are monotone over the tested range.

## How it compares

- **[colour-science](https://www.colour-science.org/)** is the reference Python
  color library, much larger, with far more models, datasets and plotting. Use it
  when you need breadth. build-color is smaller, adds real-time tone mapping
  operators such as ACES, AgX, Hable and PBR Neutral, a CLI, and a GUI.
- **[ColorAide](https://facelessuser.github.io/coloraide/)** is pure Python with
  no NumPy, organized around CSS Color 4 and color objects. build-color works on
  NumPy arrays and covers HDR transfer functions and appearance models.
- **[colorspacious](https://github.com/njsmith/colorspacious)** is a small library
  for CIECAM02, CAM02-UCS and color vision deficiency simulation.
- **[OpenColorIO](https://opencolorio.org/)** runs color pipelines from config
  files inside VFX and imaging applications, on CPU and GPU. build-color does not
  read OCIO configs. It can write `.cube` and CLF LUTs, two formats OCIO reads.
- The license differs. colour-science is BSD-3-Clause and ColorAide is MIT.
  build-color is FSL-1.1-MIT, which allows any use other than a competing
  commercial product. Each release becomes MIT two years after it ships.

![Eight stages of taking one color out of sRGB and back: sRGB in, linearize, to XYZ, perceptual, adapt, appearance, invert, and measure. A hex triple is decoded to eight bits a channel, the sRGB transfer curve is undone, and a single three by three matrix carrying the primaries as columns lands the color in XYZ. From there it reaches the perceptual spaces, Oklab and CIELAB and JzAzBz and ICtCp among twenty-six named conversions in all. Chromatic adaptation moves the white point using any of nine matrices across seven illuminants, and the appearance models, CIECAM02 and CAM16, add viewing conditions: a white point, an adapting luminance, a background and a surround. Then the steps that carry an inverse run backwards, CIECAM02 and Oklab among them, and the result is measured against where it started. Round tripping sRGB to Oklab and back over a twenty-six cubed grid never moves a channel more than four times ten to the minus fourteen, and adapting D65 to D50 and back returns within three units in the last place for all nine matrices. Three outcomes: the round trip holds, the color is out of gamut, or the input was never a color.](docs/art/round-trip.svg)

## Features

### Color Spaces (15+)
sRGB, Linear RGB, XYZ, xyY, CIELAB, LCH, Oklab, Oklch, JzAzBz, JzCzhz, ICtCp, HSV, Display P3, BT.2020, Adobe RGB, ACEScg

### Tone Mapping (12 operators)
ACES (Narkowicz + Hill), AgX (neutral/punchy/golden), Reinhard (simple + extended), Hable/Uncharted 2, Lottes, Uchimura/Gran Turismo, PBR Neutral (Khronos glTF), BT.2390 EETF, BT.2446 Method A, custom knee function

### HDR Processing
PQ (ST.2084) encode/decode, HLG (BT.2100) encode/decode, BT.2390 EETF tone mapping, BT.2446 HDR-to-SDR

![Eight stages of taking scene light to a panel: scene light, encode, decode, check, tone map, gamut, display, and difference. Scene light is linear and unbounded, well above one. It is encoded with PQ, which covers ten thousand candela per square metre in a signal from zero to one, or with HLG over its own zero to one domain. Decoding returns the light that went in: PQ round trips to within three parts in ten to the thirteen relative across its full range, and HLG to within seven times ten to the minus sixteen absolute inside its domain. Tone mapping applies one of twelve operators, each a single call. Gamut mapping then clips, compresses, or reduces chroma in Oklab, and the result is re-encoded for the panel. Seven difference metrics grade what changed. Eleven of the twelve operators are monotone non-decreasing over the range tested, so a brighter sample never comes out darker than a dimmer one. The Gran Turismo curve is the exception and falls at the handoff between its toe and its shoulder. Three outcomes: displayable, compressed, or answered in absolute units.](docs/art/hdr-lane.svg)

### Color Appearance Models
CIECAM02 forward/inverse (machine-epsilon roundtrip), CAM16, CAM16-UCS uniform color space, hue quadrature

### Color Difference (7 metrics)
CIE76, CIE94 (graphics/textiles), CIEDE2000, CMC(l:c), JzAzBz Delta E, Oklab Delta E, HyAB

### Chromatic Adaptation (9 methods)
Bradford, CAT16, CAT02, Sharp, Von Kries, CMCCAT2000, Fairchild, Bianco-Schettini, XYZ Scaling

### Additional
- **Spectral utilities** - Planck blackbody, CIE 1931 CMFs, daylight illuminants, SPD-to-XYZ integration
- **ICC profiles** - Generate ICC v4.4 matrix/TRC display profiles from primaries, white point and gamma
- **CVD simulation** - Protanopia, deuteranopia, tritanopia (full-severity matrices from Machado et al. 2009, blended linearly for partial severity) and achromatopsia
- **LUT files** - Read and write `.cube` (1D and 3D) and ACES CLF, bake any transform into a 3D LUT, apply a LUT with trilinear interpolation
- **Image analysis** - Histograms, gamut coverage, dominant colors (k-means in Oklab), WCAG contrast checks, palette pairs confusable under CVD
- **Color naming** - Nearest of the 148 CSS named colors, measured in Oklab
- **Gamut mapping** - Clip, soft compression, Oklab chroma reduction
- **Color harmony** - Complementary, triadic, tetradic, analogous, split complementary, monochromatic, computed in Oklch

## GUI

A PyQt6 workbench with six pages:

- **Dashboard** - Library overview and shortcuts
- **Image Analyzer** - Load an image, see its metadata, gamut coverage and dominant colors (needs Pillow)
- **Color Inspector** - Enter a color, see it in every space with CVD previews and difference metrics
- **LUT Workshop** - Bake a tone mapping operator into a LUT, preview it, export it
- **Palette Studio** - Build harmony palettes, preview them under CVD, export CSS or JSON
- **Settings** - Preferences and keyboard shortcuts

```bash
pip install "build-color[gui]"
build-color gui
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `build-color` | Launch the GUI if it is installed, otherwise print help |
| `build-color info <color>` | Show color in all spaces + metadata |
| `build-color convert <color> --to <space>` | Convert between color spaces |
| `build-color difference <c1> <c2>` | Compute color difference |
| `build-color harmony <color> --scheme <type>` | Generate palette |
| `build-color adapt <xyz> --from D65 --to D50` | Chromatic adaptation |
| `build-color spectrum --temp <K>` | Blackbody spectral data |
| `build-color icc --gamma 2.2` | Create ICC profile |
| `build-color gui` | Launch GUI workbench |

## Installation

```bash
pip install build-color              # Core: NumPy only
pip install "build-color[gui]"       # Adds the PyQt6 workbench
```

From a clone, `pip install .` installs the same core. The `all` extra adds
SciPy, Pillow and PyQt6 but not `build-ui`, so use the `gui` extra for the
workbench.

## Python API

```python
import numpy as np
from build_color.spaces import srgb_to_oklab, oklab_to_srgb
from build_color.tonemap import aces_filmic, pq_eotf
from build_color.difference import delta_e_2000
from build_color.adaptation import adapt, ILLUMINANTS
from build_color.appearance import ciecam02_forward, ViewingConditions

# Color space conversion
oklab = srgb_to_oklab(np.array([0.8, 0.2, 0.1]))

# Tone mapping
hdr = np.array([0.0, 0.18, 1.0, 4.0, 10.0])
sdr = aces_filmic(hdr)

# Color difference
lab1 = np.array([50.0, 25.0, -10.0])
lab2 = np.array([60.0, 20.0, -5.0])
de = delta_e_2000(lab1, lab2)

# Chromatic adaptation (adapt XYZ from D65 to D50)
d65 = ILLUMINANTS["D65"]
d50 = ILLUMINANTS["D50"]
xyz = np.array([0.4596, 0.2985, 0.0614])
adapted = adapt(xyz, d65, d50, method="cat16")

# CIECAM02 (published reference values assume XYZ on a 0 to 100 scale)
vc = ViewingConditions(white_point=d65 * 100)
appearance = ciecam02_forward(xyz * 100, vc)
print(f"J={appearance.J:.1f}, C={appearance.C:.1f}, h={appearance.h:.0f}")
```

## Architecture

```
build_color/
  spaces.py       15+ color space conversions
  tonemap.py      12 tone mapping operators + PQ/HLG
  appearance.py   CIECAM02, CAM16, CAM16-UCS
  difference.py   7 color difference metrics
  adaptation.py   9 chromatic adaptation methods
  spectral.py     Planck, CIE CMFs, daylight
  lut_io.py       .cube and CLF read/write, LUT baking
  image_analysis.py  Histograms, gamut coverage, dominant colors, WCAG
  naming.py       CSS color names
  icc.py          ICC v4 profile generation
  blindness.py    CVD simulation (4 types)
  gamut.py        Gamut mapping
  harmony.py      6 color harmony schemes
  cli.py          Command-line interface (8 subcommands)
  gui/            PyQt6 interactive workbench
```

![A table of twelve rows: what the workbench holds, how many of it there are, and which module the number is read from. Twenty-six named conversions in spaces.py move a color between two spaces: sRGB, linear RGB, XYZ, xyY, CIELAB, LCH, Oklab, Oklch, JzAzBz, JzCzhz, ICtCp and HSV. Five RGB gamuts carry matrix pairs instead, sRGB and Display P3 and BT.2020 and Adobe RGB and ACEScg. Twelve tone mapping operators sit in tonemap.OPERATORS, of which three answer in absolute units and can exceed one: BT.2390, the knee, and extended Reinhard. Nine chromatic adaptation matrices adapt D65 to D50 and back within three units in the last place. Seven illuminants, seven difference metrics, four colour vision deficiency types and six harmony schemes. CIECAM02 forward then inverse over seven hundred and twenty-nine sRGB colors stays under three times ten to the minus fifteen, and sRGB to Oklab and back over a twenty-six cubed grid stays under four times ten to the minus fourteen. The CIE 1931 colour matching functions carry eighty-one samples from three hundred and eighty to seven hundred and eighty nanometres. One hundred and forty-eight CSS colors back the naming lookup.](docs/art/numbers-table.svg)

See [USAGE.md](USAGE.md) for an install/build line, the full command and API
reference, and worked examples with expected output.

## License

Build Color is released under the FSL-1.1-MIT.
The source is source-available: you may read, run, modify, and build on it for
any purpose other than a competing commercial use, which is reserved to the
Licensor to fund continued development. Copyright (c) 2022-2026 Zain Dana Harper.
All rights reserved. See [LICENSE](LICENSE).

---

Built by **[Zain Dana Harper](https://harperz9.github.io)** in Seattle.

Other projects: [Project Telos](https://harperz9.github.io) | [gather](https://github.com/HarperZ9/gather) | [crucible](https://github.com/HarperZ9/crucible) | [index](https://github.com/HarperZ9/index) | [forum](https://github.com/HarperZ9/forum) | [telos](https://github.com/HarperZ9/telos) | [emet](https://github.com/HarperZ9/emet) | [buildlang](https://github.com/HarperZ9/buildlang)
