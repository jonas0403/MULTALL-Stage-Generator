# ------------------------------------------------------------------
# File:    source/core/grid/writers.py
# Author:  Luca De Francesco, Jonas Scholz
# Purpose: MULTALL .dat writer functions (head/section/end blocks, bleed cards).
# ------------------------------------------------------------------

import matplotlib.pyplot as plt
import numpy as np
import source.core.stage.stage_calculation as Stage
from source.logging import debug_log


# Writes values in blocks of 8 per line to the file
# [SA/ILOS] viscous-model selector (Card 28): 200 = Spalart-Allmaras iff the SA
# checkbox is on (Grid_data.SA_mode, roundtripped via JSON); else legacy 10.
# NLOS/IBOUND stay at doc defaults (5/0). Defensive: default = current behavior.
def _ilos_from_gui(CompressorGui):
    try:
        gd = getattr(CompressorGui, "prepop_grid_data", None) or {}
        if isinstance(gd, dict) and gd.get("SA_mode", False):
            return 200
    except Exception:
        pass
    return 10


def write_values_in_block(section, liste, file_handle, JM):
    if section >= len(liste):
        data = [0.0] * JM  # Initializes a list of zeros with length JM
    else:
        data = list(liste[section])
    
    for i in range(len(data)):
        if not np.isfinite(data[i]):
            error_msg = f"Invalid value at position {i} in sequence {section}: {data[i]}. Setting to 1e-6."
            print(error_msg)
            debug_log.debug(error_msg, context="write_values_in_block")
            data[i] = 1e-6
    
    if len(data) < JM:
        data += [0.0] * (JM - len(data))  # Pads the list with zeros if shorter than JM
    
    elif len(data) > JM:
        data = data[:JM]
    
    for k in range(0, JM, 8):
        chunk = data[k:k+8]  # Takes 8 elements at once
        line = " " +"".join(f"{element:12.6f}" for element in chunk) + "\n"
        file_handle.write(line)  # Writes the line to the file
      
def grid_adaption(grid_count, max=20, beta=2 ): # Generates grid spacings based on count
    x_norm = np.linspace(0.0, 1.0, grid_count) # Creates a list from 0 to 1 with grid_count points
    x_stretched = 0.5 * (1.0 + np.tanh(beta *(2.0 * x_norm - 1.0))) / np.tanh(beta) # Maximum grid spacing is 20
    #return x_stretched[::-1] * (grid_count-1) + 1.0 # Reverses the array and scales to grid_count
    
    spacings = np.diff(x_stretched) # Calculates the distances between points
    min_val = np.min(spacings)
    max_val = np.max(spacings)
    
    if (max_val - min_val) < 1e-9:
        return np.ones_like(spacings)  # If all spacings are equal, returns ones to avoid MULTALL errors
    
    scaled_spacings = 1 + (max - 1.0) * (spacings - min_val) / (max_val - min_val) # Scales spacings to range 1 to max
    scaled_spacings = np.nan_to_num(scaled_spacings, nan=0.0,posinf=0.0, neginf=0.0)
    
    return scaled_spacings

def create_bleed_air_card(file_path, patches_data, current_stage):
    
    stage_key = f"Stage {current_stage}"
    
    # Filter patches for this stage only
    stage_patches = [patches for patches in patches_data if patches[0] == stage_key]
    
    debug_log.debug(f"file_path={file_path}, stage_key={stage_key}, matches={len(stage_patches)}", context="create_bleed_air_card")
    with open(file_path, "a") as file:
        # One NBLEED per call (one blade row)
        file.write("NBLEED\n")
        file.write(f"{len(stage_patches)}\n")
        for patches in stage_patches:
            file.write('\t'.join(str(p) for p in patches[1:]) + '\n')
    
    '''
    # Filter patches for current stage 
    stage_key = f"Stage {current_stage}"
    
    # index 0 is stage string, rest are coords and mflow
    rotor_stage_patches = [patches for patches in rotor_data if patches[0] == stage_key]
    stator_stage_patches = [patches for patches in stator_data if patches[0] == stage_key]
    
    # Nbleed needs to be written for each row in each stage 
    print(f"file_path = {file_path}")
    with open(file_path, "a") as file:
        # Rotor NBLEED always written
        file.write("NBLEED\n")
        file.write(f"{len(rotor_stage_patches)}\n")
        for patches in rotor_stage_patches:
            file.write('\t'.join(str(p) for p in patches[1:])+ '\n')
            
        # Stator NBLEED needs to be writte if NROW != 1
        if NROW != 1:
            file.write("NBLEED\n")
            file.write(f"{len(stator_stage_patches)}\n")
            for patches in stator_stage_patches:
                file.write('\t'.join(str(p) for p in patches[1:])+ '\n')
    '''
    
    # Old bleed air card writing. Not usuable for multistage purposes
    '''
    print(f"file={file}")
    with open(file, "a") as file:
        if len(rotor_data) != 0 or len(stator_data) != 0:
            file.write("NBLEED\n")
            file.write(f"{len(rotor_data)}\n")
            for patches in rotor_data:
                file.write('\t'.join(patches)+ '\n')
            # Write Stator Bleedair Patches in NROW != 1
            if NROW != 1:
                file.write("NBLEED\n")
                file.write(f"{len(stator_data)}\n")
                for patches in stator_data:
                    file.write('\t'.join(patches)+ '\n')
    '''
## MULTALL .dat file writing
# Needs to be looped or called multiple times for each section IN EACH stage
def multall_grid_data_head_row(file_path, NSEC, row, JLE, JM, JTE, KM, tip_clearance, levels, CompressorGui, RPM, row_num, current_stage_num):
    section = 0
    
    current_stage = current_stage_num - 1
    debug_log.debug(f"current_stage (idx) = {current_stage}", context="multall_grid_data_head_row")
    debug_log.debug(f"current_stage_num = {current_stage_num}", context="multall_grid_data_head_row")
    
    global_row_num = row_num - 1
    debug_log.debug(f"global_row_num (idx) = {global_row_num}", context="multall_grid_data_head_row")
    debug_log.debug(f"global_row = {row_num}", context="multall_grid_data_head_row")
    
    
    ktipstart = 0
    ktipend = 0
    actual_tip_clearance = 0.0
    debug_log.debug(f"current_stage value = {current_stage}, type = {type(current_stage)}", context="multall_grid_data_head_row")
    if tip_clearance[current_stage] > 0:
        if row_num %2 != 0:
            ktipstart = KM - 4
            ktipend = KM
            actual_tip_clearance = tip_clearance[current_stage]
        else:
            ktipstart = 0
            ktipend = 0

    if tip_clearance[current_stage] == 0:
        ktipstart = 0
        ktipend = 0

    # Q3D mode uses KM=2 which gives ktipstart=KM-4=-2 (invalid for MULTALL)
    if KM < 4:
        ktipstart = 0
        ktipend = 0
        actual_tip_clearance = 0.0

    if section == 0:
        if row_num % 2 != 0:  # Odd rows = rotor
            x = round(Stage.p_1[current_stage], 1)
            y = round(Stage.p_2[current_stage], 1)
            z = RPM[0] #  rpm can stay 0 bceause rpm is const over stages
            blades = Stage.z_R[current_stage]
        else: # even rows = stator
            x = round(Stage.p_2[current_stage], 1)
            y = round(Stage.p_3[current_stage], 1)
            z = 0.0
            blades = Stage.z_S[current_stage]
    '''
    # section = 0 is hardcoded so this can be ignored
    # Dont delete incase of changing away from hardcoded section definition
    else:
        if row == 1:
            i = levels[section-1]
            for j in range(len(Stage.h_rel)):
                if round(Stage.h_rel[j],2) == i:
                    x = round(Stage.p_R_in[j], 1)
                    y = round(Stage.p_R_out[j], 1)

            z = Stage.RPM[0]
            blades = Stage.z_R[0]
        elif row == 2:
            i = levels[section-1]
            for j in range(len(Stage.h_rel)):
                if round(Stage.h_rel[j],2) == i:
                    x = round(Stage.p_S_in[j], 1)
                    y = round(Stage.p_S_out[j], 1)
            
            blades = Stage.z_S[0]
            z = 0.0
    '''
    with open(file_path, "a") as file:
        file.write(" ***************************************************************\n")
        file.write(" ************STARTING THE INPUT FOR EACH BLADE ROW**************\n")
        file.write(f"  BLADE ROW NUMBER =        {global_row_num + 1}                                           \n")
        file.write("    NUMBER OF BLADES IN ROW \n")
        file.write(f"        {blades}\n")                                       
        file.write("        JM        JLE       JTE \n")
        file.write(f"        {JM}        {JLE}        {JTE}\n")
        file.write("      KTIPSTART  KTIPEND \n")
        file.write(f"         {ktipstart}         {ktipend}\n")
        if ktipstart > 0:
            
            file.write("  FRACTIP1,     FRACTIP2 \n")
            file.write(f"  {actual_tip_clearance:.8f}       {actual_tip_clearance:.8f}\n")
        
            file.write("  FTHICK(K) \n")
            ftchick_values = [1.0] * KM
            if tip_clearance[current_stage] > 0:
                ftchick_values[ktipstart-2] = 0.9
                ftchick_values[ktipstart-1] = 0.5
            for k in range(ktipstart, KM):
                ftchick_values[k] = 0.0
            
        
            for i in range(0, KM, 8): # Counts in steps of 8
                line_number = ftchick_values[i:i+8] # Gets intermediate values from the grid distribution
                file.write(" ".join(f"{value:.6f}" for value in line_number) + "\n") # Writes the constructed line
        
        file.write("       BOUNDARY LAYER TRANSITION POINTS \n")
        file.write("         0         0         0         0\n")
        file.write("  SET NEWGRID= 1 TO GENERATE A NEW GRID WITH DIFFERENT \"J\" POINTS AND SPACINGS.\n")
        file.write("         0\n")
        file.write("   RPMROW,    RPMHUB \n")
        file.write(f"    {z}    {z}\n")
        file.write("       JROTHS    JROTHE    JROTTS    JROTTE \n")
        file.write("         1         1         1         1\n")
        file.write("   PUPROW    PLEROW   PTEROW    PDROW \n")
        file.write(f"   {x}   {x}   {y}  {y}\n")
        file.write("      NSECS_ROW   INSURF  \n")
        file.write(f"         {NSEC}         0\n")
        file.write("  IF_CUSP   IFANGLES \n")
        file.write("         0         0\n")
    
def write_head_file(KM_grid_density, IM_grid_density, file_path, section, NROW, NSEC, Q3D_value, enable_bleed_air, CompressorGui):
    if enable_bleed_air == True:
        bleed_air = 1
    else: 
        bleed_air = 0 
    with open(file_path, "w+") as file:
        file.write(" DATA SET FOR \"multall\" . GENERATED BY \"stagen\" .                       \n")
        file.write("    CP   and   GAMMA \n")
        file.write(f" {Stage.cp}    {Stage.kappa}\n")
        file.write("       ITIMST \n")
        file.write("         3\n")
        file.write("     CFL,    DAMP,    MACHLIM,    F_PDOWN \n")
        file.write("  0.320000 9.000000  2.000000  0.000000\n")
        file.write("  IF_RESTART \n")
        file.write("         0\n")
        file.write("  NSTEPS_MAX, CONLIM\n")
        if CompressorGui.stages_to_calc > 1:
            file.write("      12000  0.007500\n") # Documentation calls for more steps in multistage applications
        elif section == 0:
            file.write("      9000  0.006000\n")
        else: 
            file.write("      60000  0.005000\n")
        file.write("   SFX,      SFT,      FAC_4TH,     NCHANGE \n")
        file.write("  0.005000  0.005000  0.800000      1000\n")
        file.write("       NUMBER OF BLADE ROWS \n")# Number of blades in row?
        file.write(f"         {CompressorGui.stages_to_calc * NROW}\n")
        file.write("        IM        KM \n")
        
        if section == 0:
            file.write(f"        {IM_grid_density}        {KM_grid_density}\n")
        else:
            file.write(f"        {IM_grid_density}        2\n")
            
        value_IM = grid_adaption(IM_grid_density)
        file.write("  FP(I),I=1,IMM1 \n")
        for i in range(0, len(value_IM), 8): # Counts in steps of 8
            chunk = value_IM[i:i+8] # Gets intermediate values from the grid distribution
            line_value = " " # Inserts a leading space
            for value in chunk:
                line_value += f"{value:.6f} " # Adds 8 numbers with 6 decimal places
            line_value += "\n" # Adds a newline
            file.write(line_value) # Writes the constructed line
        
        if section == 0 and not Q3D_value:        
            value_KM = grid_adaption(KM_grid_density)
            file.write("  FR(K),K=1,KMM1 \n")
            for i in range(0, len(value_KM), 8): # Counts in steps of 8
                chunk = value_KM[i:i+8] # Gets intermediate values from the grid distribution
                line_value = " " # Inserts a leading space
                for value in chunk:
                    line_value += f"{value:.6f} " # Adds 8 numbers with 6 decimal places
                line_value += "\n" # Adds a newline
                file.write(line_value) # Writes the constructed line        
        else: # Sets FR to 1 when Q3D is active or only one row exists
             file.write("  FR(K),K=1,KMM1 \n")
             file.write("  1.000000\n")

        file.write("        IR        JR        KR        IRBB      JRBB      KRBB \n")
        if Q3D_value:
            file.write("         3         3         1         9         9         1\n")
        else:
            file.write("         3         3         3         9         9         9\n")
        file.write("   FBLK1,     FBLK2,     FBLK3  \n")
        file.write("  0.400000  0.200000  0.100000\n")
        file.write("       IFMIX \n")
        file.write("         1\n")
        file.write("   RFMIX,    FEXTRAP,   FSMTHB,    FANGLE \n")
        file.write("  0.020000  0.800000  1.000000  0.800000\n")
        file.write("      IFCOOL    IFBLEED    IF_ROUGH \n")
        file.write(f"         0         {bleed_air}         0\n")
        file.write("       NSECS_IN \n")
        file.write(f"         {NSEC}\n")
        file.write("       IN_PRESS  IN_VTAN   IN_VR    IN_FLOW  IF_REPEAT  RFIN \n")
        file.write("         0         0         1         0         0   0.50000\n")
        file.write("  IPOUT  SFEXIT  NSFEXIT \n")
        file.write("    1  0.000000    0\n")
        file.write("  PLATE_LOSS  THROTTLE_EXIT \n")
        file.write("  0.000000  0.000000\n")
        file.write("        ILOS      NLOS      IBOUND \n")
        # [SA/ILOS] 200 = Spalart-Allmaras when SA checkbox on, else legacy 10.
        file.write(f"        {_ilos_from_gui(CompressorGui):d}         5         0\n")
        file.write("   REYNO,     RF_VIS,   FTRANS, TURBVIS_LIM, PRANDTL, YPLUSWALL\n")
        if CompressorGui.stages_to_calc >1:
            file.write("  800000.0     0.500     0.000  3000.000       1.0     0.000\n") #  The doc explicitly states: "higher values, up to 3000, may be necessary in multistage machines." 
        else:
            file.write("  800000.0     0.500     0.000  1000.000       1.0     0.000\n")
        # [SA/ILOS] Card 30 (S-A source-term multipliers) exists ONLY for ILOS=200.
        # Doc defaults: STMIX 0.0, ST0/ST1/ST2/ST3 1.0, SFVIS 2.0, VORT/PGRAD 1.0.
        if _ilos_from_gui(CompressorGui) == 200:
            file.write("   FAC_STMIX, FAC_ST0, FAC_ST1, FAC_ST2, FAC_ST3, FAC_SFVIS, FAC_VORT, FAC_PGRAD \n")
            file.write("   0.000000  1.000000  1.000000  1.000000  1.000000  2.000000  1.000000  1.000000\n")
        file.write("   YPLAM      YPTURB \n")
        file.write("  5.000000 25.000000\n")
        file.write("      ISHIFT    NEXTRAP_LE  NEXTRAP_TE \n")
        file.write("         2        10        10\n")
        file.write("  (NSTG(N),N=1,NROWS) \n")
        
        nstg_values = " ".join([str((i // NROW) + 1) for i in range(CompressorGui.stages_to_calc * NROW)])
        
        file.write(nstg_values + "\n")
        file.write("  5  TIME STEPS FOR PRINTOUT \n")
        file.write("      9000      9000      9000      9000      9000\n")
        file.write("  MARKER FOR VARIABLES TO BE SENT TO THE OUTPUT FILE.\n")
        file.write(" 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")
        file.write("  STREAM SURFACES ON WHICH RESULTS ARE TO BE SENT TO   THE OUTPUT FILE \n")
        file.write(" ".join(f"0  " for _ in range(KM_grid_density)) + "\n")
        

# Writes the coordinates of all sections to a file for MULTALL
# MULTALL section geometry writer for a blade row.
# MULTALL format expects per section (confirmed by 10stg-compr-17.4.dat reference):
#   1. x-coordinates
#   2. FAC1=1.0 XSHIFT=0.0
#   3. Upper surface R*theta
#   4. FAC2=1.0 TSHIFT=0.0
#   5. Blade tangential thickness d (= upper - lower), ZERO upstream/downstream of blade
#   6. FAC3=1.0
#   7. r-coordinates
#   8. FAC4=1.0 RSHIFT=0.0
#
# NOTE: Card 63 must be BLADE TANGENTIAL THICKNESS d, NOT the lower surface R*theta.
# MULTALL computes lower_surface = upper_surface - d internally, then derives
# passage width = pitch - d. Writing the lower surface directly makes MULTALL
# interpret (rtheta - d) as a huge "thickness" exceeding pitch, causing NaN.
def write_coordinates(x, rtheta, d, r, file, row, a, b, JM, global_row_num, current_stage):
    with open(file, "a") as file:
        for i in range(a, b):       
            file.write(" ***************************************************************\n")
            file.write(f"  ROW NUMBER           {row}  SECTION NUMBER            {i+1}\n           0           0           0  IF_DESIGN etc \n   1.00000   0.00000    0\n")
            write_values_in_block(i, x, file, JM)
            file.write("  1.000000  0.000000\n")
            write_values_in_block(i, rtheta, file, JM)
            file.write("  1.000000\n")
            write_values_in_block(i, d, file, JM)
            file.write("  1.000000  0.000000\n")
            write_values_in_block(i, r, file, JM)
            
# writes information for Q3D calculation
# MULTALL expects Q3D data after each blade row's last section.
# Format matched to the Session 10 format that produced correct MULTALL output.
def Q3D_information(file_handle):
    file_handle.write("  DATA FOR STREAM SURFACE THICKNESS\n")
    file_handle.write("   1.00000000      Q3DFORCE\n")
    file_handle.write("           5  A UNIFORM  SS THICKNESS IS INITIALLY SET\n")
    file_handle.write("   0.00000000      0.250000000      0.500000000      0.750000000      1.00000000\n")
    file_handle.write("   1.00000000      1.00000000      1.00000000      1.00000000      1.00000000\n")     

def write_end_file(total_rows, file, section, KM, levels, CompressorGui, radial_data_R, radial_data_S):
    """
    Writes the inlet boundary conditions, exit pressure (PDOWN), and mixing length 
    limits for the MULTALL grid file. Refactored to pull from Stage module.
    """
    # Identify the last stage to set the exit backpressure (PDOWN)
    last_stg_idx = CompressorGui.stages_to_calc
    
    debug_log.debug(f"Starting write_end_file for {total_rows} rows. Last stage index: {last_stg_idx}", context="write_end_file")

    try:
        # 1. Get Inlet Boundary Conditions (from global Stage module)
        # These was causing the AttributeError when called on CompressorGui
        t_inlet = round(Stage.T_t1[0], 4)
        p_inlet = round(Stage.p_t1[0], 1)
        um_inlet = round(Stage.cm1[0], 4)
        
        debug_log.debug(f"Inlet data loaded -> P:{p_inlet}, T:{t_inlet}", context="write_end_file")

        # 2. Get Exit Boundary Conditions (PDOWN) from the last stage
        if last_stg_idx in radial_data_S:
            last_stg_data = radial_data_S[last_stg_idx]
            p_out_array = last_stg_data['p_S_out']
            debug_log.debug(f"Pulling PDOWN from Stator {last_stg_idx}", context="write_end_file")
        elif last_stg_idx in radial_data_R:
            last_stg_data = radial_data_R[last_stg_idx]
            p_out_array = last_stg_data['p_R_out']
            debug_log.debug(f"Pulling PDOWN from Rotor {last_stg_idx}", context="write_end_file")
        else:
            raise KeyError(f"Stage {last_stg_idx} not found in radial data")

        p_exit_hub = round(p_out_array[0], 1)
        p_exit_tip = round(p_out_array[-1], 1)

    except (KeyError, IndexError, AttributeError) as e:
        debug_log.debug(f"Error accessing stage data: {e}. Using safety fallbacks.", context="write_end_file")
        # Engineering fallbacks to prevent crash
        p_exit_hub, p_exit_tip = 101325.0, 101325.0
        t_inlet, p_inlet, um_inlet = 288.15, 101325.0, 150.0

    with open(file, "a", encoding='ascii') as f:
        if section == 0:
            f.write("  STARTING INLET BOUNDARY CONDITION DATA .\n")
            f.write("  NUMBER OF POINTS FOR INLET BOUNDARY CONDITIONS \n")
            f.write(f"        {KM}\n") 
            f.write("  SPACING OF INLET BOUNDARY CONDITION POINTS \n")
            
            value_KM = grid_adaption(KM)
            for i in range(0, len(value_KM), 8):
                f.write(" ".join(f"{v:.6f}" for v in value_KM[i:i+8]) + "\n")
            
            f.write("   INLET STAGNATION PRESSURES \n")
            for i in range(0, KM, 8):
                f.write(" ".join(f"{p_inlet:.6f}" for _ in range(KM)[i:i+8]) + "\n")
            
            f.write("   INLET STAGNATION TEMPERATURES \n")
            for i in range(0, KM, 8):
                f.write(" ".join(f"{t_inlet:.6f}" for _ in range(KM)[i:i+8]) + "\n")
            
            f.write("   INLET ABSOLUTE TANGENTIAL VELOCITY \n")
            for i in range(0, KM, 8):
                f.write(" ".join(f"0.000000" for _ in range(KM)[i:i+8]) + "\n")
            
            f.write("   INLET MERIDIONAL VELOCITY \n")
            for i in range(0, KM, 8):
                f.write(" ".join(f"{um_inlet:.6f}" for _ in range(KM)[i:i+8]) + "\n")
            
            f.write("   INLET MERIDIONAL YAW ANGLE \n")
            for i in range(0, KM, 8):
                f.write(" ".join(f"0.000000" for _ in range(KM)[i:i+8]) + "\n")
            
            f.write("   INLET PITCH ANGLE \n")
            for i in range(0, KM, 8):
                f.write(" ".join(f"0.000000" for _ in range(KM)[i:i+8]) + "\n")
            
            f.write("   PDOWN_HUB   PDOWN_TIP \n")
            f.write(f"  {p_exit_hub}  {p_exit_tip}\n")
            
            f.write(" MIXING LENGTH LIMITS ON ALL BLADE ROWS\n")
            # [SA/ILOS] ILOS=10 -> Card 83 (legacy block, unchanged); ILOS=100/200 ->
            # Card 84: XLLIM_IN/LE/TE/DN, FSTURB, TURBVIS_DAMP (doc defaults, uniform rows).
            if _ilos_from_gui(CompressorGui) == 10:
                # Loop for NROW (total blade rows)
                for _ in range(total_rows):
                    f.write("  0.030000  0.030000  0.030000  0.030000  0.030000  0.020000\n")
            else:
                for _ in range(total_rows):
                    f.write("  0.020000  0.030000  0.040000  0.050000  1.000000  0.500000\n")
            
            f.write("  FACTOR TO INCREASE THE TURBULENT VISCOSITY OVER THE FIRST NMIXUP STEPS \n")
            f.write("   2.00000 1000\n")
            
        else:
            # Fallback for alternative grid sections
            f.write("STARTING INLET BOUNDARY CONDITION DATA .\n")
            f.write("  NUMBER OF POINTS FOR INLET BOUNDARY CONDITIONS \n")
            f.write("         2\n")
            f.write("  SPACING OF INLET BOUNDARY CONDITION POINTS \n")
            f.write("  1.000000\n")
            f.write("   INLET STAGNATION PRESSURES \n")
            f.write(f"  {p_inlet} {p_inlet}\n")
            f.write("   INLET STAGNATION TEMPERATURES \n")
            f.write(f"  {t_inlet} {t_inlet}\n")
            f.write("   INLET ABSOLUTE TANGENTIAL VELOCITY \n")
            f.write("    0.0000 0.0000\n")
            f.write("   INLET MERIDIONAL VELOCITY\n")
            f.write(f"  {um_inlet} {um_inlet}\n")
            f.write("   INLET MERIDIONAL YAW ANGLE\n")
            f.write("    0.0000 0.0000\n")
            f.write("   INLET PITCH ANGLE\n")
            f.write("    0.0000 0.0000\n")
            f.write("   PDOWN_HUB   PDOWN_TIP\n")
            f.write(f"  {p_exit_hub}  {p_exit_tip}\n")
            
            f.write(" MIXING LENGTH LIMITS ON ALL BLADE ROWS\n")
            # [SA/ILOS] ILOS=10 -> Card 83 (legacy block, unchanged); ILOS=100/200 ->
            # Card 84: XLLIM_IN/LE/TE/DN, FSTURB, TURBVIS_DAMP (doc defaults, uniform rows).
            if _ilos_from_gui(CompressorGui) == 10:
                for _ in range(total_rows):
                    f.write("  0.030000  0.030000  0.030000  0.030000  0.030000  0.020000\n")
            else:
                for _ in range(total_rows):
                    f.write("  0.020000  0.030000  0.040000  0.050000  1.000000  0.500000\n")
            
            f.write("  FACTOR TO INCREASE THE TURBULENT VISCOSITY OVER THE FIRST NMIXUP STEPS\n")
            f.write("   2.00000 1000\n")

# Plotting:

