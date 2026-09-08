"""Layer 1 — end-to-end smoke test: the headless pipeline runs and produces a
structurally valid .dat file. No MULTALL solver is launched.

Baseline (2026-09-08, 3-stage template-equivalent real input):
  - run exits 0, writes one .dat, writes debug log
  - 6 blade rows, JM / blade counts per row as recorded
  - two known, pre-existing FAIL classes remain allowed:
      Rtheta monotonicity (camber-line reversals)
      Thickness < Pitch at Row 6 tip section
    everything else must stay clean.
"""

import re

import pytest

from tools.dat_validator import (
    parse_dat,
    check_x_monotonicity,
    check_inter_row_x_continuity,
    check_rtheta_monotonicity,
    check_thickness_positive,
    check_thickness_vs_pitch,
    check_section_span_ordering,
    check_radial_continuity,
    check_jm_consistency,
    check_r_monotonicity_spanwise,
)

pytestmark = pytest.mark.integration

EXPECTED_MUST_PASS = (
    "X-Monotonicity (per section)",
    "Inter-row X-Continuity",
    "Thickness > 0",
    "Spanwise Section Ordering",
    "Radial Continuity at Interfaces",
    "JM Consistency across Sections",
    "R Monotonicity Hub->Shroud",
)

EXPECTED_PREEXISTING = (
    "Rtheta Monotonicity (camber-line)",
    "Thickness < Pitch (passage width)",
)

EXPECTED_JMs = [262, 129, 198, 98, 129, 68]


def test_headless_run_succeeds_and_writes_artifacts(pipeline_run):
    run = pipeline_run
    assert run["returncode"] == 0, (
        f"exit code {run['returncode']}\nSTDOUT:\n{run['stdout']}\nSTDERR:\n{run['stderr']}"
    )
    assert "ERROR:" not in run["stdout"]
    assert run["dat_path"] is not None and run["dat_path"].exists()
    assert run["debug_log"].exists()


def test_dat_has_six_rows_and_expected_jm(pipeline_run):
    data = parse_dat(str(pipeline_run["dat_path"]))
    assert data["nrows"] == 6
    rows = {r: m for r, m in data["row_meta"].items()}
    assert [rows[i]["JM"] for i in range(1, 7)] == EXPECTED_JMs


def test_no_new_failure_classes(pipeline_run):
    data = parse_dat(str(pipeline_run["dat_path"]))

    failed = set()
    for name, fn in (
        ("X-Monotonicity (per section)", check_x_monotonicity),
        ("Inter-row X-Continuity", check_inter_row_x_continuity),
        ("Rtheta Monotonicity (camber-line)", check_rtheta_monotonicity),
        ("Thickness > 0", check_thickness_positive),
        ("Thickness < Pitch (passage width)", check_thickness_vs_pitch),
        ("Spanwise Section Ordering", check_section_span_ordering),
        ("Radial Continuity at Interfaces", check_radial_continuity),
        ("JM Consistency across Sections", check_jm_consistency),
        ("R Monotonicity Hub->Shroud", check_r_monotonicity_spanwise),
    ):
        issues = fn(data)
        if issues:
            failed.add(name)
            assert name in EXPECTED_PREEXISTING, f"{name} FAILED (new class):\n{issues[:5]}"

    assert not failed - set(EXPECTED_PREEXISTING), f"unexpected failures: {failed}"
    assert failed, "expected the known pre-existing FAIL classes to still be present"


def test_thickness_pitch_failures_confined_to_row6_tip(pipeline_run):
    data = parse_dat(str(pipeline_run["dat_path"]))
    issues = check_thickness_vs_pitch(data)
    for issue in issues:
        assert re.match(r"\s*Row 6 ", issue), f"thickness<pitch outside Row 6: {issue}"


def test_pipeline_wrote_back_json(pipeline_run):
    import json as _json

    data = _json.loads(pipeline_run["json_path"].read_text(encoding="utf-8"))
    assert data["Metadata"] and data["Grid_data"]
    bezier = data.get("Bezier_point_data", {})
    assert "rotor_stage_1" in bezier and "stator_stage_1" in bezier
    assert "rotor_stage_3" in bezier and "stator_stage_3" in bezier