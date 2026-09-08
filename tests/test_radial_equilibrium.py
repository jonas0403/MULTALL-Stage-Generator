"""Layer 3 — unit tests for the radial equilibrium module.

Note (corrected 2026-09-08): the module also contains OLD COPIES of
radial_equilibrium_R/S and references inside triple-quoted comment blocks
(Radial_equilibrium.py:81-134, 448-622). Those are string literals and are
NEVER executed — the only active definitions are references() at .py:136,
radial_equilibrium_R at .py:162, radial_equilibrium_S at .py:327. The call
below mirrors the pipeline call site (stage_calculation.py:905) with per-stage
scalar inputs.

Key regression: the Session 8 bug made ALL stages use Stage 1 data. The
stage-differentiation test below is specifically designed to catch that class.
"""

import math

import pytest

from Radial_equilibrium import radial_equilibrium_R

R_OUTPUT_LENGTH_HINT = "h_rel"  # outputs are lists of spanwise values


def _out_values(result):
    """Flatten the 24-tuple return into the arrays that must be finite."""
    return [v for v in result if isinstance(v, (list, tuple))]


def _stage_args(ml, s):
    i = s - 1
    return {
        "D_S1": ml["D_S1"][i], "D_S2": ml["D_S2"][i], "D_S3": ml["D_S3"][i],
        "D_H1": ml["D_H1"][i], "D_H2": ml["D_H2"][i], "D_H3": ml["D_H3"][i],
        "D_m1": ml["D_M1"][i], "D_m2": ml["D_M2"][i], "D_m3": ml["D_M3"][i],
        "b1": ml["b1"][i], "b2": ml["b2"][i], "b3": ml["b3"][i],
        "cu1": ml["cu1"][i], "cu2": ml["cu2"][i], "cu3": ml["cu3"][i],
        "u1": ml["u1"][i], "u2": ml["u2"][i], "u3": ml["u3"][i],
        "cm1": ml["cm1"][i], "cm2": ml["cm2"][i], "cm3": ml["cm3"][i],
        "delta_h_t": ml["delta_h_t"][i],
        "T_t1": ml["T_t1"][i], "T_t2": ml["T_t2"][i], "T_t3": ml["T_t3"][i],
        "p_t1": ml["p_t1"][i], "p_t2": ml["p_t2"][i], "p_t3": ml["p_t3"][i],
    }


@pytest.fixture
def radial_outputs(meanline_data, cg_with_meanline):
    """radial_equilibrium_R result per stage for the real input."""
    outputs = {}
    for s in (1, 2, 3):
        outputs[s] = radial_equilibrium_R(
            s, 1, 1, **_stage_args(meanline_data, s), CompressorGui=cg_with_meanline
        )
    return outputs


def test_outputs_finite_nonempty(radial_outputs):
    for s, result in radial_outputs.items():
        arrays = _out_values(result)
        assert arrays, f"stage {s} returned no arrays"
        for arr in arrays:
            assert len(arr) >= 5, f"stage {s} array too short ({len(arr)})"
            for v in arr:
                assert math.isfinite(float(v)), f"stage {s}: non-finite {v}"


def test_stage_outputs_differ(radial_outputs):
    """Session-8 discriminator: stage 2/3 must NOT reuse stage 1 data."""
    l1 = radial_outputs[1][1]  # l_R
    l2 = radial_outputs[2][1]
    l3 = radial_outputs[3][1]
    assert l1 != l2, "stage 2 rotor reused stage 1 data (Session 8 bug class)"
    assert l2 != l3, "stage 3 rotor reused stage 2 data (Session 8 bug class)"


def test_documented_duplicate_definitions_exist():
    """Findings note: the module keeps obsolete function copies inside string
    comment blocks. Only the FIRST occurrence of each is executed; this test
    pins that the commented-out copies are still preserved (a maintenance
    hazard — someone could edit them thinking they are live, or a future
    cleanup could remove them)."""
    import inspect

    import Radial_equilibrium

    source = inspect.getsource(Radial_equilibrium)
    assert source.count("def radial_equilibrium_R(") == 2
    assert source.count("def radial_equilibrium_S(") == 2
    assert source.count("def references(") == 2