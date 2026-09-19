# ------------------------------------------------------------------
# File:    source/core/stage/orchestration.py
# Author:  Jonas Scholz
# Purpose: Main calculation flow: channel, radial equilibrium, adjust.
# ------------------------------------------------------------------

# Verbatim move of run_main_logic (stage_calculation.py :555-559 + :728-945,
# plus the dead commented-out block :948-1111, kept per user decision). The
# meanline unpack lives in state_sync now. Bare-name globals became base.
# attributes (same single home, so all Stage.* readers keep working).

import json

import numpy as np

from source.logging import debug_log
from source.core.radial.radial_equilibrium import radial_equilibrium_R, radial_equilibrium_S
from source.gui.dialogs.bezier_editors import adjustBezierCurve_beta, adjustBezierCurve_d
from source.core.stage.channel_setup import init_channel_data
from source.core.stage.state_sync import sync_meanline_state
from source.core.stage.section_general import calculation_of_section
import source.core.stage.stage_calculation as base


def run_main_logic(new_adjustment_data, compressor_gui_data, json_path):# approach = 1 constant_r_parameter = 1 need to be defined here
    # Calls the channel function to initialise the channel coordinates for all stages that are beeing calculated
    init_channel_data(compressor_gui_data)
    base.ACTIVE_JSON_PATH = json_path

    sync_meanline_state(compressor_gui_data.meanline_data)

    # --- DEBUGGING CHECK ---
    debug_log.debug(f"DEBUG LOOP START: stage_to_calc={compressor_gui_data.stages_to_calc}")
    debug_log.debug(f"DEBUG TYPE CHECK: b1 is {type(base.b1)}, cu1 is {type(base.cu1)}, cm1 is {type(base.cm1)}")

    base.radial_data_S = {}
    base.radial_data_R = {}

    for s in range(1, compressor_gui_data.stages_to_calc + 1):
        debug_log.debug(f"--- Processing Stage {s} ---")
        # Verify indexing will work
        debug_log.debug(f"DEBUG Stage {s}: b1[s-1]={base.b1[s-1]}")

        compressor_gui_data.stage = s


        (h_rel_s, l_S_s, c_m_S_in_s, c_m_S_out_s, c_u_S_in_s, c_u_S_out_s, c_S_out_s,
        T_S_in_s, T_S_out_s, p_S_in_s, p_S_out_s, alpha_S_in_s, beta_S_in_s,
        alpha_S_out_s, beta_blade_S_in_s, beta_blade_S_out_s, D_S_s) = radial_equilibrium_S(
            s, base.approach, base.constant_r_parameter,
            base.D_S1[s-1], base.D_S2[s-1], base.D_S3[s-1],
            base.D_H1[s-1], base.D_H2[s-1], base.D_H3[s-1],
            base.D_m1[s-1], base.D_m2[s-1], base.D_m3[s-1],
            base.b1[s-1], base.b2[s-1], base.b3[s-1],
            base.cu1[s-1], base.cu2[s-1], base.cu3[s-1],
            base.u1[s-1], base.u2[s-1], base.u3[s-1],
            base.cm1[s-1], base.cm2[s-1], base.cm3[s-1],
            base.delta_h_t[s-1], base.T_t1[s-1], base.T_t2[s-1], base.T_t3[s-1],
            base.p_t1[s-1], base.p_t2[s-1], base.p_t3[s-1],
            compressor_gui_data)

        base.radial_data_S[s] = {
            'h_rel': h_rel_s, 'l_S': l_S_s, 'c_m_S_in': c_m_S_in_s,
            'c_m_S_out': c_m_S_out_s, 'c_u_S_in': c_u_S_in_s, 'c_u_S_out': c_u_S_out_s,
            'c_S_out': c_S_out_s, 'T_S_in': T_S_in_s, 'T_S_out': T_S_out_s,
            'p_S_in': p_S_in_s, 'p_S_out': p_S_out_s, 'alpha_S_in': alpha_S_in_s,
            'beta_S_in': beta_S_in_s, 'alpha_S_out': alpha_S_out_s,
            'beta_blade_S_in': beta_blade_S_in_s, 'beta_blade_S_out': beta_blade_S_out_s,
            'D_S': D_S_s
        }

        (h_rel_r, l_R_r, r_R_out_r, c_m_R_in_r, c_m_R_out_r, c_u_R_in_r, c_u_R_out_r,
        c_R_out_r, u_R_in_r, u_R_out_r, T_R_in_r, T_R_out_r, p_R_in_r, p_R_out_r,
        Ma_abs_R_in_r, Ma_rel_R_in_r, roh_R_in_r, alpha_R_in_r, beta_R_in_r,
        alpha_R_out_r, beta_R_out_r, beta_blade_R_in_r, beta_blade_R_out_r, D_R_r) = radial_equilibrium_R(
            s, base.approach, base.constant_r_parameter,
            base.D_S1[s-1], base.D_S2[s-1], base.D_S3[s-1],
            base.D_H1[s-1], base.D_H2[s-1], base.D_H3[s-1],
            base.D_m1[s-1], base.D_m2[s-1], base.D_m3[s-1],
            base.b1[s-1], base.b2[s-1], base.b3[s-1],
            base.cu1[s-1], base.cu2[s-1], base.cu3[s-1],
            base.u1[s-1], base.u2[s-1], base.u3[s-1],
            base.cm1[s-1], base.cm2[s-1], base.cm3[s-1],
            base.delta_h_t[s-1], base.T_t1[s-1], base.T_t2[s-1], base.T_t3[s-1],
            base.p_t1[s-1], base.p_t2[s-1], base.p_t3[s-1],
            compressor_gui_data)

        base.radial_data_R[s] = {
            'h_rel': h_rel_r, 'l_R': l_R_r, 'r_R_out': r_R_out_r,
            'c_m_R_in': c_m_R_in_r, 'c_m_R_out': c_m_R_out_r,
            'c_u_R_in': c_u_R_in_r, 'c_u_R_out': c_u_R_out_r,
            'c_R_out': c_R_out_r, 'u_R_in': u_R_in_r, 'u_R_out': u_R_out_r,
            'T_R_in': T_R_in_r, 'T_R_out': T_R_out_r,
            'p_R_in': p_R_in_r, 'p_R_out': p_R_out_r,
            'Ma_abs_R_in': Ma_abs_R_in_r, 'Ma_rel_R_in': Ma_rel_R_in_r,
            'roh_R_in': roh_R_in_r, 'alpha_R_in': alpha_R_in_r,
            'beta_R_in': beta_R_in_r, 'alpha_R_out': alpha_R_out_r,
            'beta_R_out': beta_R_out_r, 'beta_blade_R_in': beta_blade_R_in_r,
            'beta_blade_R_out': beta_blade_R_out_r, 'D_R': D_R_r
        }

    all_done_msg = "Successfully calculated meanline and radial equilibrium for all stages"
    print(all_done_msg)
    debug_log.debug(all_done_msg, context="run_main_logic")
    ### Debugging Screen to verify correct stage wise implementation of correct calling order

    debug_log.debug(f"VERIFY radial_data_R keys: {list(base.radial_data_R.keys())}")
    for s in base.radial_data_R:
        debug_log.debug(f"stage {s}: l_R[10]={base.radial_data_R[s]['l_R'][10]:.2f}", context="run_main_logic")

    debug_log.section("Radial Equilibrium Results")
    debug_log.debug(f"radial_equilibrium_S Results (Last Stage Calculated: {s})", context="run_main_logic")

    # Use the variables ending in _s as they represent the data from the last loop iteration
    debug_vars = {
        "Geometry": {"h_rel": h_rel_s, "l_S": l_S_s, "D_S_param": D_S_s},
        "Velocities (cm)": {"c_m_S_in": c_m_S_in_s, "c_m_S_out": c_m_S_out_s},
        "Velocities (cu/c)": {"c_u_S_in": c_u_S_in_s, "c_u_S_out": c_u_S_out_s, "c_S_out": c_S_out_s},
        "Thermodynamics": {"T_S_in": T_S_in_s, "T_S_out": T_S_out_s, "p_S_in": p_S_in_s, "p_S_out": p_S_out_s},
        "Angles (Deg)": {"alpha_S_in": alpha_S_in_s, "alpha_S_out": alpha_S_out_s, "beta_S_in": beta_S_in_s},
        "Blade Angles": {"beta_blade_S_in": beta_blade_S_in_s, "beta_blade_S_out": beta_blade_S_out_s}
    }

    for category, vars_dict in debug_vars.items():
        debug_log.debug(f"[{category}]", context="run_main_logic")
        for name, value in vars_dict.items():
            if isinstance(value, (list, np.ndarray)) and len(value) > 0:
                debug_log.debug(f"  {name:20}: {value[0]:.4f} ... {value[-1]:.4f} (len: {len(value)})", context="run_main_logic")
            else:
                debug_log.debug(f"  {name:20}: {value}", context="run_main_logic")

    # main_choice = new_adjustment_data.get('main_choice', 'default')
    main_choice = new_adjustment_data['main_choice']
    #path = settings.get("output_folder", ".")
    #NROW = int(settings.get("nrow", 2))
    #levels_input = new_adjustment_data.get("levels", "0.0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 0.95, 1.00")


    levels_input = new_adjustment_data.get("levels", [0.0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 0.95, 1.00])

    # Handle both string and list input
    if isinstance(levels_input, str):
        levels_input = [float(x.strip()) for x in levels_input.split(',')]
    elif isinstance(levels_input, list):
        levels_input = [float(x) for x in levels_input]


    h_H = [0.0, 0.2, 0.5, 0.8, 1.0] # Standard values for the sections


    #levels_input = [float(x.strip()) for x in levels_input.split(',')] # Reads the levels and converts them into a list of float values

    #chord_length_R = np.interp(h_H, h_rel, l_R) # Interpolates the chord length for the standard sections
    #chord_length_S = np.interp(h_H, h_rel, l_S)


    if main_choice == 'adjust': # Adjustment of Bezier points
        try:

            section_idx_str = new_adjustment_data['adjust_section_idx']
            section_idx_float = float(section_idx_str)

            # Base heights
            h_H_base = [0.0, 0.2, 0.5, 0.8, 1.0] # Why hardcoded?
            section_idx = h_H_base.index(section_idx_float)

            row_str = new_adjustment_data['adjust_row']
            parameter_str = new_adjustment_data['adjust_parameter']
            h_val = h_H_base[section_idx]

            is_rotor = (row_str == 'Rotor')
            # [FIX bug #2] stage selection: adjust any stage (dialog offers 1..N).
            # Default 1 preserves the previous rows-1/2 behavior.
            try:
                stage_sel = int(new_adjustment_data.get('adjust_stage', 1))
            except (TypeError, ValueError):
                stage_sel = 1
            row_num = 2 * (stage_sel - 1) + (1 if is_rotor else 2)
            new_key = ("rotor_stage_%d" % stage_sel) if is_rotor else ("stator_stage_%d" % stage_sel)
            legacy_key = "rotor" if is_rotor else "stator"
            angle_key = "beta_S" if is_rotor else "alpha_S"

            with open(json_path, 'r') as file:
                data = json.load(file)

            store = data.get("Bezier_point_data", {})
            # [FIX bug #2] prefer per-stage keys, fall back to legacy keys;
            # write back to whichever key was read (same JSON syntax as everything else).
            read_key = new_key if new_key in store else legacy_key
            b_data = store.get(read_key, {})
            if not b_data:
                err_msg = f"Error: No bezier data found for {row_str} (stage {stage_sel}). Please generate profiles first."
                print(err_msg)
                debug_log.debug(err_msg, context="adjust_bezier")
                return

            angles_flat = b_data.get(angle_key, [0]*20)
            d_l_flat = b_data.get("d/l", [0]*20)

            debug_log.debug(f"Selected parameter is: {parameter_str}", context="adjust_bezier")

            if parameter_str == 'Angle':
                adj_msg = f"Adjustments for Angle in row {row_str}, section: {h_val}"
                print(adj_msg)
                debug_log.debug(adj_msg, context="adjust_bezier")

                original_points = [angles_flat[section_idx + i*5] for i in range(4)]


                new_points = adjustBezierCurve_beta(original_points)


                for i in range(4):
                    angles_flat[section_idx + i*5] = new_points[i]
                b_data[angle_key] = angles_flat

            elif parameter_str == 'Thickness':
                adj_msg = f"Adjustments for Thickness in row {row_str}, section: {h_val}"
                print(adj_msg)
                debug_log.debug(adj_msg, context="adjust_bezier")

                chord, *_ = calculation_of_section(h_val, row_num)

                original_points = [d_l_flat[section_idx + i*5] for i in range(4)]
                new_points = adjustBezierCurve_d(original_points, chord)


                for i in range(4):
                    d_l_flat[section_idx + i*5] = new_points[i]
                b_data["d/l"] = d_l_flat

            data["Bezier_point_data"][read_key] = b_data
            with open(json_path, "w") as file:
                json.dump(data, file, indent=4)

            if hasattr(compressor_gui_data, "prepop_bezier_point_rotor"):
                if is_rotor:
                    compressor_gui_data.prepop_bezier_point_rotor = b_data
                else:
                    compressor_gui_data.prepop_bezier_point_stator = b_data


            save_adj_msg = f"Adjustments successfully saved to JSON for {row_str}!"
            print(save_adj_msg)
            debug_log.debug(save_adj_msg, context="adjust_bezier")

        except Exception as e:
            err_msg = f"Error during adjustment: {e}"
            print(err_msg)
            debug_log.debug(err_msg, context="adjust_bezier")
            return


#area to change rotor:
# length = []
# h = [0.0 , 0.2, 0.5, 0.8, 1.0]
# row = 1
# for k in range(len(h)):
#     i = h[k]
#     chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
#     length.append(chord)

# #print(f"chordlength of 5 segments of rotor (approx):{length}")


# if use_default_rotor_bezier == 1:
#     bezier_control_points("bezier_control_points_R.txt", 1, beta_blade_R_in, beta_blade_R_out, length)

# if use_default_stator_bezier == 1:
#     bezier_control_points("bezier_control_points_S.txt", 2, beta_blade_S_in, beta_blade_S_out, length)


# #metal angle Bezierpoint for the new rotor design:
# beta_S_BP_R_new = [[] for _ in range(5)]
# d_l_BP_R_new = [[] for _ in range(5)]

# with open('bezier_control_points_R.txt', 'r') as file:
#     beta_S_read = [[] for _ in range(4)]
#     d_l_read = [[] for _ in range(4)]

#     csv_reader = csv.reader(file)

#     # Skip all non-relevant lines (descriptive text)
#     for row in csv_reader:
#         if row and row[0].strip().startswith("1st to 4th control points for beta_S"):
#             break

#     # Read the next 4 rows for beta_S (control points)
#     for i in range(4):
#         row = next(csv_reader)
#         beta_S_read[i] = [float(val) for val in row]

#     for i in range(5):
#         beta_S_BP_R_new[i] = [beta_S_read[0][i], beta_S_read[1][i], beta_S_read[2][i], beta_S_read[3][i]]

#     # Skip until reaching d/l section
#     for row in csv_reader:
#         if row and row[0].strip().startswith("1st to 4th control points for d/l"):
#             break

#     # Read the next 4 rows for d/l (control points)
#     for i in range(4):
#         row = next(csv_reader)
#         d_l_read[i] = [float(val) for val in row]

#     for i in range(5):
#         d_l_BP_R_new[i] = [d_l_read[0][i], d_l_read[1][i], d_l_read[2][i], d_l_read[3][i]]

#     if adjust_rotor_thickness == 1:
#         for i in range(5):
#             d_l_BP_R_new[i] = adjustBezierCurve_d(d_l_BP_R_new[i], length[i])

#     if adjust_rotor_angle == 1:
#         for i in range(5):
#             beta_S_BP_R_new[i] = adjustBezierCurve_beta(beta_S_BP_R_new[i])

#     with open('bezier_control_points_R.txt', "w+") as file:
#         file.write("For each level h/H = [0, 0.2, 0.5, 0.8, 1.0], there are four control points for the blade angle beta_S and the thickness d/l. The first and last control points for the blade angle beta_S are determined by radial equilibrium.\n\n")

#         file.write("1st to 4th control points for beta_S for all levels:\n")
#         for i in range(4):
#             file.write(f"{beta_S_BP_R_new[0][i]},{beta_S_BP_R_new[1][i]},{beta_S_BP_R_new[2][i]},{beta_S_BP_R_new[3][i]},{beta_S_BP_R_new[4][i]}\n")

#         file.write("\n")
#         file.write("1st to 4th control points for d/l for all levels:\n")

#         for i in range(4):
#             file.write(f"{beta_S_BP_R_new[0][i]},{beta_S_BP_R_new[1][i]},{beta_S_BP_R_new[2][i]},{beta_S_BP_R_new[3][i]},{beta_S_BP_R_new[4][i]}\n")

#         for i in range(4):
#             file.write(f"{d_l_BP_R_new[0][i]},{d_l_BP_R_new[1][i]},{d_l_BP_R_new[2][i]},{d_l_BP_R_new[3][i]},{d_l_BP_R_new[4][i]}\n")

#         for i in range(4):
#             file.write(f"{d_l_BP_R_new[0][i]},{d_l_BP_R_new[1][i]},{d_l_BP_R_new[2][i]},{d_l_BP_R_new[3][i]},{d_l_BP_R_new[4][i]}\n")

#         file.write("\n")
#         file.write("m* for all levels:\n")

#         file.write("0.0, 0.0, 0.0, 0.0, 0.0\n")
#         file.write("0.3, 0.3, 0.3, 0.3, 0.3\n")
#         file.write("0.7, 0.7, 0.7, 0.7, 0.7\n")
#         file.write("1.0, 1.0, 1.0, 1.0, 1.0\n")


#     # area to change stator:
#     length = []
#     row = 2
#     for k in range(len(h)):
#         i = h[k]
#         chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
#         length.append(chord)

#     #print(f"Chordlength of 5 segments of stator (approx):{length}")


#     #metal angle Bezierpoint for the new stator design:
#     beta_S_BP_S_new = [[] for _ in range(5)]
#     d_l_BP_S_new = [[] for _ in range(5)]

#     with open('bezier_control_points_S.txt', 'r') as file:
#         beta_S_read = [[] for _ in range(4)]
#         d_l_read = [[] for _ in range(4)]

#         csv_reader = csv.reader(file)

#         # Skip all non-relevant lines (descriptive text)
#         for row in csv_reader:
#             if row and row[0].strip().startswith("1st to 4th control points for alpha_S"):
#                 break

#         # Read the next 4 rows for beta_S (control points)
#         for i in range(4):
#             row = next(csv_reader)
#             beta_S_read[i] = [float(val) for val in row]

#         for i in range(5):
#             beta_S_BP_S_new[i] = [beta_S_read[0][i], beta_S_read[1][i], beta_S_read[2][i], beta_S_read[3][i]]

#         # Skip until reaching d/l section
#         for row in csv_reader:
#             if row and row[0].strip().startswith("1st to 4th control points for d/l"):
#                 break

#         # Read the next 4 rows for d/l (control points)
#         for i in range(4):
#             row = next(csv_reader)
#             beta_S_read[i] = [float(val) for val in row]

#         for i in range(5):
#             beta_S_BP_S_new[i] = [beta_S_read[0][i], beta_S_read[1][i], beta_S_read[2][i], beta_S_read[3][i]]

#         # Skip until reaching d/l section
#         for row in csv_reader:
#             if row and row[0].strip().startswith("1st to 4th control points for d/l"):
#                 break

#         # Read the next 4 rows for d/l (control points)
#         for i in range(4):
#             row = next(csv_reader)
#             d_l_read[i] = [float(val) for val in row]

#         for i in range(5):
#             d_l_BP_S_new[i] = [d_l_read[0][i], d_l_read[1][i], d_l_read[2][i], d_l_read[3][i]]

#         if adjust_stator_thickness == 1:
#             for i in range(5):
#                 d_l_BP_S_new[i] = adjustBezierCurve_d(d_l_BP_S_new[i], length[i])

#         if adjust_stator_angle == 1:
#             for i in range(5):
#                 beta_S_BP_S_new[i] = adjustBezierCurve_beta(beta_S_BP_S_new[i])

#         with open('bezier_control_points_S.txt', "w+") as file:
#             file.write("For each level h/H = [0, 0.2, 0.5, 0.8, 1.0], there are four control points for the blade angle beta_S and the thickness d/l. The first and last control points for the blade angle beta_S are determined by radial equilibrium.\n\n")

#             file.write("1st to 4th control points for alpha_S for all levels:\n")
#             for i in range(4):
#                 file.write(f"{beta_S_BP_S_new[0][i]},{beta_S_BP_S_new[1][i]},{beta_S_BP_S_new[2][i]},{beta_S_BP_S_new[3][i]},{beta_S_BP_S_new[4][i]}\n")

#             file.write("\n")
#             file.write("1st to 4th control points for d/l for all levels:\n")

#             for i in range(4):
#                 file.write(f"{beta_S_BP_S_new[0][i]},{beta_S_BP_S_new[1][i]},{beta_S_BP_S_new[2][i]},{beta_S_BP_S_new[3][i]},{beta_S_BP_S_new[4][i]}\n")

#             for i in range(4):
#                 file.write(f"{beta_S_BP_S_new[0][i]},{beta_S_BP_S_new[1][i]},{beta_S_BP_S_new[2][i]},{beta_S_BP_S_new[3][i]},{beta_S_BP_S_new[4][i]}\n")

#             file.write("\n")
#             file.write("m* for all levels:\n")

#             file.write("0.0, 0.0, 0.0, 0.0, 0.0\n")
#             file.write("0.3, 0.3, 0.3, 0.3, 0.3\n")
#             file.write("0.7, 0.7, 0.7, 0.7, 0.7\n")
#             file.write("1.0, 1.0, 1.0, 1.0, 1.0\n")

#     # 0: all sections or any number between 1 and NSECS
#     section = 0
#     print(f"rotor_patches = {rotor_patches_data}")
