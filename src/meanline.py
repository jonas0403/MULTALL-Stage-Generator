# Author: Jonas Scholz (modified by Luca De Francesco)
# Based on Code by Marco Wiens
# Version: 17.07.2025
# Meanline calculation 1-Dimensional
# Program for meanline calculation and iterating the geometry and contour of the channel 


import math
import os 
import debug_log

wdpath = os.getcwd()
if __name__ == "__main__":
    src_folder = os.path.dirname(os.path.abspath(__file__))
    os.chdir(src_folder)


#from thermodynamic_calculation import Thermo
from plot_channel import plot_channel
from loss_models import xi_ac_pro, xi_ac_te, xi_a_cl, xi_ac_inc, xi_a_sec, xi_ac_ma, diffusion, angle_blade_in, angle_blade_out, Re 

Pi = math.pi


def meanline(thermo_data, meanline_data, diameter_data, plot_channel_contour):
       
    n = meanline_data["n"]
    psi_h = meanline_data["psi_h"]
    phi_1 = meanline_data["phi_1"]
    phi_2 = meanline_data["phi_2"]
    phi_3 = meanline_data['phi_3']
    z_R = meanline_data["z_R"]
    l_R = meanline_data["l_R"]  
    d_R_l_R = meanline_data["d_R_l_R"]
    d_Cl_R = meanline_data["d_Cl_R"]
    d_TE_R = meanline_data["d_TE_R"]
    incidence_R = meanline_data["incidence_R"]
    z_S = meanline_data["z_S"]
    l_S = meanline_data["l_S"]
    d_S_l_S = meanline_data["d_S_l_S"]
    d_TE_S = meanline_data["d_TE_S"]
    d_CL_S = meanline_data["d_CL_S"]
    incidence_S = meanline_data["incidence_S"]
    
    fixed_radius_type = diameter_data["fixed_radius_type"]
    D_f1 = diameter_data["D_f1"]
    D_f2 = diameter_data["D_f2"]
    D_f3 = diameter_data["D_f3"]
    
    
    mflow = thermo_data["mflow"]
    p_t_in = thermo_data["p_t_in"]
    T_t_in = thermo_data["T_t_in"]
    kappa = thermo_data["kappa"]
    R = thermo_data["R"]
    cp = thermo_data["cp"]
    h_R = thermo_data["h_R"]
    h_S = thermo_data["h_S"]
    i_st = thermo_data["i_st"]
    design_TPR = thermo_data["TPR"]

    
    # Iteration Parameters Outer Iteration loop
    iter_count_TPR = 0
    max_iter_steps_TPR = 50
    conv_limit_TPR = 0.01
    
    # Preallocate TPR-Iteration Variables
    n_history = []
    TPR_history = []   
    n_history.append(n[0])
    
    
    relaxation_factor = 0.5 # Kleinere Werte stabilisieren mehr, aber verlangsamen.
                            # Größere Werte sind schneller, aber ggf. instabiler.
                            
            
    #region Preallocating Variables
          
    D_S1 = [0.0] * i_st
    D_S2 = [0.0] * i_st
    D_S3 = [0.0] * i_st
    D_M1 = [0.0] * i_st
    D_M2 = [0.0] * i_st
    D_M3 = [0.0] * i_st
    D_H1 = [0.0] * i_st
    D_H2 = [0.0] * i_st
    D_H3 = [0.0] * i_st
    
    D_m_initial_guess = 0.508


    # This will hold the *iterating* mean diameter guess for each 'i'
    next_guess1 = [D_m_initial_guess]*i_st 
    next_guess2 = [D_m_initial_guess]*i_st
    next_guess3 = [D_m_initial_guess]*i_st
    
    q = [0]*i_st
    
    
    
    alpha_1 = [90]*i_st
    alpha_3 = [90]*i_st

    # --- Pre-allocate lists for calculated flow properties ---
    # These will be populated stage by stage in the main loop
    u1, u2, u3, u1_u2, u2_u2= [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    h_R_l_R, t_R, l_R_t_R = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    t_S, l_S_t_S, h_S_l_S = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    c1_u2, cu1_u2, c3_u2, cu2_u2, c2_u2 = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    alpha_2, delta_alpha = [0.0]*i_st, [0.0]*i_st
    c1, c2, c3, cu3_u2, wu1_u2, wu2_u2, w1_u2, w1, w2_u2, w2, c_m1, c_m2, c_m3 = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    cu1, cu2, cu3, cm1, cm2, cm3 = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    cu1, cu2, cu3, cm1, cm2, cm3 = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    beta_1, beta_2, delta_beta, a, delta_h_t = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    
    # Inlet total temperature for the first stage
    T_t1 = [0.0] * i_st
    T_t1[0] = T_t_in
    T_t3, T_t2, T_1, T_2, T_3 = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    
    # Inlet total pressure for the first stage
    p_t1 = [0.0] * i_st
    p_t1[0] = p_t_in
    p_1, p_2, p_3, p_t3, p_t2 = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    roh_1, roh_2, roh_3 = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st

    Re_l_R, Re_l_S = [0.0]*i_st, [0.0]*i_st
    
    beta_blade_1, beta_blade_2, delta_beta_in, delta_beta_out = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    xi_R_pro, xi_R_cl, xi_R_sec, xi_R_inc, xi_R_ma, xi_R_te, xi_R = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    Ma_w1, Ma_w2, Ma_c1, Ma_c2, Ma_c3, Ma_m1, Ma_m2, Ma_m3 = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    alpha_blade_2, alpha_blade_3, delta_alpha_in, delta_alpha_out = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    w2_w1, B_R, c_L_R, D_R = [0.0]*i_st, [00]*i_st, [0.0]*i_st, [0.0]*i_st
    c3_c2, B_S, c_L_S, D_S_diff = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st # Renamed D_S to D_S_diff to avoid conflict with D_S1, D_S2, D_S3
    T_2is = [0.0]*i_st
    xi_S_pro, xi_S_cl, xi_S_sec, xi_S_inc, xi_S_ma, xi_S_te, xi_S = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    eta_s = [0.0]*i_st
    TPR, roh_h_des = [0.0]*i_st, [0.0]*i_st
    delta_h, delta_h_R, delta_h_S, delta_h_loss, delta_h_loss_R, delta_h_loss_S = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    eta_sC_tt, eta_pC_tt = [0.0]*i_st, [0.0]*i_st
    
    # Stage geometry related lists (some might be filled later)
    # b1, b2, b3 represent span at various stations - if used in formula they also need to be pre-allocated.
    b1, b2, b3 = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    nue_in, delta_D_target_12, delta_D_target_23 = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    
    #endregion

    # --- MAINLOOP ---
    # Iterating over the stages
    while iter_count_TPR < max_iter_steps_TPR:        
        
        # Calculate all Stages
        for i in range(i_st):
            
                
            current_D_M1_guess=next_guess1[i] 
            current_D_M2_guess=next_guess2[i]
            current_D_M3_guess=next_guess3[i]

            iteration_count=0
            max_iteration_steps=1000
            tolerance=0.0005

            stage_msg = f"\n--- Starting calculation for Stage {i+1}/{i_st} ---"
            print(stage_msg)
            debug_log.debug(stage_msg, context="meanline")

            if fixed_radius_type == "hub":
                D_H1[i]=D_f1[i]
                D_H2[i]=D_f2[i]
                D_H3[i]=D_f3[i]

            elif fixed_radius_type == "shroud":
                D_S1[i]=D_f1[i]
                D_S2[i]=D_f2[i]
                D_S3[i]=D_f3[i]
            elif fixed_radius_type == "mean":
                D_M1[i]=D_f1[i]
                D_M2[i]=D_f2[i]
                D_M3[i]=D_f3[i]
            else:
                raise ValueError("Invalid fixed_radius_type specified.")
            
            
            # --- Inner Iteration Loop: Solves for the Channel Diameters ---
            # Runs until all Diameters are calculated or max Iteration count is reached
            while iteration_count < max_iteration_steps:
                # Saves previous Guesses
                old_D_M1_guess=current_D_M1_guess
                old_D_M2_guess=current_D_M2_guess
                old_D_M3_guess=current_D_M3_guess

                # Calculates the Circumferential Speeds (u)
                u1[i]=(2*Pi*n[i])/60*current_D_M1_guess/2
                u2[i]=(2*Pi*n[i])/60*current_D_M2_guess/2
                
                
                
                if i > 0 :
                    u3[i-1]=u2[i] 
                else:
                    u3[i] = 0
                    
                u1_u2[i]=u1[i]/u2[i]
                u2_u2[i]=u2[i]/u2[i]
                #u3_u2[i]=u3[i]/u2[i] # Stators dont move


                #region Calculates the flow Properties 

                #Rotor
                h_R_l_R[i]=h_R[i]/l_R[i]
                t_R[i]=round(Pi*current_D_M2_guess/z_R[i]*1000,2)
                l_R_t_R[i]=l_R[i]/t_R[i] 

                #Stator
                h_S_l_S[i]=h_S[i]/l_S[i]
                t_S[i]=round(Pi*current_D_M2_guess/z_S[i]*1000,2)
                l_S_t_S[i]=l_S[i]/t_S[i] 

                # Non Dimensinal Velocities
                c1_u2[i]=phi_1[i]/math.sin(math.radians(alpha_1[i])) if math.sin(math.radians(alpha_1[i]))!=0 else float('inf')
                cu1_u2[i]=c1_u2[i]*math.cos(math.radians(alpha_1[i]))
                c3_u2[i]=phi_3[i]/math.sin(math.radians(alpha_3[i])) if math.sin(math.radians(alpha_3[i]))!=0 else float('inf')
                cu2_u2[i]=u1_u2[i]*cu1_u2[i]+psi_h[i]/2-q[i]/u2[i]**2+c3_u2[i]**2/2-c1_u2[i]**2/2
                c2_u2[i]=math.sqrt(phi_2[i]**2+cu2_u2[i]**2)

                alpha_2[i]=math.degrees(math.acos(cu2_u2[i]/c2_u2[i]))
                delta_alpha[i]=alpha_2[i]-alpha_3[i]


                # Absolut and Relative Velocities
                c1[i]=c1_u2[i]*u2[i]
                c2[i]=c2_u2[i]*u2[i]
                c3[i]=c3_u2[i]*u2[i]
                cu3_u2[i]=c3_u2[i]*math.cos(math.radians(alpha_3[i]))
                wu1_u2[i]=cu1_u2[i]-u1_u2[i]
                wu2_u2[i]=cu2_u2[i]-u2_u2[i]
                w1_u2[i]=math.sqrt(phi_1[i]**2+wu1_u2[i]**2)
                w1[i]=w1_u2[i]*u2[i]
                w2_u2[i]=math.sqrt(phi_2[i]**2+wu2_u2[i]**2)
                w2[i]=w2_u2[i]*u2[i]

                # Angles and Enthalpy
                # Überprüfe Argumente für math.acos, um Domain-Fehler zu vermeiden (-1 <= x <= 1)
                
                # potential error source:
                '''
                beta_1_arg=wu1_u2[i]/w1_u2[i] if w1_u2[i]!=0 else 0.0
                beta_1_arg=max(-1.0, min(1.0, beta_1_arg)) # Clamping
                beta_1[i]=math.degrees(math.acos(beta_1_arg))
                beta_2_arg=wu2_u2[i]/w2_u2[i] if w2_u2[i]!=0 else 0.0
                beta_2_arg=max(-1.0, min(1.0, beta_2_arg)) # Clamping
                beta_2[i]=math.degrees(math.acos(beta_2_arg))
                '''
                beta_1[i]=math.degrees(math.acos(wu1_u2[i]/w1_u2[i]))
                beta_2[i]=math.degrees(math.acos(wu2_u2[i]/w2_u2[i]))
                delta_beta[i]=beta_2[i]-beta_1[i]

                a[i]=(cu2_u2[i]-u1_u2[i]*cu1_u2[i])*u2[i]**2 
                delta_h_t[i]=a[i]+q[i]

                # Total and Static Temperatures
                if i>0:
                    T_t1[i]=T_t3[i-1]# Rotor Inlet temperature is equal to stator exit Temperatur
                    p_t1[i]=p_t3[i-1]# Rotor Inlet pressure is equal to stator exit Temperatur

                T_t3[i]=T_t1[i]+delta_h_t[i]/cp
                T_t2[i]=T_t3[i]# For stator inlet

                T_1[i]=T_t1[i]-c1[i]**2/(2*cp)
                
                T_2[i]=T_t2[i]-c2[i]**2/(2*cp)

                T_3[i]=T_t3[i]-c3[i]**2/(2*cp)
        

                # Static and Total pressure and Density
                p_1[i]=p_t1[i]*(T_1[i]/T_t1[i])**(kappa/(kappa-1))
                if i > 0:
                    roh_1[i]=roh_3[i-1]
                else:
                    roh_1[i]=p_1[i]/(R*T_1[i])

                # Blade Angles, Reynoldsnumbers, Machnumbers and Losses

                
                debug_log.debug(f"beta_blade_1[i]={beta_blade_1[i]}=angle_blade_in(...)", context="meanline")

                Re_l_R[i]=Re(roh_1[i],w1[i],l_R[i],T_1[i])
                beta_blade_1[i]=angle_blade_in(beta_1[i], beta_2[i], w1[i], w2[i], T_1[i], T_2[i], l_R_t_R[i], d_R_l_R[i], incidence_R[i], R, kappa)
                beta_blade_2[i]=angle_blade_out(beta_1[i], beta_2[i], w1[i], w2[i], T_1[i], T_2[i], l_R_t_R[i], d_R_l_R[i], incidence_R[i], R, kappa)
                delta_beta_in[i]=beta_blade_1[i]-beta_1[i]
                delta_beta_out[i]=beta_2[i]-beta_blade_2[i]

                # Rotor Losses

                xi_R_pro[i]=xi_ac_pro(beta_1[i],beta_2[i], l_R_t_R[i])
                xi_R_cl[i]=xi_a_cl(beta_1[i], beta_2[i], l_R_t_R[i], d_Cl_R[i], h_R[i])
                xi_R_sec[i]=xi_a_sec(beta_1[i], beta_2[i], l_R_t_R[i], t_R[i], h_R[i])
                xi_R_inc[i]=xi_ac_inc(beta_1[i], beta_2[i],incidence_R[i])
                xi_R_ma[i]=xi_ac_ma(w1[i], T_1[i])
                xi_R_te[i]=xi_ac_te(beta_1[i], beta_2[i], l_R_t_R[i], t_R[i], d_TE_R[i], Re_l_R[i])
                xi_R[i]=xi_R_pro[i] + xi_R_te[i] + xi_R_cl[i] + xi_R_sec[i] + xi_R_inc[i] + xi_R_ma[i]

                # Machnumbers

                Ma_w1[i]=w1[i]/math.sqrt(kappa*R*T_1[i])
                Ma_w2[i]=w2[i]/math.sqrt(kappa*R*T_2[i])
                Ma_c1[i]=c1[i]/math.sqrt(kappa*R*T_1[i])
                Ma_c2[i]=c2[i]/math.sqrt(kappa*R*T_2[i])
                Ma_c3[i]=c3[i]/math.sqrt(kappa*R*T_3[i])
                Ma_m1[i]=phi_1[i]*u2[i]/math.sqrt(kappa*R*T_1[i])
                Ma_m2[i]=phi_2[i]*u2[i]/math.sqrt(kappa*R*T_2[i])
                Ma_m3[i]=phi_3[i]*u2[i]/math.sqrt(kappa*R*T_3[i])


                alpha_blade_2[i]=angle_blade_in(alpha_2[i], alpha_3[i], c2[i], c3[i], T_2[i], T_3[i], l_S_t_S[i], d_S_l_S[i], incidence_S[i], R, kappa)
                alpha_blade_3[i]=angle_blade_out(alpha_2[i], alpha_3[i], c2[i], c3[i], T_2[i], T_3[i], l_S_t_S[i], d_S_l_S[i], incidence_S[i], R, kappa)
                delta_alpha_in[i]=alpha_2[i]-alpha_blade_2[i]
                delta_alpha_out[i]=alpha_blade_3[i]-alpha_3[i]
                

                # Rotor design Parameters

                w2_w1[i]=w2_u2[i]/w1_u2[i]
                B_R[i]=2*abs(wu2_u2[i]-wu1_u2[i])/((w2_u2[i]+w1_u2[i])/2)
                c_L_R[i]=B_R[i]/l_R_t_R[i]
                D_R[i]=diffusion(beta_1[i], beta_2[i], w1[i], w2[i], l_R_t_R[i])


                # Stator deign parameters

                c3_c2[i]=c3_u2[i]/c2_u2[i]
                B_S[i]=2*abs(cu3_u2[i] - cu2_u2[i])/((c3_u2[i] + c2_u2[i])/2)
                c_L_S[i]=B_S[i]/l_S_t_S[i]
                D_S_diff[i]=diffusion(alpha_2[i], alpha_3[i], c2[i], c3[i], l_R_t_R[i]) # ????? diffusion has to be calculated with l_S_t_S
                


                # Pressures, Densities and losses continued

                T_2is[i]=T_2[i]-xi_R[i]*w1[i]**2/(2*cp)
                p_2[i]=p_1[i]*(T_2is[i]/T_1[i])**(kappa/(kappa-1))
                roh_2[i]=p_2[i]/(T_2[i]*R)

                Re_l_S[i]=Re(roh_2[i], c2[i], l_S[i], T_2[i])

                xi_S_pro[i]=xi_ac_pro(alpha_2[i],alpha_3[i], l_S_t_S[i])
                xi_S_cl[i]=xi_a_cl(alpha_2[i], alpha_3[i], l_S_t_S[i], d_CL_S[i], h_S[i])
                xi_S_sec[i]=xi_a_sec(alpha_2[i], alpha_3[i], l_S_t_S[i], t_S[i], h_S[i])
                xi_S_inc[i]=xi_ac_inc(alpha_2[i], alpha_3[i] ,incidence_S[i])
                xi_S_ma[i]=xi_ac_ma(c2[i], T_2[i])
                xi_S_te[i]=xi_ac_te(alpha_2[i], alpha_3[i], l_S_t_S[i], t_S[i], d_TE_S[i], Re_l_S[i])
                xi_S[i]=xi_S_pro[i] + xi_S_te[i] + xi_S_cl[i] + xi_S_sec[i] + xi_S_inc[i] + xi_S_ma[i]

                eta_s[i]=(psi_h[i]-xi_R[i]*w1_u2[i]**2-xi_S[i]*c2_u2[i]**2)/psi_h[i]
                p_t3[i]=p_t1[i]*(eta_s[i]*(T_t3[i]/T_t1[i]-1)+1)**(kappa/(kappa-1))
                p_3[i]=p_t3[i]*(T_3[i]/T_t3[i])**(kappa/(kappa-1))
                roh_3[i]=p_3[i]/(T_3[i]*R)

                TPR[i]=p_t3[i]/p_t1[i]
                p_t2[i]=p_2[i]*(T_t2[i]/T_2[i])**(kappa/(kappa-1))
                roh_h_des[i]=(2*(cu2_u2[i]-u1_u2[i]*cu1_u2[i])-(cu2_u2[i]**2-cu1_u2[i]**2))/(2*(cu2_u2[i]-u1_u2[i]*cu1_u2[i])-(c3_u2[i]**2-c1_u2[i]**2))

                delta_h[i]=psi_h[i]*u2[i]**2/2
                delta_h_R[i]=delta_h[i]*roh_h_des[i]
                delta_h_S[i]=delta_h[i]-delta_h_R[i] 
                delta_h_loss_R[i]=xi_R[i]*w1[i]**2/2
                delta_h_loss_S[i]=xi_S[i]*c2[i]**2/2
                delta_h_loss[i]=delta_h_loss_R[i]+delta_h_loss_S[i]

                eta_sC_tt[i]=eta_s[i]
                eta_pC_tt[i]=R*math.log(TPR[i],math.e)/(cp*math.log(T_t3[i]/T_t1[i],math.e))

                # endregion
                
                # Calculating C_m for the Diameter Calculation to Gurantee Continuity        
                if i > 0:
                    c_m1[i] = c_m3[i-1]
                else:
                    c_m1[i] = phi_1[i]*u2[i]
                    
                c_m2[i] = phi_2[i]*u2[i]
                c_m3[i] = phi_3[i]*u2[i]

                # Calculates the new Diameter based on massflow
                if fixed_radius_type == "hub":
                    # D_H1[i] is fixed
                    under_sqrt1=D_H1[i]**2+(4*mflow)/(Pi*roh_1[i]*c_m1[i])
                    under_sqrt2=D_H2[i]**2+(4*mflow)/(Pi*roh_2[i]*c_m2[i])
                    under_sqrt3=D_H3[i]**2+(4*mflow)/(Pi*roh_3[i]*c_m3[i])
                    
                    # print(f"Stage:{i+1}    under_sqrt1({under_sqrt1})=D_H3[i]({D_H1[i]})**2+(4*mflow({mflow}))/(Pi*roh_3[i]({roh_1[i]})*c_m3[i]({c_m1[i]}))")
                    # print(f"Stage:{i+1}    under_sqrt3({under_sqrt3})=D_H3[i]({D_H3[i]})**2+(4*mflow({mflow}))/(Pi*roh_3[i]({roh_3[i]})*c_m3[i]({c_m3[i]}))")

                    if under_sqrt1 < 0:
                        warn_msg = f"Warning: Term under sqrt for D_S1 at stage {i} is negative. Setting D_S1[i] = D_H1[i]."
                        print(warn_msg)
                        debug_log.debug(warn_msg, context="meanline")
                        D_S1[i]=D_H1[i]
                    else:
                        D_S1[i]=math.sqrt(under_sqrt1)
                    new_D_M1_guess=(D_H1[i]+D_S1[i])/2

                    if under_sqrt2 < 0:
                        warn_msg = f"Warning: Term under sqrt for D_S2 at stage {i} is negative. Setting D_S2[i] = D_H2[i]."
                        print(warn_msg)
                        debug_log.debug(warn_msg, context="meanline")
                        D_S2[i]=D_H2[i]
                    else:
                        D_S2[i]=math.sqrt(under_sqrt2)
                    new_D_M2_guess=(D_H2[i]+D_S2[i])/2

                    if under_sqrt3 < 0:
                        warn_msg = f"Warning: Term under sqrt for D_S3 at stage {i} is negative. Setting D_S3[i] = D_H3[i]."
                        print(warn_msg)
                        debug_log.debug(warn_msg, context="meanline")
                        D_S3[i]=D_H3[i]
                    else:
                        D_S3[i]=math.sqrt(under_sqrt3)
                    new_D_M3_guess=(D_H3[i]+D_S3[i])/2

                    # Update next_guess with the current converged Values
                    D_M1[i]=new_D_M1_guess
                    D_M2[i]=new_D_M2_guess
                    D_M3[i]=new_D_M3_guess

                if fixed_radius_type == "shroud":
                    # D_S1[i] is fixed 
                    
                    #val_to_subtract1 = (4 * mflow) / (Pi * roh_1[i] * phi_1[i] * u1[i])
                    #print(f"DEBUG: Stage {i+1} - D_S1[i]^2: {D_S1[i]**2:.6f}")
                    #print(f"DEBUG: Stage {i+1} - 4*mflow/(Pi*roh_1*phi*u1): {val_to_subtract1:.6f}")
                    #under_sqrt1 = D_S1[i]**2 - val_to_subtract1
                    #print(f"DEBUG: Stage {i+1} - under_sqrt1: {under_sqrt1:.6f}")
                    
                    #print(f"roh={roh_3[i]}")
                    #print(f"phi={phi_3[i]}")
                    #print(f"u2={u2}")
                    #print(f"u={u3}")
                    under_sqrt1=D_S1[i]**2-(4*mflow)/(Pi*roh_1[i]*c_m1[i])
                    under_sqrt2=D_S2[i]**2-(4*mflow)/(Pi*roh_2[i]*c_m2[i])
                    under_sqrt3=D_S3[i]**2-(4*mflow)/(Pi*roh_3[i]*c_m3[i])
                    
                    if under_sqrt1 < 0:
                        warn_msg = f"Warning: Term under sqrt for D_H1 at stage {i} is negative. Setting D_H1[i] = D_S1[i]."
                        print(warn_msg)
                        debug_log.debug(warn_msg, context="meanline")
                        D_H1[i]=D_S1[i]
                    else:
                        D_H1[i]=math.sqrt(under_sqrt1)
                    new_D_M1_guess=(D_H1[i]+D_S1[i])/2

                    if under_sqrt2 < 0:
                        warn_msg = f"Warning: Term under sqrt for D_H2 at stage {i} is negative. Setting D_H2[i] = D_S2[i]."
                        print(warn_msg)
                        debug_log.debug(warn_msg, context="meanline")
                        D_H2[i]=D_S2[i]
                    else:
                        D_H2[i]=math.sqrt(under_sqrt2)
                    new_D_M2_guess=(D_H2[i]+D_S2[i])/2

                    if under_sqrt3 < 0:
                        warn_msg = f"Warning: Term under sqrt for D_H3 at stage {i} is negative. Setting D_H3[i] = D_S3[i]."
                        print(warn_msg)
                        debug_log.debug(warn_msg, context="meanline")
                        D_H3[i]=D_S3[i]
                    else:
                        D_H3[i]=math.sqrt(under_sqrt3)
                    new_D_M3_guess=(D_H3[i]+D_S3[i])/2
                    
                    # Update next_guess with the current converged Values
                    D_M1[i]=new_D_M1_guess
                    D_M2[i]=new_D_M2_guess
                    D_M3[i]=new_D_M3_guess
                    
                if fixed_radius_type == "mean":
                    # D_M1[i] is fixed
                    # Calculate Channel height
                    b1[i]=mflow/(roh_1[i]*phi_1[i]*u2[i]*Pi*D_M1[i])
                    b2[i]=mflow/(roh_2[i]*phi_2[i]*u2[i]*Pi*D_M2[i])
                    b3[i]=mflow/(roh_3[i]*phi_3[i]*u2[i]*Pi*D_M3[i])
                    
                    # Calculate Shroud Diameter 
                    D_S1[i]=D_M1[i]+b1[i]
                    D_S2[i]=D_M2[i]+b2[i]
                    D_S3[i]=D_M3[i]+b3[i]
                    
                    # Calculate Hub Diameter
                    D_H1[i]=D_M1[i]-b1[i]
                    D_H2[i]=D_M2[i]-b2[i]
                    D_H3[i]=D_M3[i]-b3[i]
                    
                    # Overwrite D_M guesses to check for convergence
                    new_D_M1_guess=D_M1[i]
                    new_D_M2_guess=D_M2[i]
                    new_D_M3_guess=D_M3[i]
                    
                    # Set converged to True because fixed mean line does not need to be iteratated
                    converged = True
                    
                    
                    
                # Appling relaxation factor
                # Used for the stability of an non-linear system
                # Only use when not in meanline fixed design

                if fixed_radius_type != "mean":
                    current_D_M1_guess=old_D_M1_guess*(1-relaxation_factor)+new_D_M1_guess*relaxation_factor
                    current_D_M2_guess=old_D_M2_guess*(1-relaxation_factor)+new_D_M2_guess*relaxation_factor
                    current_D_M3_guess=old_D_M3_guess*(1-relaxation_factor)+new_D_M3_guess*relaxation_factor
                else:
                    # Wenn fixed_radius_type "mean" ist, übernehmen wir die fixierten Werte
                    current_D_M1_guess=D_M1[i]
                    current_D_M2_guess=D_M2[i]
                    current_D_M3_guess=D_M3[i]


                # Update the mealine diameters

                D_M1[i]=current_D_M1_guess
                D_M2[i]=current_D_M2_guess
                D_M3[i]=current_D_M3_guess


                if fixed_radius_type == "hub":
                    # D_H ist fest, D_S muss sich anpassen
                    D_S1[i]=2*D_M1[i]-D_H1[i]
                    D_S2[i]=2*D_M2[i]-D_H2[i]
                    D_S3[i]=2*D_M3[i]-D_H3[i]
                elif fixed_radius_type == "shroud":
                    # D_S ist fest, D_H muss sich anpassen
                    D_H1[i]=2*D_M1[i]-D_S1[i]
                    D_H2[i]=2*D_M2[i]-D_S2[i]
                    D_H3[i]=2*D_M3[i]-D_S3[i]
                    
                    
                # Update the Rotor and Stator Height
                h_S[i]=((D_S2[i]-D_H2[i])+(D_S3[i]-D_H3[i]))/4*1000
                h_R[i]=((D_S1[i]-D_H1[i])+(D_S2[i]-D_H2[i]))/4*1000

                # Check for Convergence
                converged=(abs(new_D_M1_guess-old_D_M1_guess)<tolerance and abs(new_D_M2_guess-old_D_M2_guess)<tolerance and abs(new_D_M3_guess-old_D_M3_guess)<tolerance)
                #print(f"\n in Iteration {iteration_count} the convergend is {new_D_M1_guess} {old_D_M1_guess} ")

                # Debug-Prints useful for debugging
                if iteration_count % 10 == 0 or converged: # Every 10 iterations or at convergence
                    debug_log.debug(f"Stage {i+1}, Iteration {iteration_count+1}: D_M1={current_D_M1_guess:.4f}, D_M2={current_D_M2_guess:.4f}, D_M3={current_D_M3_guess:.4f}", context="meanline")
                    debug_log.debug(f"Changes: dD_M1={abs(current_D_M1_guess - old_D_M1_guess):.6f}, dD_M2={abs(current_D_M2_guess - old_D_M2_guess):.6f}, dD_M3={abs(current_D_M3_guess - old_D_M3_guess):.6f} (Tol: {tolerance})", context="meanline")
                    debug_log.debug(f"Diameters: D_S1={D_S1[i]:.4f} D_M1={D_M1[i]:.4f} D_H1={D_H1[i]:.4f}  D_S2={D_S2[i]:.4f} D_M2={D_M2[i]:.4f} D_H2={D_H2[i]:.4f}  D_S3={D_S3[i]:.4f} D_M3={D_M3[i]:.4f} D_H3={D_H3[i]:.4f}", context="meanline")
                    debug_log.debug(f"T_t1={T_t1[i]:.2f}K p_t1={p_t1[i]:.2f}Pa roh_1={roh_1[i]:.4f}  Ma_w1={Ma_w1[i]:.3f} Ma_c1={Ma_c1[i]:.3f}  eta_s={eta_s[i]:.3f} TPR={TPR[i]:.3f}", context="meanline")


                if converged:
                    conv_msg = f"Stage {i+1}: Converged in {iteration_count+1} iterations."
                    print(conv_msg)
                    debug_log.debug(conv_msg, context="meanline")
                    if fixed_radius_type == "hub" and i < i_st:
                        current_D_M1_guess = current_D_M3_guess
                    elif fixed_radius_type == "shroud" and i < i_st:
                        current_D_M1_guess = current_D_M3_guess
                    #elif fixed_radius_type == "mean" and i < i_st:
                    #    current_D_M1_guess = current_D_M3_guess
                    break # Exit the iteration loop for this stage
            

                # Update Iteration Count
                iteration_count += 1
                #print(f"TPR={TPR}")
                
                

            else: # This 'else' block executes if the while loop completes WITHOUT a 'break'
                nonconv_msg = f"Warning: Diameters for stage {i} did not converge after {max_iteration_steps} iterations."
                print(nonconv_msg)
                debug_log.debug(nonconv_msg, context="meanline")
                # The last calculated values are stored in D_M1[i], D_S1[i] etc.


            # Gurantee the Contunity of the diameters between stages
            
            # if i > 0:
            #     if fixed_radius_type == 'hub':
            #         D_S3[i-1]=D_S1[i]
            #     elif fixed_radius_type == 'shroud':
            #         D_H3[i-1]=D_H1[i] 
                
            
            #  Important: The initial Guess for the next sate (i+1) have to be the converged D_M of the current stage (i)
            
            if i < i_st - 1: # Only do this if it is not the last stage 
                next_guess1[i+1] = D_M1[i] 
                next_guess2[i+1] = D_M2[i]
                next_guess3[i+1] = D_M3[i]

        # Overall Mashine Performance
        TPR_M=p_t3[i_st-1]/p_t1[0]# TPR over all stages
        TPR_history.append(TPR_M)
        debug_log.debug(f"TPR_M={TPR_history}", context="meanline_TPR")
        debug_log.debug(f"iter count = {iter_count_TPR}", context="meanline_TPR")
        debug_log.debug(f"length TPR_history 1 = {len(TPR_history)}", context="meanline_TPR")

        
        # Initialize both secant values
        if len(n_history) == 1: 
            # Adjust RPM to change TPR to match designed TPR
            if TPR_M < design_TPR:
                # reduce RPM
                
                if iter_count_TPR == 0:
                    n_history.append(n_history[0]*1.05)
                
            elif TPR_M > design_TPR:
                # increase RPM
                
                if iter_count_TPR == 0:
                    n_history.append(n_history[0]*0.95)
        
          
        # Secant Method to Calculate the next RPM 
        if len(TPR_history) >= 2:
            # Set current and old TPR Value for the Calculation
            curr_TPR = TPR_history[-1]
            old_TPR = TPR_history[-2]
            
            # Set current and old n Value for the Calculation
            curr_n = n_history[-1]
            old_n = n_history[-2]
            
            # Secante Calculation
            if abs(curr_TPR - old_TPR) > 1e-6: # Prevent Division by Zero
                next_n = curr_n - (curr_TPR - design_TPR) * (curr_n - old_n) / ((curr_TPR-design_TPR) - (old_TPR-design_TPR))
            else:
                # Fallback strategy in case of no or very small TPR changes but not near the Design TPR
                tpr_warn = "Warning: No significant TPR changes. Applying a small linear adjustment."
                print(tpr_warn)
                debug_log.debug(tpr_warn, context="meanline_TPR")
                if curr_TPR < design_TPR:
                    next_n = curr_n * 1.02
                else:
                    next_n = curr_n * 0.98
        
        else:
            # First iteration not enough values to calculate using the secant methode
            # Using second RPM value instead
            next_n = n_history[iter_count_TPR + 1]
        
        # Set the old mean Diameter as the next guess for the inner loop for faster iterations
        # next_guess1 = D_M1
        # next_guess2 = D_M2
        # next_guess3 = D_M3
                    
        # Update the List for the next Iteration
        n_history.append(next_n)
            
        # Set global RPM to current guess
            
        n = [next_n] * i_st
            
        # Increase Iteration Count
        iter_count_TPR +=1
            
            
            
            
            

        if abs(TPR_M - design_TPR) < conv_limit_TPR:
            tpr_done = f"\nTotal Pressure Ratio has converged after {iter_count_TPR} iterations. TPR = {TPR_M:.3f} at RPM = {n[0]:.0f}, massflow = {mflow}"
            print(tpr_done)
            debug_log.debug(tpr_done, context="meanline_TPR")
            n = [curr_n] * i_st
            break
    else: # This 'else' block executes if the while loop completes WITHOUT a 'break'
        tpr_fail = f"Warning: Total Pressure Ratio did not converge after {max_iter_steps_TPR} iterations."
        print(tpr_fail)
        debug_log.debug(tpr_fail, context="meanline_TPR")


    



    # BUGFIX
    # print(f"Stg:{i} D_S3={D_S3[i]} D_M3={D_M3[i]} D_H3={D_H3[i]} ")
    # if i < i_st:
    #     print(f"Stg:{i+1} D_S1={D_S1[i]} D_M1={D_M1[i]} D_H1={D_H1[i]} ")

    # --- Calculation after all Diameters converged ---
    
    
    # Convert all Diameters to mm
    
    D_H1_mm=[val*1000 for val in D_H1]
    D_H2_mm=[val*1000 for val in D_H2]
    D_H3_mm=[val*1000 for val in D_H3]
    D_M1_mm=[val*1000 for val in D_M1]
    D_M2_mm=[val*1000 for val in D_M2]
    D_M3_mm=[val*1000 for val in D_M3]
    D_S1_mm=[val*1000 for val in D_S1]
    D_S2_mm=[val*1000 for val in D_S2]
    D_S3_mm=[val*1000 for val in D_S3]
    

    
   
    # Check for T_t3[i_st-1] - T_t_in > 0 to avoid division by zero
    if (T_t3[i_st-1] - T_t_in) != 0:
        eta_sC_tt_M=(TPR_M**((kappa-1)/kappa)-1)/((T_t3[i_st-1]/T_t_in)-1)
        eta_pC_tt_M=R*math.log(TPR_M, math.e)/(cp*math.log((T_t3[i_st-1]/T_t_in), math.e))
    else:
        eta_sC_tt_M=0.0 # Or handle as an error
        eta_pC_tt_M=0.0 # Or handle as an error


    eta_sC_tt, eta_pC_tt = [], []
    for i in range(i_st):
        eta_sC_tt.append(eta_s[i])
        eta_pC_tt.append(R*math.log(TPR[i], math.e)/(cp*math.log((T_t3[i]/T_t1[i]), math.e)))

    #Stage geometry
    # Calculating Span (b) based on channel geometry

    for i in range(i_st):
        # Only calculate Channel hight if meanline is not fixed because it was calculated earlier
        if fixed_radius_type != "mean":
            # Using the actual D_M values from calculation 
            b1[i]=mflow/(roh_1[i]*phi_1[i]*u2[i]*Pi*D_M1[i])*1000
            b2[i]=mflow/(roh_2[i]*phi_2[i]*u2[i]*Pi*D_M2[i])*1000
            b3[i]=mflow/(roh_3[i]*phi_3[i]*u2[i]*Pi*D_M3[i])*1000
    
    for i in range(i_st):
        nue_in.append(D_H1[i]/D_S1[i])
        delta_D_target_12.append(D_S1[i]-D_S2[i])
        delta_D_target_23.append(D_S2[i]-D_S3[i])
        
        
        # Specific Values for the radial Equlibrium
        cu1[i]=cu1_u2[i]*u2[i]
        cu2[i]=cu2_u2[i]*u2[i]
        cu3[i]=cu3_u2[i]*u2[i]
        cm1[i]=phi_1[i]*u2[i]
        cm2[i]=phi_2[i]*u2[i]
        cm3[i]=phi_3[i]*u2[i]
        
    
    # Add last T_t3 value onto the T_t1 
    T_t1.append(T_t3[i_st-1])
    
    
    
    # Convert Span to mm 
    b1=[val*1000 for val in b1]
    b2=[val*1000 for val in b2]
    b3=[val*1000 for val in b3]
        
        
    if plot_channel_contour == True:
        debug_log.debug("plot incoming", context="meanline")
        plot_channel(D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_M1, D_M2, D_M3, i_st, l_R, l_S, beta_blade_1, beta_blade_2, alpha_blade_2, alpha_blade_3)
        
    
    for i in range(i_st):
        debug_log.debug(f"Stg:{i} D_S3={D_S3[i]} D_M3={D_M3[i]} D_H3={D_H3[i]}", context="meanline")
        if i < i_st:
            debug_log.debug(f"Stg:{i+1} D_S1={D_S1[i]} D_M1={D_M1[i]} D_H1={D_H1[i]}", context="meanline")


    result = {
        # Process- & Fluidparameter
        'mflow': mflow,
        'n': n,
        'kappa': kappa,
        'R': R,
        'cp': cp,
        'i_st': i_st,
        
        # Temperatures (Static & Total)
        'T_t1': T_t1,
        'T_t2': T_t2,
        'T_t3': T_t3,
        'T_1': T_1,
        'T_2': T_2,
        'T_3': T_3,
        
        # Pressures (Static & Total)
        'p_1': p_1,
        'p_2': p_2,
        'p_3': p_3,
        'p_t1': p_t1,
        'p_t2': p_t2,
        'p_t3': p_t3,
        
        # Gemoetrydiameters in Milimeters(Shroud, Hub, Mean)
        'D_S1_mm': D_S1_mm, 'D_S2_mm': D_S2_mm, 'D_S3_mm': D_S3_mm,
        'D_H1_mm': D_H1_mm, 'D_H2_mm': D_H2_mm, 'D_H3_mm': D_H3_mm,
        'D_M1_mm': D_M1_mm, 'D_M2_mm': D_M2_mm, 'D_M3_mm': D_M3_mm,
        
        # Gemoetrydiameters in Meters(Shroud, Hub, Mean)
        'D_S1': D_S1, 'D_S2': D_S2, 'D_S3': D_S3,
        'D_H1': D_H1, 'D_H2': D_H2, 'D_H3': D_H3,
        'D_M1': D_M1, 'D_M2': D_M2, 'D_M3': D_M3,
        
        # Velocity triangles & widths
        'b1': b1, 'b2': b2, 'b3': b3,
        'cu1': cu1, 'cu2': cu2, 'cu3': cu3,
        'u1': u1, 'u2': u2, 'u3': u3,
        'cm1': cm1, 'cm2': cm2, 'cm3': cm3,
        
        # Energetics- & Bladeparameters
        'delta_h_t': delta_h_t,
        'l_R': l_R,
        'l_S': l_S,
        'l_R_t_R': l_R_t_R,
        'l_S_t_S': l_S_t_S,
        'd_R_l_R': d_R_l_R,
        'd_S_l_S': d_S_l_S,
        'incidence_R': incidence_R,
        'incidence_S': incidence_S,
        'z_R': z_R,
        'z_S': z_S,
        
        # Angles & Efficienties
        'beta_blade_1': beta_blade_1,
        'beta_blade_2': beta_blade_2,
        'alpha_blade_2': alpha_blade_2,
        'alpha_blade_3': alpha_blade_3,
        'TPR_M': TPR_M,
        'eta_sC_tt_M': eta_sC_tt_M,
        'eta_pC_tt_M': eta_pC_tt_M,
        
        # Configurations
        'fixed_radius_type': fixed_radius_type,
        'plot_channel_contour': plot_channel_contour
    
    }
 
    return result
           
           
