"""Layer 3 — unit tests for the Bezier helper (src/Bezier_curve.py).

The 4-point branch uses the exact cubic Bernstein basis. The 5-point branch is a
degree-4 Bernstein curve (t**4 last term — fixed 2026-09-08, previously t**5);
endpoints hold and the midpoint of symmetric control points is exact.
"""

import numpy as np
import pytest

from Bezier_curve import bezier


def test_bezier4_endpoints(control_4):
    assert bezier(4, 0.0, control_4) == pytest.approx(control_4[0])
    assert bezier(4, 1.0, control_4) == pytest.approx(control_4[3])


def test_bezier4_midpoint_inside_range(control_4):
    value = bezier(4, 0.5, control_4)
    assert min(control_4) <= value <= max(control_4)


def test_bezier4_monotone_preserves_order(control_4):
    points = np.linspace(0.0, 1.0, 50)
    values = [bezier(4, float(t), control_4) for t in points]
    assert values == sorted(values)


def test_bezier5_endpoints(control_5):
    assert bezier(5, 0.0, control_5) == pytest.approx(control_5[0])
    assert bezier(5, 1.0, control_5) == pytest.approx(control_5[4])


def test_bezier5_symmetric_midpoint_exact(control_5):
    # 5-point curve is degree-4; for symmetric control points the midpoint is exact.
    # The pre-fix t**5 term would have produced t**5=1/32 on control point 4 and
    # returned 46.875 instead of 50.0 here.
    mid = bezier(5, 0.5, control_5)
    assert mid == pytest.approx(50.0, abs=1e-9)


def test_bezier5_midpoint_inside_range(control_5):
    value = bezier(5, 0.5, control_5)
    assert min(control_5) <= value <= max(control_5)


@pytest.fixture
def control_4():
    return [0.0, 10.0, 20.0, 30.0]


@pytest.fixture
def control_5():
    return [0.0, 25.0, 50.0, 75.0, 100.0]