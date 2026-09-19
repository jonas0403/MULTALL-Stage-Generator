# ------------------------------------------------------------------
# File:    source/core/stage/stage_calculation.py
# Author:  Marco Wiens (modified by Jonas Scholz)
# Purpose: Shared stage state + dialog/robustness helpers (split modules).
# ------------------------------------------------------------------


# Session 26 split: all computation moved verbatim to plots / duct_coordinates /
# blade_coordinates / section_midspan / section_general / blade_profiles /
# channel_setup / state_sync / orchestration (bodies use base.<name> for the
# state below, so every external Stage.* reader keeps working). Untouched
# backup: old/stage_before_split.py.

import math
import os
import tkinter as tk

import tkinter.messagebox as messagebox

wdpath = os.getcwd()

''' Here needs to be a fix radial equilibirium needs to be called for all stages
# parameter for radial equilibrium
stage = 1
approach = 1
constant_r_parameter = 1
'''
stage = 1
approach = 1
constant_r_parameter = 1

ACTIVE_JSON_PATH = None
h_H = [0.0, 0.2, 0.5, 0.8, 1.0]
LE_shift = 0.025
Pi = math.pi

# [Robustness] degenerate-profile guards: coincident camber nodes (dx=dy=0) or axial
# camber (tan=0) make these denominators vanish -> ZeroDivisionError. Each guard triggers
# ONLY on the exact-zero case (which crashes today) and returns the neutral value.
def _seg_unit(dx, dy):
    seg = math.sqrt(dx * dx + dy * dy)
    if seg < 1e-12:
        return (0.0, 0.0)
    return (dx / seg, dy / seg)


def _dtan_div(dm, beta_deg):
    t = math.tan(beta_deg * Pi / 180)
    if abs(t) < 1e-12:
        return 0.0
    return dm / t


def _gui_messagebox(show_func, title, message):
    # [FIX bug #7] suppress modal dialogs in headless runs: explicit env flag
    # (MULTALL_HEADLESS=1) or a non-interactive matplotlib backend (pytest sets
    # MPLBACKEND=Agg). A withdrawn Tk root alone must NOT trigger popups.
    try:
        if os.environ.get("MULTALL_HEADLESS", "") == "1":
            return
        try:
            import matplotlib
            if str(matplotlib.get_backend()).lower() == "agg":
                return
        except Exception:
            pass
        if tk._default_root is not None:
            show_func(title, message)
    except Exception:
        pass

channel_data = {}
# Move the declarations to module level
radial_data_R = {}
radial_data_S = {}
