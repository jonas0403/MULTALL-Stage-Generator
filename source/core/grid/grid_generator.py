# ------------------------------------------------------------------
# File:    source/core/grid/grid_generator.py
# Author:  Luca De Francesco
# Purpose: Grid-generation orchestration (MULTALL .dat assembly).
# ------------------------------------------------------------------

import os
import source.core.stage.stage_calculation as Stage
from source.core.stage.section_general import calculation_of_section
from source.core.stage.blade_coordinates import calc_blade_row_coordinates
import json
from source.logging import debug_log
from source.core.grid.writers import (Q3D_information, create_bleed_air_card,
                                     multall_grid_data_head_row, write_coordinates,
                                     write_end_file, write_head_file)

#from old.stage_calculation import NROW


def generate_var_grid_data(nrow, IM_grid_density, KM_grid_density, JM_grid_density, inlet_percentage, outlet_percentage, reference_chord_length, levels, CompressorGui):
    
    # List to store results for each blade row
    all_rows_grid_data = []
    all_rows_data_plot = []

    # Variable to calc which rows will be calculated
    nrow_wert = nrow * CompressorGui.stages_to_calc

    grid_param_msg = (
        f"Grid params: IM={IM_grid_density} KM={KM_grid_density} "
        f"JM_ref={JM_grid_density} ref_chord={reference_chord_length}mm "
        f"inlet={inlet_percentage*100:.0f}% outlet={outlet_percentage*100:.0f}% "
        f"total_rows={nrow_wert}"
    )
    print(grid_param_msg)
    debug_log.debug(grid_param_msg, context="generate_var_grid_data")
    
    for row_num in range(1, nrow_wert + 1):
        status_msg = f"Processing blade row {row_num} (Density: {JM_grid_density})"
        print(f"\n{status_msg}")
        debug_log.debug(status_msg, context="generate_var_grid_data")

        # Checks blade size at 50% span and compares with reference value
        actual_chord, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = calculation_of_section(0.5, row_num)
        
        chord_msg = f"Chord length for row {row_num}: {actual_chord:.2f} mm"
        print(chord_msg)
        debug_log.debug(chord_msg, context="generate_var_grid_data")

        JM_dynamic = int(round((actual_chord / reference_chord_length) * JM_grid_density))
        
        # Dynamic calculation of grid points at inlet and outlet
        n_max_in = int(round(JM_dynamic * inlet_percentage))
        j_prime_max = JM_dynamic
        n_max_out = int(round(JM_dynamic * outlet_percentage))
        
        JLE = n_max_in
        JTE = n_max_in + j_prime_max - 1
        JM = n_max_in + n_max_out + j_prime_max - 2
        
        if row_num % 2 != 0:
            JM_dynamic_rotor = JM_dynamic
        else:
            JM_dynamic_stator = JM_dynamic
        dynamic_msg = f"Dynamic grid points (blade only): {JM_dynamic}"
        print(dynamic_msg)
        debug_log.debug(dynamic_msg, context="generate_var_grid_data")
        points_msg = f"Total points (JM): {JM}, Inlet index (JLE): {JLE}, Outlet index (JTE): {JTE}"
        print(points_msg)
        debug_log.debug(points_msg, context="generate_var_grid_data")
        i_o_msg = f"Inlet points: {n_max_in}, Outlet points: {n_max_out}"
        print(i_o_msg)
        debug_log.debug(i_o_msg, context="generate_var_grid_data")
        
        x_new, d_new, R_new, Rtheta_new = calc_blade_row_coordinates(
            row=row_num, 
            j_prime_max=JM_dynamic, 
            num_planes=5, 
            n_max_in=n_max_in, 
            l_inlet=1, 
            n_max_out=n_max_out, 
            l_outlet=1, 
            Z_H=0.05, 
            Z_S=0.95, 
            levels=levels)
        
        
        debug_log.debug(f"row_num={row_num}: x_new[0][0]={x_new[0][0]:.4f}, x_new[0][-1]={x_new[0][-1]:.4f}, R_new[0][0]={R_new[0][0]:.6f}", context="generate_var_grid_data")
        # x_new_plot, d_new_plot, R_new_plot, Rtheta_new_plot = Stage.calc_blade_row_coordinates(
        #     row=row_num, 
        #     j_prime_max=j_prime_max_plot, 
        #     num_planes=5, 
        #     n_max_in=n_max_in, 
        #     l_inlet=1, 
        #     n_max_out=n_max_out, 
        #     l_outlet=1, 
        #     Z_H=0.05, 
        #     Z_S=0.95, 
        #     levels=[h_H_plot]
        # )
        
        # Store the calculated data for this row
        all_rows_grid_data.append({
            'row_num': row_num,
            'x_new': x_new,
            'd_new': d_new,
            'R_new': R_new,
            'Rtheta_new': Rtheta_new,
            'JM': JM,
            'JLE': JLE,
            'JTE': JTE,
            'IM': IM_grid_density,
            'KM': KM_grid_density,
            'JM_dynamic': JM_dynamic
        })
        
        # all_rows_data_plot.append({
        #     'row_num': row_num,
        #     'x_new': x_new_plot,
        #     'd_new': d_new_plot,
        #     'R_new': R_new_plot,
        #     'Rtheta_new': Rtheta_new_plot
        # })
    
    return all_rows_grid_data


def validate_bezier_data(all_json_data):
    # [Guardrail] fail fast on degenerate blade profiles (garbage Bezier data once caused
    # silent ZeroDivision crashes and 400k-negative-volume solver runs). Calibrated on clean
    # template data: max spanwise CP jump 20.45 deg -> limit 30; GUI slider envelope [0, 170].
    # JSON-only opt-out (NOT in GUI): Grid_data.suppress_blade_check = true.
    grid = all_json_data.get("Grid_data", {}) or {}
    if grid.get("suppress_blade_check", False):
        debug_log.debug("Blade profile check suppressed via suppress_blade_check.",
                        context="blade_check")
        return
    store = all_json_data.get("Bezier_point_data")
    if not store:
        raise ValueError("Blade profile check failed: no Bezier_point_data in JSON. "
                         "Generate profiles via Create Default Profiles first.")
    keys = [k for k in store if k.startswith("rotor_stage_") or k.startswith("stator_stage_")
            or k in ("rotor", "stator")]
    if not keys:
        raise ValueError("Blade profile check failed: no rotor/stator stage data in "
                         "Bezier_point_data. Generate profiles via Create Default Profiles first.")
    hint = "Regenerate via Create Default Profiles (or set Grid_data.suppress_blade_check=true)."
    for key in sorted(keys):
        b = store.get(key) or {}
        angle_key = "beta_S" if "rotor" in key else "alpha_S"
        for param, need_len in ((angle_key, 20), ("d/l", 20)):
            vals = b.get(param)
            if not isinstance(vals, list) or len(vals) != need_len:
                raise ValueError(f"Blade profile check failed: {key}/{param} must hold 20 numbers. " + hint)
            try:
                nums = [float(v) for v in vals]
            except (TypeError, ValueError):
                raise ValueError(f"Blade profile check failed: {key}/{param} holds non-numeric data. " + hint)
            if any(v != v or v in (float("inf"), float("-inf")) for v in nums):
                raise ValueError(f"Blade profile check failed: {key}/{param} holds NaN/Inf. " + hint)
            if param == "d/l":
                if any(v <= 0 for v in nums):
                    raise ValueError(f"Blade profile check failed: {key}/d/l holds non-positive thickness. " + hint)
            else:
                if any(v < 0 or v > 170 for v in nums):
                    bad = next(v for v in nums if v < 0 or v > 170)
                    raise ValueError(f"Blade profile check failed: {key}/{param} angle {bad:.2f} outside [0, 170]. " + hint)
                for cp in range(4):
                    col = [nums[cp * 5 + s] for s in range(5)]
                    jump = max(abs(col[s + 1] - col[s]) for s in range(4))
                    if jump > 30.0:
                        raise ValueError(f"Blade profile check failed: {key}/{param} control point {cp + 1} jumps {jump:.1f} deg across sections (limit 30). " + hint)
        ms = b.get("m*")
        if ms is not None:
            try:
                mn = [float(v) for v in ms]
            except (TypeError, ValueError):
                raise ValueError(f"Blade profile check failed: {key}/m* holds non-numeric data. " + hint)
            if any(v < 0 or v > 1 for v in mn) or any(mn[k + 1] < mn[k] for k in range(len(mn) - 1)):
                raise ValueError(f"Blade profile check failed: {key}/m* must rise 0..1. " + hint)
    debug_log.debug("Blade profile check passed.", context="blade_check")


def process_grid_data(json_path, CompressorGui):
    '''
    Multistage LOGIC :
    # 1. Write once
        write_head_file(...)

    # 2. Loop over rows
        for row in all_rows_grid_data:
            multall_grid_data_head_row(...)   # row header
            write_coordinates(...)             # geometry sections
            if enable_bleed_air:
                create_bleed_air_card(...)     # bleed cards per row # Here will be issues at the moment bleed is only working for first stage

    # 3. Write once at the end
        write_end_file(NROW, ...)   # inlet BCs + mixing length limits
    # Note: Q3D data is written inside the per-row loop (after write_coordinates),
    # NOT at the end of file. See line ~926.
    '''
    
    
    
    """
    Receives data from the main GUI, unpacks it and
    starts the grid generation (MULTALL .dat creation).
    """
    unpack_msg = "\n--- Starting to unpack GUI data in grid_generator ---"
    print(unpack_msg)
    debug_log.debug(unpack_msg, context="process_grid_data")
    
    try:
        all_json_data = {}
        
        try:
            with open(json_path, 'r') as file:
                all_json_data = json.load(file)
        
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        grid_data_gui = all_json_data['Grid_data'] 
        meanline_data_gui = all_json_data['Meanline_input_data']
        #thermo_data_gui = all_json_data['Thermo_data']
        Metadata = all_json_data['Metadata']
        bleed_air_data = all_json_data['Bleed_air_data']
        


        
                   
    except ValueError:
        error_msg = "Please enter valid numbers for all conditions."
        print(error_msg)
        debug_log.debug(error_msg, context="process_grid_data")
        
        '''
        Unpacking Grid Data
    
        '''
    # [Guardrail] fail fast with a CLEAR message (moved out of the try above: an
    # inner except ValueError relabeled it "valid numbers" and continued into the crash).
    validate_bezier_data(all_json_data)

    IM_grid_density = int(grid_data_gui['im_selection'])
    KM_grid_density = int(grid_data_gui['km_selection'])
    JM_grid_density = int(grid_data_gui['JM_grid_density'])
    nrow_wert = int(grid_data_gui['nrow'])
    tip_clearance_mm_rotor = float(grid_data_gui['tip_clearance_rotor'])
    Q3D_value = grid_data_gui['Q3D_mode']
    ref_chord_length = float(grid_data_gui['ref_chord_length'])
    inlet_percentage = float(grid_data_gui['inlet_percentage'])
    outlet_percentage = float(grid_data_gui['outlet_percentage'])
    SA_Mode = grid_data_gui['SA_mode']

    RPM = meanline_data_gui['n']
    
    output_path = Metadata['output_folder']
    levels = Metadata['levels']

    # NOTE: debug_log.open_file() is called ONCE in GUI.py:2845 before process_grid_data,
    # so channel init messages from run_main_logic() are preserved in the log.
    debug_log.debug(f"tip_clearance_mm_rotor = {tip_clearance_mm_rotor}, b2 = {CompressorGui.meanline_data['b2']}", context="process_grid_data")
    tip_clearance_multall = [tip_clearance_mm_rotor / x for x in CompressorGui.meanline_data['b2']]


    

    enable_bleed_air = bleed_air_data['enable_bleed_air']
    # [FIX] no patches -> disabled even if the flag is stale (must match save-side rule).
    _n_bleed = int(bleed_air_data.get('rotor_patches', 0) or 0) + int(bleed_air_data.get('stator_patches', 0) or 0)
    if enable_bleed_air and _n_bleed == 0:
        debug_log.debug('Bleed flag on but zero patches: treating as disabled.', context='bleed')
        enable_bleed_air = False
    
    all_rows_grid_data = generate_var_grid_data(nrow_wert, IM_grid_density, KM_grid_density, JM_grid_density, inlet_percentage, outlet_percentage, ref_chord_length, levels, CompressorGui)    
    
    # --- X-RANGE MONOTONICITY CHECK ---
    debug_log.section("X-Range Monotonicity Check")
    prev_max_x = -float('inf')
    all_ok = True
    for data in all_rows_grid_data:
        min_x = min(data['x_new'][0])
        max_x = max(data['x_new'][0])
        status = "OK" if min_x >= prev_max_x - 1e-10 else "*** OVERLAP ***"
        debug_log.debug(f"Row {data['row_num']}: x=[{min_x:.4f}, {max_x:.4f}]  {status}", context="monotonicity")
        if status != "OK":
            all_ok = False
        prev_max_x = max_x
    debug_log.debug(f"Result: {'PASSED' if all_ok else 'FAILED'}", context="monotonicity")
    
    # Old hardcoded first value
    #JM_dynamic_rotor = all_rows_grid_data[0]['JM_dynamic']
    JM_dynamic_rotor = [row['JM_dynamic'] for row in all_rows_grid_data[::2]]
    
    if nrow_wert > 1:
        JM_dynamic_stator = [row['JM_dynamic'] for row in all_rows_grid_data[1::2]]
    else:
        JM_dynamic_stator = 0

    # [FIX output name] user prefix from GUI (manual entry); sanitized, default "grid".
    raw_prefix = str(getattr(CompressorGui, "grid_name_prefix", "grid") or "grid")
    prefix = "".join(c for c in raw_prefix.strip() if c.isalnum() or c in ("_", "-")) or "grid"
    nstages = len(all_rows_grid_data) // max(nrow_wert, 1)  # [FIX output name] compact, filesystem-friendly grid filenames
    n_bleed = int(bleed_air_data.get("rotor_patches", 0) or 0) + int(bleed_air_data.get("stator_patches", 0) or 0)
    suffix = ("_bleed%d" % n_bleed if (enable_bleed_air and n_bleed > 0) else "") + ("_Q3D" if Q3D_value else "") + ("_Ronly" if nrow_wert == 1 else "")
    output_name = f"{prefix}_{nstages}stg_IM_{IM_grid_density}_KM_{KM_grid_density}{suffix}.dat"
        
    full_output_path = os.path.join(output_path, output_name)
    
    NSEC = 1 if Q3D_value else len(levels)

    head_msg = "Writing MULTALL grid data head row..."
    print(head_msg)
    debug_log.debug(head_msg, context="process_grid_data")
    write_head_file(KM_grid_density, IM_grid_density, full_output_path, 0, nrow_wert, NSEC, Q3D_value, enable_bleed_air, CompressorGui)

    
    # Calls grid/row data writing for each blade row across all stages
    for i, data in enumerate(all_rows_grid_data):
        row_num = data['row_num']
        x_coords = data['x_new'] 
        d_coords = data['d_new']
        r_coords = data['R_new']
        rtheta_coords = data['Rtheta_new']
        
        # SAFETY: If r_coords somehow arrive in mm instead of meters (max_r < 0.05),
        # convert to meters. The root cause (channel.py returning r in meters
        # while x in mm) was fixed, so this should not trigger.
        max_r = max(max(sec) for sec in r_coords)
        if max_r < 0.05:
            r_coords = [[val * 1000.0 for val in sec] for sec in r_coords]
        
        JLE = data['JLE']
        JTE = data['JTE']
        JM_row = data['JM']
        NSEC_new = 1 if Q3D_value else len(data['x_new'])

        # Q3D: use mid-span section (closest to 0.5 span) instead of hub (section 0).
        # The hub has the thickest blade and narrowest passage, which can cause the
        # initial flow field calculation to fail in MULTALL's Q3D solver for
        # small-chord stages (e.g., Stage 3 rotor/passage too narrow at hub).
        # Mid-span provides a more representative section for 2D flow initialization,
        # matching what the meanline calculation uses (50% span as reference).
        if Q3D_value:
            q3d_sec = min(range(len(levels)), key=lambda i: abs(levels[i] - 0.5))
            debug_log.debug(f"Q3D mid-span: section idx={q3d_sec} (span={levels[q3d_sec]})", context="process_grid_data")
        else:
            q3d_sec = 0

        # Global row number (1-based across all stages)
        global_row_num = i + 1
        
        # Stage number derived from row index
        current_stage = (i // 2) + 1
        
        debug_log.debug(f"i={i}, row_num={row_num}, current_stage={current_stage}", context="process_grid_data")
        debug_log.debug(f"Row {global_row_num} (stage {current_stage}):", context="process_grid_data")
        debug_log.debug(f"  x_coords first section first point: {x_coords[0][0]:.4f}", context="process_grid_data")
        debug_log.debug(f"  x_coords first section last point:  {x_coords[0][-1]:.4f}", context="process_grid_data")
        debug_log.debug(f"  r_coords first section first point: {r_coords[0][0]:.4f}", context="process_grid_data")
        debug_log.debug(f"  r_coords first section last point:  {r_coords[0][-1]:.4f}", context="process_grid_data")
        debug_log.debug(f"  r_coords LAST section first point: {r_coords[-1][0]:.4f}", context="process_grid_data")
        debug_log.debug(f"  r_coords LAST section last point:  {r_coords[-1][-1]:.4f}", context="process_grid_data")
        debug_log.debug(f"  rtheta_coords first section first point: {rtheta_coords[0][0]:.6f}", context="process_grid_data")
        debug_log.debug(f"  rtheta_coords first section last point:  {rtheta_coords[0][-1]:.6f}", context="process_grid_data")
        debug_log.debug(f"  d_coords first section first point: {d_coords[0][0]:.6f}", context="process_grid_data")
        debug_log.debug(f"  d_coords first section last point:  {d_coords[0][-1]:.6f}", context="process_grid_data")
        
        # BUGFIX VERIFICATION: log passage width before (wrong) and after (correct)
        sec0_rtheta = rtheta_coords[0]
        sec0_d = d_coords[0]
        sec0_r = r_coords[0]
        # Number of blades for this row from meanline data
        if row_num % 2 != 0:
            z_blades = CompressorGui.meanline_data['z_R'][current_stage - 1]
        else:
            z_blades = CompressorGui.meanline_data['z_S'][current_stage - 1]
        # Blade mid index (JM/2) as representative sample
        mid_k = JM_row // 2
        r_mid = sec0_r[mid_k]
        pitch = 2 * 3.14159265 * r_mid / z_blades if z_blades > 0 else 0
        thick = sec0_d[mid_k]
        old_passage = abs(sec0_d[mid_k] - sec0_rtheta[mid_k])  # what MULTALL previously saw
        new_passage = abs((sec0_rtheta[mid_k] - sec0_d[mid_k]) - sec0_rtheta[mid_k])  # what MULTALL now sees = thick
        debug_log.debug(f"  BUGFIX: row {row_num} first section mid: r={r_mid:.4f}, z={z_blades}, pitch={pitch:.6f}, thick={thick:.6f}", context="passage_width")
        debug_log.debug(f"  BUGFIX: OLD block3=d -> MULTALL saw passage width = {old_passage:.6f} (WRONG, should be ~pitch)", context="passage_width")
        debug_log.debug(f"  BUGFIX: NEW block3=rtheta-d -> MULTALL sees thickness = {new_passage:.6f}, pitch-thickness = {pitch - thick:.6f}", context="passage_width")
        
        multall_grid_data_head_row(full_output_path, NSEC_new, row_num, JLE, JM_row, JTE, KM_grid_density, tip_clearance_multall, levels, CompressorGui, RPM, global_row_num, current_stage)
        sec_start = q3d_sec if Q3D_value else 0
        sec_end = (q3d_sec + 1) if Q3D_value else NSEC_new
        write_coordinates(x_coords, rtheta_coords, d_coords, r_coords, full_output_path, row_num, sec_start, sec_end, JM_row, global_row_num, current_stage)
        if Q3D_value:
            with open(full_output_path, "a") as f:
                Q3D_information(f)
                # Do NOT write IF_CUSP/IFANGLES here — that card belongs in the
                # row header (multall_grid_data_head_row). After Q3D data MULTALL
                # returns to the main data loop and expects the next row's Card 51.
        '''
        # possible worng location of bleed air 
        if enable_bleed_air:
            rotor_data = [
                bleed_air_data[f"rotor_patch_{j+1}"] 
                for j in range(bleed_air_data.get('rotor_patches', 0))
                if f"rotor_patch_{j+1}" in bleed_air_data
            ]
            stator_data = [
                bleed_air_data[f"stator_patch_{j+1}"] 
                for j in range(bleed_air_data.get('stator_patches', 0))
                if f"stator_patch_{j+1}" in bleed_air_data
            ]
            
            # call once per row, passing rotor or stator data depending on row type
            if row_num == 1:  # rotor row
                create_bleed_air_card(full_output_path, rotor_data, current_stage)
            else:  # stator row
                create_bleed_air_card(full_output_path, stator_data, current_stage)
        '''
        row_done_msg = f"Grid data for row {row_num} written successfully."
        print(row_done_msg)
        debug_log.debug(row_done_msg, context="process_grid_data")
    '''
    # Maybe placement of bleedair was wrong 
    if enable_bleed_air:
        rotor_data = [
            bleed_air_data[f"rotor_patch_{j+1}"] 
            for j in range(bleed_air_data.get('rotor_patches', 0))
            if f"rotor_patch_{j+1}" in bleed_air_data
        ]
        stator_data = [
            bleed_air_data[f"stator_patch_{j+1}"] 
            for j in range(bleed_air_data.get('stator_patches', 0))
            if f"stator_patch_{j+1}" in bleed_air_data
        ]
        
        # CHANGE: one NBLEED card per blade row, in order rotor then stator per stage
        for i, data in enumerate(all_rows_grid_data):
            row_num = data['row_num']
            current_stage = (i // 2) + 1
            
            if i % 2 == 0:  # rotor
                create_bleed_air_card(full_output_path, rotor_data, current_stage)
            else:  # stator
                create_bleed_air_card(full_output_path, stator_data, current_stage)

    
    # --- INTER-ROW CONTINUITY CHECK ---
    debug_log.section("Inter-Row Continuity Check (matching planes)")
    for j in range(len(all_rows_grid_data) - 1):
        row_a = all_rows_grid_data[j]
        row_b = all_rows_grid_data[j + 1]
        x_prev_max = max(row_a['x_new'][0])
        x_next_min = min(row_b['x_new'][0])
        R_prev_last = row_a['R_new'][0][-1] if row_a['R_new'][0] else -1
        R_next_first = row_b['R_new'][0][0] if row_b['R_new'][0] else -1
        gap = x_next_min - x_prev_max
        R_jump = R_next_first - R_prev_last
        debug_log.debug(f"Row {row_a['row_num']}→{row_b['row_num']}: x_gap={gap:.4f}m  R_jump={R_jump:.4f}m", context="continuity")
        if abs(R_jump) > 0.001:
            debug_log.debug(f"  *** R discontinuity at matching plane: {R_prev_last:.4f} → {R_next_first:.4f} (jump={R_jump:.4f}m)", context="continuity")
    
    '''
    
    endfile_msg = "Starting writing end of file..."
    print(endfile_msg)
    debug_log.debug(endfile_msg, context="process_grid_data")
    
    total_blade_rows = nrow_wert * CompressorGui.stages_to_calc
    
    write_end_file(total_blade_rows, full_output_path, 0, KM_grid_density, levels, CompressorGui, Stage.radial_data_R, Stage.radial_data_S)
    
    done_msg = f"Grid data for all rows written to {full_output_path} successfully."
    print(done_msg)
    debug_log.debug(done_msg, context="process_grid_data")
    all_done_msg = "All tasks completed successfully."
    print(all_done_msg)
    debug_log.debug(all_done_msg, context="process_grid_data")

    
    if enable_bleed_air:
        rotor_data = [
            bleed_air_data[f"rotor_patch_{j+1}"] 
            for j in range(bleed_air_data.get('rotor_patches', 0))
            if f"rotor_patch_{j+1}" in bleed_air_data
        ]
        stator_data = [
            bleed_air_data[f"stator_patch_{j+1}"] 
            for j in range(bleed_air_data.get('stator_patches', 0))
            if f"stator_patch_{j+1}" in bleed_air_data
        ]
        
        # one NBLEED card per blade row, in order rotor then stator per stage
        for i, data in enumerate(all_rows_grid_data):
            row_num = data['row_num']
            current_stage = (i // 2) + 1
            
            if i % 2 == 0:  # rotor
                create_bleed_air_card(full_output_path, rotor_data, current_stage)
            else:  # stator
                create_bleed_air_card(full_output_path, stator_data, current_stage)

    