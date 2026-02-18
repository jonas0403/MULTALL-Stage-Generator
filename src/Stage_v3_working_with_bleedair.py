# Author: Marco Wiens
# Modified by: Jonas Scholz
# Version: 01.10.2025
# Stage
# Programm for calculation of blade geometry and creating the data for MULTALL

import math 
import numpy as np
import matplotlib.pyplot as plt
import csv
import os 
import sys
import shutil 
from matplotlib.widgets import Slider
import tkinter as tk
from tkinter import filedialog


import tkinter as tk
from tkinter import ttk, filedialog, Label, Toplevel

from Cubspline_function_v2 import cubspline
from Fixed_radii_Meanline_GUI_v4 import meanline 
from Radial_equilibrium import radial_equilibrium_R, radial_equilibrium_S
from Bezier_curve import bezier
from Interpolation import intpol, intp_new
from Channel_v2 import channel

wdpath = os.getcwd()
   
#print(wdpath)

scriptpath = os.path.dirname(sys.argv[0])

#print(scriptpath)
os.chdir(scriptpath)

# parameter for radial equilibrium
stage = 1
approach = 1
constant_r_parameter = 1


LOCK_FILE = 'settings.lock'

h_H = [0.0, 0.2, 0.5, 0.8, 1.0]
LE_shift = 0.025
Pi = math.pi


#Radial distribution of Temperature:
def plot_temp_alpha_beta(T_Plot, beta_R_Plot, alpha_S_Plot):
    #Temp plot
    if T_Plot == 1:
        plt.plot(T_S_out, h_rel, label = "T_out'")
        plt.plot(T_R_in, h_rel, label = 'T_in"')
        plt.plot(T_R_out, h_rel, label = "T_out'' = T_in'")
        plt.legend()
        plt.show()
        
    #Beta plot
    if beta_R_Plot == 1:
        plt.plot(beta_blade_R_in, h_rel, label = "beta_blade_R_in'")
        plt.plot(beta_blade_R_out, h_rel, label = "beta_blade_R_out'")
        plt.plot(beta_R_in, h_rel, label = "beta_R_in'")
        plt.plot(beta_R_out, h_rel, label = "beta_R_out''")
        plt.legend()
        plt.show()

    # Alpha plot
    if alpha_S_Plot == 1:
        plt.plot(alpha_S_in, h_rel, label = "alpha_S_in'")
        plt.plot(alpha_S_out, h_rel, label = "alpha_S_out'")
        plt.plot(beta_blade_S_in, h_rel, label = "beta_blade_S_in''")
        plt.plot(beta_blade_S_out, h_rel, label = "beta_blade_S_out''")
        plt.legend()
        plt.show()



#function for writing Bézier-points
def bezier_control_points(file, row, angle_in, angle_out, chord_length):
    
    with open(file, "w+") as file:
        file.write("For each level h/H = [0, 0.2, 0.5, 0.8, 1.0], there are four control points for the blade angle beta_S and the thickness d/l. The first and last control points for the blade angle beta_S are determined by radial equilibrium.\n\n")
        
        beta_S_BP_1, beta_S_BP_2, beta_S_BP_3, beta_S_BP_4 = [],[],[],[]
        alpha_S_BP_1, alpha_S_BP_2, alpha_S_BP_3, alpha_S_BP_4 = [],[],[],[]
        
        # Calculated values for NACA similar
        c_03 = 0.277558
        c_08 = 0.165432
        
        for i in range(len(h_H)):
            for j in range(len(h_rel)):
                if row == 1:
                    if h_rel[j] == h_H[i]:
                        beta_1 = angle_in[j]
                        beta_2 = angle_out[j]
                        
                        delta_beta_0 = beta_2 - beta_1
                        
                        beta_new_03 = beta_1 - delta_beta_0 * c_03
                        beta_new_08 = beta_1 - delta_beta_0 * c_08
                        
                        beta_S_BP_1.append(round(angle_in[j], 2))
                        beta_S_BP_4.append(round(angle_out[j], 2))
                        beta_S_BP_2.append(round(beta_new_03, 2))
                        beta_S_BP_3.append(round(beta_new_08, 2))
                elif row == 2:
                    if h_rel[j] == h_H[i]:
                        alpha_1 = alpha_S_in[i]
                        alpha_2 = alpha_S_out[i]
                        
                        delta_alpha_0 = alpha_2 - alpha_1
                        
                        alpha_new_03 = alpha_1 - delta_alpha_0 * c_03
                        alpha_new_08 = alpha_1 - delta_alpha_0 * c_08
                        
                        alpha_S_BP_1.append(round(alpha_S_in[j], 2))
                        alpha_S_BP_4.append(round(alpha_S_out[j], 2))
                        alpha_S_BP_2.append(round(alpha_new_03, 2))
                        alpha_S_BP_3.append(round(alpha_new_08, 2))
                
        if row == 1:
            file.write("1st to 4th control points for beta_S for all levels:\n")
            for i in range(5):
                file.write(f"{beta_S_BP_1[i]}")
                if i != 4:
                    file.write(", ")
            file.write("\n")

            for i in range(5):
                file.write(f"{beta_S_BP_2[i]}")
                if i != 4:
                    file.write(", ")
            file.write("\n")
            
            for i in range(5):
                file.write(f"{beta_S_BP_3[i]}")
                if i != 4:
                    file.write(", ")            
            file.write("\n")

            for i in range(5):
                file.write(f"{beta_S_BP_4[i]}")
                if i != 4:
                    file.write(", ")
            file.write("\n")
            file.write("\n")
            file.write("1st to 4th control points for d/l for all levels:\n")
            
            
            # Relative NACA values 
            
            rel_thick = np.array([[0.023, 0.020, 0.015, 0.011, 0.007],
                                  [0.082, 0.071, 0.055, 0.038, 0.027],
                                  [0.017, 0.015, 0.011, 0.008, 0.005],
                                  [0.010, 0.009, 0.007, 0.005, 0.003]])
            
            abs_thick = rel_thick * chord_length
            
            
            for i in range(abs_thick.shape[0]):
                val_write = [f"{value:.3f}" for value in abs_thick[i,:]]
                
                file.write(",".join(val_write))
                file.write("\n")

            #file.write('2.71,2.37,1.86,1.46,1.27\n')
            #file.write('3.58,3.13,2.45,1.93,1.68\n')
            #file.write('3.58,3.13,2.45,1.93,1.68\n')
            #file.write('2.71,2.37,1.86,1.46,1.27\n')
                                    
            file.write("\n")
            file.write("m* for all levels:\n")
            file.write("0.0, 0.0, 0.0, 0.0, 0.0\n")
            file.write("0.3, 0.3, 0.3, 0.3, 0.3\n")
            file.write("0.7, 0.7, 0.7, 0.7, 0.7\n")
            file.write("1.0, 1.0, 1.0, 1.0, 1.0\n") 

        elif row == 2:
            file.write("1st to 4th control points for alpha_S for all levels:\n")
            for i in range(5):
                file.write(f"{alpha_S_BP_1[i]}")
                if i != 4:
                    file.write(", ")
            file.write("\n")

            for i in range(5):
                file.write(f"{alpha_S_BP_2[i]}")
                if i != 4:
                    file.write(", ")
            file.write("\n")
            
            for i in range(5):
                file.write(f"{alpha_S_BP_3[i]}")
                if i != 4:
                    file.write(", ")            
            file.write("\n")

            for i in range(5):
                file.write(f"{alpha_S_BP_4[i]}")
                if i != 4:
                    file.write(", ")
            file.write("\n")
            file.write("\n")
            file.write("1st to 4th control points for d/l for all levels:\n")
            
             # Relative NACA values 
            
            rel_thick = np.array([[0.015, 0.015, 0.015, 0.015, 0.015],
                                  [0.058, 0.058, 0.058, 0.058, 0.058],
                                  [0.011, 0.011, 0.011, 0.011, 0.011],
                                  [0.006, 0.006, 0.006, 0.006, 0.006]])
        
            
            abs_thick = rel_thick * chord_length[2]
            
            for i in range(abs_thick.shape[0]):
                val_write = [f"{value:.3f}" for value in abs_thick[i,:]]
                
                file.write(",".join(val_write))
                file.write("\n")
            
            
            #file.write('1.42, 1.48, 1.54, 1.59, 1.61\n')
            #file.write('2.93, 3.06, 3.19, 3.28, 3.32\n')
            #file.write('2.93, 3.06, 3.19, 3.28, 3.32\n')
            #file.write('1.42, 1.48, 1.54, 1.59, 1.61\n')
   
            file.write("\n")
            file.write("m* for all levels:\n")
            file.write("0.0, 0.0, 0.0, 0.0, 0.0\n")
            file.write("0.3, 0.3, 0.3, 0.3, 0.3\n")
            file.write("0.7, 0.7, 0.7, 0.7, 0.7\n")
            file.write("1.0, 1.0, 1.0, 1.0, 1.0\n") 

def create_default_profiles(self):
    
    if not os.path.exists("bezier_control_points_R.txt"):
        print("Generiere default Rotor File")
        chord_length_R =  np.interp(h_H, h_rel, l_R) # Interpoliert die Sehnenlänge für die Standard Abschnitte
        bezier_control_points("bezier_control_points_R.txt", 1, beta_blade_R_in, beta_blade_R_out, chord_length_R)
    if not os.path.exists("bezier_control_points_S.txt"):
        print("Generiere default Stator File")
        chord_length_S =  np.interp(h_H, h_rel, l_S)
        bezier_control_points("bezier_control_points_S.txt", 2, beta_blade_S_in, beta_blade_S_out, chord_length_S)
    
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
            print(f"Profil erfolgreich gespeichert in {filepath}")
        except Exception as e:
            print(f"Error {e} beim speichern")                                                        

def run_main_logic(new_adjustment_data):
    
    global mflow, RPM, kappa, R, cp, i_st, T_t1, T_t2, T_t3, T_1, T_2, T_3, p_1, p_2, p_3, p_t1, p_t2, p_t3
    global D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_m1, D_m2, D_m3, b1, b2, b3
    global cu1, cu2, cu3, u1, u2, u3, cm1, cm2, cm3, delta_h_t, l_R, l_S
    global l_R_t_R, l_S_t_S, d_R_l_R, d_S_l_S, incidence_R, incidence_S, z_R, z_S
    global beta_blade_1, beta_blade_2, alpha_blade_2, alpha_blade_3, TPR_M, eta_sC_tt_M, eta_pC_tt_M, fixed_radius_type
    global h_rel, l_S_rad, c_m_S_in, c_m_S_out, c_u_S_in, c_u_S_out, c_S_out, T_S_in, T_S_out, p_S_in, p_S_out, alpha_S_in, beta_S_in, alpha_S_out, beta_blade_S_in, beta_blade_S_out, D_S
    global l_R_rad, r_R_out, c_m_R_in, c_m_R_out, c_u_R_in, c_u_R_out, c_R_out, u_R_in, u_R_out, T_R_in, T_R_out, p_R_in, p_R_out, Ma_abs_R_in, Ma_rel_R_in, roh_R_in, alpha_R_in, beta_R_in, alpha_R_out, beta_R_out, beta_blade_R_in, beta_blade_R_out, D_R

    global x_values, r_values, m_prime_values, x0
    
    results_meanline = meanline(GUI_On=0)

    (mflow, RPM, kappa, R, cp, i_st, T_t1, T_t2, T_t3, T_1, T_2, T_3, p_1, p_2, p_3, p_t1, p_t2, p_t3, 
    D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_m1, D_m2, D_m3, b1, b2, b3, cu1, cu2, cu3, u1, u2, u3, 
    cm1, cm2, cm3, delta_h_t, l_R, l_S, l_R_t_R, l_S_t_S, d_R_l_R, d_S_l_S, incidence_R, incidence_S, 
    z_R, z_S, beta_blade_1, beta_blade_2, alpha_blade_2, alpha_blade_3, TPR_M, eta_sC_tt_M, eta_pC_tt_M, 
    fixed_radius_type) = results_meanline

    # values from radial equilibrium
    h_rel, l_S, c_m_S_in, c_m_S_out, c_u_S_in, c_u_S_out, c_S_out, T_S_in, T_S_out, p_S_in, p_S_out, alpha_S_in, beta_S_in, alpha_S_out, beta_blade_S_in, beta_blade_S_out, D_S = radial_equilibrium_S(stage, approach, constant_r_parameter, D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_m1, D_m2, D_m3, b1, b2, b3, cu1, cu2, cu3, u1, u2, u3, cm1, cm2, cm3, delta_h_t, T_t1, T_t2, T_t3, p_t1, p_t2, p_t3)
    h_rel, l_R, r_R_out, c_m_R_in, c_m_R_out, c_u_R_in, c_u_R_out, c_R_out, u_R_in, u_R_out, T_R_in, T_R_out, p_R_in, p_R_out, Ma_abs_R_in, Ma_rel_R_in, roh_R_in, alpha_R_in, beta_R_in, alpha_R_out, beta_R_out, beta_blade_R_in, beta_blade_R_out, D_R = radial_equilibrium_R(stage, approach, constant_r_parameter, D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_m1, D_m2, D_m3, b1, b2, b3, cu1, cu2, cu3, u1, u2, u3, cm1, cm2, cm3, delta_h_t, T_t1, T_t2, T_t3, p_t1, p_t2, p_t3)
    print("Successfully calculated meanline and radial equilibrium")

    main_choice = new_adjustment_data.get('main_choice', 'default')
    #path = settings.get("output_folder", ".")
    #NROW = int(settings.get("nrow", 2))
    levels_input = new_adjustment_data.get("levels", "0.0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 0.95, 1.00")
    h_H = [0.0, 0.2, 0.5, 0.8, 1.0] # Standard Werte für die Abschnitte
    

    levels_input = [float(x.strip()) for x in levels_input.split(',')] # Liest die Levels ein und wandelt sie in eine Liste von Float-Werten um
    
    #chord_length_R = np.interp(h_H, h_rel, l_R) # Interpoliert die Sehnenlänge für die Standard Abschnitte
    #chord_length_S = np.interp(h_H, h_rel, l_S) 

    
    if main_choice == 'adjust': # Anpassung der Bézier Punkte
        try:
            
            section_idx_str = new_adjustment_data['adjust_section_idx']
            section_idx_float = float(section_idx_str)
            section_idx = h_H.index(section_idx_float)
            
            row_str = new_adjustment_data['adjust_row']
            parameter_str = new_adjustment_data['adjust_parameter']
            h_val = h_H[section_idx] 
            is_rotor = row_str == 'Rotor' # True für Rotor, False für Stator
            row_num = 1 if is_rotor else 2 # 1 für Rotor, 2 für Stator
            bcp_file = "bezier_control_points_R.txt" if is_rotor else "bezier_control_points_S.txt"
            bcp_header = "beta_S" if is_rotor else "alpha_S"
               
            with open(bcp_file, 'r') as file:
                lines = file.readlines()
        
            beta_points_all = []
            d_l_points_all = []
        
            for i, line in enumerate(lines): #"enumerate" gibt sowohl den Index als auch den Wert der Zeile zurück
                if line.strip().startswith(f"1st to 4th control points for {bcp_header}"): # sucht nach der Zeile mit dem Header
                    raw_data =[lines[i+j+1].strip().split(',') for j in range(4)] # Liest die nächsten 4 Zeilen ein und teilt sie bei Kommas
                    beta_points_all = [[float(raw_data[j][k]) for j in range(4)] for k in range(5)] # Transponieren der Daten zur weiteren Benutzung
                    break
    
            for i, line in enumerate(lines):
                if line.strip().startswith(f"1st to 4th control points for d/l"):
                    raw_data =[lines[i+j+1].strip().split(',') for j in range(4)]
                    d_l_points_all = [[float(raw_data[j][k]) for j in range(4)] for k in range(5)]
                    break
            
            print(f"Debugging: Gelesener Parameter ist: {parameter_str}")
    
            # Je nach ausgewähltem Parameter die entsprechenden Bézier-Punkte anpassen
            if parameter_str == 'Angle':
                print(f"Adjustments for Angle in row {row_str}, section: {h_val}")
                original_points = beta_points_all[section_idx] # Liste der Bézier-Punkte für den ausgewählten Abschnitt
                new_points = adjustBezierCurve_beta(original_points) # Ruft die Funktion zum Anpassen der Bézier-Punkte auf
                beta_points_all[section_idx] = new_points # Aktualisiert die Bézier-Punkte in der Liste
    
            elif parameter_str == 'Thickness':
                print(f"Adjustments for Thickness in row {row_str}, section: {h_val}")
                chord, *_ = calculation_of_section(h_val, row_num) #
                original_points = d_l_points_all[section_idx]
                new_points = adjustBezierCurve_d(original_points, chord)
                d_l_points_all[section_idx] = new_points 

            # Speichern der aktualisierten Bézier-Punkte zurück in die Datei
            with open(bcp_file, "w+", newline='') as file:
                file.write("For each level h/H = [0, 0.2, 0.5, 0.8, 1.0]\n\n")
                file.write(f"1st to 4th control points for {bcp_header} for all levels:\n")
                for i in range(4):
                    file.write(','.join(map(str, [beta_points_all[j][i] for j in range(5)])) + '\n')
                file.write("\n1st to 4th control points for d/l for all levels:\n")
                for i in range(4):
                    file.write(','.join(map(str, [d_l_points_all[j][i] for j in range(5)])) + '\n')
                file.write("\n")
                file.write("m* for all levels:\n")
                file.write("0.0,0.0,0.0,0.0,0.0\n0.3,0.3,0.3,0.3,0.3\n0.7,0.7,0.7,0.7,0.7\n1.0,1.0,1.0,1.0,1.0\n")  
            
            channel(results_meanline)    
            print(f"Veränderungen wurden gespeichert in {bcp_file}")
            save_profile(bcp_file)
            
                              
        except(IOError, IndexError, ValueError) as e:
            print(f"Error {e}")
            return
    
    return {
        'cp':                      cp,
        'kappa':                   kappa,
        'RPM':                     RPM,
        'z_R':                     z_R,
        'z_S':                     z_S,
        'h_rel':                   h_rel,
        'p_1':                     p_1,
        'p_2':                     p_2,
        'p_3':                     p_3,
        'p_R_in':                  p_R_in,
        'p_R_out':                 p_R_out,
        'p_S_in':                  p_S_in,
        'p_S_out':                 p_S_out,
        'p_t1':                    p_t1,
        'T_t1':                    T_t1,
        'cm1':                     cm1,
        'D_S1':                    D_S1,
        'D_H1':                    D_H1,
        'enable_bleed_air':        enable_bleed_air,
        'h_rel':                   h_rel,

        'calculation_of_section':    calculation_of_section,
        'calc_blade_row_coordinates': calc_blade_row_coordinates,
    }  
    
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

# if adjust_rotor_thickness == 1:
#     for i in range(5):
#         d_l_BP_R_new[i] = adjustBezierCurve_d(d_l_BP_R_new[i], length[i])

# if adjust_rotor_angle == 1:
#     for i in range(5):
#         beta_S_BP_R_new[i] = adjustBezierCurve_beta(beta_S_BP_R_new[i])

# with open('bezier_control_points_R.txt', "w+") as file:
#     file.write("For each level h/H = [0, 0.2, 0.5, 0.8, 1.0], there are four control points for the blade angle beta_S and the thickness d/l. The first and last control points for the blade angle beta_S are determined by radial equilibrium.\n\n")

#     file.write("1st to 4th control points for beta_S for all levels:\n")
#     for i in range(4):
#         file.write(f"{beta_S_BP_R_new[0][i]},{beta_S_BP_R_new[1][i]},{beta_S_BP_R_new[2][i]},{beta_S_BP_R_new[3][i]},{beta_S_BP_R_new[4][i]}\n")

#     file.write("\n")
#     file.write("1st to 4th control points for d/l for all levels:\n")

#     for i in range(4):
#         file.write(f"{d_l_BP_R_new[0][i]},{d_l_BP_R_new[1][i]},{d_l_BP_R_new[2][i]},{d_l_BP_R_new[3][i]},{d_l_BP_R_new[4][i]}\n")
                    
#     file.write("\n")
#     file.write("m* for all levels:\n")
    
#     file.write("0.0, 0.0, 0.0, 0.0, 0.0\n")
#     file.write("0.3, 0.3, 0.3, 0.3, 0.3\n")
#     file.write("0.7, 0.7, 0.7, 0.7, 0.7\n")
#     file.write("1.0, 1.0, 1.0, 1.0, 1.0\n")
    

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
#             d_l_read[i] = [float(val) for val in row]

#         for i in range(5):
#             d_l_BP_S_new[i] = [d_l_read[0][i], d_l_read[1][i], d_l_read[2][i], d_l_read[3][i]]

#     if adjust_stator_thickness == 1:
#         for i in range(5):
#             d_l_BP_S_new[i] = adjustBezierCurve_d(d_l_BP_S_new[i], length[i])

#     if adjust_stator_angle == 1:
#         for i in range(5):
#             beta_S_BP_S_new[i] = adjustBezierCurve_beta(beta_S_BP_S_new[i])

#     with open('bezier_control_points_S.txt', "w+") as file:
#         file.write("For each level h/H = [0, 0.2, 0.5, 0.8, 1.0], there are four control points for the blade angle beta_S and the thickness d/l. The first and last control points for the blade angle beta_S are determined by radial equilibrium.\n\n")

#         file.write("1st to 4th control points for alpha_S for all levels:\n")
#         for i in range(4):
#             file.write(f"{beta_S_BP_S_new[0][i]},{beta_S_BP_S_new[1][i]},{beta_S_BP_S_new[2][i]},{beta_S_BP_S_new[3][i]},{beta_S_BP_S_new[4][i]}\n")

#         file.write("\n")
#         file.write("1st to 4th control points for d/l for all levels:\n")

#         for i in range(4):
#             file.write(f"{d_l_BP_S_new[0][i]},{d_l_BP_S_new[1][i]},{d_l_BP_S_new[2][i]},{d_l_BP_S_new[3][i]},{d_l_BP_S_new[4][i]}\n")
                        
#         file.write("\n")
#         file.write("m* for all levels:\n")
        
#         file.write("0.0, 0.0, 0.0, 0.0, 0.0\n")
#         file.write("0.3, 0.3, 0.3, 0.3, 0.3\n")
#         file.write("0.7, 0.7, 0.7, 0.7, 0.7\n")
#         file.write("1.0, 1.0, 1.0, 1.0, 1.0\n")

#     # 0: all sections or any number between 1 and NSECS
#     section = 0   
#     print(f"rotor_patches = {rotor_patches_data}")
                                                           


# general values, ellipis of LE and TE
def overall_values(row, z_R, l_R, l_S):
    if row == 1:
        z = z_R
        # lenth of rotor blade h_rel = 50%
        s_1D = round(l_R[10]/1000, 4)                   
        s_0_5 = s_1D
        elipse_LE = 3
        elipse_TE = 3
    
    elif row == 2:
        z = z_S
        # lenth of rotor blade h_rel = 50%
        s_1D = round(l_S[10]/1000, 4)                      
        s_0_5 = s_1D
        elipse_LE = 3
        elipse_TE = 4
    
    # beginning of LE
    x_LE = []
    for i in range(len(h_H)):
        x_LE.append(round((-2*LE_shift*h_H[i]+LE_shift),5))  

    return z, s_1D, s_0_5, x_LE, elipse_LE, elipse_TE

'''
Old bezier control points from csv read
# Bézier control points from csv file
def blade_metal_BP(ROW):
    beta_M_e, beta_M_2, beta_M_3, beta_M_a, d_l_e, d_l_2, d_l_3, d_l_a = [], [], [], [], [], [], [], []   #beta_M_e: Liste mit Schaufeleintrittswinkel (Metall) für alle relativen Höhen aus h/H 
    m_star_BP = [[], [], [], []]
    if ROW == 1:
        BCPfile = "bezier_control_points_R.txt"
    elif ROW == 2:
        BCPfile = "bezier_control_points_S.txt"
    
    with open(BCPfile, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 3:
                for value in row:
                    beta_M_e.append(float(value))
            elif i == 4:
                for value in row:
                    beta_M_2.append(float(value))
            elif i == 5:
                for value in row:
                    beta_M_3.append(float(value))            
            elif i == 6:
                for value in row:
                    beta_M_a.append(float(value))
            elif i == 9:
                for value in row:
                    d_l_e.append(float(value))
            elif i == 10:
                for value in row:
                    d_l_2.append(float(value))
            elif i == 11:
                for value in row:
                    d_l_3.append(float(value))
            elif i == 12:
                for value in row:
                    d_l_a.append(float(value))
            elif i == 15:
                for value in row:
                    m_star_BP[0].append(float(value))
            elif i == 16:
                for value in row:
                    m_star_BP[1].append(float(value))
            elif i == 17:
                for value in row:
                    m_star_BP[2].append(float(value))
            elif i == 18:
                for value in row:
                    m_star_BP[3].append(float(value))

    return beta_M_a, beta_M_2, beta_M_3,  beta_M_e, d_l_a, d_l_2, d_l_3, d_l_e, m_star_BP
'''

# Bézier control points from csv file new
def blade_metal_BP(ROW):
    # beta_M_e, beta_M_2, beta_M_3, beta_M_a = [], [], [], []
    # d_l_e, d_l_2, d_l_3, d_l_a = [], [], [], []
    # m_star_BP = [[], [], [], []] 
    
    if ROW == 1:
        BCPfile = "bezier_control_points_R.txt"
        angle_header = "1st to 4th control points for beta_S for all levels:"
    elif ROW == 2:
        BCPfile = "bezier_control_points_S.txt"
        angle_header = "1st to 4th control points for alpha_S for all levels:"
    else:
        return [], [], [], [], [], [], [], [], [[], [], [], []]
        
    
    try:
        with open(BCPfile, 'r') as file:
            lines = file.readlines()
    except (FileNotFoundError) as e:
        print(f"Fehler beim lesen {BCPfile}: {e}")
        return [], [], [], [], [], [], [], [], [[], [], [], []]
    
    def find_and_read_data(header_text):
        data_block = []
        header_found_at = -1
        
        
        for i, line in enumerate(lines):
            if line.strip() == header_text:
                header_found_at = i
      
                break
            
        
        if header_found_at != -1 and len(lines) >= header_found_at + 5:
            for i in range(1, 5):
                data_row = [float(val) for val in lines[header_found_at + i].strip().split(',')]
                data_block.append(data_row)
            
        return data_block
    
    
    angle_data = find_and_read_data(angle_header)
    d_l_data = find_and_read_data("1st to 4th control points for d/l for all levels:") 
    m_star_data = find_and_read_data("m* for all levels:")
    
    beta_M_e, beta_M_2, beta_M_3, beta_M_a = (angle_data + [[]]*4)[:4] # stellt sicher, dass immer 4 Listen zurückgegeben werden, wenn weniger als 4 vorhanden sind wird aufgefüllt mit leeren Listen
    d_l_e, d_l_2, d_l_3, d_l_a = (d_l_data + [[]]*4)[:4]
    m_star_BP = (m_star_data + [[]]*4)[:4]
    
    return beta_M_a, beta_M_3, beta_M_2, beta_M_e, d_l_a, d_l_3, d_l_2, d_l_e, m_star_BP 

#Section to fix center of gravity for all sections
#Calculation for h/H = 0.5 cut
def calculation_of_section_0_5(row):
    rel_h = 0.5

    beta_M_a, beta_M_2, beta_M_3,  beta_M_e, d_l_a, d_l_2, d_l_3, d_l_e, m_star_BP= blade_metal_BP(row)
    z, s_1D, s_0_5, x_LE, elipse_LE, elipse_TE = overall_values(row, z_R, l_R, l_S)
    
    LE_TE_fac_1 = [0.0, 2.0, 5.0, 9.0, 15.0, 22.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0]
     
    LE_TE_fac_2 = LE_TE_fac_1.copy()
    LE_TE_fac_2.reverse()

    k = 125-2*len(LE_TE_fac_1)
    Nulls = [0.0]*k
    LE_TE_fac = LE_TE_fac_1 + Nulls + LE_TE_fac_2

    m_BP = []
    for i in range(4): 
        m_BP.append(cubspline(3, rel_h, h_H, m_star_BP[i]))

    beta_BP = []    
    beta_BP.append(cubspline(3, rel_h, h_H, beta_M_e))
    beta_BP.append(cubspline(3, rel_h, h_H, beta_M_2))
    beta_BP.append(cubspline(3, rel_h, h_H, beta_M_3))
    beta_BP.append(cubspline(3, rel_h, h_H, beta_M_a))

    d_l_BP =[]
    d_l_BP.append(cubspline(3, rel_h, h_H, d_l_e)/200)
    d_l_BP.append(cubspline(3, rel_h, h_H, d_l_2)/200)
    d_l_BP.append(cubspline(3, rel_h, h_H, d_l_3)/200)
    d_l_BP.append(cubspline(3, rel_h, h_H, d_l_a)/200)
    
    FAK_m_LE = elipse_LE*d_l_BP[0]/bezier(4, elipse_LE*d_l_BP[0], m_BP)
    FAK_m_TE = (1-elipse_TE*d_l_BP[3])/bezier(4, 1-elipse_TE*d_l_BP[3], m_BP)
    
    t_LE = []
    for i in range(len(LE_TE_fac_1)):
        t_LE.append((1-math.cos(Pi*LE_TE_fac_1[i]/180))*elipse_LE*d_l_BP[0]*FAK_m_LE)

    t_TE = []
    for i in range(len(LE_TE_fac_2)):
        t_TE.append((1-(1-math.cos(Pi*LE_TE_fac_2[i]/180))*elipse_TE*d_l_BP[3]*FAK_m_TE))

    Dt = (round(t_TE[0], 3)-round(t_LE[12], 3))/100

    t = []
    t = t_LE
    for i in range(len(Nulls)):
        t.append(t[-1]+Dt)

    t += t_TE 

    m_prime = []      
    for i in range(len(t)):
        m_prime.append(bezier(4, t[i], m_BP))

    beta_S = []
    for i in range(len(t)):
        beta_S.append(bezier(4, m_prime[i], beta_BP))

    R_theta_s_prime = [0.0]
    for i in range(len(t)-1):
        R_theta_s_prime.append(R_theta_s_prime[-1]+1/math.tan((beta_S[i] + beta_S[i+1])/2*Pi/180) *(m_prime[i+1]-m_prime[i]))

    s_star = math.sqrt(1+R_theta_s_prime[124]**2)

    p = (len(LE_TE_fac_1)-1)
    q = (len(Nulls))
    
    d_l = []
    for i in range(len(m_prime)):
        if i <= p:
            d_l.append(bezier(4,m_prime[i], d_l_BP)*math.sin(Pi*LE_TE_fac[i]/180))
        elif i > p and i <= p+q+1:
            d_l.append(bezier(4, m_prime[i], d_l_BP))
        elif i > p+q+1:
            d_l.append(bezier(4, m_prime[i], d_l_BP)*math.sin(Pi*LE_TE_fac[i]/180))
        
    m_prime_u, m_prime_l =[], []
    for i in range(0, len(m_prime)):
        if i == 0:
            m_prime_u.append(m_prime[i]-d_l[i]*(R_theta_s_prime[i+1]-R_theta_s_prime[i])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i])**2+(m_prime[i+1]-m_prime[i])**2))
            m_prime_l.append(m_prime[i]+d_l[i]*(R_theta_s_prime[i+1]-R_theta_s_prime[i])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i])**2+(m_prime[i+1]-m_prime[i])**2))
        elif i>0 and i<124:
            m_prime_u.append(m_prime[i]-d_l[i]*(R_theta_s_prime[i+1]-R_theta_s_prime[i-1])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i-1])**2+(m_prime[i+1]-m_prime[i-1])**2))
            m_prime_l.append(m_prime[i]+d_l[i]*(R_theta_s_prime[i+1]-R_theta_s_prime[i-1])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i-1])**2+(m_prime[i+1]-m_prime[i-1])**2))
        elif i == 124:
            m_prime_u.append(m_prime[i]-d_l[i]*(R_theta_s_prime[i]-R_theta_s_prime[i-1])/math.sqrt((R_theta_s_prime[i]-R_theta_s_prime[i-1])**2+(m_prime[i]-m_prime[i-1])**2))
            m_prime_l.append(m_prime[i]+d_l[i]*(R_theta_s_prime[i]-R_theta_s_prime[i-1])/math.sqrt((R_theta_s_prime[i]-R_theta_s_prime[i-1])**2+(m_prime[i]-m_prime[i-1])**2))

    R_theta_s_prime_u, R_theta_s_prime_l = [], []
    for i in range(len(m_prime)):
        if i == 0:
            R_theta_s_prime_u.append(R_theta_s_prime[i]+s_star*d_l[i]*(m_prime[i+1]-m_prime[i])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i])**2+(m_prime[i+1]-m_prime[i])**2))
            R_theta_s_prime_l.append(R_theta_s_prime[i]-s_star*d_l[i]*(m_prime[i+1]-m_prime[i])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i])**2+(m_prime[i+1]-m_prime[i])**2))
        elif i>0 and i<124:
            R_theta_s_prime_u.append(R_theta_s_prime[i]+s_star*d_l[i]*(m_prime[i+1]-m_prime[i-1])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i-1])**2+(m_prime[i+1]-m_prime[i-1])**2))
            R_theta_s_prime_l.append(R_theta_s_prime[i]-s_star*d_l[i]*(m_prime[i+1]-m_prime[i-1])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i-1])**2+(m_prime[i+1]-m_prime[i-1])**2))
        elif i == 124:
            R_theta_s_prime_u.append(R_theta_s_prime[i]+s_star*d_l[i]*(m_prime[i]-m_prime[i-1])/math.sqrt((R_theta_s_prime[i]-R_theta_s_prime[i-1])**2+(m_prime[i]-m_prime[i-1])**2))
            R_theta_s_prime_l.append(R_theta_s_prime[i]-s_star*d_l[i]*(m_prime[i]-m_prime[i-1])/math.sqrt((R_theta_s_prime[i]-R_theta_s_prime[i-1])**2+(m_prime[i]-m_prime[i-1])**2))

    # section for new calculation of upper/lower side coordinates 
    def min_max(m_prime):
        m_prime_min = float('inf') 
        pos_m_prime_min = 0
        m_prime_max = float('-inf')  
        pos_m_prime_max = 0
        
        for i in range(len(m_prime_u)):
            if m_prime[i] <= m_prime_min:
                m_prime_min = m_prime[i]
                pos_m_prime_min = i
            elif m_prime[i] >= m_prime_max:
                m_prime_max = m_prime[i]
                pos_m_prime_max = i
            
        return pos_m_prime_min, pos_m_prime_max

    pos_m_prime_min_u, pos_m_prime_max_u = min_max(m_prime_u)        
    pos_m_prime_min_l, pos_m_prime_max_l = min_max(m_prime_l)        

    def global_maxima(pos_m_prime_min_u, pos_m_prime_min_l, pos_m_prime_max_u, pos_m_prime_max_l):
        pos_m_prime_min = float('inf')  
        pos_m_prime_max = float('-inf')

        m_prime_min = min(m_prime_u[pos_m_prime_min_u], m_prime_l[pos_m_prime_min_l])
        m_prime_max = max(m_prime_u[pos_m_prime_max_u], m_prime_l[pos_m_prime_max_l])
        
        return pos_m_prime_min, pos_m_prime_max, m_prime_min, m_prime_max

    pos_m_prime_min, pos_m_prime_max, m_prime_min, m_prime_max = global_maxima(pos_m_prime_min_u, pos_m_prime_min_l, pos_m_prime_max_u, pos_m_prime_max_l)
    
    if m_prime_min == m_prime_u[pos_m_prime_min_u]:
        pos_m_prime_min = pos_m_prime_min_u
        
        if m_prime_max == m_prime_u[pos_m_prime_max_u]:    
            pos_m_prime_max = pos_m_prime_max_u
            
            #supporting lists:
            helping_list_m = m_prime_u[0:pos_m_prime_min+1]
            helping_list_m.reverse()
            helping_list_m2 = m_prime_u[pos_m_prime_max:]
            helping_list_m2.reverse()

            helping_list_R = R_theta_s_prime_u[0:pos_m_prime_min+1]
            helping_list_R.reverse()
            helping_list_R2 = R_theta_s_prime_u[pos_m_prime_max:]
            helping_list_R2.reverse()
            
            #new upper side
            m_prime_u = m_prime_u[pos_m_prime_min:pos_m_prime_max+1]
            R_theta_s_prime_u = R_theta_s_prime_u[pos_m_prime_min:pos_m_prime_max+1]
            
            #new lower side
            m_prime_l = helping_list_m + m_prime_l+ helping_list_m2
            R_theta_s_prime_l = helping_list_R + R_theta_s_prime_l + helping_list_R2
            
        elif m_prime_max == m_prime_l[pos_m_prime_max_l]:
            pos_m_prime_max = pos_m_prime_max_l 
            
            #supporting list:
            helping_list_m = m_prime_u[0:pos_m_prime_min]
            helping_list_m.reverse()   
            helping_list_R = R_theta_s_prime_u[0:pos_m_prime_min]
            helping_list_R.reverse()   

            #upper side
            m_prime_u = m_prime_u[pos_m_prime_min:]+m_prime_l[pos_m_prime_max:]
            R_theta_s_prime_u = R_theta_s_prime_u[pos_m_prime_min:] +R_theta_s_prime_u[pos_m_prime_max:]

            #lower side
            m_prime_l = helping_list_m + m_prime_l[0:pos_m_prime_max]
            R_theta_s_prime_l = helping_list_R + R_theta_s_prime_l[0:pos_m_prime_max]
            print("2")

    elif m_prime_min == m_prime_l[pos_m_prime_min_l]:
        pos_m_prime_min = pos_m_prime_min_l
        if m_prime_max == m_prime_u[pos_m_prime_max_u]:
            pos_m_prime_max = pos_m_prime_max_u

            #supporting lists:
            helping_list_m = m_prime_l[0:pos_m_prime_min_l+1] 
            helping_list_m.reverse()

            helping_list_m2 = m_prime_u[pos_m_prime_max:] 
            helping_list_m2.reverse()

            helping_list_R = R_theta_s_prime_l[0:pos_m_prime_min_l+1]
            helping_list_R.reverse()

            helping_list_R2 = R_theta_s_prime_u[pos_m_prime_max:]
            helping_list_R2.reverse()
            
            helping_list_d = d_l[1:pos_m_prime_min_l]
            helping_list_d.reverse()

            #upper side
            m_prime_u = helping_list_m + m_prime_u[0:pos_m_prime_max+1]
            R_theta_s_prime_u = helping_list_R + R_theta_s_prime_u[0:pos_m_prime_max+1]
            
            #lower side
            m_prime_l = m_prime_l[pos_m_prime_min:] + helping_list_m2
            R_theta_s_prime_l = R_theta_s_prime_l[pos_m_prime_min:] + helping_list_R2

        elif m_prime_max == m_prime_l[pos_m_prime_max_l]:
            pos_m_prime_max = pos_m_prime_max_l
            
            #supporting lists:
            helping_list_m = m_prime_l[0:pos_m_prime_min_l+1] 
            helping_list_m2 = m_prime_l[pos_m_prime_max:-1] 
            helping_list_m.reverse()
            helping_list_m2.reverse()

            helping_list_R = R_theta_s_prime_l[0:pos_m_prime_min_l+1]
            helping_list_R2 = R_theta_s_prime_l[pos_m_prime_max:-1] 
            helping_list_R.reverse()
            helping_list_R2.reverse()

            helping_list_d = d_l[1:pos_m_prime_min_l]
            helping_list_d2 = d_l[pos_m_prime_max:-1] 
            helping_list_d.reverse()
            helping_list_d2.reverse()

            #upper side
            m_prime_u = helping_list_m + m_prime_u + helping_list_m2  
            R_theta_s_prime_u = helping_list_R + R_theta_s_prime_u + helping_list_R2

            #lower side
            m_prime_l = m_prime_l[pos_m_prime_min:pos_m_prime_max+1]
            R_theta_s_prime_l = R_theta_s_prime_l[pos_m_prime_min:pos_m_prime_max+1]

    # check if first coordinate of upper and lower side are the same 
    if m_prime_l[0]!=m_prime_u[0]:
        print("not equal")

    dif_list_len_u = len(m_prime_u)-125
    
    if dif_list_len_u > 0:
        for i in range(dif_list_len_u):
            k = 15+i*4
            del m_prime_u[k]
            del R_theta_s_prime_u[k]

    elif dif_list_len_u < 0:
        for i in range(abs(dif_list_len_u)):
            k = 15+i*4
            new_m_value = m_prime_u[k]+(m_prime_u[k+1]-m_prime_u[k])/2
            m_prime_u.insert(k+1, new_m_value)
            new_Rtheta_value = R_theta_s_prime_u[k]+(R_theta_s_prime_u[k+1]-R_theta_s_prime_u[k])/2
            R_theta_s_prime_u.insert(k+1, new_Rtheta_value)

    dif_list_len_l = len(m_prime_l)-125
    
    if dif_list_len_l > 0:
        for i in range(dif_list_len_l):
            k = 15+i*4
            del m_prime_l[k]
            del R_theta_s_prime_l[k]

    elif dif_list_len_l < 0:
        for i in range(abs(dif_list_len_l)):
            k = 15+i*4
            new_m_value = m_prime_l[k]+(m_prime_l[k+1]-m_prime_l[k])/2
            m_prime_l.insert(k+1, new_m_value)
            new_Rtheta_value = R_theta_s_prime_l[k]+(R_theta_s_prime_l[k+1]-R_theta_s_prime_l[k])/2
            R_theta_s_prime_l.insert(k+1, new_Rtheta_value)
    
    # calculation of center of area 
    coa1, coa2, coa3 = [], [], []
    for i in range(len(m_prime)-1):
        coa1.append(math.sqrt((m_prime[i+1]-m_prime[i])**2+(R_theta_s_prime[i+1]-R_theta_s_prime[i])**2)*2*s_star*(d_l[i+1]+d_l[i])/2*(m_prime[i+1]+m_prime[i])/2)
        coa2.append(math.sqrt((m_prime[i+1]-m_prime[i])**2+(R_theta_s_prime[i+1]-R_theta_s_prime[i])**2)*2*s_star*(d_l[i+1]+d_l[i])/2*(R_theta_s_prime[i+1]+R_theta_s_prime[i])/2)
        coa3.append(math.sqrt((m_prime[i+1]-m_prime[i])**2+(R_theta_s_prime[i+1]-R_theta_s_prime[i])**2)*2*s_star*(d_l[i+1]+d_l[i])/2)

    coa1.append(sum(coa1))   
    coa2.append(sum(coa2))  
    coa3.append(sum(coa3))

    m_prime_cntr = coa1[124]/coa3[124]
    Rtet_prime_cntr = coa2[124]/coa3[124]

    if row == 1:
        k = 2
    elif row == 2:
        k = 5

    m_cntr_0_5 = m_prime_cntr*s_0_5/s_star*1000+x0[k]                               #m*cntr
    
    return  m_cntr_0_5, m_prime_cntr

# calculation of LE and TE coordinates
def mLE_TE_cntr(row):
    
    if row == 1:
        k = 2
    elif row == 2:
        k = 5
    
    m_cntr_0_5, m_prime_cntr = calculation_of_section_0_5(row)

    m_LE_0_5 = x0[k]
    m_TE_0_5 = m_cntr_0_5 + (m_cntr_0_5-m_LE_0_5)*(1-m_prime_cntr)/m_prime_cntr

    return m_LE_0_5, m_TE_0_5, m_cntr_0_5, m_prime_cntr

# calculation of a section coordiantes of a single row
def calculation_of_section(rel_h, row):

    m_LE_0_5, m_TE_0_5, m_cntr_0_5, m_prime_cntr = mLE_TE_cntr(row)
    beta_M_a, beta_M_2, beta_M_3,  beta_M_e, d_l_a, d_l_2, d_l_3, d_l_e, m_star_BP= blade_metal_BP(row)
    z, s_1D, s_0_5, x_LE, elipse_LE, elipse_TE = overall_values(row, z_R, l_R, l_S)
    
    LE_TE_fac_1 = [0.0, 2.0, 5.0, 9.0, 15.0, 22.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0]
    
    LE_TE_fac_2 = LE_TE_fac_1.copy()
    LE_TE_fac_2.reverse()

    k = 125-2*len(LE_TE_fac_1)
    Nulls = [0.0]*k
    LE_TE_fac = LE_TE_fac_1 + Nulls + LE_TE_fac_2
    

    m_BP = []
    for i in range(4): 
        m_BP.append(cubspline(3, rel_h, h_H, m_star_BP[i]))

    beta_BP = []    
    beta_BP.append(cubspline(3, rel_h, h_H, beta_M_e))
    beta_BP.append(cubspline(3, rel_h, h_H, beta_M_2))
    beta_BP.append(cubspline(3, rel_h, h_H, beta_M_3))
    beta_BP.append(cubspline(3, rel_h, h_H, beta_M_a))

    d_l_BP =[]
    d_l_BP.append(cubspline(3, rel_h, h_H, d_l_e)/100)
    d_l_BP.append(cubspline(3, rel_h, h_H, d_l_2)/100)
    d_l_BP.append(cubspline(3, rel_h, h_H, d_l_3)/100)
    d_l_BP.append(cubspline(3, rel_h, h_H, d_l_a)/100)
    

    FAK_m_LE = elipse_LE*d_l_BP[0]/bezier(4, elipse_LE*d_l_BP[0], m_BP)
    FAK_m_TE = (1-elipse_TE*d_l_BP[3])/bezier(4, 1-elipse_TE*d_l_BP[3], m_BP)

    t_LE = []
    for i in range(len(LE_TE_fac_1)):
        t_LE.append((1-math.cos(Pi*LE_TE_fac_1[i]/180))*elipse_LE*d_l_BP[0]*FAK_m_LE)
    
    t_TE = []
    for i in range(len(LE_TE_fac_2)):
        t_TE.append((1-(1-math.cos(Pi*LE_TE_fac_2[i]/180))*elipse_TE*d_l_BP[3]*FAK_m_TE))

    Dt = (round(t_TE[0], 3)-round(t_LE[12], 3))/100

    t = []
    t = t_LE
    for i in range(len(Nulls)):
        t.append(t[-1]+Dt)
    t += t_TE 
    
    m_prime = []                              
    for i in range(len(t)):
        m_prime.append(float(bezier(4, t[i], m_BP)))

    beta_S = []
    for i in range(len(t)):
        beta_S.append(bezier(4, m_prime[i], beta_BP))

    R_theta_s_prime = [0.0]
    for i in range(len(t)-1):
        R_theta_s_prime.append(R_theta_s_prime[-1]+1/math.tan((beta_S[i] + beta_S[i+1])/2*Pi/180) *(m_prime[i+1]-m_prime[i]))

    #Chordlength
    s_star = math.sqrt(1+R_theta_s_prime[124]**2)       
    p = (len(LE_TE_fac_1)-1)
    q = (len(Nulls))
    
    d_l = []
    for i in range(len(m_prime)):
        if i <= p:
            d_l.append(bezier(4,m_prime[i], d_l_BP)*math.sin(Pi*LE_TE_fac[i]/180))
        elif i > p and i <= p+q+1:
            d_l.append(bezier(4, m_prime[i], d_l_BP))
        elif i > p+q+1:
            d_l.append(bezier(4, m_prime[i], d_l_BP)*math.sin(Pi*LE_TE_fac[i]/180))


    m_prime_u, m_prime_l =[], []
    for i in range(len(m_prime)):
        if i == 0:
            m_prime_u.append(m_prime[i]-d_l[i]*(R_theta_s_prime[i+1]-R_theta_s_prime[i])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i])**2+(m_prime[i+1]-m_prime[i])**2))
            m_prime_l.append(m_prime[i]+d_l[i]*(R_theta_s_prime[i+1]-R_theta_s_prime[i])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i])**2+(m_prime[i+1]-m_prime[i])**2))
        elif i>0 and i<124:
            m_prime_u.append(m_prime[i]-d_l[i]*(R_theta_s_prime[i+1]-R_theta_s_prime[i-1])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i-1])**2+(m_prime[i+1]-m_prime[i-1])**2))
            m_prime_l.append(m_prime[i]+d_l[i]*(R_theta_s_prime[i+1]-R_theta_s_prime[i-1])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i-1])**2+(m_prime[i+1]-m_prime[i-1])**2))
        elif i == 124:
            m_prime_u.append(m_prime[i]-d_l[i]*(R_theta_s_prime[i]-R_theta_s_prime[i-1])/math.sqrt((R_theta_s_prime[i]-R_theta_s_prime[i-1])**2+(m_prime[i]-m_prime[i-1])**2))
            m_prime_l.append(m_prime[i]+d_l[i]*(R_theta_s_prime[i]-R_theta_s_prime[i-1])/math.sqrt((R_theta_s_prime[i]-R_theta_s_prime[i-1])**2+(m_prime[i]-m_prime[i-1])**2))


    R_theta_s_prime_u, R_theta_s_prime_l = [], []
    for i in range(len(m_prime)):
        if i == 0:
            R_theta_s_prime_u.append(R_theta_s_prime[i]+s_star*d_l[i]*(m_prime[i+1]-m_prime[i])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i])**2+(m_prime[i+1]-m_prime[i])**2))
            R_theta_s_prime_l.append(R_theta_s_prime[i]-s_star*d_l[i]*(m_prime[i+1]-m_prime[i])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i])**2+(m_prime[i+1]-m_prime[i])**2))
        elif i>0 and i<124:
            R_theta_s_prime_u.append(R_theta_s_prime[i]+s_star*d_l[i]*(m_prime[i+1]-m_prime[i-1])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i-1])**2+(m_prime[i+1]-m_prime[i-1])**2))
            R_theta_s_prime_l.append(R_theta_s_prime[i]-s_star*d_l[i]*(m_prime[i+1]-m_prime[i-1])/math.sqrt((R_theta_s_prime[i+1]-R_theta_s_prime[i-1])**2+(m_prime[i+1]-m_prime[i-1])**2))
        elif i == 124:
            R_theta_s_prime_u.append(R_theta_s_prime[i]+s_star*d_l[i]*(m_prime[i]-m_prime[i-1])/math.sqrt((R_theta_s_prime[i]-R_theta_s_prime[i-1])**2+(m_prime[i]-m_prime[i-1])**2))
            R_theta_s_prime_l.append(R_theta_s_prime[i]-s_star*d_l[i]*(m_prime[i]-m_prime[i-1])/math.sqrt((R_theta_s_prime[i]-R_theta_s_prime[i-1])**2+(m_prime[i]-m_prime[i-1])**2))

    coa1, coa2, coa3 = [], [], []
    for i in range(len(m_prime)-1):
        coa1.append(math.sqrt((m_prime[i+1]-m_prime[i])**2+(R_theta_s_prime[i+1]-R_theta_s_prime[i])**2)*2*s_star*(d_l[i+1]+d_l[i])/2*(m_prime[i+1]+m_prime[i])/2)
        coa2.append(math.sqrt((m_prime[i+1]-m_prime[i])**2+(R_theta_s_prime[i+1]-R_theta_s_prime[i])**2)*2*s_star*(d_l[i+1]+d_l[i])/2*(R_theta_s_prime[i+1]+R_theta_s_prime[i])/2)
        coa3.append(math.sqrt((m_prime[i+1]-m_prime[i])**2+(R_theta_s_prime[i+1]-R_theta_s_prime[i])**2)*2*s_star*(d_l[i+1]+d_l[i])/2)

    coa1.append(sum(coa1))   
    coa2.append(sum(coa2))  
    coa3.append(sum(coa3))

    m_prime_cntr = coa1[124]/coa3[124]
    Rtet_prime_cntr = coa2[124]/coa3[124]    

   
    def min_max(m_prime):
        m_prime_min = float('inf') 
        pos_m_prime_min = 0
        m_prime_max = float('-inf')  
        pos_m_prime_max = 0
        
        for i in range(len(m_prime_u)):
            if m_prime[i] <= m_prime_min:
                m_prime_min = m_prime[i]
                pos_m_prime_min = i
            elif m_prime[i] >= m_prime_max:
                m_prime_max = m_prime[i]
                pos_m_prime_max = i
            
        return pos_m_prime_min, pos_m_prime_max

    pos_m_prime_min_u, pos_m_prime_max_u = min_max(m_prime_u)        
    #print(pos_m_prime_min_u, pos_m_prime_max_u)
    #plt.scatter(m_prime_u[pos_m_prime_min_u], R_theta_s_prime_u[pos_m_prime_min_u], s = 50)
    #plt.scatter(m_prime_u[pos_m_prime_max_u], R_theta_s_prime_u[pos_m_prime_max_u], s = 50)

    pos_m_prime_min_l, pos_m_prime_max_l = min_max(m_prime_l)        
    #print(pos_m_prime_min_l, pos_m_prime_max_l)
    #plt.scatter(m_prime_l[pos_m_prime_min_l], R_theta_s_prime_l[pos_m_prime_min_l], s = 50)
    #plt.scatter(m_prime_l[pos_m_prime_max_l], R_theta_s_prime_l[pos_m_prime_max_l], s = 50)

    def global_maxima(pos_m_prime_min_u, pos_m_prime_min_l, pos_m_prime_max_u, pos_m_prime_max_l):
        pos_m_prime_min = float('inf')  
        pos_m_prime_max = float('-inf')

        m_prime_min = min(m_prime_u[pos_m_prime_min_u], m_prime_l[pos_m_prime_min_l])
        m_prime_max = max(m_prime_u[pos_m_prime_max_u], m_prime_l[pos_m_prime_max_l])
        
        return pos_m_prime_min, pos_m_prime_max, m_prime_min, m_prime_max

    pos_m_prime_min, pos_m_prime_max, m_prime_min, m_prime_max = global_maxima(pos_m_prime_min_u, pos_m_prime_min_l, pos_m_prime_max_u, pos_m_prime_max_l)
    
    if m_prime_min == m_prime_u[pos_m_prime_min_u]:
        pos_m_prime_min = pos_m_prime_min_u
        
        if m_prime_max == m_prime_u[pos_m_prime_max_u]:    
            pos_m_prime_max = pos_m_prime_max_u
            
            #supporting lists:
            helping_list_m = m_prime_u[0:pos_m_prime_min+1]
            helping_list_m.reverse()
            helping_list_m2 = m_prime_u[pos_m_prime_max:]
            helping_list_m2.reverse()

            helping_list_R = R_theta_s_prime_u[0:pos_m_prime_min+1]
            helping_list_R.reverse()
            helping_list_R2 = R_theta_s_prime_u[pos_m_prime_max:]
            helping_list_R2.reverse()
            
            #new upper side
            m_prime_u = m_prime_u[pos_m_prime_min:pos_m_prime_max+1]
            R_theta_s_prime_u = R_theta_s_prime_u[pos_m_prime_min:pos_m_prime_max+1]
            
            #new lower side
            m_prime_l = helping_list_m + m_prime_l+ helping_list_m2
            R_theta_s_prime_l = helping_list_R + R_theta_s_prime_l + helping_list_R2
            
        elif m_prime_max == m_prime_l[pos_m_prime_max_l]:
            pos_m_prime_max = pos_m_prime_max_l 
            
            #supporting list:
            helping_list_m = m_prime_u[0:pos_m_prime_min]
            helping_list_m.reverse()   
            helping_list_R = R_theta_s_prime_u[0:pos_m_prime_min]
            helping_list_R.reverse()   

            #upper side
            m_prime_u = m_prime_u[pos_m_prime_min:]+m_prime_l[pos_m_prime_max:]
            R_theta_s_prime_u = R_theta_s_prime_u[pos_m_prime_min:] +R_theta_s_prime_u[pos_m_prime_max:]
            
            #lower side
            m_prime_l = helping_list_m + m_prime_l[0:pos_m_prime_max]
            R_theta_s_prime_l = helping_list_R + R_theta_s_prime_l[0:pos_m_prime_max]
            print("2")

    elif m_prime_min == m_prime_l[pos_m_prime_min_l]:
        pos_m_prime_min = pos_m_prime_min_l
        if m_prime_max == m_prime_u[pos_m_prime_max_u]:
            pos_m_prime_max = pos_m_prime_max_u

            #supporting lists:
            helping_list_m = m_prime_l[0:pos_m_prime_min_l+1] 
            helping_list_m.reverse()

            helping_list_m2 = m_prime_u[pos_m_prime_max:] 
            helping_list_m2.reverse()

            helping_list_R = R_theta_s_prime_l[0:pos_m_prime_min_l+1]
            helping_list_R.reverse()

            helping_list_R2 = R_theta_s_prime_u[pos_m_prime_max:]
            helping_list_R2.reverse()
            
            helping_list_d = d_l[1:pos_m_prime_min_l]
            helping_list_d.reverse()

            #upper side
            m_prime_u = helping_list_m + m_prime_u[0:pos_m_prime_max+1]
            R_theta_s_prime_u = helping_list_R + R_theta_s_prime_u[0:pos_m_prime_max+1]
            
            #lower side
            m_prime_l = m_prime_l[pos_m_prime_min:] + helping_list_m2
            R_theta_s_prime_l = R_theta_s_prime_l[pos_m_prime_min:] + helping_list_R2

        elif m_prime_max == m_prime_l[pos_m_prime_max_l]:
            pos_m_prime_max = pos_m_prime_max_l
            
            #supporting lists:
            helping_list_m = m_prime_l[0:pos_m_prime_min_l+1] 
            helping_list_m2 = m_prime_l[pos_m_prime_max:-1] 
            helping_list_m.reverse()
            helping_list_m2.reverse()

            helping_list_R = R_theta_s_prime_l[0:pos_m_prime_min_l+1]
            helping_list_R2 = R_theta_s_prime_l[pos_m_prime_max:-1] 
            helping_list_R.reverse()
            helping_list_R2.reverse()

            helping_list_d = d_l[1:pos_m_prime_min_l]
            helping_list_d2 = d_l[pos_m_prime_max:-1] 
            helping_list_d.reverse()
            helping_list_d2.reverse()

            #upper side
            m_prime_u = helping_list_m + m_prime_u + helping_list_m2  
            R_theta_s_prime_u = helping_list_R + R_theta_s_prime_u + helping_list_R2

            #lower side
            m_prime_l = m_prime_l[pos_m_prime_min:pos_m_prime_max+1]
            R_theta_s_prime_l = R_theta_s_prime_l[pos_m_prime_min:pos_m_prime_max+1]

    if m_prime_l[0]!=m_prime_u[0]:
        print("ne")

    # activate for plotting of blade geometry
    """
    plt.scatter(m_prime_u, R_theta_s_prime_u, s = 3)
    plt.plot(m_prime_u, R_theta_s_prime_u) 
    plt.scatter(m_prime, R_theta_s_prime, s = 3)
    plt.plot(m_prime_l, R_theta_s_prime_l)
    plt.scatter(m_prime_l, R_theta_s_prime_l, s = 3)
    plt.plot(m_prime, R_theta_s_prime)
    plt.xlabel("m' [-]")
    plt.ylabel("R\u03b8 [-]")
    plt.xlim(-0.005,0.015)
    plt.ylim(-0.01,0.0025)
    plt.axis('equal')
    plt.show()
    """
    
    dif_list_len_u = len(m_prime_u)-125
    
    if dif_list_len_u > 0:
        for i in range(dif_list_len_u):
            k = 20+i*5
            del m_prime_u[k]
            del R_theta_s_prime_u[k]

    elif dif_list_len_u < 0:
        for i in range(abs(dif_list_len_u)):
            k = 20+i*5
            new_m_value = m_prime_u[k]+(m_prime_u[k+1]-m_prime_u[k])/2
            m_prime_u.insert(k+1, new_m_value)
            new_Rtheta_value = R_theta_s_prime_u[k]+(R_theta_s_prime_u[k+1]-R_theta_s_prime_u[k])/2
            R_theta_s_prime_u.insert(k+1, new_Rtheta_value)

    dif_list_len_l = len(m_prime_l)-125
    
    if dif_list_len_l > 0:
        for i in range(dif_list_len_l):
            k = 20+i*5
            del m_prime_l[k]
            del R_theta_s_prime_l[k]

    elif dif_list_len_l < 0:
        for i in range(abs(dif_list_len_l)):
            k = 20+i*5
            new_m_value = m_prime_l[k]+(m_prime_l[k+1]-m_prime_l[k])/2
            m_prime_l.insert(k+1, new_m_value)
            new_Rtheta_value = R_theta_s_prime_l[k]+(R_theta_s_prime_l[k+1]-R_theta_s_prime_l[k])/2
            R_theta_s_prime_l.insert(k+1, new_Rtheta_value)
    
    # calculation of the second blade row
    m_LE = m_cntr_0_5-(m_cntr_0_5-m_LE_0_5)*(1+cubspline(3, rel_h, h_H, x_LE))
    m_TE = m_cntr_0_5+(m_cntr_0_5-m_LE)*(1-m_prime_cntr)/m_prime_cntr
    
    s = (m_TE-m_LE)*s_star

    R_LE = intpol(m_LE, len(m_prime_values[0]), m_prime_values[0], r_values[0]) + 0.5*(intpol(m_LE,len(m_prime_values[4]), m_prime_values[4], r_values[4]) -intpol(m_LE, len(m_prime_values[0]), m_prime_values[0], r_values[0])) 
    t_s_s_star = s_star*2*Pi*R_LE/(z[0]*s)
    m_star, m_star_u, m_star_l, R_theta_s_star, R_theta_s_star_u, R_theta_s_star_l = [], [], [], [], [], []
    for i in range(len(m_prime)):
        m_star.append((m_prime[i]-m_prime_cntr)*s/s_star+m_cntr_0_5)
        m_star_u.append((m_prime_u[i]-m_prime[i])*s/s_star+m_star[i])
        m_star_l.append((m_prime_l[i]-m_prime[i])*s/s_star+m_star[i])
        R_theta_s_star.append((R_theta_s_prime[i]-Rtet_prime_cntr)*s/s_star)
        R_theta_s_star_u.append((R_theta_s_prime_u[i]-Rtet_prime_cntr)*s/s_star)
        R_theta_s_star_l.append((R_theta_s_prime_l[i]-Rtet_prime_cntr)*s/s_star)
    
    chord = math.sqrt((m_TE-m_LE)**2+(R_theta_s_star[0]-R_theta_s_star[-1])**2)
   
    R_theta_s_prime_2, R_theta_s_prime_2_u, R_theta_s_prime_2_l = [], [], []
    for i in range(len(R_theta_s_prime_u)):
        R_theta_s_prime_2.append(R_theta_s_prime[i]-t_s_s_star)
        R_theta_s_prime_2_u.append(R_theta_s_prime_u[i]-t_s_s_star)
        R_theta_s_prime_2_l.append(R_theta_s_prime_l[i]-t_s_s_star)
    
    R_theta_s_star_2, R_theta_s_star_u_2, R_theta_s_star_l_2 = [], [], []
    for i in range(len(m_prime)):
        R_theta_s_star_2.append((R_theta_s_prime_2[i]-Rtet_prime_cntr)*s/s_star)
        R_theta_s_star_u_2.append((R_theta_s_prime_2_u[i]-Rtet_prime_cntr)*s/s_star)
        R_theta_s_star_l_2.append((R_theta_s_prime_2_l[i]-Rtet_prime_cntr)*s/s_star) 

    return chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2

#R, x, y, and z coordinates for h/H = [0.0, 0.2, 0.5, 0.8, 1.0] 
def coordinates(row):
    R_u, x_u, y_u, z_u, R_l, x_l, y_l, z_l = [], [], [], [], [], [], [], []
    R_theta_s_star_u, R_theta_s_star_l, beta_S, m_star_l,m_star_u = [], [], [], [], []

    for i in range(len(h_H)):
        if h_H[i] == 0.0:
            k = 0
        elif h_H[i] == 0.2:
            k = 1
        elif h_H[i] == 0.5:
            k = 2
        elif h_H[i] == 0.8:
            k = 3
        elif h_H[i] == 1.0:
            k = 4

        chord, m_star_i, R_theta_s_star_i, m_star_u_i, R_theta_s_star_u_i, m_star_l_i, R_theta_s_star_l_i, m_prime, m_prime_u, m_prime_l, m_BP, beta_S_i, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(h_H[i], row)
        R_theta_s_star_u.extend(R_theta_s_star_u_i)
        R_theta_s_star_l.extend(R_theta_s_star_l_i)
        beta_S.extend(beta_S_i)
        

        for j in range(len(m_star_u_i)):
            R_u.append(intpol(m_star_u_i[j], len(r_values[k]), m_prime_values[k], r_values[k]))
            R_l.append(intpol(m_star_l_i[j], len(r_values[k]), m_prime_values[k], r_values[k]))
            x_u.append(intpol(m_star_u_i[j], len(x_values[k]), m_prime_values[k], x_values[k]))
            x_l.append(intpol(m_star_l_i[j], len(x_values[k]), m_prime_values[k], x_values[k]))
            y_u.append(R_u[-1] * math.cos(R_theta_s_star_u_i[j] / R_u[-1]))
            y_l.append(R_l[-1] * math.cos(R_theta_s_star_l_i[j] / R_l[-1]))
            z_u.append(R_u[-1] * math.sin(R_theta_s_star_u_i[j] / R_u[-1]))
            z_l.append(R_l[-1] * math.sin(R_theta_s_star_l_i[j] / R_l[-1]))

    return x_u, R_theta_s_star_u, x_l, R_theta_s_star_l, R_u, beta_S

#calculation of stage_new.dat values
def calculate_m_prime_new(j_prime):
    poly_expression = 7.5613 * (j_prime ** 6) - 19.232 * (j_prime ** 5) + 14.97 * (j_prime ** 4) - 3.2001 * (j_prime ** 3) + 0.6354 * (j_prime ** 2) + 0.2687 * j_prime
    return min(poly_expression, 1)

#for Multall, we need j_prime_max sets of values of the blade by interpolation 
def calculation_blade_coordinates(j_prime_max, row):

    n_B = []                                                            
    for i in range(1, j_prime_max + 1):
        n_B.append(float(i))

    j_prime, m_prime_new = [], []
    for i in range(len(n_B)):
        j_prime.append((n_B[i]-1)/(j_prime_max-1))
        m_prime_new.append(calculate_m_prime_new(j_prime[i]))
     
    x_u, R_theta_s_star_u, x_l, R_theta_s_star_l, R_u, beta_S = coordinates(row) 

    x_sec, Rtheta_sec, d_sec, R_sec = [], [], [], []
    for i in range(len(h_H)):
        x_sec.append([])
        Rtheta_sec.append([])
        d_sec.append([])
        R_sec.append([])
        
    for i in range(len(h_H)):          
        chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u_, m_star_l, R_theta_s_star_l_, m_prime_0_0, m_prime_u, m_prime_l, m_BP, beta_S_0_0, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2= calculation_of_section(h_H[i], row)
        
        delt_x_u = m_prime_u[-1]-m_prime_u[0]
        delt_x_l = m_prime_l[-1]-m_prime_l[0]
        m_prime_upper, m_prime_lower = [], []
        for k in range(len(m_prime_u)):    
            mu0 = m_prime_u[0]
            m_prime_upper.append((m_prime_u[k]-mu0)/delt_x_u) 
            ml0 = m_prime_l[0]
            m_prime_lower.append((m_prime_l[k]-ml0)/delt_x_l)

        for j in range(0, j_prime_max):
            a = int(125*i)
            b = int(125+125*i)

            x_sec_value = intpol(m_prime_new[j], len(m_prime_upper), m_prime_upper, x_u[a:b])/1000
            Rtheta_sec_value = intpol(m_prime_new[j], len(m_prime_upper), m_prime_upper, R_theta_s_star_u[a:b])/1000

            x_sec[i].append(x_sec_value)
            Rtheta_sec[i].append(Rtheta_sec_value)
            d_sec_value = Rtheta_sec[i][j] - intpol(m_prime_new[j], len(m_prime_lower), m_prime_lower, R_theta_s_star_l[a:b])/1000
            R_sec_value = intpol(m_prime_new[j], len(m_prime_upper), m_prime_upper, R_u[a:b])/1000

            d_sec[i].append(d_sec_value)
            R_sec[i].append(R_sec_value)

    return x_sec, d_sec, R_sec, Rtheta_sec, beta_S, j_prime_max

# calculation of inlet coordinates
def inlet_coordinates(row, num_planes, n_max_in, l_inlet, x_sec, d_sec, R_sec, Rtheta_sec, beta_S, j_prime_max):        
    
    DX_in, DX1_in = [], []

    Rtheta_in_BP, Rtheta_in, Rtheta_prime_in_BP, Rtheta_prime_in, dx_in, l_in, x_in, R_in, d_in = [], [], [], [], [], [], [], [], []
    for _ in range(num_planes):
        Rtheta_in_BP.append([])
        Rtheta_in.append([])
        Rtheta_prime_in_BP.append([])
        Rtheta_prime_in.append([])
        dx_in.append([])
        l_in.append([])
        x_in.append([])
        R_in.append([])
        d_in.append([])
    
    if row == 1:
        k = 0
    elif row == 2:
        k = 3

    for i in range(num_planes):
        DX_in.append(x0[k]/1000-x_sec[i][0])
        DX1_in.append(x_sec[i][1]-x_sec[i][0])
        x = max(Rtheta_sec[0][0], Rtheta_sec[4][0])*2.2
        Rtheta_in_BP[i].append(x)
        Rtheta_in_BP[i].append(x)
        Rtheta_in_BP[i].append(Rtheta_sec[i][0])
        Rtheta_prime_in_BP[i].append(Rtheta_in_BP[i][0]/abs(DX_in[i]))
        Rtheta_prime_in_BP[i].append(Rtheta_in_BP[i][0]/abs(DX_in[i]))
        y = Rtheta_in_BP[i][2]/abs(DX_in[i])
        Rtheta_prime_in_BP[i].append(y+1/math.tan(beta_S[0+125*i]/180*Pi)*(-1/3))       
        Rtheta_prime_in_BP[i].append(y)

    for i in range(num_planes):
        for j in range(n_max_in):
            d_in[i].append(0.0)

    a_in, b_in = [], []
    for i in range(num_planes): 
        a_in.append(abs(DX1_in[i]/DX_in[i]))
        b_in.append(2*((l_inlet-a_in[i])/(n_max_in-2)-a_in[i]))

    n_in = []                                                            
    for i in range(1, n_max_in + 1):
        n_in.append(float(i))

    n_in_prime = []
    for i in range(len(n_in)):
        n_in_prime.append((n_in[i]-1)/(n_max_in-1))

    for i in range(num_planes):
        for j in range(len(n_in)):
            dx_in[i].append(a_in[i]+0.5*(1-math.cos(Pi*(1-n_in_prime[j])))*b_in[i])

    for i in range(num_planes):
        l_in[i].append(0.0)
        for j in range(1, len(n_in)):
            l_in[i].append(dx_in[i][j]+l_in[i][-1])

    for i in range(num_planes):
        for j in range(len(n_in)):
            Rtheta_in[i].append(bezier(4, l_in[i][j], Rtheta_prime_in_BP[i])*abs(DX_in[i]))
            x_in[i].append(x_sec[i][0]+DX_in[i]*(1-l_in[i][j]))
            R_in[i].append(intpol(round(x_in[i][j]*1000, 10), len(x_values[i]), x_values[i], r_values[i])/1000)  

    for i in range(num_planes):
        x_in[i] = x_in[i][:-1] 
        R_in[i] = R_in[i][:-1] 
        d_in[i] = d_in[i][:-1] 
        Rtheta_in[i] = Rtheta_in[i][:-1] 
    
    return x_in, d_in, R_in, Rtheta_in

# calculation of outlet coordinates
def outlet_coordinates(row, n_max_out, l_outlet, num_planes, x_sec, Rtheta_sec, beta_S):
    DX_out, DX1_out = [], []
    Rtheta_out_BP, Rtheta_out, Rtheta_prime_out_BP, Rtheta_prime_out, dx_out, l_out, x_out, R_out, d_out = [], [], [], [], [], [], [], [], []
    for _ in range(num_planes):
        Rtheta_out_BP.append([])
        Rtheta_out.append([])
        Rtheta_prime_out_BP.append([])
        Rtheta_prime_out.append([])
        dx_out.append([])
        l_out.append([])
        x_out.append([])
        R_out.append([])
        d_out.append([])

    if row == 1:
        k = 3       

    elif row == 2:
        k = 6    

    for i in range(num_planes):
        s = len(x_sec[i])-1
        
        DX_out.append(x0[k]/1000-x_sec[i][s])
        DX1_out.append(x_sec[i][s]-x_sec[i][s-1])      
        x = Rtheta_sec[i][s]
        Rtheta_out_BP[i].append(x)
        Rtheta_out_BP[i].append(x+1/math.tan(beta_S[124+125*i]/180*Pi)*DX_out[i])
        Rtheta_prime_out_BP[i].append(Rtheta_out_BP[i][0]/abs(DX_out[i]))
        Rtheta_prime_out_BP[i].append(Rtheta_out_BP[i][1]/abs(DX_out[i]))

    for i in range(num_planes):
        for j in range(n_max_out):
            d_out[i].append(0.0)

    a_out, b_out = [], []
    for i in range(num_planes): 
        a_out.append(abs(DX1_out[i]/DX_out[i]))
        b_out.append(2*((l_outlet-a_out[i])/(n_max_out-2)-a_out[i]))

    n_out = []                                                            
    for i in range(1, n_max_out + 1):
        n_out.append(float(i))

    n_out_prime = []
    for i in range(len(n_out)):
        n_out_prime.append((n_out[i]-1)/(n_max_out-1))

    for i in range(num_planes):
        for j in range(len(n_out)):
            dx_out[i].append(a_out[i]+0.5*(1-math.cos(Pi*n_out_prime[j]))*b_out[i])

    for i in range(num_planes):
        l_out[i].append(0.0)
        for j in range(len(n_out)-1):
            l_out[i].append(dx_out[i][j]+l_out[i][-1])

    for i in range(num_planes):
        for j in range(len(n_out)):
            Rtheta_out[i].append((Rtheta_out_BP[i][1] - Rtheta_out_BP[i][0])*l_out[i][j] + Rtheta_out_BP[i][0])
            x_out[i].append(x_sec[i][s] + DX_out[i]*l_out[i][j])
            R_out[i].append(intpol(round(x_out[i][j]*1000, 10), len(r_values[i]), x_values[i], r_values[i])/1000) 
     
    for i in range(num_planes):
        x_out[i] = x_out[i][1:] 
        R_out[i] = R_out[i][1:]
        d_out[i] = d_out[i][1:]
        Rtheta_out[i] = Rtheta_out[i][1:]
    
    return x_out, d_out, R_out, Rtheta_out

# merging of inlet, blade and outlet coordinates
def merge_coordinates(num_planes, j_prime_max, n_max_in, x_in, x_sec, x_out, d_in, d_sec, d_out, R_in, R_sec, R_out, Rtheta_in, Rtheta_sec, Rtheta_out):
    #Now all values from inlet, blade and outlet are put in one list
    x, Rtheta, d, R =  [], [], [], []
    x_sec_s, Rtheta_sec_s = [], []
    for _ in range(num_planes):
        x.append([])
        Rtheta.append([])
        d.append([])
        R.append([])
        x_sec_s.append([])
        Rtheta_sec_s.append([])

    for i in range(5):
        for j in range(len(x_sec[i])):
            x_sec_s[i].append(x_sec[i][j]*1000)     
            Rtheta_sec_s[i].append(Rtheta_sec[i][j]*1000)     
    
    sehnenlaenge = []
    for i in range(5):
        sehnenlaenge.append(math.sqrt((x_sec[i][0]-x_sec[i][-1])**2+(Rtheta_sec[i][0]-Rtheta_sec[i][-1])**2)*1000)

    for i in range(num_planes):
        x[i] = x_in[i]+x_sec[i]+x_out[i]
        Rtheta[i] = Rtheta_in[i]+Rtheta_sec[i]+Rtheta_out[i]
        d[i] = d_in[i]+d_sec[i]+d_out[i]
        R[i] = R_in[i]+R_sec[i]+R_out[i]
    
    return x, d, R, Rtheta 

# There are 5 sets of coordinates. For better interpolation, we create two additional sets, one at the hub and one at the shroud.
def additional_section(Z_H, Z_S, x, d, R, Rtheta):
    R_0_05, X_0_05, Rtheta_0_05, d_0_05 = [], [], [], [] 
    for i in range(len(R[0])):
        XN = [R[0][i], R[1][i]]
        N = len(XN)
        Z = (R[4][i]-R[0][i])*Z_H + R[0][i]
        A = [x[0][i], x[1][i]]
        B = [Rtheta[0][i], Rtheta[1][i]]
        C = [d[0][i], d[1][i]]
        D = [R[0][i], R[1][i]]
        X_0_05.append(intp_new(2, N, XN, A, Z))
        Rtheta_0_05.append(intp_new(2, N, XN, B, Z))
        d_0_05.append(intp_new(2 ,N, XN, C, Z))
        R_0_05.append(intp_new(2, N, XN, D, Z))

    R_0_95, X_0_95, Rtheta_0_95, d_0_95 = [], [], [], [] 
    Z_S = 0.95
    for i in range(len(R[0])):
        XN = [R[3][i], R[4][i]]
        N = len(XN)
        Z = (R[4][i]-R[0][i])*Z_S + R[0][i]
        A = [x[3][i], x[4][i]]
        B = [Rtheta[3][i], Rtheta[4][i]]
        C = [d[3][i], d[4][i]]
        D = [R[3][i], R[4][i]]  
        X_0_95.append(intp_new(2, N, XN, A, Z))
        Rtheta_0_95.append(intp_new(2, N, XN, B, Z))
        d_0_95.append(intp_new(2 ,N, XN, C, Z))
        R_0_95.append(intp_new(2, N, XN, D, Z))

    #Inserts the new two planes in the old lists
    x.insert(1, X_0_05)
    x.insert(4, X_0_95)
    Rtheta.insert(1, Rtheta_0_05)
    Rtheta.insert(4, Rtheta_0_95)
    d.insert(1, d_0_05)
    d.insert(4, d_0_95)
    R.insert(1, R_0_05)
    R.insert(4, R_0_95)
    
    return x, d, R, Rtheta

# coordinates for every selected value in levels by interpolation
def coordinates_levels(levels, x, d, R, Rtheta):
    #creating new liste for all interpolated sections
    x_new, Rtheta_new, d_new, R_new = [], [], [], []
    for _ in range(len(levels)):
        x_new.append([])
        Rtheta_new.append([])
        d_new.append([])
        R_new.append([])

    #calculation of new sections:
    for j in range(len(levels)):
        element = levels[j]        
        for i in range(len(R[0])):
            XN = [R[0][i], R[1][i], R[2][i], R[3][i], R[4][i], R[5][i], R[6][i]]
            N = len(XN)
            Z = (R[4][i]-R[0][i])*element + R[0][i]
            A = [x[0][i], x[1][i], x[2][i], x[3][i], x[4][i], x[5][i], x[6][i]]
            B = [Rtheta[0][i], Rtheta[1][i], Rtheta[2][i], Rtheta[3][i], Rtheta[4][i],Rtheta[5][i], Rtheta[6][i]]
            C = [d[0][i], d[1][i], d[2][i], d[3][i], d[4][i], d[5][i], d[6][i]]
            D = [R[0][i], R[1][i], R[2][i], R[3][i], R[4][i], R[5][i], R[6][i]]
            x_new[j].append(intp_new(2, N, XN, A, Z))
            Rtheta_new[j].append(intp_new(2, N, XN, B, Z))
            d_new[j].append(intp_new(2, N, XN, C, Z))
            R_new[j].append(intp_new(2, N, XN, D, Z))
        
    return x_new, d_new, R_new, Rtheta_new

# function for calculation of blade row coordinates. It just activates other functions
def calc_blade_row_coordinates(row, j_prime_max, num_planes, n_max_in, l_inlet, n_max_out, l_outlet, Z_H, Z_S, levels):
    x_sec, d_sec, R_sec, Rtheta_sec, beta_S, j_prime_max = calculation_blade_coordinates(j_prime_max, row) 
    x_in, d_in, R_in, Rtheta_in = inlet_coordinates(row, num_planes, n_max_in, l_inlet, x_sec, d_sec, R_sec, Rtheta_sec, beta_S, j_prime_max) 
    x_out, d_out, R_out, Rtheta_out = outlet_coordinates(row, n_max_out, l_outlet, num_planes, x_sec, Rtheta_sec, beta_S)
    x, d, R, Rtheta = merge_coordinates(num_planes, j_prime_max, n_max_in, x_in, x_sec, x_out, d_in, d_sec, d_out, R_in, R_sec, R_out, Rtheta_in, Rtheta_sec, Rtheta_out)
    x, d, R, Rtheta = additional_section(Z_H, Z_S, x, d, R, Rtheta)
    x_new, d_new, R_new, Rtheta_new = coordinates_levels(levels, x, d, R, Rtheta )
    
    return x_new, d_new, R_new, Rtheta_new


## Functions that write the file for MULTALL
#writes coordinates in the right format
def write_values_in_block(section, liste, file, JM):
    for k in range(0, JM, 8):
        zeile = liste[section][k:k+8]
        file.write(' ')
        for element in zeile:
            if element < 0.0:
                file.write(f"{element:.6f} ")
            else:
                file.write(' ')
                file.write(f"{element:.6f} ")
        file.write('\n')  

#writes the coordinates of all sections in a file for MULTALL: 
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

# writes head of the file
def write_head_file(file, NSEC, NROW, section, enable_bleed_air):
    if enable_bleed_air == True:
        bleed_air = 1
    else: 
        bleed_air = 0
    with open(file, "w+") as file:
        file.write(" DATA SET FOR \"multall\" . GENERATED BY \"stagen\" .                       \n")
        file.write("    CP   and   GAMMA \n")
        file.write(f" {cp}    {kappa}\n")
        file.write("       ITIMST \n")
        file.write("         3\n")
        file.write("     CFL,    DAMP,    MACHLIM,    F_PDOWN \n")
        file.write("  0.320000 9.000000  2.000000  0.000000\n")
        file.write("  IF_RESTART \n")
        file.write("         0\n")
        file.write("  NSTEPS_MAX, CONLIM\n")
        if section == 0:
            file.write("      9000  0.005000\n")
        else: 
            file.write("      60000  0.005000\n")
        file.write("   SFX,      SFT,      FAC_4TH,     NCHANGE \n")
        file.write("  0.005000  0.005000  0.800000      1000\n")
        file.write("       NUMBER OF BLADE ROWS \n")
        file.write(f"         {NROW}\n")
        file.write("        IM        KM \n")
        
        if section == 0:
            file.write("        37        37\n")
        else:
            file.write("        37        2\n")
        
        file.write("  FP(I),I=1,IMM1 \n")
        file.write("  1.000000  1.250000  1.562500  1.953125  2.441406  3.051758  3.814697  4.768372\n")
        file.write("  5.960464  7.450581  9.313226 11.641532 14.551915 18.189894 20.000000 20.000000\n")
        file.write(" 20.000000 20.000000 20.000000 20.000000 20.000000 20.000000 18.189894 14.551915\n")
        file.write(" 11.641532  9.313226  7.450581  5.960464  4.768372  3.814697  3.051758  2.441406\n")
        file.write("  1.953125  1.562500  1.250000  1.000000\n")
        
        if section == 0:
            file.write("  FR(K),K=1,KMM1 \n")
            file.write("  1.000000  1.250000  1.562500  1.953125  2.441406  3.051758  3.814697  4.768372\n")
            file.write("  5.960464  7.450581  9.313226 11.641532 14.551915 18.189894 20.000000 20.000000\n")
            file.write(" 20.000000 20.000000 20.000000 20.000000 20.000000 20.000000 18.189894 14.551915\n")
            file.write(" 11.641532  9.313226  7.450581  5.960464  4.768372  3.814697  3.051758  2.441406\n")
            file.write("  1.953125  1.562500  1.250000  1.000000\n")
        else:
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
        file.write("         1         1\n")
        file.write("  5  TIME STEPS FOR PRINTOUT \n")
        file.write("      9000      9000      9000      9000      9000\n")
        file.write("  MARKER FOR VARIABLES TO BE SENT TO THE OUTPUT FILE.\n")
        file.write(" 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")
        file.write("  STREAM SURFACES ON WHICH RESULTS ARE TO BE SENT TO   THE OUTPUT FILE \n")
        file.write(" 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")

# writes head of the row
def write_head_row(file, row, JM, JLE, JTE, RPM, section, NSEC):
    if section == 0:
        if row == 1:
            x = round(p_1[0], 1)
            y = round(p_2[0], 1)
            z = RPM[0]
            blades = z_R[0]
        elif row == 2:
            x = round(p_2[0], 1)
            y = round(p_3[0], 1)
            z = 0.0
            blades = z_S[0]
    else:
        if row == 1:
            i = levels[section-1]
            for j in range(len(h_rel)):
                if round(h_rel[j],2) == i:
                    x = round(p_R_in[j], 1)
                    y = round(p_R_out[j], 1)

            z = RPM[0]
            blades = z_R[0]
        elif row == 2:
            i = levels[section-1]
            for j in range(len(h_rel)):
                if round(h_rel[j],2) == i:
                    x = round(p_S_in[j], 1)
                    y = round(p_S_out[j], 1)
            
            blades = z_S[0]
            z = 0.0

    with open(file, "a") as file:
        file.write(" ***************************************************************\n")
        file.write(" ************STARTING THE INPUT FOR EACH BLADE ROW**************\n")
        file.write(f"  BLADE ROW NUMBER =        {row}                                           \n")
        file.write("    NUMBER OF BLADES IN ROW \n")
        file.write(f"        {blades}\n")                                       
        file.write("        JM        JLE       JTE \n")
        file.write(f"       {JM}        {JLE}        {JTE}\n")
        file.write("      KTIPSTART  KTIPEND \n")
        file.write("         0         0\n")
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

# writes end of the file 
def write_end_file(row, file, section):
    
    if row == 1:
        x = round(p_R_out[0], 1)
        y = round(p_R_out[len(h_rel)-1], 1)
        t = round(T_t1[0], 4)
        p = round(p_t1[0], 1)
        um = round(cm1[0], 4)
    
    elif row == 2:
        x = round(p_S_out[0], 1)
        y = round(p_S_out[len(h_rel)-1], 1)
        t = round(T_t1[0], 4)
        p = round(p_t1[0], 1)
        um = round(cm1[0], 4)
        
    with open(file, "a") as file:
        if section == 0:
            file.write("  STARTING INLET BOUNDARY CONDITION DATA .\n")
            file.write("  NUMBER OF POINTS FOR INLET BOUNDARY CONDITIONS \n")
            file.write("        37\n")
            file.write("  SPACING OF INLET BOUNDARY CONDITION POINTS \n")
            file.write("  1.000000  1.250000  1.562500  1.953125  2.441406  3.051758  3.814697  4.768372\n")
            file.write("  5.960464  7.450581  9.313226 11.641532 14.551915 18.189894 20.000000 20.000000\n")
            file.write(" 20.000000 20.000000 20.000000 20.000000 20.000000 20.000000 18.189894 14.551915\n")
            file.write(" 11.641532  9.313226  7.450581  5.960464  4.768372  3.814697  3.051758  2.441406\n")
            file.write("  1.953125  1.562500  1.250000  1.000000\n")
            file.write("   INLET STAGNATION PRESSURES \n")
            file.write(f"  {p}  {p}  {p}  {p}  {p}  {p}  {p}  {p}\n")
            file.write(f"  {p}  {p}  {p}  {p}  {p}  {p}  {p}  {p}\n")
            file.write(f"  {p}  {p}  {p}  {p}  {p}  {p}  {p}  {p}\n")
            file.write(f"  {p}  {p}  {p}  {p}  {p}  {p}  {p}  {p}\n")
            file.write(f"  {p}  {p}  {p}  {p}  {p}\n")
            file.write("   INLET STAGNATION TEMPERATURES \n")
            file.write(f"  {t}  {t}  {t}  {t}  {t}  {t}  {t}  {t}\n")
            file.write(f"  {t}  {t}  {t}  {t}  {t}  {t}  {t}  {t}\n")
            file.write(f"  {t}  {t}  {t}  {t}  {t}  {t}  {t}  {t}\n")
            file.write(f"  {t}  {t}  {t}  {t}  {t}  {t}  {t}  {t}\n")
            file.write(f"  {t}  {t}  {t}  {t}  {t}\n")
            file.write("   INLET ABSOLUTE TANGENTIAL VELOCITY \n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("   INLET MERIDIONAL VELOCITY \n")
            file.write(f"  {um}  {um}  {um}  {um}  {um}  {um}  {um}  {um}\n")
            file.write(f"  {um}  {um}  {um}  {um}  {um}  {um}  {um}  {um}\n")
            file.write(f"  {um}  {um}  {um}  {um}  {um}  {um}  {um}  {um}\n")
            file.write(f"  {um}  {um}  {um}  {um}  {um}  {um}  {um}  {um}\n")
            file.write(f"  {um}  {um}  {um}  {um}  {um}\n")
            file.write("   INLET MERIDIONAL YAW ANGLE \n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("   INLET PITCH ANGLE \n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("    0.0000    0.0000    0.0000    0.0000    0.0000\n")
            file.write("   PDOWN_HUB   PDOWN_TIP \n")
            file.write(f"  {x}  {y}\n")
            file.write(" MIXING LENGTH LIMITS ON ALL BLADE ROWS\n")
            file.write("  0.030000  0.030000  0.030000  0.030000  0.030000  0.020000\n")
            file.write("  0.030000  0.030000  0.030000  0.030000  0.030000  0.020000\n")
            file.write("  FACTOR TO INCREASE THE TURBULENT VISCOSITY OVER THE FIRST NMIXUP STEPS \n")
            file.write("   2.00000 1000\n")
        else:         
            if row == 1:
                i = levels[section-1]
                for j in range(len(h_rel)):
                    if round(h_rel[j],2) == i:
                        x = round(p_R_out[j], 1)
                        y = round(p_R_out[j], 1)

            elif row == 2:
                i = levels[section-1]
                for j in range(len(h_rel)):
                    if round(h_rel[j],2) == i:
                        x = round(p_S_out[j], 1)
                        y = round(p_S_out[j], 1)

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
            file.write("  0.030000 0.030000 0.030000 0.030000 0.030000 0.020000\n")
            file.write("  0.030000 0.030000 0.030000 0.030000 0.030000 0.020000\n")
            file.write("  FACTOR TO INCREASE THE TURBULENT VISCOSITY OVER THE FIRST NMIXUP STEPS\n")
            file.write("   2.00000 1000\n")


#Plots the x-Rtheta of all sections in 3D:
def xRtheta_plot(Rtheta_new, R_new, x_new):
    fig = plt.figure(figsize=(10, 8))
    theta_radians = np.deg2rad(Rtheta_new)
    y_values = [r * np.cos(theta) for r, theta in zip(R_new, Rtheta_new)]
    z_values = [r * np.sin(theta) for r, theta in zip(R_new, Rtheta_new)]
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x_new, y_values, z_values, c='r', marker='o')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()
    
# Write the Bleed Air Cards for the Multall Input File
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


# Class to create Tooltips
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        
    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25  
        y += self.widget.winfo_rooty() + 25     
        
        self.tooltip_window = Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = Label(self.tooltip_window, text = self.text, background = '#ffffe0', relief = 'solid', borderwidth = 1, font=("tahoma", '11', 'normal'), wraplength=500)
        label.pack(ipadx=1) 
        
    def hide_tooltip(self, event = None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None
    

class CompressorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Settings for MULTALL file")
        
        # Add a dictionary for storing bleedair data
        self.bleed_air_data = {
            'rotor': {'patches': [], 'count': 0},
            'stator': {'patches': [], 'count': 0}
        }
        
        # Potential error fix for attribute error
        self.rotor_patch_entries = []
        self.stator_patch_entries = []
        
        # Variables for Inlet and Outlet Adjustment
        self.inlet_area_var = tk.DoubleVar()
        self.inlet_dist_var = tk.DoubleVar()
        self.outlet_area_var = tk.DoubleVar()
        self.outlet_dist_var = tk.DoubleVar()
        
        # Create notebook for multiple pages
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create frames for each section
        self.parameters_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.parameters_frame, text="Parameters")

        self.plot_options_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.plot_options_frame, text="Plot Options")
        
        self.bleed_air_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bleed_air_frame, text="Bleed Air")
        # Creat container frame for inputs for the bleed air
        self.bleed_input_container = ttk.Frame(self.bleed_air_frame)
        self.bleed_input_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.inlet_outlet_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inlet_outlet_frame, text="Define Inlet and Outlet")

        self.output_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.output_frame, text="Output")

        # Parameters Page
        self.use_default_rotor_bezier_var = tk.BooleanVar()
        self.use_default_rotor_bezier_var.set(False)
        ttk.Checkbutton(self.parameters_frame, text="Use default Bezier points for rotor", variable=self.use_default_rotor_bezier_var).grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.adjust_rotor_thickness_var = tk.BooleanVar()
        self.adjust_rotor_thickness_var.set(False)
        ttk.Checkbutton(self.parameters_frame, text="Adjust Bezier points of rotor for thickness distribution", variable=self.adjust_rotor_thickness_var).grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.adjust_rotor_angle_var = tk.BooleanVar()
        self.adjust_rotor_angle_var.set(False)
        ttk.Checkbutton(self.parameters_frame, text="Adjust Bezier points of rotor for blade angle distribution", variable=self.adjust_rotor_angle_var).grid(row=2, column=0, padx=5, pady=5, sticky='w')

        # Add spacing between rotor and stator parameters
        ttk.Label(self.parameters_frame, text="").grid(row=3, column=0, pady=20)

        self.use_default_stator_bezier_var = tk.BooleanVar()
        self.use_default_stator_bezier_var.set(False)
        ttk.Checkbutton(self.parameters_frame, text="Use default Bezier points for stator", variable=self.use_default_stator_bezier_var).grid(row=4, column=0, padx=5, pady=5, sticky='w')

        self.adjust_stator_thickness_var = tk.BooleanVar()
        self.adjust_stator_thickness_var.set(False)
        ttk.Checkbutton(self.parameters_frame, text="Adjust Bezier points of stator for thickness distribution", variable=self.adjust_stator_thickness_var).grid(row=5, column=0, padx=5, pady=5, sticky='w')

        self.adjust_stator_angle_var = tk.BooleanVar()
        self.adjust_stator_angle_var.set(False)
        ttk.Checkbutton(self.parameters_frame, text="Adjust Bezier points of stator for blade angle distribution", variable=self.adjust_stator_angle_var).grid(row=6, column=0, padx=5, pady=5, sticky='w')

        # Plot Options Page
        self.show_section_plot_var = tk.BooleanVar()
        self.show_section_plot_var.set(False)
        ttk.Checkbutton(self.plot_options_frame, text="Show section plot", variable=self.show_section_plot_var).grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.show_angle_distribution_plots_var = tk.BooleanVar()
        self.show_angle_distribution_plots_var.set(False)
        ttk.Checkbutton(self.plot_options_frame, text="Show angle distribution plots", variable=self.show_angle_distribution_plots_var).grid(row=1, column=0, padx=5, pady=5, sticky='w')

        
        # Inlet and Outlet Area Definition Page
        
        
        # Bleed Air Page
        # self.enable_bleed_air_var = tk.BooleanVar(value=False)
        # self.enable_bleed_air_var.trace_add("write", self.update_bleed_air_display)
        # self.enable_bleed_air_checkbox = ttk.Checkbutton(self.bleed_air_frame, text="Enable Bleed Air", variable=self.enable_bleed_air_var)
        # self.enable_bleed_air_checkbox.pack(padx=10, pady=10, anchor='w', side='top')
        
        bleed_air_container = ttk.Frame(self.bleed_air_frame)
        bleed_air_container.pack(padx=10, pady=10, anchor='w', side='top')
        
        self.enable_bleed_air_var = tk.BooleanVar(value=False)
        self.enable_bleed_air_var.trace_add("write", self.update_bleed_air_display)
        self.enable_bleed_air_checkbox = ttk.Checkbutton(bleed_air_container, text="Enable Bleed Air", variable= self.enable_bleed_air_var)
        self.enable_bleed_air_checkbox.pack(side='left')
        
        # Add Tooltip Questionmark
        help_button = ttk.Label(bleed_air_container, text="?", cursor="question_arrow")
        help_button.pack(side='left', padx=(5, 0))
        help_text = "Coordinate Explaination"
        Tooltip(help_button, help_text)
        
        # Output Page
        output_folder_label = ttk.Label(self.output_frame, text="Output Folder Path:")
        output_folder_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.output_folder_entry = ttk.Entry(self.output_frame, width=50)
        self.output_folder_entry.grid(row=0, column=1, padx=5, pady=5)

        output_folder_browse_button = ttk.Button(self.output_frame, text="Browse", command=self.browse_output_folder)
        output_folder_browse_button.grid(row=0, column=2, padx=5, pady=5)

        levels_label = ttk.Label(self.output_frame, text="Levels:")
        levels_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        self.levels_entry = ttk.Entry(self.output_frame, width=50)
        self.levels_entry.grid(row=1, column=1, padx=5, pady=5)

        nrow_label = ttk.Label(self.output_frame, text="Number of Rows [only Rotor: '1' or 1st Stage: '2']")
        nrow_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        self.nrow_entry = ttk.Entry(self.output_frame, width=10)
        self.nrow_entry.insert(0, "2")
        self.nrow_entry.grid(row=2, column=1, padx=5, pady=5)

        save_button_parameters = ttk.Button(self.parameters_frame, text="Save", command=self.save_and_initialize)
        save_button_parameters.grid(row=7, columnspan=2)

        save_button_plot_options = ttk.Button(self.plot_options_frame, text="Save", command=self.save_and_initialize)
        save_button_plot_options.grid(row=2, columnspan=2)
        
        save_button_bleed_air = ttk.Button(self.bleed_air_frame, text="Save", command=self.save_and_initialize)
        save_button_bleed_air.pack(pady=10, side='bottom')

        save_button_output_options = ttk.Button(self.output_frame, text="Save", command=self.save_and_initialize)
        save_button_output_options.grid(row=3, columnspan=3)
        
        # Define Inlet and Outlet Page
        
        inlet_outlet_title_frame = ttk.Frame(self.inlet_outlet_frame)
        inlet_outlet_title_frame.pack(fill='x', padx=10, pady=10)
        
        inlet_outlet_title_label = ttk.Label (inlet_outlet_title_frame, text="Inlet and Outlet Geometry Definition")
        inlet_outlet_title_label.pack(side='left', padx= (0, 5))
        
        inlet_outlet_help = ttk.Label(inlet_outlet_title_frame, text= "?", cursor="question_arrow")
        inlet_outlet_help.pack(side='left', padx=(5, 0))
        inlet_outlet_help_text = "Define the geometry parameters of the Inlet and Outlet Area"
        Tooltip(inlet_outlet_help, inlet_outlet_help_text)
        
        inlet_frame = ttk.LabelFrame(self.inlet_outlet_frame, text="Inlet Area Definition")
        inlet_frame.pack(fill='x', padx=10, pady=10)
        
        # Inlet 
        inlet_area_label = ttk.Label(inlet_frame, text="Inlet Area")
        inlet_area_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        # Area
        inlet_area_help = ttk.Label(inlet_frame, text= "?", cursor="question_arrow")
        inlet_area_help.grid(row=0, column=2, padx=(5, 0))
        inlet_area_help_text = "Enter the Size of the Inlet as a factor of the Diameter of the first Blade Row. Default = 1 (same Size as the Diameter of the first Blade Row)"
        Tooltip(inlet_area_help, inlet_area_help_text)
        
        self.inlet_area_entry = ttk.Entry(inlet_frame, width=10, textvariable=self.inlet_area_var)
        self.inlet_area_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Distanz
        inlet_dist_label = ttk.Label(inlet_frame, text="Inlet Distance")
        inlet_dist_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        inlet_dist_help = ttk.Label(inlet_frame, text= "?", cursor="question_arrow")
        inlet_dist_help.grid(row=1, column=2, padx=(5, 0))
        inlet_dist_help_text = "Enter the Distanz of the Inlet to the first stage as a factor of the first Blade length. Default = 2 (length between the Inlet and the first Blade Row is equal to two times the Blade length) "
        Tooltip(inlet_dist_help, inlet_dist_help_text)
        
        self.inlet_dist_entry = ttk.Entry(inlet_frame, width=10, textvariable=self.inlet_dist_var)
        self.inlet_dist_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Outlet        
        outlet_frame = ttk.LabelFrame(self.inlet_outlet_frame, text="Outlet Area Definition")
        outlet_frame.pack(fill='x', padx=10, pady=10)
        
        # Area
        outlet_area_label = ttk.Label(outlet_frame, text="Outlet Area")
        outlet_area_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        outlet_area_help = ttk.Label(outlet_frame, text= "?", cursor="question_arrow")
        outlet_area_help.grid(row=0, column=2, padx=(5, 0))
        outlet_area_help_text = "Enter the Size of the Outlet as a factor of the Diameter of the last Blade Row. Default = 1 (same Size as the Diameter of the last Blade Row)"
        Tooltip(outlet_area_help, outlet_area_help_text)
        
        self.outlet_area_entry = ttk.Entry(outlet_frame, width=10, textvariable=self.outlet_area_var)
        self.outlet_area_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Distanz
        outlet_dist_label = ttk.Label(outlet_frame, text="Outlet Distance")
        outlet_dist_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        outlet_dist_help = ttk.Label(outlet_frame, text= "?", cursor="question_arrow")
        outlet_dist_help.grid(row=1, column=2, padx=(5, 0))
        outlet_dist_help_text = "Enter the Distanz of the last Blade row to the Outlet as a factor of the last Blade length. Default = 2 (length between the last Blade Row and the Output is equal to two times the Blade length) "
        Tooltip(outlet_dist_help, outlet_dist_help_text)
        
        self.outlet_dist_entry = ttk.Entry(outlet_frame, width=10, textvariable=self.outlet_dist_var)
        self.outlet_dist_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Save Button
        save_button_inlet_outlet = ttk.Button(self.inlet_outlet_frame, text="Save", command=self.save_and_initialize)
        save_button_inlet_outlet.pack(pady=10, side='bottom')

        # Load last output folder path and levels if available
        try:
            with open('Setting.txt', 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('output_folder = '):
                        last_output_folder = line[16:].strip()
                        self.output_folder_entry.insert(0, last_output_folder)
                    elif line.startswith('levels = '):
                        last_levels = line[8:].strip()
                        self.levels_entry.delete(0)
                        self.levels_entry.insert(0, last_levels)
                    elif line.startswith('use_default_rotor_bezier'):
                        self.use_default_rotor_bezier_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('use_default_stator_bezier'):
                        self.use_default_stator_bezier_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('adjust_rotor_thickness'):
                        self.adjust_rotor_thickness_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('adjust_rotor_angle'):
                        self.adjust_rotor_angle_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('adjust_stator_thickness'):
                        self.adjust_stator_thickness_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('adjust_stator_angle'):
                        self.adjust_stator_angle_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('show_section_plot'):
                        self.show_section_plot_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('show_angle_distribution_plots'):
                        self.show_angle_distribution_plots_var.set(line.split('=')[1].strip() == 'True')
                    # Read Saved Bleed Air Settings
                    elif line.startswith('enable_bleed_air'):
                        self.enable_bleed_air_var.set(line.split('=')[1].strip()=='True')
                    # Read Number of Patches and its Coordinates
                    elif line.startswith('rotor_patches = '):
                        self.bleed_air_data['rotor']['count'] = int(line.split('=')[1].strip())
                    elif line.startswith('stator_patches = '):
                        self.bleed_air_data['stator']['count'] = int(line.split('=')[1].strip())
                    elif line.startswith('rotor_patches_'):
                        try:
                            values = [v.strip() for v in line.split('=')[1].strip().split(',')]
                            self.bleed_air_data['rotor']['patches'].append(values)
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing Rotor patchline: line={line}. Error: {e}")
                    elif line.startswith('stator_patches_'):
                        try:
                            values = [v.strip() for v in line.split('=')[1].strip().split(',')]
                            self.bleed_air_data['stator']['patches'].append(values)
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing Stator patchline: line={line}. Error: {e}")    
                    elif line.startswith('inlet_area = '):
                        self.inlet_area_var.set(float(line.split('=')[1].strip()))
                    elif line.startswith('inlet_dist = '):
                        self.inlet_dist_var.set(float(line.split('=')[1].strip()))
                    elif line.startswith('outlet_area = '):
                        self.outlet_area_var.set(float(line.split('=')[1].strip()))
                    elif line.startswith('outlet_dist = '):
                        self.outlet_dist_var.set(float(line.split('=')[1].strip()))



        except FileNotFoundError:
            print("No previous parameters found. Starting with defaults.")
        
        # Initial call to set up the Bleed AIr Tab based on loaded values
        self.update_bleed_air_display()
        
    def update_bleed_air_display(self, *args):
        if self.enable_bleed_air_var.get():
            self.bleed_input_container.pack(fill='both', expand=True, padx=10, pady=10)
            self.create_bleed_input_widget()
        else:
            self.bleed_input_container.pack_forget()
            
    def create_bleed_input_widget(self):
        # Clear existing Widgets
        for widget in self.bleed_input_container.winfo_children():
            widget.destroy()
            
        # Split window into two sides for Rotor and Stator
        self.rotor_frame = ttk.Frame(self.bleed_input_container)
        self.rotor_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        self.stator_frame = ttk.Frame(self.bleed_input_container)
        self.stator_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Add lables for both Rows
        ttk.Label(self.rotor_frame, text="Rotor Bleed Air", style="Bold.TLabel").pack(anchor='w')
        ttk.Label(self.stator_frame, text="Stator Bleed Air", style="Bold.TLabel").pack(anchor='w')
        
        # Add input for number of patches
        self.rotor_patches_frame = ttk.Frame(self.rotor_frame)
        self.rotor_patches_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(self.rotor_patches_frame, text="Number of Bleed Air Patches").pack(side='left')
        q_label_patches_rotor = ttk.Label(self.rotor_patches_frame, text="?", cursor="question_arrow")
        q_label_patches_rotor.pack(side='left', padx=(5, 5))
        Tooltip(q_label_patches_rotor, " Enter the number of Bleed air patches. Each patch is an area where a specific amout of air is bled from")
        self.rotor_patches_entry = ttk.Entry(self.rotor_patches_frame, width=5)
        self.rotor_patches_entry.pack(side='left')
        self.rotor_patches_entry.bind('<Return>', lambda event: self.update_patches('rotor'))
        # Insert loaded Patches
        self.rotor_patches_entry.insert(0, str(self.bleed_air_data['rotor']['count']))
        
        self.stator_patches_frame = ttk.Frame(self.stator_frame)
        self.stator_patches_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(self.stator_patches_frame, text="Number of Bleed Air Patches").pack(side='left')
        q_label_patches_stator = ttk.Label(self.stator_patches_frame, text="?", cursor="question_arrow")
        q_label_patches_stator.pack(side='left', padx=(5, 5))
        Tooltip(q_label_patches_stator, " Enter the number of Bleed air patches. Each patch is an area where a specific amout of air is bled from")
        self.stator_patches_entry = ttk.Entry(self.stator_patches_frame, width=5)
        self.stator_patches_entry.pack(side='left')
        self.stator_patches_entry.bind('<Return>', lambda event: self.update_patches('stator'))
        # Insert loaded Patches
        self.stator_patches_entry.insert(0, str(self.bleed_air_data['stator']['count']))
        
        # Call update_patches to create coordinates in fields upon loading
        self.update_patches('rotor')
        self.update_patches('stator')
        
    def update_patches(self, blade_type):
        if blade_type == 'rotor':
            num_patches_str = self.rotor_patches_entry.get()
            parent_frame = self.rotor_frame
            # Save patches data in dedicated list
            self.rotor_patch_entries.clear()
            patches_data = self.bleed_air_data['rotor']['patches']
        else:
            num_patches_str = self.stator_patches_entry.get()
            parent_frame = self.stator_frame
            # Save patches data in dedicated list
            self.stator_patch_entries.clear()
            patches_data = self.bleed_air_data['stator']['patches']
            
        try:
            num_patches = int(num_patches_str)
            if num_patches < 0:
                raise ValueError
        except (ValueError, IndexError):
            num_patches = 0
            
        # Remove previouse Patch Frames
        for widget in parent_frame.winfo_children():
            # Check if widget is in a patch inputframe
            if isinstance(widget, ttk.LabelFrame):
                widget.destroy()
        
        # Creat new Input widget for each Patch
        for i in range(num_patches):
            patch_frame = ttk.LabelFrame(parent_frame, text=f"Bleed Air Patch {i+1}")
            patch_frame.pack(fill='x',padx=5, pady=5)
            
            patch_entries = []
            
            # I coordinates
            i_label = ttk.Label(patch_frame, text="I start/end:")
            i_label.grid(row=0,column=0,padx=5, pady=2, sticky='w')
            i_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
            i_q_label.grid(row=0, column=3, padx=2, pady=2, sticky='w')
            Tooltip(i_q_label, " The I-Coordinates define the Spanwise direction. Choose Values between 1 and 37. If you want to have bleed air over the whole spane enter 1 and 37")
            i_start_entry = ttk.Entry(patch_frame, width=5)
            i_start_entry.grid(row=0, column=1, padx=5, pady=2)
            i_end_entry = ttk.Entry(patch_frame, width=5)
            i_end_entry.grid(row=0, column=2, padx=5, pady=2)
            
            # J coordinates
            j_label = ttk.Label(patch_frame, text="J start/end:")
            j_label.grid(row=1,column=0,padx=5, pady=2, sticky='w')
            j_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
            j_q_label.grid(row=1, column=3, padx=2, pady=2, sticky='w')
            Tooltip(j_q_label, f"The J-Coordinates define the Axial direction. 1 is defined as the start of the Blade while {JTE} is defined as the End of the blade")
            j_start_entry = ttk.Entry(patch_frame, width=5)
            j_start_entry.grid(row=1, column=1, padx=5, pady=2)
            j_end_entry = ttk.Entry(patch_frame, width=5)
            j_end_entry.grid(row=1, column=2, padx=5, pady=2)
            
            # K coordinates
            k_label = ttk.Label(patch_frame, text="K start/end:")
            k_label.grid(row=2,column=0,padx=5, pady=2, sticky='w')
            k_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
            k_q_label.grid(row=2, column=3, padx=2, pady=2, sticky='w')
            Tooltip(k_q_label, "The K-Coordinate is defined as the Radial direction with 1 being the Hub wall and 37 being the Shroud wall. If you only want Bleed air to be extracted from one of the wall enter 1 and 1 or 37 and 37. It is also possible to extract Bleed air from the Stators and Rotors")
            k_start_entry = ttk.Entry(patch_frame, width=5)
            k_start_entry.grid(row=2, column=1, padx=5, pady=2)
            k_end_entry = ttk.Entry(patch_frame, width=5)
            k_end_entry.grid(row=2, column=2, padx=5, pady=2)
            
            # Massflow
            mflow_label = ttk.Label(patch_frame, text="Extraced Bleed Air (kg/s):")
            mflow_label.grid(row=3, column=0, padx=5, pady=2, sticky='w')
            mflow_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
            mflow_q_label.grid(row=3, column=3, padx=2, pady=2, sticky='w')
            Tooltip(mflow_q_label, "The massflow rate is defined in kg/s. Specify how much Bleed air you want to be extracted in this Bleed air patch")
            massflow_entry = ttk.Entry(patch_frame, width=10)
            massflow_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=2)
            
            # Store Enter entries
            patch_entries.extend([i_start_entry, i_end_entry, j_start_entry, j_end_entry, k_start_entry, k_end_entry, massflow_entry])
            
            # Insert loaded values if exisiting
            if i < len(patches_data):
                for idx, entry in enumerate(patch_entries):
                    if idx < len(patches_data[i]):
                        entry.insert(0,patches_data[i][idx])
                        
            if blade_type == 'rotor':
                self.rotor_patch_entries.append(patch_entries)
            else: 
                self.stator_patch_entries.append(patch_entries)
            

    def browse_output_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, path)

    def save_and_initialize(self):
        use_default_rotor_bezier = self.use_default_rotor_bezier_var.get()
        use_default_stator_bezier = self.use_default_stator_bezier_var.get()
        adjust_rotor_thickness = self.adjust_rotor_thickness_var.get()
        adjust_rotor_angle = self.adjust_rotor_angle_var.get()
        adjust_stator_thickness = self.adjust_stator_thickness_var.get()
        adjust_stator_angle = self.adjust_stator_angle_var.get()
        output_folder = self.output_folder_entry.get()
        
        levels = self.levels_entry.get()
        nrow = self.nrow_entry.get()
        
        show_section_plot = self.show_section_plot_var.get()
        show_angle_distribution_plots = self.show_angle_distribution_plots_var.get()
        
        inlet_area = self.inlet_area_var.get()
        inlet_dist = self.inlet_dist_var.get()
        outlet_area = self.outlet_area_var.get()
        outlet_dist = self.outlet_dist_var.get()
        
        # Get bleed Air Settings
        enable_bleed_air = self.enable_bleed_air_var.get()

        with open('Setting.txt', 'w') as file:
            file.write(f"use_default_rotor_bezier = {use_default_rotor_bezier}\n")
            file.write(f"use_default_stator_bezier = {use_default_stator_bezier}\n")
            file.write(f"adjust_rotor_thickness = {adjust_rotor_thickness}\n")
            file.write(f"adjust_rotor_angle = {adjust_rotor_angle}\n")
            file.write(f"adjust_stator_thickness = {adjust_stator_thickness}\n")
            file.write(f"adjust_stator_angle = {adjust_stator_angle}\n")
            file.write(f"output_folder = {output_folder}\n")
            file.write(f"levels = {levels}\n")
            file.write(f"nrow = {nrow}\n")
            file.write(f"show_section_plot = {show_section_plot}\n")
            file.write(f"show_angle_distribution_plots = {show_angle_distribution_plots}\n")
            # Save Bleed Air data
            file.write(f"enable_bleed_air = {enable_bleed_air}\n")
            if enable_bleed_air:
                file.write(f"rotor_patches = {len(self.rotor_patch_entries)}\n")
                for i, entries in enumerate(self.rotor_patch_entries):
                    i_start = entries[0].get()
                    i_end= entries[1].get()
                    j_start = entries[2].get()
                    j_end= entries[3].get()
                    k_start = entries[4].get()
                    k_end= entries[5].get()
                    massflow = entries[6].get()
                    file.write(f"rotor_patch_{i+1} = {i_start}, {i_end}, {j_start}, {j_end}, {k_start}, {k_end}, {massflow}\n")
                    
                file.write(f"stator_patches = {len(self.stator_patch_entries)}\n")
                for i, entries in enumerate(self.stator_patch_entries):
                    i_start = entries[0].get()
                    i_end= entries[1].get()
                    j_start = entries[2].get()
                    j_end= entries[3].get()
                    k_start = entries[4].get()
                    k_end= entries[5].get()
                    massflow = entries[6].get()
                    file.write(f"stator_patch_{i+1} = {i_start}, {i_end}, {j_start}, {j_end}, {k_start}, {k_end}, {massflow}\n")
                    
            file.write(f"inlet_area = {inlet_area}\n")
            file.write(f"inlet_dist = {inlet_dist}\n")
            file.write(f"outlet_area = {outlet_area}\n")
            file.write(f"outlet_dist = {outlet_dist}\n")

        print("Parameters saved successfully.")

if __name__ == "__main__":
    
    root = tk.Tk() 
    app = CompressorGUI(root) 
    root.mainloop()



def read_parameters_from_file(filename):
    global use_default_rotor_bezier, use_default_stator_bezier
    global adjust_rotor_thickness, adjust_rotor_angle
    global adjust_stator_thickness, adjust_stator_angle
    global output_folder, levels, nrow
    global show_section_plot, show_angle_distribution_plots
    global enable_bleed_air, rotor_patches_data, stator_patches_data
    global inlet_area, inlet_dist, outlet_area, outlet_dist

    # Initialize default values
    use_default_rotor_bezier = 0
    use_default_stator_bezier = 0
    adjust_rotor_thickness = 0
    adjust_rotor_angle = 0
    adjust_stator_thickness = 0
    adjust_stator_angle = 0
    output_folder = ""
    levels = []
    nrow = 2
    show_section_plot = 0
    show_angle_distribution_plots = 0
    enable_bleed_air = False
    rotor_patches_data = []
    stator_patches_data = []
    inlet_area = 0 
    inlet_dist = 0
    outlet_area = 0
    outlet_dist = 0

    try:
        with open(filename, 'r') as file:
            # Read all lines simultaneously to handle patches easily
            lines = file.readlines()
            # Use a state machine to parse bleed air patches
        is_reading_rotor = False
        is_reading_stator = False
        for line in lines:
            line = line.strip()
            if line.startswith('use_default_rotor_bezier'):
                is_reading_rotor = False
                is_reading_stator = False
                use_default_rotor_bezier = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('use_default_stator_bezier'):
                is_reading_rotor = False
                is_reading_stator = False
                use_default_stator_bezier = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('adjust_rotor_thickness'):
                is_reading_rotor = False
                is_reading_stator = False
                adjust_rotor_thickness = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('adjust_rotor_angle'):
                is_reading_rotor = False
                is_reading_stator = False
                adjust_rotor_angle = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('adjust_stator_thickness'):
                is_reading_rotor = False
                is_reading_stator = False
                adjust_stator_thickness = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('adjust_stator_angle'):
                is_reading_rotor = False
                is_reading_stator = False
                adjust_stator_angle = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('output_folder'):
                is_reading_rotor = False
                is_reading_stator = False
                output_folder = line.split('=')[1].strip()
            elif line.startswith('levels'):
                is_reading_rotor = False
                is_reading_stator = False
                levels_input = line.split('=')[1].strip()
                levels = [float(x) for x in levels_input.split(',')]  # Convert levels to list of floats
            elif line.startswith('nrow'):
                is_reading_rotor = False
                is_reading_stator = False
                nrow = int(line.split('=')[1].strip())
            elif line.startswith('show_section_plot'):
                is_reading_rotor = False
                is_reading_stator = False
                show_section_plot = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('show_angle_distribution_plots'):
                is_reading_rotor = False
                is_reading_stator = False
                show_angle_distribution_plots = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('enable_bleed_air'):
                enable_bleed_air = line.split('=')[1].strip() == 'True'
            elif line.startswith('rotor_patches = '):
                is_reading_rotor = True
            elif line.startswith('stator_patches = '):
                is_reading_rotor = False
                is_reading_stator = True
            elif is_reading_rotor and line.startswith('rotor_patch_'):
                values_str = line.split('=')[1].strip().split(',')
                rotor_patches_data.append([v.strip() for v in values_str])
            elif is_reading_stator and line.startswith('stator_patch_'):
                values_str = line.split('=')[1].strip().split(',')
                stator_patches_data.append([v.strip() for v in values_str])
            elif line.startswith('inlet_area = '):
                is_reading_rotor = False
                is_reading_stator = False
                inlet_area = line.split('=')[1].strip()
            elif line.startswith('inlet_dist = '):
                is_reading_rotor = False
                is_reading_stator = False
                inlet_dist = line.split('=')[1].strip()
            elif line.startswith('outlet_area = '):
                is_reading_rotor = False
                is_reading_stator = False
                outlet_area = line.split('=')[1].strip()
            elif line.startswith('outlet_dist = '):
                is_reading_rotor = False
                is_reading_stator = False
                outlet_dist = line.split('=')[1].strip()
                   
            print(f"Levels = {levels}")
            print(f"Folder = {output_folder}")
            
        return use_default_rotor_bezier, use_default_stator_bezier, adjust_rotor_thickness, adjust_rotor_angle, adjust_stator_thickness, adjust_stator_angle, \
        output_folder, levels, nrow, show_section_plot, show_angle_distribution_plots, enable_bleed_air, rotor_patches_data, stator_patches_data, \
        inlet_area, inlet_dist, outlet_area, outlet_dist   

    except FileNotFoundError:
        print("File not found. Please ensure the Setting.txt exists.")

read_parameters_from_file('Setting.txt')
NROW = nrow

# values from channel calculation
global x_values, r_values, m_prime_values, x0 
#x_values, r_values, m_prime_values, x0 = channel(h_H,stage, float(inlet_area), float(inlet_dist), float(outlet_area), float(outlet_dist), fixed_radius_type)

path = output_folder


# function to create a MULTALL Dat
def create_multall_dat(NROW, section, levels, rotor_data, stator_data):
    NSEC = len(levels)
    
    
    # data for all levels
    if section == 0:
        if NROW == 2:
            print(f"stage_1_{NSEC}.dat with all {NSEC} sections for rotor and stator of first stage.")
            dataName = f"stage_1_{NSEC}.dat"
            output = os.path.join(path, dataName)
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
        if NROW == 1:
            print(f"R_{NSEC}.dat with all {NSEC} sections for the rotor of first stage.")
            dataName = f"R_{NSEC}.dat"
            output = os.path.join(path, dataName)
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)

        a = 0
        b = NSEC
        row = 1
        
        # define grid size
        global JTE 
        JM = 111
        JLE = 26
        JTE = 96
        """

        JM = 300
        JLE = 30
        JTE = 280
        """

        j_prime_max = JTE - (JLE - 1)
        num_planes = 5
        n_max_in = JLE
        l_inlet = 1
        n_max_out = JM - (JTE - 1)
        l_outlet = 1
        Z_H = 0.05
        Z_S = 0.95

        write_head_file(output, NSEC, NROW, section, enable_bleed_air)    
        write_head_row(output, row, JM, JLE, JTE, RPM, section, NSEC)
        z, s_1D, s_0_5, x_LE, elipse_LE, elipse_TE = overall_values(row, z_R, l_R, l_S)
        beta_M_a, beta_M_2, beta_M_3, beta_M_e, d_l_a, d_l_2, d_l_3, d_l_e, m_star_BP = blade_metal_BP(row)   
        m_LE_0_5, m_TE_0_5, m_cntr_0_5, m_prime_cntr = mLE_TE_cntr(row)

        x_new, d_new, R_new, Rtheta_new = calc_blade_row_coordinates(row, j_prime_max, num_planes, n_max_in, l_inlet, n_max_out, l_outlet, Z_H, Z_S, levels)
        
        """
        #xRtheta_plot(Rtheta_new, R_new, x_new)
        Rtheta_new_low = []
        for i in range(len(Rtheta_new)):
            Rtheta_new_low.append([])
        
        for i in range(len(d_new)):
            for j in range(len(d_new[i])):
                Rtheta_new_low[i].append(Rtheta_new[i][j]-d_new[i][j]) 

        for i in range(len(levels)):
            for j in range(len(x_new[0])-1):
                if x_new[i][j]>x_new[i][j+1]:
                    print("To many J Values")

        for i in range(len(levels)):
            plt.plot(x_new[i], Rtheta_new[i])
            plt.plot(x_new[i], Rtheta_new_low[i])
            plt.scatter(x_new[i], Rtheta_new[i], s = 3)
            plt.scatter(x_new[i], Rtheta_new_low[i],s = 3)

        plt.axis('equal')
        plt.show()
        """

        write_coordinates(x_new, Rtheta_new, d_new, R_new, output, row, a, b, JM)
        
        if NROW == 2:

            row = 2
            z, s_1D, s_0_5, x_LE, elipse_LE, elipse_TE = overall_values(row, z_R, l_R, l_S)
            beta_M_a, beta_M_2, beta_M_3, beta_M_e, d_l_a, d_l_2, d_l_3, d_l_e, m_star_BP = blade_metal_BP(row)   
            m_LE_0_5, m_TE_0_5, m_cntr_0_5, m_prime_cntr = mLE_TE_cntr(row)
            
            # define grid size
            
            JM =  150
            JLE = 21
            JTE = 140
            """
            JM =  104
            JLE = 21
            JTE = 91
            """
            j_prime_max = JTE - (JLE - 1)
            num_planes = 5
            n_max_in = JLE
            l_inlet = 1
            n_max_out = JM - (JTE - 1)
            l_outlet = 1
            Z_H = 0.05
            Z_S = 0.95

            x_new, d_new, R_new, Rtheta_new = calc_blade_row_coordinates(row, j_prime_max, num_planes, n_max_in, l_inlet, n_max_out, l_outlet, Z_H, Z_S, levels)
            """
            Rtheta_new_low = []
            for i in range(len(Rtheta_new)):
                Rtheta_new_low.append([])
        
            for i in range(len(d_new)):
                for j in range(len(d_new[i])):
                    Rtheta_new_low[i].append(Rtheta_new[i][j]-d_new[i][j]) 
            
            for i in range(len(levels)):
                plt.plot(x_new[i], Rtheta_new[i])
                plt.plot(x_new[i], Rtheta_new_low[i])
                plt.scatter(x_new[i], Rtheta_new[i], s = 3)
                plt.scatter(x_new[i], Rtheta_new_low[i],s = 3)

            plt.xlabel("x [m]")
            plt.ylabel("R\u03b8 [m]")
            plt.show()
            """
            #xRtheta_plot(Rtheta_new, R_new, x_new)

            write_head_row(output, row, JM, JLE, JTE, section, section, NSEC)
            write_coordinates(x_new, Rtheta_new, d_new, R_new, output, row, a, b, JM)
    
        write_end_file(NROW, output, section)
        create_bleed_air_card(NROW, output, rotor_data, stator_data)
        
        if NROW == 1:
            plt.show()

    else:
        #data for a single selected level
        if section <= 0 or section > NSEC:
            print("Not allowed section range.")

        if NROW == 2:
            print(f"stage_1_section_{section}_of_{NSEC}.dat with section {section} of {NSEC} for rotor and stator of first stage.")
            dataName = f"stage_1_section_{section}_of_{NSEC}.dat"
            output = os.path.join(path, dataName)
        
        if NROW == 1:
            print(f"rotor_1_section_{section}_of_{NSEC}.dat with section {section} of {NSEC} for rotor of first stage.")
            dataName = f"rotor_1_section_{section}_of_{NSEC}.dat"
            output = os.path.join(path, dataName)
            
        row = 1
        a = section - 1
        b = section

        NSEC = 1
        row = 1
        
        """
        JM = 120
        JLE = 26
        JTE = 105
        """
        JM = 140
        JLE = 26
        JTE = 125
        

        j_prime_max = JTE - (JLE - 1)
        num_planes = 5
        n_max_in = JLE
        l_inlet = 1
        n_max_out = JM - (JTE - 1)
        l_outlet = 1
        Z_H = 0.05
        Z_S = 0.95

        write_head_file(output, NSEC, NROW, section, enable_bleed_air)    
        write_head_row(output, row, JM, JLE, JTE, RPM, section, NSEC)
        z, s_1D, s_0_5, x_LE, elipse_LE, elipse_TE = overall_values(row, z_R, l_R, l_S)
        beta_M_a, beta_M_2, beta_M_3, beta_M_e, d_l_a, d_l_2, d_l_3, d_l_e, m_star_BP = blade_metal_BP(row)   
        m_LE_0_5, m_TE_0_5, m_cntr_0_5, m_prime_cntr = mLE_TE_cntr(row)

        x_new, d_new, R_new, Rtheta_new = calc_blade_row_coordinates(row, j_prime_max, num_planes, n_max_in, l_inlet, n_max_out, l_outlet, Z_H, Z_S, levels)
        """
        #xRtheta_plot(Rtheta_new, R_new, x_new)
        Rtheta_new_low = []
        for i in range(len(Rtheta_new)):
            Rtheta_new_low.append([])
        
        for i in range(len(d_new)):
            for j in range(len(d_new[i])):
                Rtheta_new_low[i].append(Rtheta_new[i][j]-d_new[i][j]) 
        
        for i in range(len(levels)):
            for j in range(len(x_new[0])-1):
                if x_new[i][j]>x_new[i][j+1]:
                    print("negative Volumes")

        
        for i in range(len(levels)):
            plt.plot(x_new[i], Rtheta_new[i])
            plt.plot(x_new[i], Rtheta_new_low[i])
            plt.scatter(x_new[i], Rtheta_new[i], s = 3)
            plt.scatter(x_new[i], Rtheta_new_low[i],s = 3)

        plt.axis('equal')
        plt.show()
        """
        if NROW == 1:
            plt.show()
        
        write_coordinates(x_new, Rtheta_new, d_new, R_new, output, row, a, b, JM)
        Q3D_information(output)
        
        if NROW == 2:
            
            row = 2
            
            # define grid size
            JM =  150
            JLE = 21
            JTE = 140

            """
            JM =  104
            JLE = 21
            JTE = 91
            """

            j_prime_max = JTE - (JLE - 1)
            num_planes = 5
            n_max_in = JLE
            l_inlet = 1
            n_max_out = JM - (JTE - 1)
            l_outlet = 1
            Z_H = 0.05
            Z_S = 0.95
        
            z, s_1D, s_0_5, x_LE, elipse_LE, elipse_TE = overall_values(row, z_R, l_R, l_S)
            beta_M_a, beta_M_2, beta_M_3, beta_M_e, d_l_a, d_l_2, d_l_3, d_l_e, m_star_BP = blade_metal_BP(row)   
            m_LE_0_5, m_TE_0_5, m_cntr_0_5, m_prime_cntr = mLE_TE_cntr(row)
            x_new, d_new, R_new, Rtheta_new = calc_blade_row_coordinates(row, j_prime_max, num_planes, n_max_in, l_inlet, n_max_out, l_outlet, Z_H, Z_S, levels)
            
            #xRtheta_plot(Rtheta_new, R_new, x_new)
            """
            Rtheta_new_low = []
            for i in range(len(Rtheta_new)):
                Rtheta_new_low.append([])

            for i in range(len(d_new)):
                for j in range(len(d_new[i])):
                    Rtheta_new_low[i].append(Rtheta_new[i][j]-d_new[i][j]) 
            
            for i in range(len(levels)):
                for j in range(len(x_new[0])-1):
                    if x_new[i][j]>x_new[i][j+1]:
                        print("negative Volumes")
            
            for i in range(len(levels)):
                plt.plot(x_new[i], Rtheta_new[i])
                plt.plot(x_new[i], Rtheta_new_low[i])
                plt.scatter(x_new[i], Rtheta_new[i], s = 3)
                plt.scatter(x_new[i], Rtheta_new_low[i],s = 3)
            
            plt.show()
            """
        
            write_head_row(output, row, JM, JLE, JTE, RPM, section, NSEC)
            write_coordinates(x_new, Rtheta_new, d_new, R_new, output, row, a, b, JM)
            Q3D_information(output)

        write_end_file(NROW, output, section)
        create_bleed_air_card(NROW, output, rotor_data, stator_data)

# functions for adjusting bezier point
def adjustBezierCurve_d_l(BezierPoints):

    d_lB = BezierPoints
    mB = [0.0, 0.3, 0.7, 1.0] 
    t = np.arange(0, 1.01, 0.01)

    x = bezier(4, t, mB)
    y = bezier(4, t, d_lB)

    # Create the plot
    fig, ax = plt.subplots(num='Thickness Distribution')
    plt.subplots_adjust(bottom=0.5)  # Leave more space for the sliders

    # Plot the points
    points, = plt.plot(mB, d_lB, 'o-', label="Points")
    curve, = plt.plot(x,y)
    plt.title("Thickness Distribution - Béziercurve")
    plt.xlabel("x/l [-]")
    plt.ylabel("d/l [%]")


    # Set axis limits
    ax.set_xlim(0, 1)

    d_l_min = 0.0
    d_l_max = 10.0

    ax.set_ylim(d_l_min, d_l_max)

    # Add sliders for each point
    sliders = []  # Store slider objects
    slider_axes = []  # Store axes for sliders

    for i in range(4):  # Create one slider for each point
        ax_slider = plt.axes([0.2, 0.25 - i * 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        slider = Slider(ax_slider, f'Point {i + 1}', d_l_min, d_l_max, valinit=d_lB[i])
        sliders.append(slider)
        slider_axes.append(ax_slider)

    # Define update function for sliders
    def update(val):
        for i, slider in enumerate(sliders):
            d_lB[i] = slider.val  # Update y-coordinate for each point
        
        y = bezier(4, t, d_lB)
        curve.set_ydata(y)
        points.set_ydata(d_lB)  # Update the plot
        fig.canvas.draw_idle()

    # Connect sliders to the update function
    for slider in sliders:
        slider.on_changed(update)

    # Show the interactive plot
    plt.show()
    for i in range(len(d_lB)):
        d_lB[i] = round(d_lB[i], 2)

    print(f"New Bézier Point: {d_lB}")
    
    return BezierPoints

def adjustBezierCurve_d(BezierPoints, cordlenght):

    d_lB = [point * cordlenght / 100 for point in BezierPoints]
    mB = [0.0, 0.3, 0.7, 1.0] 
    t = np.arange(0, 1.01, 0.01)

    x = bezier(4, t, mB)
    y = bezier(4, t, d_lB)

    # Create the plot
    fig, ax = plt.subplots(num='Thickness Distribution')
    plt.subplots_adjust(bottom=0.5)  # Leave more space for the sliders

    # Plot the points
    points, = plt.plot(mB, d_lB, 'o-', label="Points")
    curve, = plt.plot(x,y)
   # plt.figure(num='This is the title');
    plt.title("Thickness Distribution - Béziercurve")
    plt.xlabel("x/l [-]")
    plt.ylabel("d [mm]")
    plt.grid('on')


    # Set axis limits
    ax.set_xlim(0, 1)

    dmin = 0.0
    dmax = 5.0

    ax.set_ylim(dmin, dmax)

    # Add sliders for each point
    sliders = []  # Store slider objects
    slider_axes = []  # Store axes for sliders

    for i in range(4):  # Create one slider for each point
        ax_slider = plt.axes([0.2, 0.25 - i * 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        slider = Slider(ax_slider, f'Point {i + 1}', dmin, dmax, valinit=d_lB[i])
        sliders.append(slider)
        slider_axes.append(ax_slider)

    # Define update function for sliders
    def update(val):
        for i, slider in enumerate(sliders):
            d_lB[i] = slider.val  # Update y-coordinate for each point
        
        y = bezier(4, t, d_lB)
        curve.set_ydata(y)
        points.set_ydata(d_lB)  # Update the plot
        fig.canvas.draw_idle()

    # Connect sliders to the update function
    for slider in sliders:
        slider.on_changed(update)

    # Show the interactive plot
    plt.show()
    for i in range(len(d_lB)):
        d_lB[i] = round(d_lB[i]*100/cordlenght, 2)

    
    print(f"New Bézier Point: {d_lB}")
    return d_lB

def adjustBezierCurve_beta(BezierPoints):

    beta = BezierPoints

    mB = [0.0, 0.3, 0.7, 1.0] 
    t = np.arange(0, 1.01, 0.01)

    x = bezier(4, t, mB)
    y = bezier(4, t, beta)

    # Create the plot
    fig, ax = plt.subplots(num='Blade Angle Distribution')
    plt.subplots_adjust(bottom=0.5)  # Leave more space for the sliders

    # Plot the points
    points, = plt.plot(mB, beta, 'o-', label="Points")
    curve, = plt.plot(x,y)
    plt.title("Blade Angle Distribution - Béziercurve")
    plt.xlabel("x/l [-]")
    plt.ylabel("blade angle [°]")


    # Set axis limits
    ax.set_xlim(0, 1)

    beta_min = 0.0
    beta_max = 170

    ax.set_ylim(beta_min, beta_max)

    # Add sliders for each point
    sliders = []  # Store slider objects
    slider_axes = []  # Store axes for sliders

    for i in range(4):  # Create one slider for each point
        ax_slider = plt.axes([0.2, 0.25 - i * 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        slider = Slider(ax_slider, f'Point {i + 1}', beta_min, beta_max, valinit=beta[i])
        sliders.append(slider)
        slider_axes.append(ax_slider)

    # Define update function for sliders
    def update(val):
        for i, slider in enumerate(sliders):
            beta[i] = slider.val  # Update y-coordinate for each point
        
        y = bezier(4, t, beta)
        curve.set_ydata(y)
        points.set_ydata(beta)  # Update the plot
        fig.canvas.draw_idle()

    # Connect sliders to the update function
    for slider in sliders:
        slider.on_changed(update)

    # Show the interactive plot
    plt.show()
    for i in range(len(beta)):
        beta[i] = round(beta[i], 2)

    print(f"New Bézier Point: {beta}")
    return BezierPoints



# section to create a plot of geometry, blade angle and thickniss distribution 
def show_plots():
    global z_R, l_R, l_S, i_st, show_section_plot, show_angle_distribution_plots
    global length, row, h, farben
    
    if show_section_plot == 1:
        length = []
        row = 1
        for k in range(len(h)):
                h = [0.0 , 0.2, 0.5, 0.8, 1.0]
                farben = ["pink", "blue", "green", "red", "black"]
                i = h[k]
                chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
                plt.plot(m_star_u, R_theta_s_star_u, color = farben[k], label = f"{h[k]*100}%")
                plt.plot(m_star_l, R_theta_s_star_l, color = farben[k])
                plt.legend()  

        
        if NROW == 2:    
            length = []
            row = 2
            for k in range(len(h)):
                h = [0.0 , 0.2, 0.5, 0.8, 1.0]
                farben = ["pink", "blue", "green", "red", "black"]
                i = h[k]
                chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
                #length.append(chord)
                plt.plot(m_star_u, R_theta_s_star_u, color = farben[k], label = f"{h[k]*100}%")
                plt.plot(m_star_l, R_theta_s_star_l, color = farben[k])
        
        plt.xlabel("x [mm]")
        plt.ylabel("R\u03b8 [mm]") 
                
        plt.show()

    if show_angle_distribution_plots == 1:
        row = 1
        for k in range(len(h)):
                h = [0.0 , 0.2, 0.5, 0.8, 1.0]
                farben = ["pink", "blue", "green", "red", "black"]
                i = h[k]
                chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
                plt.plot(m_prime, beta_S, label = f"{h[k]*100}%", color = farben[k])
                plt.scatter(m_BP, beta_BP, color = farben[k])
                plt.legend() 
        
        if NROW == 2:    
            length = []
            row = 2
            for k in range(len(h)):
                h = [0.0 , 0.2, 0.5, 0.8, 1.0]
                farben = ["pink", "blue", "green", "red", "black"]
                i = h[k]
                chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
                plt.plot(m_prime, beta_S, label = f"{h[k]*100}%", color = farben[k])
                plt.scatter(m_BP, beta_BP, color = farben[k])
                

        plt.xlabel('x/s [%]')
        plt.ylabel("blade angle [°]")           
        plt.show()

