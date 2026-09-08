"""Layer 3 — unit tests for the cubic spline helpers (src/cubic_spline.py).

- spline()/splint(): Numerical-Recipes natural cubic spline — interpolates
  through the control points. A natural spline is NOT guaranteed monotone on
  monotone data (it can overshoot by a tiny amount), so the checks here are
  exact pass-through + containment in the data range.
- cubspline(Method, xi, xx, yy): scalar query point xi, scalar result, dispatches
  method 3 to spline_x3(), which is explicitly designed not to overshoot — there
  a monotone-input/monotone-output check is meaningful.
"""

import math

import numpy as np
import pytest

from cubic_spline import spline, splint, cubspline


def test_spline_recovers_control_points():
    x = [0.0, 1.0, 2.0, 3.0, 4.0]
    y = [0.0, 1.0, 4.0, 9.0, 16.0]
    y2 = [0.0] * len(x)
    spline(x, y, len(x), 1e30, 1e30, y2)
    for xi, yi in zip(x, y):
        assert splint(x, y, y2, len(x), xi) == pytest.approx(yi, abs=1e-8)


def test_spline_values_stay_within_data_range():
    rng = np.random.default_rng(0)
    xs = np.linspace(0.0, 1.0, 30)
    ys = np.sort(rng.random(30))
    y2 = [0.0] * len(xs)
    spline(list(xs), list(ys), len(xs), 1e30, 1e30, y2)
    query = np.linspace(0.0, 1.0, 200)
    lo, hi = float(min(ys)), float(max(ys))
    for t in query:
        v = float(splint(list(xs), list(ys), y2, len(xs), t))
        assert math.isfinite(v)
        # natural spline may overshoot slightly; require no wild excursion
        assert lo - 0.1 * (hi - lo) <= v <= hi + 0.1 * (hi - lo)


def test_cubspline_passes_through_control_points():
    xx = [0.0, 1.0, 2.0, 3.0]
    yy = [0.1, 0.4, 0.9, 1.6]
    for reference, expected in zip(xx, yy):
        assert cubspline(3, reference, xx, yy) == pytest.approx(expected, abs=1e-8)


def test_cubspline_interpolates_between_points():
    xx = [0.0, 1.0, 2.0, 3.0]
    yy = [0.0, 1.0, 4.0, 9.0]
    mid = cubspline(3, 1.5, xx, yy)
    assert 1.0 <= mid <= 4.0, f"midpoint {mid} outside bracket [1, 4]"
    assert math.isfinite(mid)


def test_cubspline_is_monotone_for_monotone_data():
    xs = np.linspace(0.0, 1.0, 15)
    ys = np.sort(np.random.default_rng(1).random(15))
    query = np.linspace(0.0, 1.0, 100)
    prev = -math.inf
    for t in query:
        v = cubspline(3, float(t), list(xs), list(ys))
        assert v >= prev - 1e-12, f"non-monotone cubspline at t={t}"
        assert math.isfinite(v)
        prev = v