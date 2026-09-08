"""Layer 3 — unit tests for the meanline calculation (src/meanline.py).

meanline() returns a dict of primarily per-stage arrays. Physical sanity checks:
finite values, correct stage count, decreasing annulus heights, thousands of
future tests won't catch a broadcast/index bug like Session 8's.
"""

import math

import pytest

NUMERIC_KEYS = (
    "b1", "b2", "b3",
    "D_S1_mm", "D_S2_mm", "D_S3_mm",
    "D_H1_mm", "D_H2_mm", "D_H3_mm",
    "D_M1_mm", "D_M2_mm", "D_M3_mm",
    "T_t1", "T_t2", "T_t3",
    "p_1", "p_2", "p_3",
    "u1", "u2", "u3",
    "cm1", "cm2", "cm3",
    "cu1", "cu2", "cu3",
)


def test_stage_count_is_three(meanline_data):
    assert len(meanline_data["b1"]) == 3
    assert len(meanline_data["z_R"]) == 3
    assert len(meanline_data["z_S"]) == 3


def test_numeric_arrays_are_finite(meanline_data):
    for key in NUMERIC_KEYS:
        values = meanline_data[key]
        assert isinstance(values, (list, tuple))
        # meanline() stores T_t1 with 4 entries (inlet total temperature +
        # per-stage outlet temperatures); every other per-stage array has 3.
        expected = 4 if key == "T_t1" else 3
        assert len(values) == expected, key
        for value in values:
            assert math.isfinite(value), f"{key} has non-finite {value}"


def test_annulus_heights_decrease_across_stages(meanline_data):
    b1, b2, b3 = (meanline_data[k] for k in ("b1", "b2", "b3"))
    for stage in range(3):
        assert b1[stage] > b2[stage] > b3[stage] > 0.0


def test_hub_diameters_positive_and_tip_above_hub(meanline_data):
    for stage in range(3):
        hub = meanline_data["D_H1_mm"][stage]
        tip = meanline_data["D_S1_mm"][stage]
        assert hub > 0.0
        assert tip > hub


def test_velocity_triangle_consistency(meanline_data):
    # axial velocity must be positive and the swirl not absurd relative to u
    for stage in range(3):
        assert meanline_data["cm1"][stage] > 0.0
        assert abs(meanline_data["cu1"][stage]) < meanline_data["u1"][stage]