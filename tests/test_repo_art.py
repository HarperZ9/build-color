"""The drawings in the README, held against the code they describe.

The art gate settles whether a drawing fits its columns and matches the spec it was
rendered from. Both sides of that check read the same JSON, so it cannot settle
whether a drawing is TRUE. That is the job of this file: every count, bound and
rule the three drawings put on the page is asserted here against the code that
produces it, so a claim that stops holding fails the suite rather than staying on
the page. The rest of the suite already covers the math; nothing here repeats it.

Writing these caught five false claims. The conversion count included a matrix
builder that moves no color. The appearance row promised a CAM16 inverse that does
not exist. The adaptation round trip is three units in the last place rather than
one, and the Oklab and PQ round trips are both a little wider than the bounds I had
drawn. The fifth is a defect in the library rather than in the drawing: the Gran
Turismo curve is not monotone, so the claim that every operator preserves order was
false. Every drawing was corrected. No check was loosened to let one pass.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from build_color import (
    adaptation,
    appearance,
    blindness,
    cli,
    difference,
    gamut,
    harmony,
    naming,
    spaces,
    spectral,
    tonemap,
)

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "docs/art/build-color.art.json").read_text(encoding="utf-8"))
DRAWINGS = (
    "build-color-header.svg",
    "round-trip.svg",
    "hdr-lane.svg",
    "numbers-table.svg",
)
CARD = {field["key"]: field for field in SPEC["cards"][0]["fields"]}
ABSOLUTE_UNIT_OPERATORS = ("bt2390", "knee", "reinhard_extended")
GAMUTS = ("SRGB", "P3", "BT2020", "ADOBE", "ACESCG")


def rgb_grid(step):
    """An evenly spaced cube of sRGB colors, used as the sweep behind every bound."""
    axis = np.linspace(0.0, 1.0, step)
    red, green, blue = np.meshgrid(axis, axis, axis, indexing="ij")
    return np.stack([red.ravel(), green.ravel(), blue.ravel()], axis=1)


def named_conversions():
    """Public functions in spaces.py that move a color from one space to another."""
    return sorted(
        name
        for name, value in vars(spaces).items()
        if callable(value)
        and "_to_" in name
        and not name.startswith("_")
        and getattr(value, "__module__", "") == spaces.__name__
        and name != "primaries_to_matrix"
    )


def test_every_drawing_is_committed_and_shown_in_the_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for name in DRAWINGS:
        path = ROOT / "docs/art" / name
        assert path.is_file(), f"{name} is drawn but not committed"
        assert path.stat().st_size > 0
        assert f"docs/art/{name}" in readme, f"{name} is committed but never shown"


def test_the_card_counts_the_conversions_that_actually_convert():
    """primaries_to_matrix carries _to_ in its name and moves no color, so it is out."""
    assert CARD["color spaces"]["value"] == "26 conversions"
    assert len(named_conversions()) == 26
    assert "primaries_to_matrix" not in named_conversions()
    assert callable(spaces.primaries_to_matrix)


def test_five_rgb_gamuts_carry_matrix_pairs_that_undo_each_other():
    """The card says matrix pairs rather than functions. This is what that means.

    The two halves of each pair are separately rounded published constants rather
    than one computed from the other, so the product lands about two parts in ten
    million from the identity. That is the real bound and the assertion says so.
    """
    for gamut_name in GAMUTS:
        forward = getattr(spaces, f"{gamut_name}_TO_XYZ")
        inverse = getattr(spaces, f"XYZ_TO_{gamut_name}")
        assert forward.shape == (3, 3)
        assert inverse.shape == (3, 3)
        assert np.allclose(forward @ inverse, np.eye(3), atol=5e-7)
        assert np.allclose(inverse @ forward, np.eye(3), atol=5e-7)


def test_the_registry_holds_twelve_tone_operators():
    assert len(tonemap.OPERATORS) == 12
    assert CARD["tone operators"]["value"] == "twelve of them"
    for name, operator in tonemap.OPERATORS.items():
        assert callable(operator), name


def test_three_operators_answer_in_absolute_units_and_nine_do_not():
    """The honest null on the HDR lane: a convention, so the row carries no mark."""
    assert "tone" not in CARD["absolute units"]
    assert CARD["absolute units"]["value"] == "three of the twelve"
    scene = np.array([0.0, 0.18, 1.0, 4.0, 100.0, 1000.0])
    over_one = sorted(name for name, operator in tonemap.OPERATORS.items() if float(np.max(operator(scene))) > 1.0)
    assert tuple(over_one) == ABSOLUTE_UNIT_OPERATORS
    for name, operator in tonemap.OPERATORS.items():
        if name in ABSOLUTE_UNIT_OPERATORS:
            continue
        mapped = operator(scene)
        assert float(np.min(mapped)) >= 0.0, name
        assert float(np.max(mapped)) <= 1.0, name


def test_eleven_of_twelve_operators_preserve_order():
    """A brighter sample comes back no darker, for every operator but one."""
    scene = np.concatenate([np.linspace(0.0, 4.0, 400), np.linspace(4.0, 2000.0, 400)])
    for name, operator in tonemap.OPERATORS.items():
        if name == "uchimura":
            continue
        mapped = np.asarray(operator(scene), dtype=float)
        assert np.all(np.diff(mapped) >= -1e-12), f"{name} inverts two samples"
    assert CARD["order preserved"]["value"] == "eleven of twelve"
    assert CARD["order preserved"]["tone"] == "drift"


def test_the_gran_turismo_curve_falls_where_its_toe_hands_off():
    """The exception, pinned so it cannot be fixed without the drawing following.

    uchimura computes its toe weight and discards the result, so the linear segment
    the reference curve puts between toe and shoulder is missing and the output
    jumps down at x equal to m. If that is ever repaired, this test fails and the
    drawing has to be corrected back.
    """
    scene = np.linspace(0.0, 4.0, 400)
    step = np.diff(np.asarray(tonemap.uchimura(scene), dtype=float))
    assert float(np.min(step)) < -0.1
    handoff = float(scene[int(np.argmin(step))])
    assert 0.20 < handoff < 0.22


def test_nine_adaptation_matrices_undo_within_three_units_in_the_last_place():
    assert len(adaptation.MATRICES) == 9
    assert CARD["adaptation"]["value"] == "nine matrices"
    assert CARD["adapt and undo"]["value"] == "under 1e-15"
    d65, d50 = adaptation.ILLUMINANTS["D65"], adaptation.ILLUMINANTS["D50"]
    worst = 0.0
    for method in adaptation.MATRICES:
        for rgb in rgb_grid(6):
            xyz = spaces.srgb_to_xyz(rgb)
            there = adaptation.adapt(xyz, d65, d50, method=method)
            back = adaptation.adapt(there, d50, d65, method=method)
            worst = max(worst, float(np.max(np.abs(back - xyz))))
    assert worst <= 3 * np.finfo(float).eps
    assert worst < 1e-15


def test_seven_illuminants_are_held_as_white_points():
    assert set(adaptation.ILLUMINANTS) == {"A", "D50", "D55", "D65", "D75", "F2", "F11"}
    assert CARD["illuminants"]["value"] == "seven of them"
    for name, white in adaptation.ILLUMINANTS.items():
        white = np.asarray(white, dtype=float)
        assert white.shape == (3,), name
        assert white[1] == pytest.approx(1.0, abs=1e-6), name


def test_seven_difference_metrics_are_callable():
    metrics = sorted(name for name in vars(difference) if name.startswith("delta_e"))
    assert len(metrics) == 7
    assert CARD["difference"]["value"] == "seven metrics"
    lab1, lab2 = np.array([50.0, 25.0, -10.0]), np.array([60.0, 20.0, -5.0])
    for name in metrics:
        value = float(getattr(difference, name)(lab1, lab2))
        assert value > 0.0, name
        assert float(getattr(difference, name)(lab1, lab1)) == pytest.approx(0.0, abs=1e-9)


def test_the_appearance_row_does_not_promise_a_cam16_inverse():
    """CAM16 ships forward only. The card said forward and inverse until this test."""
    assert hasattr(appearance, "ciecam02_forward")
    assert hasattr(appearance, "ciecam02_inverse")
    assert hasattr(appearance, "cam16_forward")
    assert hasattr(appearance, "cam16_ucs")
    assert not hasattr(appearance, "cam16_inverse")
    assert "CAM16 forward" in CARD["appearance"]["note"]


def test_ciecam02_forward_then_inverse_stays_under_three_femto():
    d65 = adaptation.ILLUMINANTS["D65"]
    conditions = appearance.ViewingConditions(white_point=d65)
    colors = rgb_grid(9)
    assert len(colors) == 729
    worst = 0.0
    for rgb in colors:
        xyz = spaces.srgb_to_xyz(rgb)
        seen = appearance.ciecam02_forward(xyz, conditions)
        back = appearance.ciecam02_inverse(seen.J, seen.C, seen.h, conditions)
        worst = max(worst, float(np.max(np.abs(back - xyz))))
    assert worst < 3e-15
    assert CARD["CIECAM02 return"]["value"] == "under 1e-14"


def test_srgb_to_oklab_and_back_stays_under_four_hundredths_of_a_pico():
    colors = rgb_grid(26)
    back = np.array([spaces.oklab_to_srgb(spaces.srgb_to_oklab(c)) for c in colors])
    worst = float(np.max(np.abs(back - colors)))
    assert worst < 4e-14
    assert CARD["Oklab return"]["value"] == "under 1e-13"


def test_both_hdr_curves_decode_what_they_encode():
    """The first return edge on the HDR lane, on each curve's own documented domain."""
    nits = np.concatenate([np.linspace(0.0, 100.0, 500), np.linspace(100.0, 10_000.0, 500)])
    pq_back = tonemap.pq_eotf(tonemap.pq_oetf(nits))
    lit = nits > 0.0
    relative = np.abs(pq_back[lit] - nits[lit]) / nits[lit]
    assert float(np.max(relative)) < 3e-13
    scene = np.linspace(0.0, 1.0, 1000)
    hlg_back = tonemap.hlg_eotf(tonemap.hlg_oetf(scene))
    assert float(np.max(np.abs(hlg_back - scene))) < 1e-12


def test_the_matching_functions_carry_eighty_one_samples():
    waves = np.asarray(spectral.CMF_WAVELENGTHS, dtype=float)
    assert waves.shape == (81,)
    assert waves[0] == pytest.approx(380.0)
    assert waves[-1] == pytest.approx(780.0)
    assert np.allclose(np.diff(waves), 5.0)
    for channel in (spectral.CMF_X, spectral.CMF_Y, spectral.CMF_Z):
        assert np.asarray(channel).shape == (81,)
    assert CARD["spectral"]["value"] == "81 samples"


def test_the_out_of_gamut_outcome_names_three_paths_that_exist():
    outcome = next(o for f in SPEC["flows"] for o in f["outcomes"] if o["label"] == "OUT OF GAMUT")
    assert outcome["note"] == "clipped, compressed, or reduced"
    wide = np.array([1.4, -0.3, 0.2])
    assert not gamut.is_in_gamut(wide)
    for brought_back in (
        gamut.clip(wide),
        gamut.compress(wide),
        gamut.oklab_chroma_reduce(wide),
    ):
        assert gamut.is_in_gamut(brought_back, tolerance=1e-6)


def test_the_not_a_color_outcome_is_a_real_failure():
    """The drawing says the input never parsed. This is the code that says so."""
    for text in ("#ff6030", "ff6030", "255,96,48"):
        parsed = np.asarray(cli._parse_color(text), dtype=float)
        assert parsed.shape == (3,)
    for text in ("not-a-color", "", "zzzzzz", "1,2"):
        with pytest.raises(ValueError):
            cli._parse_color(text)


def test_the_alt_text_counts_match_the_registries_behind_them():
    alt = SPEC["cards"][0]["alt"]
    assert len(blindness.DEFICIENCY_TYPES) == 4
    assert "four colour vision deficiency types" in alt
    assert len(harmony.SCHEMES) == 6
    assert "six harmony schemes" in alt
    assert len(naming.CSS_COLORS) == 148
    assert "One hundred and forty-eight CSS colors" in alt


def test_the_card_marks_exactly_one_row():
    toned = [f for f in SPEC["cards"][0]["fields"] if f.get("tone")]
    assert len(toned) == 1
    assert toned[0]["key"] == "order preserved"
    assert toned[0]["tone"] == "drift"
