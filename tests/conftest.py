"""Shared fixtures for the MULTALL Stage Generator test suite.

All tests run against copies of the project input JSON in pytest temp dirs.
Tests import from source/ and tools/ only (never the frozen src/ tree).
"""

import contextlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

# Non-interactive backend before any source/ import (stage.py pulls in
# pyplot at module level).
os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib

matplotlib.use("Agg", force=True)

ROOT = Path(__file__).resolve().parent.parent
SOURCE_JSON = ROOT / "static" / "Populated_data.template.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session", autouse=True)
def _stay_in_project_root():
    """Keep CWD at the project root for the whole run."""
    os.chdir(ROOT)
    yield


def require_source_json():
    if not SOURCE_JSON.exists():
        pytest.fail(
            f"{SOURCE_JSON.relative_to(ROOT)} not found. The test suite reads the"
            " committed template — restore it (see static/Populated_data.template.json) "
            "before running the suite."
        )


def make_input_json(target_dir: Path) -> Path:
    """Copy the template JSON into a temp dir and point its output there.

    The grid lands in Metadata['output_folder'], so an absolute temp path
    keeps the test off the real outputFiles/.
    """
    require_source_json()
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    grid_dir = target_dir / "grid"
    grid_dir.mkdir(parents=True, exist_ok=True)
    data["Metadata"]["output_folder"] = str(grid_dir)
    json_path = target_dir / "input.json"
    json_path.write_text(json.dumps(data, indent=4), encoding="utf-8")
    return json_path


@pytest.fixture(scope="session")
def pipeline_run(tmp_path_factory):
    """One real headless pipeline run, shared by smoke + regression tests.

    Runs source/headless.py as a subprocess (it owns its tk root and cwd),
    on the temp JSON whose Metadata already points at the temp grid dir —
    no --output flag, single knob, no ambiguity.
    """
    base = tmp_path_factory.mktemp("pipeline")
    json_path = make_input_json(base)
    grid_dir = base / "grid"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "source.headless",
            "--json",
            str(json_path),
        ],
        cwd=str(ROOT),
        env={**os.environ, "MPLBACKEND": "Agg", "MULTALL_HEADLESS": "1"},
        capture_output=True,
        text=True,
        timeout=180,
    )
    dat_candidates = sorted(grid_dir.glob("*.dat")) if grid_dir.exists() else []
    return {
        "base": base,
        "json_path": json_path,
        "out_dir": grid_dir,
        "grid_dir": grid_dir,
        "dat_path": dat_candidates[0] if dat_candidates else None,
        "debug_log": grid_dir / "debug_headless.txt",
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


@pytest.fixture(scope="session")
def meanline_data():
    """3-stage meanline result dict built from the template JSON (~3-5s)."""
    require_source_json()
    from source.core.meanline.thermodynamics import Thermo
    from source.core.meanline.meanline import meanline

    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    ti = data["Thermodynamic_input_data"]
    mi = data["Meanline_input_data"]
    n_stages = len(mi["z_R"])
    thermo = Thermo(
        ti["p_t_in"], ti["T_t_in"], ti["mflow"],
        ti["R"], ti["cp"], ti["TPR"], n_stages,
    )
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = meanline(thermo, mi, data.get("Diameter_data", {}), plot_channel_contour=False)
    return result


class _FakeDVar:
    """Float-valued var stand-in. channel()/radial-equilibrium only call
    .get() on inlet/outlet vars; a lightweight fake avoids the (broken,
    flaky) Tk runtime entirely while keeping the tests GUI-free."""

    def __init__(self, value):
        self._value = float(value)

    def get(self):
        return self._value

    def set(self, value):
        self._value = float(value)


@pytest.fixture
def cg_with_meanline(meanline_data):
    """Minimal CompressorGui proxy carrying meanline_data + channel vars."""
    cg = SimpleNamespace()
    cg.stage = 3
    cg.stages_to_calc = 3
    cg.meanline_data = meanline_data
    cg.inlet_area_var = _FakeDVar(1.1)
    cg.inlet_dist_var = _FakeDVar(1.5)
    cg.outlet_area_var = _FakeDVar(0.9)
    cg.outlet_dist_var = _FakeDVar(2.0)
    return cg
