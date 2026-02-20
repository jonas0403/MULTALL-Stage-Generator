# Autor: Luca De Francesco
# Skript zur Bachelorarbeit
    

import matplotlib.pyplot as plt
import numpy as np
import os



script_dir = os.path.dirname(os.path.abspath(__file__)) # Holt den Dateipfad vom Skript
settings_file_path = os.path.join(script_dir, "Setting.txt" )
        
# Schreiben der Settings in eine Datei        
def save_settings_to_file(settings_to_save):
    
    all_settings = loaded_settings_from_file()
    all_settings.update(settings_to_save) # Aktualisiert die geladenen Einstellungen mit den neuen Werten

    try:
        with open('Setting.txt', 'w') as file:
            for key, value in settings_to_save.items():
                file.write(f"{key} = {value}\n")
    except IOError as e:
        print(f"Error: {e}")

#laden der Settings aus einer Datei        
def loaded_settings_from_file(default_levels=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]):
    settings_stage = {}
    try:
        with open(settings_file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if ' = ' in line:
                    key, value = line.split(' = ', 1)
                    settings_stage[key.strip()] = value.strip()
    except FileNotFoundError:
        print("Einstellungsdatei nicht gefunden. Standardwerte werden verwendet.")
    return settings_stage 

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

def create_bleed_air_card(NROW, file, rotor_data, stator_data):
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

## Multall .dat File schreiben
def multall_grid_data_head_row(file_path, NSEC, row, JLE, JM, JTE, KM, tip_clearance, levels, stage_data):
    section = 0
    NSEC
    
    ktipstart = 0
    ktipend = 0
    actual_tip_clearance = 0
    
    if tip_clearance > 0:
        if row == 1:
            ktipstart = KM - 2
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
            x = round(stage_data['p_1'][0], 1)
            y = round(stage_data['p_2'][0], 1)
            z = stage_data['RPM'][0]
            blades = stage_data['z_R'][0]
        elif row == 2:
            x = round(stage_data['p_2'][0], 1)
            y = round(stage_data['p_3'][0], 1)
            z = 0.0
            blades = stage_data['z_S'][0]
    else:
        if row == 1:
            i = levels[section-1]
            for j in range(len(stage_data['h_rel'])):
                if round(stage_data['h_rel'][j],2) == i:
                    x = round(stage_data['p_R_in'][j], 1)
                    y = round(stage_data['p_R_out'][j], 1)

            z = stage_data['RPM'][0]
            blades = stage_data['z_R'][0]
        elif row == 2:
            i = levels[section-1]
            for j in range(len(stage_data['h_rel'])):
                if round(stage_data['h_rel'][j],2) == i:
                    x = round(stage_data['p_S_in'][j], 1)
                    y = round(stage_data['p_S_out'][j], 1)
            
            blades = stage_data['z_S'][0]
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
    
def write_head_file(KM_grid_density, IM_grid_density, file_path, section, NROW, NSEC, Q3D_value, enable_bleed_air, stage_data):
    if enable_bleed_air == True:
        bleed_air = 1
    else: 
        bleed_air = 0 
    with open(file_path, "w+") as file:
        file.write(" DATA SET FOR \"multall\" . GENERATED BY \"stagen\" .                       \n")
        file.write("    CP   and   GAMMA \n")
        file.write(f" {stage_data['cp']}    {stage_data['kappa']}\n")
        file.write("       ITIMST \n")
        file.write("         3\n")
        file.write("     CFL,    DAMP,    MACHLIM,    F_PDOWN \n")
        file.write("  0.320000 9.000000  2.000000  0.000000\n")
        file.write("  IF_RESTART \n")
        file.write("         0\n")
        file.write("  NSTEPS_MAX, CONLIM\n")
        if section == 0:
            file.write("      9000  0.006000\n")
        else: 
            file.write("      60000  0.005000\n")
        file.write("   SFX,      SFT,      FAC_4TH,     NCHANGE \n")
        file.write("  0.005000  0.005000  0.800000      1000\n")
        file.write("       NUMBER OF BLADE ROWS \n")
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
        file.write("  800000.0     0.500     0.000  1000.000       1.0     0.000\n")
        file.write("   YPLAM      YPTURB \n")
        file.write("  5.000000 25.000000\n")
        file.write("      ISHIFT    NEXTRAP_LE  NEXTRAP_TE \n")
        file.write("         2        10        10\n")
        file.write("  (NSTG(N),N=1,NROWS) \n")
        nstg_values = " ".join(["   1"] * NROW)
        file.write(nstg_values + "\n")
        file.write("  5  TIME STEPS FOR PRINTOUT \n")
        file.write("      9000      9000      9000      9000      9000\n")
        file.write("  MARKER FOR VARIABLES TO BE SENT TO THE OUTPUT FILE.\n")
        file.write(" 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")
        file.write("  STREAM SURFACES ON WHICH RESULTS ARE TO BE SENT TO   THE OUTPUT FILE \n")
        file.write(" ".join(f"0  " for _ in range(KM_grid_density)) + "\n")
        

#writes the coordinates of all sections in a file for MULTALL
# schreibt die Koordinaten aller Abschnitte in eine Datei für MULTALL
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
def write_end_file(row, file, section, KM, levels, stage_data):
    
    if row == 1:
        x = round(stage_data['p_R_out'][0], 1)
        y = round(stage_data['p_R_out'][len(stage_data['h_rel'])-1], 1)
        t = round(stage_data['T_t1'][0], 4)
        p = round(stage_data['p_t1'][0], 1)
        um = round(stage_data['cm1'][0], 4)
    
    elif row == 2:
        x = round(stage_data['p_S_out'][0], 1)
        y = round(stage_data['p_R_out'][len(stage_data['h_rel'])-1], 1)
        t = round(stage_data['T_t1'][0], 4)
        p = round(stage_data['p_t1'][0], 1)
        um = round(stage_data['cm1'][0], 4)
        
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
            for _ in range(row):
                file.write("  0.030000  0.030000  0.030000  0.030000  0.030000  0.020000\n")
            file.write("  FACTOR TO INCREASE THE TURBULENT VISCOSITY OVER THE FIRST NMIXUP STEPS \n")
            file.write("   2.00000 1000\n")
        else:         
            if row == 1:
                i = levels[section-1]
                for j in range(len(stage_data['h_rel'])):
                    if round(stage_data['h_rel'][j],2) == i:
                        x = round(stage_data['p_S_out'][j], 1)
                        y = round(stage_data['p_R_out'][j], 1)

            elif row == 2:
                i = levels[section-1]
                for j in range(len(stage_data['h_rel'])):
                    if round(stage_data['h_rel'][j],2) == i:
                        x = round(stage_data['p_S_out'][j], 1)
                        y = round(stage_data['p_S_out'][j], 1)

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
            for _ in range(row):
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

def generate_and_plot_grid(nrow_wert, IM_grid_density, KM_grid_density, h_H_plot, JM_grid_density, inlet_percentage, outlet_percentage, reference_chord_length, levels):
    
    # Liste, um die Ergebnisse jeder Schaufelreihe zu speichern
    all_rows_data = []
    all_rows_data_plot = []

    for row_num in range(1, nrow_wert + 1):
        print(f"\nVerarbeite Schaufelreihe {row_num} (Dichte: {JM_grid_density})")

        # Schaut wie groß die Schaufel bei 50 % ist und vergleicht mit dem Referenzwert
        actual_chord, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = Stage.calculation_of_section(0.5, row_num)
        printing_chord, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = Stage.calculation_of_section(h_H_plot, row_num) 
        print(f"Sehnenlänge für Reihe {row_num}: {actual_chord:.2f} mm")

        JM_dynamic = int(round((actual_chord / reference_chord_length) * JM_grid_density))
        j_prime_max_plot = int(round((printing_chord / reference_chord_length) * JM_grid_density))      
        
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
        
        # x_new, d_new, R_new, Rtheta_new = Stage.calc_blade_row_coordinates(
        #     row=row_num, 
        #     j_prime_max=JM_dynamic, 
        #     num_planes=5, 
        #     n_max_in=n_max_in, 
        #     l_inlet=1, 
        #     n_max_out=n_max_out, 
        #     l_outlet=1, 
        #     Z_H=0.05, 
        #     Z_S=0.95, 
        #     levels=levels)
        
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
        all_rows_data.append({
            'row_num': row_num,
            'x_new': x_new,
            'd_new': d_new,
            'R_new': R_new,
            'Rtheta_new': Rtheta_new,
            'JM': JM,
            'JLE': JLE,
            'JTE': JTE,
            'IM': IM_grid_density,
            'KM': KM_grid_density
        })
        
        all_rows_data_plot.append({
            'row_num': row_num,
            'x_new': x_new_plot,
            'd_new': d_new_plot,
            'R_new': R_new_plot,
            'Rtheta_new': Rtheta_new_plot
        })
    
    return all_rows_data, all_rows_data_plot, JM_dynamic_rotor, JM

'''     
   
        # if tip_clearance_mm_rotor > 0:
        #     KM_grid_density += 3
        
        if Q3D_value:
            KM_grid_density = 2 # Setzt KM auf 2 wenn Q3D aktiv ist
        else: 
            KM_grid_density = KM_grid_density # Ansonsten bleibt KM wie ausgewählt
        
        # Berechnung der Spaltgröße in Multall
        total_height = (Stage.D_S1[0] - Stage.D_H1[0]) / 2.0
        tip_clearance_multall = (tip_clearance_mm_rotor / total_height)
        tip_clearance_percentage = (tip_clearance_mm_rotor / total_height) * 100        

        # Führt die Gittergenerierung und das Plotten durch
        print("Starting calculation of dynamic grid...")
        grid_data_list, grid_data_list_plot, JM_dynamic, JM = generate_and_plot_grid(nrow_wert, IM_grid_density, KM_grid_density, h_H_plot, JM_grid_density, inlet_percentage, outlet_percentage, ref_chord_length, stage_levels)
        print("Grid calculation completed.")
        print(f"IM: {IM_grid_density}, KM: {KM_grid_density}, Grid Density: {JM_grid_density}")
       
        if do_plot:
            print("Plotting grid data...")
            plot_all(grid_data_list_plot, JM_dynamic)
            print("Grid data plotted successfully.")
        
        else:
            print("Plotting skipped as per user selection.")
        
        if Q3D_value:
            output_name = f"multall_grid_Q3D_IM_{IM_grid_density}_JM_{JM_dynamic}_rows_{nrow_wert}.dat"
        else:
            output_name = f"multall_grid_IM_{IM_grid_density}_KM_{KM_grid_density}_JM_{JM_dynamic}_rows_{nrow_wert}_ref_chord_{ref_chord_length}.dat"
            
        full_output_path = os.path.join(output_path, output_name)
        file_path = full_output_path
        section = 0 
        
        NSEC = len(stage_levels)

        print("Writing Multall grid data head row...")
        write_head_file(KM_grid_density, IM_grid_density, full_output_path, section, nrow_wert, NSEC, Q3D_value, enable_bleed_air)
        print("Multall grid data head row written successfully.")
        
        for i, data in enumerate(grid_data_list):
            row_num = data['row_num']
            x_coords = data['x_new'] 
            d_coords = data['d_new']
            r_coords = data['R_new']
            rtheta_coords = data['Rtheta_new']
            JLE = data['JLE']
            JTE = data['JTE']
            JM = data['JM']
            NSEC_new = len(data['x_new'])
        
            print("Writing Multall grid data head row...")
            multall_grid_data_head_row(full_output_path, NSEC_new, row_num, JLE, JM, JTE, KM_grid_density, tip_clearance_multall, stage_levels)
            print("Multall grid data head row written successfully.")

            print(f"Writing coordinates for row {row_num}...")
            write_coordinates(x_coords, rtheta_coords, d_coords, r_coords, full_output_path, row_num, 0, NSEC_new, JM)
            print(f"Grid data for row {row_num} written successfully.")
        
        if Q3D_value:
            Q3D_information(full_output_path)
            print("Q3D information written successfully.")
        
        print("Starting writing end of file...")
        write_end_file(nrow_wert, full_output_path, section, KM_grid_density, stage_levels)
        print(f"Grid data for all rows written to {full_output_path} successfully.")
        
        print("All tasks completed successfully.")
        
        # dialog = MultallPathDialog(window)
        # multall_executable_path = dialog.result_path
        
        # if multall_executable_path:
        #     print(f"Multall executable path: {multall_executable_path}")
        #     run_multall_simulation(full_output_path, multall_executable_path)
        #     print("Multall simulation completed.")
        
        window.destroy()
        
        
    confirm_button = ttk.Button(main_frame, text="Generate Grid", command=on_confirm)
    confirm_button.pack(pady=15, fill="x")

    window.mainloop()



# GUI zur Eingabe der Benutzereinstellungen
def get_user_settings_from_gui(settings_loaded):

    def browse_output_folder():
        path = filedialog.askdirectory()
        if path:            
            output_folder_entry.delete(0, tk.END) # Löscht alte Inhalte
            output_folder_entry.insert(0, path) # Neuer Pfad

    window = tk.Tk()
    window.title("Dynamic Grid-Generator")
    
    loaded_levels = settings_loaded.get('levels', '0.0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 0.95, 1.00')
    loaded_output = settings_loaded.get('output_folder', '')
    
            
    settings = { # Lade die Standartwerte
        'nrow': tk.IntVar(value=2),
        'h_H_plot': tk.DoubleVar(value=0.5),
        'im_selection' : tk.StringVar(value=37),   # Default-Wert für IM
        'km_selection' : tk.StringVar(value=37),   # Default-Wert für KM
        'ref_chord_length': tk.DoubleVar(value=134.4),  # Default-Wert für Referenz-Sehnenlänge
        'JM_grid_density': tk.IntVar(value=200),  # Default-Wert für Referenz-Gitterpunkte
        'tip_clearance_rotor': tk.DoubleVar(value=1.3),  # Standardwert von 1.3mm
        #'tip_clearance_stator': tk.DoubleVar(value=1.5),  # Standardwert von 1.5mm
        'inlet_percentage': tk.DoubleVar(value=0.2),  # Standardwert von 20%
        'outlet_percentage': tk.DoubleVar(value=0.15),  # Standardwert von 15%
        'levels': tk.StringVar(value=loaded_levels),  # Standardwerte für die Ebenen
        'output_folder': tk.StringVar(value=loaded_output),  # Standardwert für den Ausgabe
        'show_plot': tk.BooleanVar(value=False),  # Standardwert für die Anzeige des Plots
        'Q3D_mode': tk.BooleanVar(value=False)  # Standardwert für Q3D Modus
    }
    
    main_frame = ttk.Frame(window, padding="10")
    main_frame.pack(fill="both", expand=True)

        
    # Fügt Tab listen ein
    notebook = ttk.Notebook(main_frame)  
    notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
    grid_tab = ttk.Frame(notebook, padding=10)
    stage_tab = ttk.Frame(notebook, padding=10)
        
    notebook.add(grid_tab, text="Grid")
    notebook.add(stage_tab, text="Additional Settings")
    
    def toggle_Q3D():
        if settings['Q3D_mode'].get():
            KM_grid_combobox.set("2") # Setzt KM auf 2
            KM_grid_combobox.config(state=tk.DISABLED) # Deaktiviert die Auswahl
        else:
            KM_grid_combobox.config(state=tk.NORMAL) # Aktiviert die Auswahl
            KM_grid_combobox.set("37")  # Setzt KM zurück auf 37

    settings_frame = ttk.LabelFrame(main_frame, text="Grid-Settings", padding="10")
    settings_frame.pack(fill="x", expand=True, pady=5)
    
    settings_frame_stage = ttk.LabelFrame(main_frame, text="Stage-Settings", padding="10")
    settings_frame_stage.pack(fill="x", expand=True, pady=5)
        
    # Füllt die Tabs mit Inhalt   
    ttk.Label(stage_tab, text="Please define the levels (0.0 to 1.0):").grid(row=10, column=0, sticky="w", pady=5)
    ttk.Entry(stage_tab, textvariable=settings['levels'], width=50).grid(row=10, column=1, sticky="w", pady=5)

    # Eingabefelder für Rotor- und Stator-Einstellungen
    ttk.Label(grid_tab, text="Stage Components (1=R, 2=R+S):").grid(row=0, column=0, sticky="w", pady=5)
    ttk.Entry(grid_tab, textvariable=settings['nrow'], width=10).grid(row=0, column=1, sticky="w", pady=5)
            
    ttk.Label(grid_tab, text="Reference Chord Length [mm]:").grid(row=1, column=0, sticky="w", pady=5)
    ttk.Entry(grid_tab, textvariable=settings['ref_chord_length'], width=10).grid(row=1, column=1, sticky="w", pady=5)

    # Gitterdichte-Auswahl IMxKM
    ttk.Label(grid_tab, text="Grid Dimension (KM):").grid(row=2, column=0, sticky="w", pady=5)
    im_km_grid_options = ["5", "13", "21", "29", "37", "45", "53", "71", "79", "86", "94"]
    KM_grid_combobox = ttk.Combobox(grid_tab, textvariable=settings['km_selection'], values=im_km_grid_options, state="readonly")
    KM_grid_combobox.grid(row=2, column=1, sticky="w", pady=5)
    KM_grid_combobox.set("37")  # Standardwert auf "37"
    
    Q3D_frame = ttk.LabelFrame(grid_tab, text="Q3D Mode", padding="10")
    Q3D_frame.grid(row=9, column=0, columnspan=2, sticky="ew", pady=10, padx=5)
    ttk.Checkbutton(
        Q3D_frame,
        text="Activate Q3D Mode (Sets KM to 2)",
        variable=settings['Q3D_mode'],
        command=toggle_Q3D
    ).grid(row=0, column=0, sticky="w")
            
    ttk.Label(grid_tab, text="Grid Dimension (IM):").grid(row=3, column=0, sticky="w", pady=5)
    im_km_grid_options = ["5", "13", "21", "29", "37", "45", "53", "71", "79", "86", "94"]
    IM_grid_combobox = ttk.Combobox(grid_tab, textvariable=settings['im_selection'], values=im_km_grid_options, state="readonly")
    IM_grid_combobox.grid(row=3, column=1, sticky="w", pady=5)
    IM_grid_combobox.set("37")  # Standardwert auf "37"
            
    # Gitterdichte-Auswahl für die Feinheit JM    
    ttk.Label(grid_tab, text="Fineness (Reference Points):").grid(row=5, column=0, sticky="w", pady=5)
    JM_value = [i for i in range(8, 800, 8)]  # Generiert Werte von 8 bis 800 in 9er-Schritten
    JM_grid_options = [str(i) for i in JM_value]
    JM_grid_combobox = ttk.Combobox(grid_tab, textvariable=settings['JM_grid_density'], values=JM_grid_options, state="readonly")
    JM_grid_combobox.grid(row=5, column=1, sticky="w", pady=5)
    JM_grid_combobox.set("296")  # Standardwert auf "300"
            
    # Drop-Down-Menü für Plotting Height
    ttk.Label(grid_tab, text="Inlet Points (% of JM):").grid(row=6, column=0, sticky="w", pady=5) 
    ttk.Entry(grid_tab, textvariable=settings['inlet_percentage'], width=10).grid(row=6, column=1, sticky="w", pady=5) 
                                
    # Drop-Down-Menü für Plotting Height
    ttk.Label(grid_tab, text="Outlet Points (% of JM):").grid(row=7, column=0, sticky="w", pady=5) 
    ttk.Entry(grid_tab, textvariable=settings['outlet_percentage'], width=10).grid(row=7, column=1, sticky="w", pady=5)  
            
    # Eingabefeld für Rotor-Spaltgröße
    ttk.Label(grid_tab, text="Spaltgröße Rotor (mm):").grid(row=8, column=0, sticky="w", pady=5)
    ttk.Entry(grid_tab, textvariable=settings['tip_clearance_rotor'], width=10).grid(row=8, column=1, sticky="w", pady=5)
            
    # Eingabefeld für Rotor-Spaltgröße
    # ttk.Label(settings_frame, text="Spaltgröße Stator (mm):").grid(row=7, column=0, sticky="w", pady=5)
    # ttk.Entry(settings_frame, textvariable=settings['tip_clearance_stator'], width=10).grid(row=7, column=1, sticky="w", pady=5)

    ttk.Label(stage_tab, text="Output Folder:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    output_folder_entry = ttk.Entry(stage_tab, textvariable=settings['output_folder'] ,width=40)
    output_folder_entry.grid(row=0, column=1, sticky='ew')
    ttk.Button(stage_tab, text="Browse", command=browse_output_folder).grid(row=0, column=2)

    plot_frame = ttk.LabelFrame(stage_tab, text="Plotting", padding="10")
    plot_frame.grid(row=11, column=0, columnspan=3, sticky="ew", pady=10, padx=5)

    #Menü für Plotting Height
    ttk.Label(plot_frame, text="Please define Plotting Height (0 to 1.0)").grid(row=0, column=0, sticky="w", pady=5) 
    ttk.Entry(plot_frame, textvariable=settings['h_H_plot'], width=10).grid(row=0, column=1, sticky="w", pady=5)

    
    ttk.Checkbutton(
        plot_frame, 
        text="Plot Grid after Generation", 
        variable=settings["show_plot"] # Standardmäßig aktiviert
    ).grid(row=0, column=3, sticky="w") 

    
    def on_confirm():

    
        
        stage_levels_str = settings['levels'].get() # Holt die Ebenen als String
        stage_levels = [float(level.strip()) for level in stage_levels_str.split(',') if level.strip()] # Wandelt den String in eine Liste von Float-Werten um
        output_path = settings["output_folder"].get() # Holt den Ausgabeordner
        
        do_plot = settings['show_plot'].get()  # Holt den Status des Plot-Checkbox

        settings_to_save = {
            'output_folder': output_path # Speichert den Ausgabeordner aus GUI Eingabe
        }

        save_settings_to_file(settings_to_save)
        
        # holt alle Einstellungen aus der GUI
        nrow_wert = settings['nrow'].get()
        h_H_plot = settings['h_H_plot'].get()
        tip_clearance_mm_rotor = settings['tip_clearance_rotor'].get()
        #tip_clearance_mm_stator = settings['tip_clearance_stator'].get()
        KM_grid_density = int(settings['km_selection'].get())
        IM_grid_density = int(settings['im_selection'].get())
        JM_grid_density = int(settings['JM_grid_density'].get())
        inlet_percentage = settings['inlet_percentage'].get()
        outlet_percentage = settings['outlet_percentage'].get()
        ref_chord_length = settings['ref_chord_length'].get()
        Q3D_value = settings['Q3D_mode'].get()
        
        # if tip_clearance_mm_rotor > 0:
        #     KM_grid_density += 3
        
        if Q3D_value:
            KM_grid_density = 2 # Setzt KM auf 2 wenn Q3D aktiv ist
        else: 
            KM_grid_density = KM_grid_density # Ansonsten bleibt KM wie ausgewählt
        
        # Berechnung der Spaltgröße in Multall
        total_height = (Stage.D_S1[0] - Stage.D_H1[0]) / 2.0
        tip_clearance_multall = (tip_clearance_mm_rotor / total_height)
        tip_clearance_percentage = (tip_clearance_mm_rotor / total_height) * 100        

        # Führt die Gittergenerierung und das Plotten durch
        print("Starting calculation of dynamic grid...")
        grid_data_list, grid_data_list_plot, JM_dynamic, JM = generate_and_plot_grid(nrow_wert, IM_grid_density, KM_grid_density, h_H_plot, JM_grid_density, inlet_percentage, outlet_percentage, ref_chord_length, stage_levels)
        print("Grid calculation completed.")
        print(f"IM: {IM_grid_density}, KM: {KM_grid_density}, Grid Density: {JM_grid_density}")
       
        if do_plot:
            print("Plotting grid data...")
            plot_all(grid_data_list_plot, JM_dynamic)
            print("Grid data plotted successfully.")
        
        else:
            print("Plotting skipped as per user selection.")
        
        if Q3D_value:
            output_name = f"multall_grid_Q3D_IM_{IM_grid_density}_JM_{JM_dynamic}_rows_{nrow_wert}.dat"
        else:
            output_name = f"multall_grid_IM_{IM_grid_density}_KM_{KM_grid_density}_JM_{JM_dynamic}_rows_{nrow_wert}_ref_chord_{ref_chord_length}.dat"
            
        full_output_path = os.path.join(output_path, output_name)
        file_path = full_output_path
        section = 0 
        
        NSEC = len(stage_levels)

        print("Writing Multall grid data head row...")
        write_head_file(KM_grid_density, IM_grid_density, full_output_path, section, nrow_wert, NSEC, Q3D_value, enable_bleed_air)
        print("Multall grid data head row written successfully.")
        
        for i, data in enumerate(grid_data_list):
            row_num = data['row_num']
            x_coords = data['x_new'] 
            d_coords = data['d_new']
            r_coords = data['R_new']
            rtheta_coords = data['Rtheta_new']
            JLE = data['JLE']
            JTE = data['JTE']
            JM = data['JM']
            NSEC_new = len(data['x_new'])
        
            print("Writing Multall grid data head row...")
            multall_grid_data_head_row(full_output_path, NSEC_new, row_num, JLE, JM, JTE, KM_grid_density, tip_clearance_multall, stage_levels)
            print("Multall grid data head row written successfully.")

            print(f"Writing coordinates for row {row_num}...")
            write_coordinates(x_coords, rtheta_coords, d_coords, r_coords, full_output_path, row_num, 0, NSEC_new, JM)
            print(f"Grid data for row {row_num} written successfully.")
        
        if Q3D_value:
            Q3D_information(full_output_path)
            print("Q3D information written successfully.")
        
        print("Starting writing end of file...")
        write_end_file(nrow_wert, full_output_path, section, KM_grid_density, stage_levels)
        print(f"Grid data for all rows written to {full_output_path} successfully.")
        
        print("All tasks completed successfully.")
        
        # dialog = MultallPathDialog(window)
        # multall_executable_path = dialog.result_path
        
        # if multall_executable_path:
        #     print(f"Multall executable path: {multall_executable_path}")
        #     run_multall_simulation(full_output_path, multall_executable_path)
        #     print("Multall simulation completed.")
        
        window.destroy()
        
        
    confirm_button = ttk.Button(main_frame, text="Generate Grid", command=on_confirm)
    confirm_button.pack(pady=15, fill="x")

    window.mainloop()






if __name__ == "__main__":
    #Stage.stage_starte_gui()
    #settings_stage = loaded_settings_from_file()
    get_user_settings_from_gui(mygui:json_data, meanline_data, thermo_data) 


'''
