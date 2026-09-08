"""Layer 3 — unit tests for the flow channel geometry (src/channel.py).

channel() returns (x_values, r_values, m_prime_values, x0, r0_N_mm, r0_G_mm).
x_values/r_values are per-spanwise-section lists along the axial channel.
"""

import math
from types import SimpleNamespace

import pytest


def _channel_for_stage(cg, stage):
    from channel import channel

    local_cg = SimpleNamespace(**cg.__dict__)
    local_cg.stage = stage
    return channel(local_cg)


@pytest.mark.parametrize("stage", [1, 2, 3])
def test_channel_x_monotonic_per_section(cg_with_meanline, stage):
    x_values = _channel_for_stage(cg_with_meanline, stage)[0]
    assert len(x_values) == 5, "expected one section per h_H level"
    for section in x_values:
        assert len(section) > 2
        prev = None
        for x in section:
            assert math.isfinite(float(x))
            if prev is not None:
                assert x > prev, f"x not strictly increasing: {prev} -> {x}"
            prev = x


@pytest.mark.parametrize("stage", [1, 2, 3])
def test_channel_radii_finite_and_sane(cg_with_meanline, stage):
    r_values = _channel_for_stage(cg_with_meanline, stage)[1]
    for section in r_values:
        for r in section:
            r = float(r)
            assert math.isfinite(r)
            # r_values are in millimetres: channel.py converts the meanline
            # diameters (meters) to mm (channel.py:636-637) for the arc-length.
            assert 0.0 < r < 2000.0, f"radius {r} [mm] out of range"


def test_channel_control_points_finite(cg_with_meanline):
    result = _channel_for_stage(cg_with_meanline, 1)
    x0, r0_N, r0_G = result[3], result[4], result[5]
    for arr in (x0, r0_N, r0_G):
        for v in arr:
            assert math.isfinite(float(v))