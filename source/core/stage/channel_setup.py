# ------------------------------------------------------------------
# File:    source/core/stage/channel_setup.py
# Author:  Jonas Scholz (based on Marco Wiens)
# Purpose: Per-stage channel geometry init with global annulus spline.
# ------------------------------------------------------------------

# Verbatim move from stage_calculation.py (init_channel_data :356-512 plus
# the dead commented-out predecessor :514-553, kept per user decision).
# Only indentation and the base. prefix for module state differ.

from source.logging import debug_log
from source.core.geometry.cubic_spline import cubspline
from source.core.geometry.channel import channel
import source.core.stage.stage_calculation as base


def init_channel_data(compressor_gui_data):
    """
    Compute channel geometry for every stage and store it in the global
    channel_data dict.  Each stage after the first is shifted by a
    cumulative axial offset so that all coordinates live in one global
    reference frame instead of each stage starting at x = 0.
    """
    base.channel_data = {}
    cumulative_x_offset = 0.0          # global axial position of stage-1 inlet

    for s in range(1, compressor_gui_data.stages_to_calc + 1):
        compressor_gui_data.stage = s
        x_values_s, r_values_s, m_prime_values_s, x0_s, r0_N_s, r0_G_s = channel(compressor_gui_data)

        # channel() returns x0 as numpy array; convert to list
        x0_s = list(x0_s)

        # ── shift every x-coordinate into the global frame ──────────────
        if cumulative_x_offset != 0.0:
            # x0: the 9 spline control points
            x0_s = [x + cumulative_x_offset for x in x0_s]
            # x_values and m_prime_values: one list per span height (h_H)
            for k in range(len(x_values_s)):
                x_values_s[k]      = [v + cumulative_x_offset for v in x_values_s[k]]
                m_prime_values_s[k] = [v + cumulative_x_offset for v in m_prime_values_s[k]]
            # r_values are radii – they are NOT shifted

        base.channel_data[s] = {
            'x_values':       x_values_s,
            'r_values':       r_values_s,
            'm_prime_values': m_prime_values_s,
            'x0':             x0_s,
            'r0_N_mm':        r0_N_s,
            'r0_G_mm':        r0_G_s,
        }

        # Stage s+1's local x0[1]=0 (rotor inlet) must land at the current
        # stage's stator outlet x0[7] in the global frame.
        cumulative_x_offset = x0_s[7]

        debug_log.debug(f"Stage {s}: channel stored. "
                         f"x0[0]={x0_s[0]:.1f} x0[7]={x0_s[7]:.1f} mm  "
                         f"→ next offset = {cumulative_x_offset:.1f} mm",
                         context="init_channel_data")
        # Verify x0 monotonicity (BUGFIX v2: all x0 values in local frame → monotonic)
        x0_all = [round(v, 1) for v in x0_s]
        x0_ok = all(x0_all[i] <= x0_all[i+1] for i in range(len(x0_all)-1))
        debug_log.debug(f"Stage {s}: x0_values = {x0_all}  monotonic={x0_ok}",
                         context="init_channel_data")

    # ── Global annulus spline (Option B) ──────────────────────────────────────
    # Build a single continuous hub/shroud annulus across all stages by
    # concatenating per-stage control points (x0[1..7], excluding duct points
    # x0[0] and x0[8]) and constructing global splines.  Each stage's r_values
    # are then re-sampled from the global spline, eliminating the radial
    # discontinuity at inter-stage interfaces that caused ~18000 negative volumes.
    # See Docs/Negative_Volume_Debug_Log.md for details.
    # m_prime_values are kept from the per-stage computation (the arc-length
    # correction from the radial adjustment is O(dr²) and negligible).

    # Log interface radii before correction
    for s in range(1, compressor_gui_data.stages_to_calc):
        hub_s   = base.channel_data[s]['r0_N_mm']
        hub_n   = base.channel_data[s + 1]['r0_N_mm']
        shrd_s  = base.channel_data[s]['r0_G_mm']
        shrd_n  = base.channel_data[s + 1]['r0_G_mm']
        x0_s    = base.channel_data[s]['x0']
        x0_n    = base.channel_data[s + 1]['x0']
        debug_log.debug(
            f"INTERFACE Stage {s}→{s+1} BEFORE: "
            f"hub={hub_s[7]:.1f}→{hub_n[1]:.1f} mm "
            f"(Δ={hub_n[1]-hub_s[7]:+.1f}), "
            f"shroud={shrd_s[7]:.1f}→{shrd_n[1]:.1f} mm "
            f"(Δ={shrd_n[1]-shrd_s[7]:+.1f}), "
            f"x={x0_s[7]:.1f}/{x0_n[1]:.1f} mm",
            context="global_annulus")

    # ── 1. Build global control-point arrays ──────────────────────────────
    num_stages = compressor_gui_data.stages_to_calc
    x_hub_all, r_hub_all = [], []
    x_shroud_all, r_shroud_all = [], []

    h_H = [0.0, 0.2, 0.5, 0.8, 1.0]

    for s in range(1, num_stages + 1):
        x0_g = base.channel_data[s]['x0']        # 9 control points, global x [mm]
        rN   = base.channel_data[s]['r0_N_mm']   # hub control points [mm]
        rG   = base.channel_data[s]['r0_G_mm']   # shroud control points [mm]

        # Stage 1: include x0[0..7] (include inlet duct point x0[0]
        #           so cubspline doesn't extrapolate for x < 0).
        # Stage 2+: include x0[2..7]  (skip x0[1] which duplicates prev x0[7]).
        # Last stage: also include x0[8] (outlet duct point) to avoid
        #             extrapolation for x > x0[7].
        if s == 1:
            start = 0
        elif s == 2:
            start = 2
        else:
            start = 2  # same for all intermediate stages

        if s == num_stages:
            end = 8
        else:
            end = 7

        for i in range(start, end + 1):
            x_hub_all.append(x0_g[i])
            r_hub_all.append(rN[i])
            x_shroud_all.append(x0_g[i])
            r_shroud_all.append(rG[i])

    debug_log.debug(
        f"Global annulus: {len(x_hub_all)} hub control points, "
        f"x range [{x_hub_all[0]:.1f}, {x_hub_all[-1]:.1f}] mm",
        context="global_annulus")

    # ── 2. Re-sample each stage from the global spline ────────────────────
    for s in range(1, num_stages + 1):
        x_stage = base.channel_data[s]['x_values'][0]  # hub x-coords, ~130 pts [mm]
        old_rN = base.channel_data[s]['r_values'][0]   # old hub radii [mm]
        old_rG = base.channel_data[s]['r_values'][4]   # old shroud radii [mm]

        # Re-sample hub and shroud via cubspline (Method 3)
        r_N_new = [cubspline(3, x, x_hub_all, r_hub_all) for x in x_stage]
        r_G_new = [cubspline(3, x, x_shroud_all, r_shroud_all) for x in x_stage]

        # Re-compute r_values for all 5 span heights
        r_values_new = []
        for k, element in enumerate(h_H):
            r_span = [r_N_new[i] + element * (r_G_new[i] - r_N_new[i])
                      for i in range(len(x_stage))]
            r_values_new.append(r_span)

        base.channel_data[s]['r_values'] = r_values_new

    # Log interface radii after correction (compare at same x-position)
    for s in range(1, num_stages):
        x_interface = base.channel_data[s]['x0'][7]  # same as next stage's x0[1]
        x_stage_s   = base.channel_data[s]['x_values'][0]
        x_stage_n   = base.channel_data[s + 1]['x_values'][0]
        hub_s       = base.channel_data[s]['r_values'][0]
        hub_n       = base.channel_data[s + 1]['r_values'][0]
        shrd_s      = base.channel_data[s]['r_values'][4]
        shrd_n      = base.channel_data[s + 1]['r_values'][4]
        # Find closest index to interface in each stage's x array
        i_s = min(range(len(x_stage_s)), key=lambda i: abs(x_stage_s[i] - x_interface))
        i_n = min(range(len(x_stage_n)), key=lambda i: abs(x_stage_n[i] - x_interface))
        debug_log.debug(
            f"INTERFACE Stage {s}→{s+1} AFTER: "
            f"hub={hub_s[i_s]:.4f}→{hub_n[i_n]:.4f} mm "
            f"(Δ={hub_n[i_n]-hub_s[i_s]:+.4f}), "
            f"shroud={shrd_s[i_s]:.4f}→{shrd_n[i_n]:.4f} mm "
            f"(Δ={shrd_n[i_n]-shrd_s[i_s]:+.4f}), "
            f"x={x_stage_s[i_s]:.1f}/{x_stage_n[i_n]:.1f} mm",
            context="global_annulus")

# def init_channel_data(compressor_gui_data):
#     '''
#     Defining variables from the channel function for further use

#     '''
#     global channel_data
#     channel_data = {}
#     cumulative_x_offset = 0.0

#     for s in range(1, compressor_gui_data.stages_to_calc + 1):
#         compressor_gui_data.stage = s
#         x_values_s, r_values_s, m_prime_values_s, x0_s = channel(compressor_gui_data)

#         x0_s = list(x0_s)

#         if cumulative_x_offset != 0.0:
#             # ── shift every x-coordinate into the global frame ──────────────
#             # x0: the 9 spline control points
#             x0_s = [x + cumulative_x_offset for x in x0_s]

#             # x_values and m_prime_values: one list per span height (h_H)
#             for k in range(len(x_values_s)):
#                 x_values_s[k]      = [v + cumulative_x_offset for v in x_values_s[k]]
#                 m_prime_values_s[k] = [v + cumulative_x_offset for v in m_prime_values_s[k]]
#             # r_values are radii – they are NOT shifted

#         channel_data[s] = {
#             'x_values':       x_values_s,
#             'r_values':       r_values_s,
#             'm_prime_values': m_prime_values_s,
#             'x0':             x0_s,
#         }

#         cumulative_x_offset = x0_s[7]

#         print(f"Stage {s}: channel stored. "
#               f"x0[1]={x0_s[1]:.1f} mm  x0[7]={x0_s[7]:.1f} mm  "
#               f"→ next offset = {cumulative_x_offset:.1f} mm")

#     #x_values, r_values, m_prime_values, x0 = channel(compressor_gui_data)
