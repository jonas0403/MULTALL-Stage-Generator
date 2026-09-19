# ------------------------------------------------------------------
# File:    source/core/stage/blade_profiles.py
# Author:  Luca De Francesco, Jonas Scholz (based on Marco Wiens)
# Purpose: Bezier blade-profile generation (default + JSON metal angles).
# ------------------------------------------------------------------

# Verbatim moves from stage_calculation.py (create_default_profiles :122-320,
# save_profile :322-350, overall_values :1114-1137, blade_metal_BP :1139-1242).
# Only indentation, the base. prefix for module state and translated comments
# differ. NOTE (user, 2026-09-19): save_profile is uncalled — integrate into
# the GUI later.

import json
import os
import shutil
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import filedialog

import numpy as np

from source.logging import debug_log
import source.core.stage.stage_calculation as base


def create_default_profiles(self, json_path):
    gen_msg = "Generating default profiles..."
    print(gen_msg)
    debug_log.debug(gen_msg, context="Stage")

    try:
        try:
            # Deferred: orchestration imports section_general, which imports
            # this module (top-level import here would be circular).
            from source.core.stage.orchestration import run_main_logic
            run_main_logic({'main_choice': 'default'}, self, json_path)
        except Exception as e:
            import traceback
            traceback.print_exc()
            base._gui_messagebox(messagebox.showerror,
                "Error",
                "Please calculate the Meanline (1D Settings) first and make sure it's saved!"
            )
            return

        # h_H is the standard spanwise sample positions
        h_H = [0.0, 0.2, 0.5, 0.8, 1.0]
        c_03 = 0.277558
        c_07 = 0.165432

        # We will build a dict of all stage bezier data to write once
        all_bezier_data = {}

        for stage_num in range(1, self.stages_to_calc + 1):
            # ---- pull per-stage radial-equilibrium results ----
            rad_R = base.radial_data_R[stage_num]   # dict stored by run_main_logic
            rad_S = base.radial_data_S[stage_num]

            h_rel_s          = rad_R['h_rel']
            l_R_s            = rad_R['l_R']
            l_S_s            = rad_S['l_S']
            beta_blade_R_in  = rad_R['beta_blade_R_in']
            beta_blade_R_out = rad_R['beta_blade_R_out']
            alpha_S_in       = rad_S['alpha_S_in']
            alpha_S_out      = rad_S['alpha_S_out']

            debug_log.debug(f"  create_default [stage={stage_num}] h_rel_s={[round(v,2) for v in h_rel_s]}", context="create_default")
            debug_log.debug(f"  create_default [stage={stage_num}] beta_blade_R_in={[round(v,2) for v in beta_blade_R_in]}", context="create_default")
            debug_log.debug(f"  create_default [stage={stage_num}] beta_blade_R_out={[round(v,2) for v in beta_blade_R_out]}", context="create_default")
            debug_log.debug(f"  create_default [stage={stage_num}] alpha_S_in={[round(v,2) for v in alpha_S_in]}", context="create_default")
            debug_log.debug(f"  create_default [stage={stage_num}] alpha_S_out={[round(v,2) for v in alpha_S_out]}", context="create_default")

            # Chord lengths interpolated to the five standard h_H positions
            chord_length_R = np.interp(h_H, h_rel_s, l_R_s)
            chord_length_S = np.interp(h_H, h_rel_s, l_S_s)

            def generate_dict_for_stage(is_rotor):
                """Build the bezier-point dict for one row of this stage."""
                beta_S_BP_1, beta_S_BP_2, beta_S_BP_3, beta_S_BP_4 = [], [], [], []
                alpha_S_BP_1, alpha_S_BP_2, alpha_S_BP_3, alpha_S_BP_4 = [], [], [], []

                if is_rotor:
                    # --- PASS 1: collect raw LE/TE angles for all 5 span positions ---
                    raw_b1_list = []
                    raw_b2_list = []
                    for i, h_val in enumerate(h_H):
                        for j in range(len(h_rel_s)):
                            if abs(h_rel_s[j] - h_val) < 1e-6:
                                raw_b1_list.append(beta_blade_R_in[j])
                                raw_b2_list.append(beta_blade_R_out[j])
                                break

                    # --- Global reflection decision ---
                    # If ALL 5 LE values are > 90°, the rotor uses the >90° convention.
                    # Reflect ALL TE values < 90° to > 90° so the Bezier curve stays
                    # on one side of 90° and 1/tan(beta) doesn't change sign.
                    le_all_above_90 = all(b1 > 90.0 for b1 in raw_b1_list)

                    # --- PASS 2: apply reflection and build control points ---
                    for i, h_val in enumerate(h_H):
                        for j in range(len(h_rel_s)):
                            if abs(h_rel_s[j] - h_val) < 1e-6:
                                b1 = raw_b1_list[i]
                                b2 = raw_b2_list[i]
                                reflected = False
                                if le_all_above_90 and b2 < 90.0:
                                    b2 = 180.0 - b2
                                    reflected = True
                                delta = b2 - b1
                                beta_S_BP_1.append(round(b1, 2))
                                beta_S_BP_4.append(round(b2, 2))
                                beta_S_BP_2.append(round(b2 - delta * c_03, 2))
                                beta_S_BP_3.append(round(b2 - delta * c_07, 2))
                                debug_log.debug(f"  create_default [stage={stage_num}, ROTOR, h={h_val:.1f}]: b1(pre)={raw_b1_list[i]:.2f}, b2(pre)={raw_b2_list[i]:.2f} → b1={b1:.2f}, b2={b2:.2f} reflected={reflected} delta={delta:.2f} le_all_above_90={le_all_above_90}", context="create_default")
                                break

                else:
                    for i, h_val in enumerate(h_H):
                        for j in range(len(h_rel_s)):
                            if abs(h_rel_s[j] - h_val) < 1e-6:
                                a1_orig = alpha_S_in[j]
                                a2_orig = alpha_S_out[j]
                                a1 = a1_orig
                                a2 = a2_orig
                                reflected = False
                                if a2 > 90.0:
                                    a2 = 180.0 - a2
                                    reflected = True
                                debug_log.debug(f"  create_default [stage={stage_num}, STATOR, h={h_val:.1f}]: a1(pre)={a1_orig:.2f}, a2(pre)={a2_orig:.2f} → a1={a1:.2f}, a2={a2:.2f} reflected={reflected} delta={a2-a1:.2f}", context="create_default")
                                delta = a2 - a1
                                alpha_S_BP_1.append(round(a1, 2))
                                alpha_S_BP_4.append(round(a2, 2))
                                alpha_S_BP_2.append(round(a2 - delta * c_03, 2))
                                alpha_S_BP_3.append(round(a2 - delta * c_07, 2))
                                break

                if is_rotor:
                    ref_chord = chord_length_R[2]   # 50% span chord
                    rel_thickness = np.array([
                        [0.023, 0.020, 0.015, 0.011, 0.007],
                        [0.082, 0.071, 0.055, 0.038, 0.027],
                        [0.017, 0.015, 0.011, 0.008, 0.005],
                        [0.010, 0.009, 0.007, 0.005, 0.003],
                    ])
                    abs_thickness = rel_thickness * ref_chord
                    # ---- Spanwise smoothing of rotor angles ----
                    # The per-section reflection can create spanwise discontinuities
                    # when beta_blade_R_out crosses 90° at some spans but not others.
                    # Apply light 3-point moving average to TE-side CPs to smooth them.
                    for cp_list in [beta_S_BP_2, beta_S_BP_3, beta_S_BP_4]:
                        orig = list(cp_list)
                        smoothed = list(cp_list)
                        for i in range(1, 4):
                            smoothed[i] = round((orig[i-1] + orig[i] + orig[i+1]) / 3.0, 2)
                        debug_log.debug(f"  create_default [stage={stage_num}, ROTOR] spanwise smoothing: {orig} → {smoothed}", context="create_default")
                        cp_list[:] = smoothed
                    angles = beta_S_BP_1 + beta_S_BP_2 + beta_S_BP_3 + beta_S_BP_4
                    angle_key = "beta_S"
                    debug_log.debug(f"  create_default [stage={stage_num}, ROTOR]: final angles={[round(v,2) for v in angles]}", context="create_default")
                else:
                    ref_chord = chord_length_S[2]
                    rel_thickness = np.array([
                        [0.015, 0.015, 0.015, 0.015, 0.015],
                        [0.058, 0.058, 0.058, 0.058, 0.058],
                        [0.011, 0.011, 0.011, 0.011, 0.011],
                        [0.006, 0.006, 0.006, 0.006, 0.006],
                    ])
                    abs_thickness = rel_thickness * ref_chord
                    angles = alpha_S_BP_1 + alpha_S_BP_2 + alpha_S_BP_3 + alpha_S_BP_4
                    angle_key = "alpha_S"
                    debug_log.debug(f"  create_default [stage={stage_num}, STATOR]: angles={[round(v,2) for v in angles]}", context="create_default")

                thickness_combined = [
                    round(float(v), 3)
                    for row_vals in abs_thickness
                    for v in row_vals
                ]

                return {
                    "h/H":   list(h_H),
                    angle_key: angles,
                    "d/l":   thickness_combined,
                    "m*":    [0.0]*5 + [0.3]*5 + [0.7]*5 + [1.0]*5,
                }

            rotor_dict  = generate_dict_for_stage(is_rotor=True)
            stator_dict = generate_dict_for_stage(is_rotor=False)

            # Keys: rotor_stage_1, stator_stage_1, rotor_stage_2, …
            all_bezier_data[f"rotor_stage_{stage_num}"]  = rotor_dict
            all_bezier_data[f"stator_stage_{stage_num}"] = stator_dict

            bp_msg = f"Stage {stage_num}: rotor/stator bezier points generated."
            print(bp_msg)
            debug_log.debug(bp_msg, context="create_default_profiles")

        # ---- write everything to JSON in one pass ----
        with open(json_path, 'r') as f:
            data = json.load(f)

        data["Bezier_point_data"] = all_bezier_data

        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)

        # Update in-memory cache on the GUI object
        if hasattr(self, "prepop_bezier_point_rotor"):
            self.prepop_bezier_point_rotor = all_bezier_data.get("rotor_stage_1", {})
            self.prepop_bezier_point_stator = all_bezier_data.get("stator_stage_1", {})

        profile_msg = f"Default profiles for {self.stages_to_calc} stage(s) saved to JSON."
        print(profile_msg)
        debug_log.debug(profile_msg, context="create_default_profiles")
        base._gui_messagebox(messagebox.showinfo,
            "Success",
            f"Default profiles for {self.stages_to_calc} stage(s) successfully created and saved to JSON!"
        )

    except NameError as e:
        var_err = f"Variable Error: {e}"
        print(var_err)
        debug_log.debug(var_err, context="create_default_profiles")
        base._gui_messagebox(messagebox.showerror, "Error", "Please calculate the Meanline (1D Settings) first! (Debug: #2)")
    except Exception as e:
        import traceback
        traceback.print_exc()
        base._gui_messagebox(messagebox.showerror, "Error", f"An unexpected error occurred: {e}")

def save_profile(source_filename):
        if not os.path.exists(source_filename):
            return

        root_dialog = tk.Tk()
        root_dialog.withdraw()

        filepath = filedialog.asksaveasfilename(
            parent=root_dialog,
            title=f"Save Profile '{source_filename} as",
            defaultextension=".txt",
            filetypes=(("Text Files", "*.txt"),("All files", "*.*"))
        )

        root_dialog.destroy()

        if not filepath:
            return

        try:
            shutil.copy(source_filename, filepath)
            save_msg = f"Profile successfully saved to {filepath}"
            print(save_msg)
            debug_log.debug(save_msg, context="save_profile")
        except Exception as e:
            err_msg = f"Error saving profile: {e}"
            print(err_msg)
            debug_log.debug(err_msg, context="save_profile")

def overall_values(row, z_R, l_R, l_S):

    if row % 2 != 0:
        z = z_R
        # lenth of rotor blade h_rel = 50%
        s_1D = round(l_R[10]/1000, 4)
        s_0_5 = s_1D
        elipse_LE = 3
        elipse_TE = 3

    elif row % 2 == 0:
        z = base.z_S
        # lenth of rotor blade h_rel = 50%
        s_1D = round(l_S[10]/1000, 4)
        s_0_5 = s_1D
        elipse_LE = 3
        elipse_TE = 4

    # beginning of LE
    x_LE = []
    for i in range(len(base.h_H)):
        x_LE.append(round((-2*base.LE_shift*base.h_H[i]+base.LE_shift),5))

    return z, s_1D, s_0_5, x_LE, elipse_LE, elipse_TE

def blade_metal_BP(row):
    """
    Read Bezier control points for blade row `row` from JSON.

    Row numbering (1-based, interleaved):
        1 = rotor  stage 1
        2 = stator stage 1
        3 = rotor  stage 2
        4 = stator stage 2
        …
    """
    json_path = base.ACTIVE_JSON_PATH

    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        json_err = f"Error while reading JSON file: {e}"
        print(json_err)
        debug_log.debug(json_err, context="blade_metal_BP")
        return [], [], [], [], [], [], [], [], [[], [], [], []]

    # Derive stage number and blade type from the row index
    stage_num = (row - 1) // 2 + 1
    is_rotor  = (row % 2 != 0)

    blade_key = f"rotor_stage_{stage_num}"  if is_rotor else f"stator_stage_{stage_num}"
    angle_key = "beta_S"                    if is_rotor else "alpha_S"

    bezier_store = data.get("Bezier_point_data", {})

    b_data = bezier_store.get(blade_key)
    if b_data is None:
        fallback_key = "rotor" if is_rotor else "stator"
        b_data = bezier_store.get(fallback_key)
        if b_data is not None:
            legacy_warn = (
                f"Warning: per-stage key '{blade_key}' not found – "
                f"falling back to legacy key '{fallback_key}'. "
                f"Re-generate profiles to fix this."
            )
            print(legacy_warn)
            debug_log.debug(legacy_warn, context="blade_metal_BP")

    if not b_data:
        no_data_msg = f"No bezier data found for '{blade_key}'!"
        print(no_data_msg)
        debug_log.debug(no_data_msg, context="blade_metal_BP")
        return [], [], [], [], [], [], [], [], [[], [], [], []]

    angles  = b_data.get(angle_key, [0] * 20)
    d_l     = b_data.get("d/l",     [0] * 20)
    m_star  = b_data.get("m*",      [0] * 20)

    beta_M_e = angles[0:5]
    beta_M_2 = angles[5:10]
    beta_M_3 = angles[10:15]
    beta_M_a = angles[15:20]

    blade_type = "ROTOR" if is_rotor else "STATOR"
    # Log the raw (pre-clamp) values from JSON
    debug_log.debug(f"  blade_metal_BP [{blade_type} row {row} stage {stage_num}] JSON_raw beta_M_e (LE): {[round(v, 2) for v in beta_M_e]}", context="blade_metal_raw")
    debug_log.debug(f"  blade_metal_BP [{blade_type} row {row} stage {stage_num}] JSON_raw beta_M_2:      {[round(v, 2) for v in beta_M_2]}", context="blade_metal_raw")
    debug_log.debug(f"  blade_metal_BP [{blade_type} row {row} stage {stage_num}] JSON_raw beta_M_3:      {[round(v, 2) for v in beta_M_3]}", context="blade_metal_raw")
    debug_log.debug(f"  blade_metal_BP [{blade_type} row {row} stage {stage_num}] JSON_raw beta_M_a (TE): {[round(v, 2) for v in beta_M_a]}", context="blade_metal_raw")

    # Clamp angles to prevent Bezier curve from crossing 90 deg,
    # which causes 1/tan(beta) to change sign (INVALID Rtheta).
    if not is_rotor:
        # Stator: reflect ALL control points > 90 deg to [0, 90] interval
        beta_M_a = [180.0 - v if v > 90.0 else v for v in beta_M_a]
        beta_M_3 = [180.0 - v if v > 90.0 else v for v in beta_M_3]
        beta_M_2 = [180.0 - v if v > 90.0 else v for v in beta_M_2]
        beta_M_e = [180.0 - v if v > 90.0 else v for v in beta_M_e]
    else:
        # Rotor: if ALL 5 LE values > 90°, reflect ALL TE-side CPs < 90° to > 90°
        # Using span-consistent logic to avoid per-section discontinuities.
        le_all_above_90 = all(v > 90.0 for v in beta_M_e)
        if le_all_above_90:
            for i in range(5):
                for cp in [beta_M_a, beta_M_3, beta_M_2]:
                    if cp[i] < 90.0:
                        cp[i] = 180.0 - cp[i]

    d_l_e = d_l[0:5]
    d_l_2 = d_l[5:10]
    d_l_3 = d_l[10:15]
    d_l_a = d_l[15:20]

    blade_type = "ROTOR" if is_rotor else "STATOR"
    debug_log.debug(f"  blade_metal_BP [{blade_type} row {row} stage {stage_num}] beta_M_e (LE): {[round(v, 2) for v in beta_M_e]}", context="blade_metal_angles")
    debug_log.debug(f"  blade_metal_BP [{blade_type} row {row} stage {stage_num}] beta_M_2:      {[round(v, 2) for v in beta_M_2]}", context="blade_metal_angles")
    debug_log.debug(f"  blade_metal_BP [{blade_type} row {row} stage {stage_num}] beta_M_3:      {[round(v, 2) for v in beta_M_3]}", context="blade_metal_angles")
    debug_log.debug(f"  blade_metal_BP [{blade_type} row {row} stage {stage_num}] beta_M_a (TE): {[round(v, 2) for v in beta_M_a]}", context="blade_metal_angles")

    m_star_BP = [
        m_star[0:5],
        m_star[5:10],
        m_star[10:15],
        m_star[15:20],
    ]

    return beta_M_a, beta_M_2, beta_M_3, beta_M_e, d_l_a, d_l_2, d_l_3, d_l_e, m_star_BP
