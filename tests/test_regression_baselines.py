"""Layer 2 — regression baselines captured from a reference 3-stage run.

Baseline (2026-09-08, real input file, --output temp):
  - TPR converges to 2.400 (+ a Warning before it), RPM 9717, massflow 60.0
  - per-row chord lengths [mm]: 131.80 64.85 99.59 50.02 64.93 34.96
  - blade counts (rotor z_R / stator z_S interleaved): [20,52,29,66,41,70]
  - grid: IM=37 KM=37, JM_ref=200, 6 rows

The chord lengths are the strongest discriminator here: the Session 8 stage-index
bug changed stage-2/3 chords by tens of percent.
"""

import json
import re

import pytest

pytestmark = pytest.mark.integration

EXPECTED_CHORDS = [131.80, 64.85, 99.59, 50.02, 64.93, 34.96]
CHORD_RE = re.compile(r"Chord length for row \d+: ([0-9.]+) mm")


def _read_debug_log(pipeline_run):
    log = pipeline_run["debug_log"]
    assert log.exists(), "debug log missing"
    return log.read_text(encoding="utf-8")


def _load_output_json(pipeline_run):
    return json.loads(pipeline_run["json_path"].read_text(encoding="utf-8"))


def test_tpr_rpm_massflow_baseline(pipeline_run):
    m = re.search(r"Total Pressure Ratio has converged after \d+ iterations\. TPR = ([0-9.]+) at RPM = ([0-9.]+), massflow = ([0-9.]+)", pipeline_run["stdout"])
    assert m, f"no TPR line in stdout:\n{pipeline_run['stdout']}"
    tpr, rpm, mflow = float(m.group(1)), float(m.group(2)), float(m.group(3))
    assert tpr == pytest.approx(2.40, abs=0.02)
    assert rpm == pytest.approx(9717, rel=0.05)
    assert mflow == pytest.approx(60.0, rel=0.01)


def test_row_chords_baseline(pipeline_run):
    chords = [float(x) for x in CHORD_RE.findall(_read_debug_log(pipeline_run))]
    assert len(chords) == 6, f"expected 6 chord lines, got {len(chords)}"
    for actual, expected in zip(chords, EXPECTED_CHORDS):
        assert actual == pytest.approx(expected, rel=0.02), "chord drifted from baseline"


def test_blade_counts_match_meanline_input(pipeline_run):
    data = _load_output_json(pipeline_run)
    z_R = data["Meanline_input_data"]["z_R"]
    z_S = data["Meanline_input_data"]["z_S"]
    expected = [v for pair in zip(z_R, z_S) for v in pair]

    from tools.dat_validator import parse_dat

    parsed = parse_dat(str(pipeline_run["dat_path"]))
    actual = [parsed["row_meta"][i]["n_blades"] for i in range(1, 7)]
    assert actual == expected, f"blade counts {actual} != meanline input {expected}"


def test_top_level_sections_preserved(pipeline_run):
    data = _load_output_json(pipeline_run)
    for section in (
        "Thermodynamic_input_data",
        "Meanline_input_data",
        "Diameter_data",
        "Bezier_point_data",
        "Metadata",
        "Grid_data",
        "Bleed_air_data",
    ):
        assert section in data