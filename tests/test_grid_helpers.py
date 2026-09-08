"""Layer 3 — unit tests for small grid-generation helpers.

grid_adaption(): hyperbolic-tangent spaced grid, scaled spacings in [1, max].
write_values_in_block(): 8-per-line Fortran-style writer with pad/truncate and
NaN-to-1e-6 sanitizing.
"""

import io

import numpy as np
import pytest

from grid_generator import grid_adaption, write_values_in_block


@pytest.mark.parametrize("count", [50, 100, 200])
def test_grid_adaption_length_and_bounds(count):
    spacings = grid_adaption(count)
    assert len(spacings) == count - 1
    assert np.all(np.isfinite(spacings))
    assert spacings.min() >= 1.0 - 1e-9
    assert spacings.max() <= 20.0 + 1e-9
    assert np.all(spacings >= 0.0)


def test_grid_adaption_returns_nontrivial_distribution():
    spacings = grid_adaption(200)
    assert spacings.max() > spacings.min() + 1e-6


def test_write_values_in_block_pads_short_data():
    out = io.StringIO()
    write_values_in_block(0, [[1.0, 2.0, 3.0]], out, 10)
    values = [float(v) for v in out.getvalue().split()]
    assert len(values) == 10
    assert values[:3] == pytest.approx([1.0, 2.0, 3.0])
    assert values[3:] == [0.0] * 7


def test_write_values_in_block_truncates_long_data():
    out = io.StringIO()
    write_values_in_block(0, [list(range(12))], out, 5)
    values = [float(v) for v in out.getvalue().split()]
    assert len(values) == 5


def test_write_values_in_block_section_out_of_range():
    out = io.StringIO()
    write_values_in_block(5, [[1.0, 2.0]], out, 4)
    assert [float(v) for v in out.getvalue().split()] == [0.0] * 4


def test_write_values_in_block_sanitizes_nan():
    out = io.StringIO()
    write_values_in_block(0, [[float("nan"), 2.0]], out, 2)
    assert [float(v) for v in out.getvalue().split()] == pytest.approx([1e-6, 2.0])