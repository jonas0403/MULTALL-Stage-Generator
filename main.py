# ------------------------------------------------------------------
# File:    main.py
# Author:  Jonas Scholz
# Purpose: Entry point — GUI or headless pipeline on the source/ tree.
# ------------------------------------------------------------------
"""MULTALL Stage Generator — Entry Point

Launches the GUI application by default. Supports headless mode for
batch processing via the --headless flag.

Usage:
    python main.py                            # Launch GUI
    python main.py --headless --json <path>   # Headless grid generation
"""

import os
import sys
import argparse

# Change to project root so relative imports resolve correctly
_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(_ROOT)

# Repo root on the path so the `source` package resolves.
# (Old src/ tree is retired; its launcher lives in old/.)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def main():
    parser = argparse.ArgumentParser(
        description="MULTALL Stage Generator — GUI and headless preprocessing tool"
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="Run in headless mode (no GUI). Requires --json."
    )
    parser.add_argument(
        "--json", type=str, default=None,
        help="Path to the JSON project file"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output directory for generated files (default: outputFiles/)"
    )

    args, _ = parser.parse_known_args()

    if args.headless:
        _run_headless(args.json, args.output)
    else:
        _run_gui()


def _run_headless(json_path, output_path):
    """Headless source/ pipeline in a subprocess (keeps GUI state isolated)."""
    import subprocess

    # -m from the repo root so the absolute source.* imports resolve.
    cmd = [sys.executable, "-m", "source.headless"]

    if json_path:
        cmd += ["--json", os.path.abspath(json_path)]
    if output_path:
        cmd += ["--output", os.path.abspath(output_path)]

    sys.exit(subprocess.call(cmd, cwd=_ROOT))


def _run_gui():
    """Launch the Tkinter GUI (source/ tree)."""
    from source.gui.app import CompressorGui

    my_gui = CompressorGui()
    my_gui.loading_prepopulated_data()
    my_gui.show_startup_dialog()


if __name__ == "__main__":
    main()
