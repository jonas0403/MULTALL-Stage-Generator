# ------------------------------------------------------------------
# File:    source/headless.py
# Author:  Jonas Scholz
# Purpose: Headless pipeline driver for the source/ tree (no GUI).
# ------------------------------------------------------------------

"""Headless runner for the refactored (source/) tree.

Pipeline: thermodynamics -> meanline -> channel/radial equilibrium ->
default blade profiles -> grid .dat.

Usage:
    python -m source.headless [--json <path>] [--output <dir>]

The JSON is written back in place (Bezier data, Metadata), so always pass
a temp copy, never the live static/Populated_data.json.
Exits 0 on success, 1 on failure.
"""

import os

# Must come first: stage.py pulls in pyplot at import time.
os.environ["MULTALL_HEADLESS"] = "1"
os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib

matplotlib.use("Agg", force=True)

import argparse
import json
import sys
import time
import traceback
from datetime import datetime
from types import SimpleNamespace

import tkinter as tk

from source.io.paths import REPO_ROOT, JSON_PATH, resolve_absolute
from source.logging import debug_log
from source.core.meanline.thermodynamics import Thermo
from source.core.meanline.meanline import meanline
from source.core.stage.orchestration import run_main_logic
from source.core.stage.blade_profiles import create_default_profiles
from source.core.grid.grid_generator import process_grid_data


def load_json_or_die(path):
    if not os.path.exists(path):
        print(f"ERROR: JSON file not found: {path}")
        sys.exit(1)
    with open(path, "r") as f:
        return json.load(f)


def build_compressor_gui_data(json_data):
    """Same in-memory state the GUI tabs build (withdrawn root, DoubleVars)."""
    cg = SimpleNamespace()
    thermo_input = json_data.get("Thermodynamic_input_data", {})
    meanline_input = json_data.get("Meanline_input_data", {})
    diameter_data = json_data.get("Diameter_data", {})
    grid_data = json_data.get("Grid_data", {})
    metadata = json_data.get("Metadata", {})
    bleed_air_data = json_data.get("Bleed_air_data", {})
    io_area = json_data.get("Intake_Outtake_area", {})

    stages_total = len(meanline_input.get("n", [3]))
    cg.stage = stages_total
    cg.stages_to_calc = stages_total

    # Withdrawn root backing the DoubleVars below (no visible windows).
    root = tk.Tk()
    root.withdraw()
    cg._tk_root = root

    cg.inlet_area_var = tk.DoubleVar(value=io_area.get("inlet_area", 1.0))
    cg.inlet_dist_var = tk.DoubleVar(value=io_area.get("inlet_dist", 1.5))
    cg.outlet_area_var = tk.DoubleVar(value=io_area.get("outlet_area", 1.0))
    cg.outlet_dist_var = tk.DoubleVar(value=io_area.get("outlet_dist", 2.0))

    cg.prepop_thermo_data = thermo_input
    cg.prepop_meanline_input_data = meanline_input
    cg.prepop_diameter_data = diameter_data
    cg.prepop_grid_data = grid_data
    cg.prepop_metadata = metadata
    cg.prepop_bleed_air_data = bleed_air_data
    cg.grid_name_prefix = "grid"
    return cg


def run_pipeline(json_path, output_dir):
    """Run all pipeline steps. Returns 0 on success, 1 on failure."""
    t0 = time.time()
    data = load_json_or_die(json_path)

    # --output wins, else Metadata.output_folder, else outputFiles.
    # Written back so the grid writer lands where the caller expects.
    metadata = data.get("Metadata", {})
    out = output_dir or metadata.get("output_folder") or "outputFiles"
    out_abs = resolve_absolute(out)
    os.makedirs(out_abs, exist_ok=True)
    if output_dir:
        data.setdefault("Metadata", {})["output_folder"] = out
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    debug_log.open_file(os.path.join(out_abs, "debug_headless.txt"))
    cg = build_compressor_gui_data(data)
    try:
        # 0D thermodynamics.
        debug_log.section("Thermodynamic calculation")
        thermo_input = data.get("Thermodynamic_input_data", {})
        cg.Thermodata = Thermo(
            thermo_input.get("p_t_in", 101325),
            thermo_input.get("T_t_in", 293.15),
            thermo_input.get("mflow", 60.0),
            thermo_input.get("R", 287.0),
            thermo_input.get("cp", 1004.5),
            thermo_input.get("TPR", 2.4),
            cg.stages_to_calc,
        )
        print("Step 1/5: thermodynamics done.")

        # 1D meanline (False = no contour plot window).
        debug_log.section("Meanline calculation")
        cg.meanline_data = meanline(
            cg.Thermodata,
            data.get("Meanline_input_data", {}),
            data.get("Diameter_data", {}),
            False,
        )
        print("Step 2/5: meanline done.")

        # Channel + radial equilibrium for all stages.
        debug_log.section("Main logic (channel + radial equilibrium)")
        run_main_logic({"main_choice": "default"}, cg, json_path)
        print("Step 3/5: channel + radial equilibrium done.")

        # Blade profiles from the fresh radial-equilibrium data.
        debug_log.section("Default blade profiles")
        create_default_profiles(cg, json_path)
        print("Step 4/5: default profiles done.")

        # Grid .dat (fails fast on bad Bezier data, see validate_bezier_data).
        debug_log.section("Grid generation")
        process_grid_data(json_path, cg)
        print("Step 5/5: grid done.")

        dt = time.time() - t0
        done_msg = f"Headless pipeline completed in {dt:.1f}s. Output: {out_abs}"
        print(done_msg)
        debug_log.debug(done_msg, context="headless")
        return 0
    except Exception:
        traceback.print_exc()
        debug_log.debug(traceback.format_exc(), context="headless_error")
        print("Headless pipeline FAILED (see traceback + debug log).")
        return 1
    finally:
        debug_log.close_file()
        try:
            cg._tk_root.destroy()
        except Exception:
            pass


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="MULTALL Stage Generator — headless pipeline (source/ tree)"
    )
    parser.add_argument(
        "--json", type=str, default=None,
        help="Path to the JSON project file (use a TEMP COPY, never the live file).",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output directory (default: Metadata.output_folder, else outputFiles/).",
    )
    args = parser.parse_args(argv)

    json_path = os.path.abspath(args.json) if args.json else str(JSON_PATH)
    output_dir = args.output
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] source headless: json={json_path}")
    return run_pipeline(json_path, output_dir)


if __name__ == "__main__":
    sys.exit(main())
