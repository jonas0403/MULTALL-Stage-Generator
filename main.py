import math 
import numpy as np
import matplotlib.pyplot as plt
import csv
import os 
import sys 
from matplotlib.widgets import Slider

import tkinter as tk
from tkinter import ttk, filedialog, Label, Toplevel


from src.Fixed_radii_Meanline_GUI_v4 import meanline 
from src.Cubspline_function_v2 import cubspline
from src.Radial_equilibrium import radial_equilibrium_R, radial_equilibrium_S
from src.Bezier_curve import bezier
from src.Interpolation import intpol, intp_new
from src.Channel_v2 import channel
from src.Stage_v3_working_with_bleedair import plot_temp_alpha_beta, read_parameters_from_file, bezier_control_points, calculation_of_section
from src.GUI import render_gui

'''
Inital values to define
'''
wdpath = os.getcwd()

scriptpath = os.path.dirname(sys.argv[0])

os.chdir(scriptpath)

# parameter for radial equilibrium
stage = 1
approach = 1
constant_r_parameter = 1

LOCK_FILE = 'settings.lock'

h_H = [0.0, 0.2, 0.5, 0.8, 1.0]
LE_shift = 0.025
Pi = math.pi

# define grid size
JM = 111
JLE = 26
JTE = 96



'''
Inital calc of start values

meanline and radial equilibirum
'''

mflow, RPM, kappa, R, cp, i_st, T_t1, T_t2, T_t3, T_1, T_2, T_3, p_1, p_2, p_3, p_t1, p_t2, p_t3, D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_m1, D_m2, D_m3, b1, b2, b3, cu1, cu2, cu3, u1, u2, u3, cm1, cm2, cm3, delta_h_t, l_R, l_S, l_R_t_R, l_S_t_S, d_R_l_R, d_S_l_S, incidence_R, incidence_S, z_R, z_S, beta_blade_1, beta_blade_2, alpha_blade_2, alpha_blade_3, TPR_M, eta_sC_tt_M, eta_pC_tt_M, fixed_radius_type = meanline(GUI_On=1)

h_rel, l_S, c_m_S_in, c_m_S_out, c_u_S_in, c_u_S_out, c_S_out, T_S_in, T_S_out, p_S_in, p_S_out, alpha_S_in, beta_S_in, alpha_S_out, beta_blade_S_in, beta_blade_S_out, D_S = radial_equilibrium_S(stage, approach, constant_r_parameter, D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_m1, D_m2, D_m3, b1, b2, b3, cu1, cu2, cu3, u1, u2, u3, cm1, cm2, cm3, delta_h_t, T_t1, T_t2, T_t3, p_t1, p_t2, p_t3)
h_rel, l_R, r_R_out, c_m_R_in, c_m_R_out, c_u_R_in, c_u_R_out, c_R_out, u_R_in, u_R_out, T_R_in, T_R_out, p_R_in, p_R_out, Ma_abs_R_in, Ma_rel_R_in, roh_R_in, alpha_R_in, beta_R_in, alpha_R_out, beta_R_out, beta_blade_R_in, beta_blade_R_out, D_R = radial_equilibrium_R(stage, approach, constant_r_parameter, D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_m1, D_m2, D_m3, b1, b2, b3, cu1, cu2, cu3, u1, u2, u3, cm1, cm2, cm3, delta_h_t, T_t1, T_t2, T_t3, p_t1, p_t2, p_t3)

'''
Plotting of Temperatur-, Alpha- and Beta distributions
'''

plot_temp_alpha_beta(T_Plot = 0, beta_R_Plot = 0, alpha_S_Plot = 0)

'''
Reading the last simulation data from the settings file
'''
use_default_rotor_bezier, use_default_stator_bezier, adjust_rotor_thickness, adjust_rotor_angle, adjust_stator_thickness, adjust_stator_angle, \
        output_folder, levels, nrow, show_section_plot, show_angle_distribution_plots, enable_bleed_air, rotor_patches_data, stator_patches_data, \
        inlet_area, inlet_dist, outlet_area, outlet_dist = read_parameters_from_file('Setting.txt')


'''
channel calculation
'''
x_values, r_values, m_prime_values, x0 = channel(h_H,stage, float(inlet_area), float(inlet_dist), float(outlet_area), float(outlet_dist), fixed_radius_type)




'''
Possibly not used
'''
#area to change rotor:
length = []
h = [0.0 , 0.2, 0.5, 0.8, 1.0]
row = 1
for k in range(len(h)):
    i = h[k]
    chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
    length.append(chord)

if use_default_rotor_bezier == 1:
    bezier_control_points("bezier_control_points_R.txt", 1, beta_blade_R_in, beta_blade_R_out, length)

if use_default_stator_bezier == 1:
    bezier_control_points("bezier_control_points_S.txt", 2, beta_blade_S_in, beta_blade_S_out, length)