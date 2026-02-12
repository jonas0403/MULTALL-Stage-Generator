# Author: Marco Wiens
# Version: 05.12.2024
# Radial-equilibrium
# Programm for calculation of radial equilibrium

import math
import numpy as np
import matplotlib as plt

Pi = math.pi



from Functions_losses import  angle_blade_in, angle_blade_out 




#function for meridional velocity
def rad_eq_cm(appr, position, r, cu_ref_in, cu_ref_out, cm_ref, r_ref, u_ref, Dh_t):
    switch = 1
    if position == 1:
        switch = -1
    
    r_rel = max(r_ref / r, 0.0000001)
    cu_inf = (cu_ref_in + cu_ref_out) / 2
    
    # Free Vortex approach
    cm = cm_ref
    A = cu_inf * r_ref
    B = r_ref * Dh_t / (2 * u_ref)
    
    # Constant Reaction approach
    if appr == 2:
        A = cu_inf / r_ref
        cmq = cm_ref ** 2 + 2 * A ** 2 * (r_ref ** 2 - r ** 2 + switch * 2 * B / A * math.log(r_rel))
        if cmq <= 0:
            cmq = 0
        cm = math.sqrt(cmq)

    # Exponential Method approach
    if appr == 3:
        A = cu_inf
        cmq = cm_ref ** 2 + 2 * A * (A * math.log(r_rel) + switch * 2 * B * (1 / r - 1 / r_rel))
        if cmq <= 0:
            cmq = 0
        cm = math.sqrt(cmq)
    
    return cm

#function for circumferential velocity
def rad_eq_cu(appr, position, r, cu_ref_in, cu_ref_out, cm_ref, r_ref, u_ref, Dh_t):
    switch = 1
    if position == 1:
        switch = -1

    r_rel = max(r_ref / r, 0.0000001)
    cu_inf = (cu_ref_in + cu_ref_out) / 2

    # Free Vortex approach
    exponent = -1
    A = cu_inf * r_ref
    B = r_ref * Dh_t / (2 * u_ref)
    cu = A * r**exponent + switch * B / r

    # Constant Reaction approach
    if appr == 2:
        exponent = 1
        A = cu_inf / r_ref
        cu = A * r**exponent + switch * B / r

    # Exponential Method approach
    if appr == 3:
        exponent = 0
        A = cu_inf
        cu = A * r**exponent + switch * B / r

    return cu

#calculation of reference valuess
def references(stage, cu1, cu2, cu3, cm1, cm2, cm3, D_m2, u1, u2, u3):
    cu_ref_in, cu_ref_out, cm_ref, r_ref, u_ref = [], [], [], [], []
    for cu_list in [cu1, cu2, cu3]:
        cu_ref_in.append(cu_list[stage-1]) 

    cu_ref_out.append(cu2[stage-1])

    cu_ref_out.append(cu2[stage-1])
    cu_ref_out.append(cu3[stage-1])

    for cm_list in [cm1, cm2, cm3]:
        cm_ref.append(cm_list[stage-1]) 

    for i in range(3):
        r_ref.append(D_m2[i]/(1000*2))

    for u_list in [u1, u2, u3]:
        u_ref.append(u_list[stage-1]) 
    
    return D_m1, D_m2, D_m3, cu_ref_in, cu_ref_out, cm_ref, r_ref, u_ref
 
# radial equilibrium for the rotor
def radial_equilibrium_R(stage, approach, constant_r_parameter, D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_m1, D_m2, D_m3, b1, b2, b3, cu1, cu2, cu3, u1, u2, u3, cm1, cm2, cm3, delta_h_t, T_t1, T_t2, T_t3, p_t1, p_t2, p_t3):
    
    h_H = [0.0, 0.2, 0.5, 0.8, 1.0]
    cu_ref_in, cu_ref_out, cm_ref, r_ref, u_ref = references(stage, cu1, cu2, cu3, cm1, cm2, cm3, D_m2, u1, u2, u3)
    
    dh = 0.05
    h_rel = np.arange(0.0, 1.0 + dh, dh)
    
    # Rotor inlet
    r_R_in = []
    for i in range(len(h_rel)): 
        if constant_r_parameter == 0:
            r_R_in.append((D_H1[stage-1]/2+h_rel[i]*b1[stage-1])/1000)

        elif constant_r_parameter == 1:
            r_R_in.append((D_m1[stage-1]/2+(h_rel[i]-0.5)*b1[stage-1])/1000)

        elif constant_r_parameter == 2:
            r_R_in.append((D_S1[stage-1]/2+(h_rel[i]-1)*b1[stage-1])/1000)

        else:
            print("Allowed constant radius parameter: 0, 1 and 2.")

    c_m_R_in, c_u_R_in, u_R_in, w_R_in, T_R_in, p_R_in, Ma_abs_R_in, Ma_rel_R_in, roh_R_in, alpha_R_in, beta_R_in = [], [], [], [], [], [], [], [], [], [], []
    for i in range(len(h_rel)):
        c_m_R_in.append(rad_eq_cm(approach, 1, r_R_in[i], cu_ref_in[0], cu_ref_out[0], cm_ref[0], r_ref[0], u_ref[0], delta_h_t[stage-1]))
        c_u_R_in.append(rad_eq_cu(approach, 1, r_R_in[i], cu_ref_in[0], cu_ref_out[0], cm_ref[0], r_ref[0], u_ref[0], delta_h_t[stage-1]))
        u_R_in.append(r_R_in[i] / r_ref[0] * u_ref[0])
        w_R_in.append(math.sqrt(c_m_R_in[i]**2 + (u_R_in[i] - c_u_R_in[i])**2))
        T_R_in.append(T_t1[stage-1] - (c_m_R_in[i]**2 + c_u_R_in[i]**2) / (2 * cp))
        p_R_in.append(p_t1[stage-1] * (T_R_in[i] / T_t1[stage-1])**(kappa / (kappa - 1)))
        Ma_abs_R_in.append(math.sqrt(c_m_R_in[i]**2 + c_u_R_in[i]**2) / math.sqrt(kappa * R * T_R_in[i]))
        Ma_rel_R_in.append(w_R_in[i] / math.sqrt(kappa * R * T_R_in[i]))
        roh_R_in.append(p_R_in[i] / (T_R_in[i] * R))
        alpha_R_in.append(math.acos(c_u_R_in[i] / math.sqrt(c_u_R_in[i]**2 + c_m_R_in[i]**2)) / Pi * 180)
        beta_R_in.append(math.acos((c_u_R_in[i] - u_R_in[i]) / (math.sqrt((c_u_R_in[i] - u_R_in[i])**2 + c_m_R_in[i]**2))) / Pi * 180)

    MF_Integral_R_in = []
    for i in range(len(h_rel)-1):
        MF_Integral_R_in.append(Pi*(r_R_in[i+1]**2-r_R_in[i]**2)*(c_m_R_in[i+1]*roh_R_in[i+1]+c_m_R_in[i]*roh_R_in[i])/2)

    MF_R_in = sum(MF_Integral_R_in)

    # Rotor outlet/ stator inlet
    r_R_out = []
    for i in range(len(h_rel)): 
        if constant_r_parameter == 0:
            r_R_out.append((D_H2[stage-1]/2+h_rel[i]*b2[stage-1])/1000)

        elif constant_r_parameter == 1:
            r_R_out.append((D_m2[stage-1]/2+(h_rel[i]-0.5)*b2[stage-1])/1000)

        elif constant_r_parameter == 2:
            r_R_out.append((D_S2[stage-1]/2+(h_rel[i]-1)*b2[stage-1])/1000)

        else:
            print("Allowed constant radius parameter: 0, 1 and 2.")

    c_m_R_out, c_u_R_out, c_R_out, u_R_out, w_R_out, T_R_out, p_R_out, Ma_abs_R_out, Ma_rel_R_out, roh_R_out, alpha_R_out, beta_R_out = [], [], [], [], [], [], [], [], [], [], [], []
    for i in range(len(h_rel)):
        c_m_R_out.append(rad_eq_cm(approach, 2, r_R_out[i], cu_ref_in[0], cu_ref_out[0], cm_ref[0], r_ref[0], u_ref[0], delta_h_t[stage-1]))
        c_u_R_out.append(rad_eq_cu(approach, 2, r_R_out[i], cu_ref_in[0], cu_ref_out[0], cm_ref[0], r_ref[0], u_ref[0], delta_h_t[stage-1]))
        c_R_out.append(math.sqrt(c_m_R_out[i]**2 + c_u_R_out[i]**2))            
        u_R_out.append(r_R_out[i] / r_ref[0] * u_ref[0])
        w_R_out.append(math.sqrt(c_m_R_out[i]**2 + (u_R_out[i] - c_u_R_out[i])**2))
        T_R_out.append(T_t2[stage-1] - (c_m_R_out[i]**2 + c_u_R_out[i]**2) / (2 * cp)) 
        Ma_abs_R_out.append(math.sqrt(c_m_R_out[i]**2 + c_u_R_out[i]**2) / math.sqrt(kappa * R * T_R_out[i]))
        Ma_rel_R_out.append(u_R_out[i] / math.sqrt(kappa * R * T_R_out[i]))
        p_R_out.append(p_t2[stage-1] * (T_R_out[i] / T_t2[stage-1])**(kappa / (kappa - 1)))
        roh_R_out.append(p_R_out[i] / (T_R_out[i] * R))
        alpha_R_out.append(math.acos(c_u_R_out[i] / math.sqrt(c_u_R_out[i]**2 + c_m_R_out[i]**2)) / Pi * 180)
        beta_R_out.append(math.acos((c_u_R_out[i] - u_R_out[i]) / (math.sqrt((c_u_R_out[i] - u_R_out[i])**2 + c_m_R_out[i]**2))) / Pi * 180)
    

    MF_Integral_R_out = []
    for i in range(len(h_rel)-1):
        MF_Integral_R_out.append(Pi*(r_R_out[i+1]**2-r_R_out[i]**2)*(c_m_R_out[i+1]*roh_R_out[i+1]+c_m_R_out[i]*roh_R_out[i])/2)
        
    MF_S = sum(MF_Integral_R_out)

    beta_blade_R_in, beta_blade_R_out = [], []
    for i in range(len(h_rel)):
        beta_blade_R_in.append(angle_blade_in(beta_R_in[i], beta_R_out[i], w_R_in[i], w_R_out[i], T_R_in[i], T_R_out[i], l_R_t_R[0],  d_R_l_R[0], incidence_R[0], R, kappa))
        beta_blade_R_out.append(angle_blade_out(beta_R_in[i], beta_R_out[i],  w_R_in[i], w_R_out[i], T_R_in[i], T_R_out[i], l_R_t_R[0],  d_R_l_R[0], incidence_R[0], R, kappa))
    
    # Rotor data
    solidity_R = [l_R_t_R[stage-1]]*len(h_rel)
    l_R, axial_length_R, delta_beta_R, w_R_out_w_R_in, D_R = [], [], [], [], []
    for i in range(len(h_rel)):
        l_R.append(solidity_R[i]*2*Pi*(r_R_out[i]+r_R_in[i])/(2*z_R[stage-1])*1000)
        axial_length_R.append(l_R[i]*math.sin((beta_blade_R_out[i]+beta_blade_R_in[i])/(2*180)*Pi))
        delta_beta_R.append(beta_R_out[i]-beta_R_in[i])
        w_R_out_w_R_in.append(w_R_out[i]/w_R_in[i])
        D_R.append(1-w_R_out_w_R_in[i]+abs((c_u_R_out[i]-u_R_out[i])-(c_u_R_in[i]-u_R_in[i]))/(2*solidity_R[i]*w_R_in[i]))
    
    return h_rel, l_R, r_R_out, c_m_R_in, c_m_R_out, c_u_R_in, c_u_R_out, c_R_out, u_R_in, u_R_out, T_R_in, T_R_out, p_R_in, p_R_out, Ma_abs_R_in, Ma_rel_R_in, roh_R_in, alpha_R_in, beta_R_in, alpha_R_out, beta_R_out, beta_blade_R_in, beta_blade_R_out, D_R

# radial equilibrium for the stator         
def radial_equilibrium_S(stage, approach, constant_r_parameter, D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_m1, D_m2, D_m3, b1, b2, b3, cu1, cu2, cu3, u1, u2, u3, cm1, cm2, cm3, delta_h_t, T_t1, T_t2, T_t3, p_t1, p_t2, p_t3):        
    
    # inlet values of the stator are the outlet values of the rotor befor
    h_rel, l_R, r_S_in, c_m_R_in, c_m_S_in, c_u_R_in, c_u_S_in, c_S_in, u_R_in, u_S_in, T_R_in, T_S_in, p_R_in, p_S_in, Ma_abs_R_in, Ma_rel_R_in, roh_R_in, alpha_R_in, beta_R_in, alpha_S_in, beta_S_in, beta_blade_R_in, beta_blade_R_out, D_R  = radial_equilibrium_R(stage, approach, constant_r_parameter, D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_m1, D_m2, D_m3, b1, b2, b3, cu1, cu2, cu3, u1, u2, u3, cm1, cm2, cm3, delta_h_t, T_t1, T_t2, T_t3, p_t1, p_t2, p_t3)
    
    # outlet values of the stator should be inlet values of the following rotor
    h_rel, l_R, r_R_out, c_m_S_out, c_m_R_out, c_u_S_out, c_u_R_out, c_R_out, u_S_out, u_R_out, T_S_out, T_R_out, p_S_out, p_R_out, Ma_abs_S_out, Ma_rel_S_out, roh_S_out, alpha_S_out, beta_R_in, alpha_R_out, beta_R_out, beta_blade_R_in, beta_blade_R_out, D_R = radial_equilibrium_R(stage+1, approach, constant_r_parameter, D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_m1, D_m2, D_m3, b1, b2, b3, cu1, cu2, cu3, u1, u2, u3, cm1, cm2, cm3, delta_h_t, T_t1, T_t2, T_t3, p_t1, p_t2, p_t3)
    
    #Stator
    r_S_out = []
    for i in range(len(h_rel)): 
        if constant_r_parameter == 0:
            r_S_out.append((D_H3[stage-1]/2+h_rel[i]*b3[stage-1])/1000)

        elif constant_r_parameter == 1:
            r_S_out.append((D_m3[stage-1]/2+(h_rel[i]-0.5)*b3[stage-1])/1000)

        elif constant_r_parameter == 2:
            r_S_out.append((D_S3[stage-1]/2+(h_rel[i]-1)*b3[stage-1])/1000)

        else:
            print("Allowed constant radius parameter: 0, 1 and 2.")

    c_S_out = []
    for i in range(len(h_rel)):
        c_S_out.append(math.sqrt(c_m_S_out[i]**2 + c_u_S_out[i]**2))
    
    
    beta_blade_S_in, beta_blade_S_out = [], []
    for i in range(len(h_rel)):
        beta_blade_S_in.append(angle_blade_in(alpha_S_in[i], alpha_S_out[i], c_S_in[i], u_S_out[i], T_S_in[i], T_S_out[i], l_S_t_S[stage-1],  d_S_l_S[stage-1], incidence_S[stage-1], R, kappa))
        beta_blade_S_out.append(angle_blade_out(alpha_S_in[i], alpha_S_out[i], c_S_in[i], c_S_out[i], T_S_in[i], T_S_out[i], l_S_t_S[stage-1],  d_S_l_S[stage-1], incidence_S[stage-1], R, kappa))
    
    #Stator data
    solidity_S = [l_S_t_S[stage-1]]*len(h_rel)
    l_S, axial_length_S, delta_beta_S, c_S_out_c_S_in, D_S = [], [], [], [], []
    for i in range(len(h_rel)):
        l_S.append(solidity_S[i]*2*Pi*(r_S_in[i]+r_S_out[i])/(2*z_S[stage-1])*1000)
        axial_length_S.append(l_S[i]*math.sin((beta_blade_S_out[i]+beta_blade_S_in[i])/(2*180)*Pi))
        delta_beta_S.append(beta_blade_S_out[i]-beta_blade_S_in[i])
        c_S_out_c_S_in.append(c_S_out[i]/c_S_in[i])
        D_S.append(1-c_S_out_c_S_in[i]+abs(c_u_S_out[i]-c_u_S_in[i])/(2*solidity_S[i]*c_S_in[i]))
    
    return h_rel, l_S, c_m_S_in, c_m_S_out, c_u_S_in, c_u_S_out, c_S_out, T_S_in, T_S_out, p_S_in, p_S_out, alpha_S_in, beta_S_in, alpha_S_out, beta_blade_S_in, beta_blade_S_out, D_S	



    

