# Autor: Luca De Francesco
# Skript zur Bachelorarbeit
    

import matplotlib.pyplot as plt
import numpy as np
import os
import Stage_v3_working_with_bleedair as Stage
import json

        

# Schreibt Werte in Blöcken von 8 pro Zeile in die Datei
def write_values_in_block(section, liste, file_handle, JM):
    if section >= len(liste):
        data = [0.0] * JM  # Initialisiert eine Liste mit Nullen der Länge JM
    else:
        data = list(liste[section])
    
    for i in range(len(data)):
        if not np.isfinite(data[i]):
            print(f"Ungültiger Wert an der Stelle {i} in der Reihenfolge {section}: {data[i]}. Dieser Wert wird auf 0.0 gesetzt.")
            data[i] = 1e-6
    
    if len(data) < JM:
        data += [0.0] * (JM - len(data))  # Füllt die Liste auf, falls sie kürzer ist als JM
    
    elif len(data) > JM:
        data = data[:JM]
    
    for k in range(0, JM, 8):
        abschnitt = data[k:k+8]  # Nimmt 8 Elemente auf einmal
        line = " " +"".join(f"{element:12.6f}" for element in abschnitt) + "\n"
        file_handle.write(line)  # Schreibt die Zeile in die Datei
      
def grid_adaption(grid_count, max=20, beta=2 ): # Erstellung von Gridabständen in Abhängigkeit von der Anzahl
    x_norm = np.linspace(0.0, 1.0, grid_count) # Erzeugt eine Liste von 0 bis 1 mit der Anzahl der Gitterpunkte
    x_stretched = 0.5 * (1.0 + np.tanh(beta *(2.0 * x_norm - 1.0))) / np.tanh(beta) # größter Grid Abstand sind 20
    #return x_stretched[::-1] * (grid_count-1) + 1.0 # Kehrt das Array um und bezieht es auf den grid_count
    
    spacings = np.diff(x_stretched) # Berechnet die Abstände zwischen den Punkten
    min_val = np.min(spacings)
    max_val = np.max(spacings)
    
    if (max_val - min_val) < 1e-9:
        return np.ones_like(spacings)  # Wenn alle Abstände gleich sind, gibt eine Liste mit Einsen zurück weil sonst Multall einen Fehler berechnet
    
    scaled_spacings = 1 + (max - 1.0) * (spacings - min_val) / (max_val - min_val) # Skaliert die Abstände auf den Bereich von 1 bis max
    scaled_spacings = np.nan_to_num(scaled_spacings, nan=0.0,posinf=0.0, neginf=0.0)
    
    return scaled_spacings

def create_bleed_air_card(NROW, file, rotor_data, stator_data, current_stage):
    # Filter patches for current stage 
    stage_key = f"stage_{current_stage}"
    
    # index 0 is stage string, rest are coords and mflow
    rotor_stage_patches = [patches for patches in rotor_data if patches[0] == stage_key]
    stator_stage_patches = [patches for patches in stator_data if patches[0] == stage_key]
    
    # Nbleed needs to be written for each row in each stage 
    print(f"file = {file}")
    with open(file, "a") as file:
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
## Multall .dat File schreiben
# Needs to be looped or called multiple times for each section IN EACH stage
def multall_grid_data_head_row(file_path, NSEC, row, JLE, JM, JTE, KM, tip_clearance, levels, CompressorGui, RPM):
    section = 0
    
    ktipstart = 0
    ktipend = 0
    actual_tip_clearance = 0
    
    if tip_clearance > 0:
        if row == 1:
            ktipstart = KM - 4
            ktipend = KM
            actual_tip_clearance = tip_clearance
        else:
            ktipstart = 0
            ktipend = 0
            actual_tip_clearance = 0.0
    
    if tip_clearance == 0:
        actual_tip_clearance = 0
        ktipstart = 0
        ktipend = 0

    if section == 0:
        if row == 1:
            x = round(Stage.p_1[0], 1)
            y = round(Stage.p_2[0], 1)
            z = RPM[0]
            blades = Stage.z_R[0]
        elif row == 2:
            x = round(Stage.p_2[0], 1)
            y = round(Stage.p_3[0], 1)
            z = 0.0
            blades = Stage.z_S[0]
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

    with open(file_path, "a") as file:
        file.write(" ***************************************************************\n")
        file.write(" ************STARTING THE INPUT FOR EACH BLADE ROW**************\n")
        file.write(f"  BLADE ROW NUMBER =        {row}                                           \n")
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
            if tip_clearance > 0:
                ftchick_values[ktipstart-2] = 0.9
                ftchick_values[ktipstart-1] = 0.5
            for k in range(ktipstart, KM):
                ftchick_values[k] = 0.0
            
        
            for i in range(0, KM, 8): # Zählweise in 8ter Schritten
                line_number = ftchick_values[i:i+8] # Holt die Zwischenschritte aus der Gridverteilung
                file.write(" ".join(f"{value:.6f}" for value in line_number) + "\n") # Schreibt die gebaute Zeile
        
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
            file.write("      120000  0.006000\n") # Documentation calls for more steps in multistage applications
        elif section == 0:
            file.write("      9000  0.006000\n")
        else: 
            file.write("      60000  0.005000\n")
        file.write("   SFX,      SFT,      FAC_4TH,     NCHANGE \n")
        file.write("  0.005000  0.005000  0.800000      1000\n")
        file.write("       NUMBER OF BLADE ROWS \n")# Number of blades in row?
        file.write(f"         {NROW}\n")
        file.write("        IM        KM \n")
        
        if section == 0:
            file.write(f"        {IM_grid_density}        {KM_grid_density}\n")
        else:
            file.write(f"        {IM_grid_density}        2\n")
           
        value_IM = grid_adaption(IM_grid_density)
        file.write("  FP(I),I=1,IMM1 \n")
        for i in range (0,len(value_IM), 8): # Zählweise in 8ter Schritten
            line_number = value_IM[i:i+8] # Holt die Zwischenschritte aus der Gridverteilung
            line_value = " " # fügt eine Leerzeile ein
            for value in line_number:
                line_value += f"{value:.6f} " # Fügt 8 Zahlen mit 6 Nachkommastellen ein
            line_value += "\n" # Fügt einen Zeilenumbruch ein
            file.write(line_value) # Schreibt die gebaute Zeile
        
        if section == 0 and not Q3D_value:        
            value_KM = grid_adaption(KM_grid_density)
            file.write("  FR(K),K=1,KMM1 \n")
            for i in range (0,len(value_KM), 8): # Zählweise in 8ter Schritten
                line_number = value_KM[i:i+8] # Holt die Zwischenschritte aus der Gridverteilung
                line_value = " " # fügt eine Leerzeile ein
                for value in line_number:
                    line_value += f"{value:.6f} " # Fügt 8 Zahlen mit 6 Nachkommastellen ein
                line_value += "\n" # Fügt einen Zeilenumbruch ein
                file.write(line_value) # Schreibt die gebaute Zeile        
        else: # Setzt FR auf 1 wenn Q3D aktiv ist oder es nur eine Reihe gibt
             file.write("  FR(K),K=1,KMM1 \n")
             file.write("  1.000000\n")

        file.write("        IR        JR        KR        IRBB      JRBB      KRBB \n")
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
        file.write("        10         5         0\n")
        file.write("   REYNO,     RF_VIS,   FTRANS, TURBVIS_LIM, PRANDTL, YPLUSWALL\n")
        if CompressorGui.stages_to_calc >1:
            file.write("  800000.0     0.500     0.000  3000.000       1.0     0.000\n") #  The doc explicitly states: "higher values, up to 3000, may be necessary in multistage machines." 
        else:
            file.write("  800000.0     0.500     0.000  1000.000       1.0     0.000\n")
        file.write("   YPLAM      YPTURB \n")
        file.write("  5.000000 25.000000\n")
        file.write("      ISHIFT    NEXTRAP_LE  NEXTRAP_TE \n")
        file.write("         2        10        10\n")
        file.write("  (NSTG(N),N=1,NROWS) \n")
        nstg_values = " ".join(["   1"] * NROW) # Needs to change to this:
        '''
        nstg_values = " ".join([str((i // 2) + 1) for i in range(NROW)])
        
        '''
        file.write(nstg_values + "\n")
        file.write("  5  TIME STEPS FOR PRINTOUT \n")
        file.write("      9000      9000      9000      9000      9000\n")
        file.write("  MARKER FOR VARIABLES TO BE SENT TO THE OUTPUT FILE.\n")
        file.write(" 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")
        file.write("  STREAM SURFACES ON WHICH RESULTS ARE TO BE SENT TO   THE OUTPUT FILE \n")
        file.write(" ".join(f"0  " for _ in range(KM_grid_density)) + "\n")
        

#writes the coordinates of all sections in a file for MULTALL
# schreibt die Koordinaten aller Abschnitte in eine Datei für MULTALL
# a? b? need a loop for writing all rows and stages
def write_coordinates(x, rtheta, d, r, file, row, a, b, JM):
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
def Q3D_information(file):
    with open(file, "a") as file:
        file.write("  DATA FOR STREAM SURFACE THICKNESS\n")
        file.write("   1.00000000      Q3DFORCE\n")
        file.write("           5  A UNIFORM  SS THICKNESS IS INITIALLY SET\n")
        file.write("   0.00000000      0.250000000      0.500000000      0.750000000      1.00000000\n")
        file.write("   1.00000000      1.00000000      1.00000000      1.00000000      1.00000000\n")     


# writes end of the file 
def write_end_file(row, file, section, KM, levels):
    # Here needs to be new logic because row only works for one stage 
    # Some logic for the rows and NROW is missing
    if row == 1: # Maybe use modulus here to get if the row is odd (rotor) or even (stator)
        x = round(Stage.p_R_out[0], 1)
        y = round(Stage.p_R_out[len(Stage.h_rel)-1], 1)
        t = round(Stage.T_t1[0], 4)
        p = round(Stage.p_t1[0], 1)
        um = round(Stage.cm1[0], 4)
    
    elif row == 2:
        x = round(Stage.p_S_out[0], 1)
        y = round(Stage.p_R_out[len(Stage.h_rel)-1], 1)
        t = round(Stage.T_t1[0], 4)
        p = round(Stage.p_t1[0], 1)
        um = round(Stage.cm1[0], 4)
        
    with open(file, "a", encoding='ascii') as file:
        if section == 0:
            file.write("  STARTING INLET BOUNDARY CONDITION DATA .\n")
            file.write("  NUMBER OF POINTS FOR INLET BOUNDARY CONDITIONS \n")
            file.write(f"        {KM}\n") # Number of Inlet Point wird Abhängig von der Gitterdichte KM 
            file.write("  SPACING OF INLET BOUNDARY CONDITION POINTS \n")
            
            value_KM = grid_adaption(KM)
            for i in range (0,len(value_KM), 8): # Zählweise in 8ter Schritten
                file.write(" ".join(f"{v:.6f}" for v in value_KM[i:i+8])+"\n") # Schreibt die gebaute Zeile
            
            # Dynamische Anpassung der Inlet Bedingungen durch KM
            file.write("   INLET STAGNATION PRESSURES \n")
            for i in range(0, KM, 8):
                file.write(" ".join(f"{p:.6f}" for _ in range(KM)[i:i+8]) + "\n")
            file.write("   INLET STAGNATION TEMPERATURES \n")
            for i in range(0, KM, 8):
                file.write(" ".join(f"{t:.6f}" for _ in range(KM)[i:i+8]) + "\n")
            file.write("   INLET ABSOLUTE TANGENTIAL VELOCITY \n")
            for i in range(0, KM, 8):
                file.write(" ".join(f"0.000" for _ in range(KM)[i:i+8]) + "\n")
            file.write("   INLET MERIDIONAL VELOCITY \n")
            for i in range(0, KM, 8):
                file.write(" ".join(f"{um:.6f}" for _ in range(KM)[i:i+8]) + "\n")
            file.write("   INLET MERIDIONAL YAW ANGLE \n")
            for i in range(0, KM, 8):
                file.write(" ".join(f"0.000" for _ in range(KM)[i:i+8]) + "\n")
            file.write("   INLET PITCH ANGLE \n")
            for i in range(0, KM, 8):
                file.write(" ".join(f"0.000" for _ in range(KM)[i:i+8]) + "\n")
            file.write("   PDOWN_HUB   PDOWN_TIP \n")
            file.write(f"  {x}  {y}\n")
            file.write(" MIXING LENGTH LIMITS ON ALL BLADE ROWS\n")
            
            for _ in range(row): # in here row needs to equal NROW (total number of blade rows), not just the current row number. 
                file.write("  0.030000  0.030000  0.030000  0.030000  0.030000  0.020000\n")
            file.write("  FACTOR TO INCREASE THE TURBULENT VISCOSITY OVER THE FIRST NMIXUP STEPS \n")
            file.write("   2.00000 1000\n")
        else:         
            if row == 1:
                i = levels[section-1]
                for j in range(len(Stage.h_rel)):
                    if round(Stage.h_rel[j],2) == i:
                        x = round(Stage.p_S_out[j], 1)
                        y = round(Stage.p_R_out[j], 1)

            elif row == 2:
                i = levels[section-1]
                for j in range(len(Stage.h_rel)):
                    if round(Stage.h_rel[j],2) == i:
                        x = round(Stage.p_S_out[j], 1)
                        y = round(Stage.p_S_out[j], 1)

            file.write("STARTING INLET BOUNDARY CONDITION DATA .\n")
            file.write("  NUMBER OF POINTS FOR INLET BOUNDARY CONDITIONS \n")
            file.write("         2\n")
            file.write("  SPACING OF INLET BOUNDARY CONDITION POINTS \n")
            file.write("  1.000000\n")
            file.write("   INLET STAGNATION PRESSURES \n")
            file.write(f"  {p} {p}\n")
            file.write("   INLET STAGNATION TEMPERATURES \n")
            file.write(f"  {t} {t}\n")
            file.write("   INLET ABSOLUTE TANGENTIAL VELOCITY \n")
            file.write("    0.0000 0.0000\n")
            file.write("   INLET MERIDIONAL VELOCITY\n")
            file.write(f"  {um} {um}\n")
            file.write("   INLET MERIDIONAL YAW ANGLE\n")
            file.write("    0.0000 0.0000\n")
            file.write("   INLET PITCH ANGLE\n")
            file.write("    0.0000 0.0000\n")
            file.write("   PDOWN_HUB   PDOWN_TIP\n")
            file.write(f"  {x}  {y}\n")
            file.write(" MIXING LENGTH LIMITS ON ALL BLADE ROWS\n")
            '''
            ### Copied from docs ###
            For each of NROWS blade rows input
                XLLIM_IN The mixing length limit at the upstream boundary to the
                blade row. Typical value = 0.02 .
                XLLIM_LE The mixing length limit at the leading edge of the blade
                row. Typical value = 0.03 .
                XLLIM_TE The mixing length limit at the trailing edge of the blade
                row. Typical value = 0.04 .
                XLLIM_DN The mixing length limit at the exit boundary of the blade
                row. Typical value = 0.05 .
                FSTURB The free stream turbulent viscosity as a multiple of the
                laminar viscosity. Usually = 0.0 but increase in regions of
                high turbulence.
                TURBVIS_DAMP On passing through a mixing plane the turbulent
                viscosity downstream of the plane is this multiple of the
                pitchwise averaged turbulent viscosity upstream of the
                mixing plane. Typical value = 0.5, but this is very much a
                guess.
                There are NROWS lines of data needed here. Increase the mixing length limits and FSTURB
                if the flow is known to be highly turbulent or in regions where separations occur.
                The defaults are XLLIM_IN = 0.02, XLLIM_LE = 0.03, XLLIM_TE = 0.04, XLLIM_DN =
                0.05, FSTURB = 1.0, TURBVIS_DAMP = 0.5 
            '''
            for _ in range(row): # This needs to loop for every row so twice per stage
                file.write("  0.030000  0.030000  0.030000  0.030000  0.030000  0.020000\n")
            file.write("  FACTOR TO INCREASE THE TURBULENT VISCOSITY OVER THE FIRST NMIXUP STEPS\n")
            file.write("   2.00000 1000\n")

            
# Plotting:

def plot_all(grid_data_list, grid_density):
    plt.figure(figsize=(15, 10))
    colors = ['blue', 'red']
    row_labels = ['Rotor', 'Stator']

    for i, data in enumerate(grid_data_list):
        row_num = data['row_num']
        x_coords = data['x_new'][0] 
        d_coords = data['d_new'][0]
        rtheta_coords = data['Rtheta_new'][0]
        
        rtheta_upper = rtheta_coords
        rtheta_lower = [upper - d for upper, d in zip(rtheta_upper, d_coords)]
        
        color = colors[i % len(colors)]
        label = f"{row_labels[i % len(row_labels)]} (Reihe {row_num})"
        
        plt.plot(x_coords, rtheta_upper, color=color, marker='.', markersize=3, label=label)
        plt.plot(x_coords, rtheta_lower, color=color, marker='.', markersize=3)
    
    plt.xlabel("x-Koordinate [mm]")
    plt.ylabel("Rθ-Koordinate [mm]")
    plt.title(f"Dynamisches Gitter (Dichte: {grid_density})")
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def generate_var_grid_data(nrow_wert, IM_grid_density, KM_grid_density, JM_grid_density, inlet_percentage, outlet_percentage, reference_chord_length, levels):
    
    # Liste, um die Ergebnisse jeder Schaufelreihe zu speichern
    all_rows_grid_data = []
    all_rows_data_plot = []

    for row_num in range(1, nrow_wert + 1):
        print(f"\nVerarbeite Schaufelreihe {row_num} (Dichte: {JM_grid_density})")

        # Schaut wie groß die Schaufel bei 50 % ist und vergleicht mit dem Referenzwert
        actual_chord, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = Stage.calculation_of_section(0.5, row_num)
        
        # h_H_plot is never in the whole of the project defined
        # try:
        #     h_H_plot = h_H_plot if h_H_plot else 0.5
        # except NameError:
        #     h_H_plot = 0.5# What values is here needed? Default at 50%?
        
        #printing_chord, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = Stage.calculation_of_section(h_H_plot, row_num) 
        print(f"Sehnenlänge für Reihe {row_num}: {actual_chord:.2f} mm")

        JM_dynamic = int(round((actual_chord / reference_chord_length) * JM_grid_density))
        #j_prime_max_plot = int(round((printing_chord / reference_chord_length) * JM_grid_density))      
        
        #dynamische Berechnung der Anzahl der Gitterpunkte im Einlass und Auslass
        n_max_in = int(round(JM_dynamic * inlet_percentage))
        j_prime_max = JM_dynamic
        n_max_out = int(round(JM_dynamic * outlet_percentage))
        
        JLE = n_max_in
        JTE = n_max_in + j_prime_max - 1
        JM = n_max_in + n_max_out + j_prime_max - 2
        
        if row_num == 1:
            JM_dynamic_rotor = JM_dynamic
        else:
            JM_dynamic_stator = JM_dynamic
        print(f"Dynamische Gitterpunkte (nur Schaufel): {JM_dynamic}")
        print(f"Punkte insgesamt (JM): {JM}, Einlass-Index (JLE): {JLE}, Auslass-Index (JTE): {JTE}")
        print(f"Anzahl der Punkte im Einlass: {n_max_in}, Anzahl der Punkte im Auslass: {n_max_out}")
        
        x_new, d_new, R_new, Rtheta_new = Stage.calc_blade_row_coordinates(
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
        
        # Speichere die berechneten Daten für diese Reihe
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
        if Q3D_value:
            Q3D_information(...)

        write_end_file(NROW, ...)   # inlet BCs + mixing length limits
    '''
    
    
    
    """
    Nimmt die Daten aus der Haupt-GUI entgegen, entpackt sie und 
    startet die Gittergenerierung (Multall .dat Erstellung).
    """
    print("\n--- Starte Entpacken der GUI-Daten in var_Grid ---")
    
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
        print("Please enter valid numbers for all conditions.")
        
        '''
        Unpacking Grid Data
        '''

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
    D_S1 = meanline_data_gui['D_S1']
    D_S2 = meanline_data_gui['D_S2']
    D_S3 = meanline_data_gui['D_S3']
    D_H1 = meanline_data_gui['D_H1']
    D_H2 = meanline_data_gui['D_H2']
    D_H3 = meanline_data_gui['D_H3']
    
    output_path = Metadata['output_folder']
    levels = Metadata['levels']

    total_height_1 = (Stage.D_S1[0] - Stage.D_H1[0]) / 2.0
    total_height_2 = (Stage.D_S2[0] - Stage.D_H2[0]) / 2.0
    total_height_3 = (Stage.D_S3[0] - Stage.D_H3[0]) / 2.0

    tip_clearance_multall_1 = (tip_clearance_mm_rotor / total_height_1)
    tip_clearance_multall_2 = (tip_clearance_mm_rotor / total_height_2)
    tip_clearance_multall_3 = (tip_clearance_mm_rotor / total_height_3)

    enable_bleed_air = bleed_air_data['enable_bleed_air']
    
    all_rows_grid_data = generate_var_grid_data(nrow_wert, IM_grid_density, KM_grid_density, JM_grid_density, inlet_percentage, outlet_percentage, ref_chord_length, levels)
    

    JM_dynamic_rotor = all_rows_grid_data[0]['JM_dynamic']
    
    if nrow_wert > 1:
        JM_dynamic_stator = all_rows_grid_data[1]['JM_dynamic']
    else:
        JM_dynamic_stator = 0

    if Q3D_value:
        output_name = f"multall_grid_Q3D_IM_{IM_grid_density}__R_{JM_dynamic_rotor}_S_{JM_dynamic_stator}_rows_{nrow_wert}.dat"
    else:
        output_name = f"multall_grid_IM_{IM_grid_density}_KM_{KM_grid_density}_R_{JM_dynamic_rotor}_S_{JM_dynamic_stator}_rows_{nrow_wert}.dat"
        
    full_output_path = os.path.join(output_path, output_name)
    
    NSEC = len(levels)

    print("Writing Multall grid data head row...")
    # Wir übergeben hier unser neues Super-Dictionary "combined_multall_data"
    write_head_file(KM_grid_density, IM_grid_density, full_output_path, 0, nrow_wert, NSEC, Q3D_value, enable_bleed_air, CompressorGui)# again what is: combined_multall_data=0 it never gets defined in the function

    
    # Calls grid/row data writing?? If so needs to be called per stage with the input of necasarry inputs
    for i, data in enumerate(all_rows_grid_data):
        row_num = data['row_num']
        x_coords = data['x_new'] 
        d_coords = data['d_new']
        r_coords = data['R_new']
        rtheta_coords = data['Rtheta_new']
        JLE = data['JLE']
        JTE = data['JTE']
        JM_row = data['JM']
        NSEC_new = len(data['x_new'])
        
        global_row_num = i + 1
        
        current_stage = (i / 2) + 1
     
        multall_grid_data_head_row(full_output_path, NSEC_new, row_num, JLE, JM_row, JTE, KM_grid_density, tip_clearance_mm_rotor, levels, CompressorGui, RPM)
        write_coordinates(x_coords, rtheta_coords, d_coords, r_coords, full_output_path, row_num, 0, NSEC_new, JM_row)
        print(f"Grid data for row {row_num} written successfully.")
    
    if Q3D_value:
        Q3D_information(full_output_path)
        print("Q3D information written successfully.")
    
    print("Starting writing end of file...")
    write_end_file(nrow_wert, full_output_path, 0, KM_grid_density, levels)
    print(f"Grid data for all rows written to {full_output_path} successfully.")
    
    print("All tasks completed successfully.")
