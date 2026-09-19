# ------------------------------------------------------------------
# File:    source/core/meanline/initialization.py
# Author:  Jonas Scholz
# Purpose: Input echo and iteration-buffer setup for the meanline solver.
# ------------------------------------------------------------------

# Verbatim move of meanline.py:26-60 (input echo) and :62-147 (iteration
# parameters + preallocation). Only the state-dict prefix was added.


def init_state(thermo_data, meanline_data, diameter_data):
    """Collect all inputs and preallocated iteration lists in one dict."""
    s = {}

    s['n'] = meanline_data["n"]
    s['psi_h'] = meanline_data["psi_h"]
    s['phi_1'] = meanline_data["phi_1"]
    s['phi_2'] = meanline_data["phi_2"]
    s['phi_3'] = meanline_data['phi_3']
    s['z_R'] = meanline_data["z_R"]
    s['l_R'] = meanline_data["l_R"]
    s['d_R_l_R'] = meanline_data["d_R_l_R"]
    s['d_Cl_R'] = meanline_data["d_Cl_R"]
    s['d_TE_R'] = meanline_data["d_TE_R"]
    s['incidence_R'] = meanline_data["incidence_R"]
    s['z_S'] = meanline_data["z_S"]
    s['l_S'] = meanline_data["l_S"]
    s['d_S_l_S'] = meanline_data["d_S_l_S"]
    s['d_TE_S'] = meanline_data["d_TE_S"]
    s['d_CL_S'] = meanline_data["d_CL_S"]
    s['incidence_S'] = meanline_data["incidence_S"]

    s['fixed_radius_type'] = diameter_data["fixed_radius_type"]
    s['D_f1'] = diameter_data["D_f1"]
    s['D_f2'] = diameter_data["D_f2"]
    s['D_f3'] = diameter_data["D_f3"]


    s['mflow'] = thermo_data["mflow"]
    s['p_t_in'] = thermo_data["p_t_in"]
    s['T_t_in'] = thermo_data["T_t_in"]
    s['kappa'] = thermo_data["kappa"]
    s['R'] = thermo_data["R"]
    s['cp'] = thermo_data["cp"]
    s['h_R'] = thermo_data["h_R"]
    s['h_S'] = thermo_data["h_S"]
    s['i_st'] = thermo_data["i_st"]
    s['design_TPR'] = thermo_data["TPR"]

    # Iteration Parameters Outer Iteration loop
    s['iter_count_TPR'] = 0
    s['max_iter_steps_TPR'] = 50
    s['conv_limit_TPR'] = 0.01

    # Preallocate TPR-Iteration Variables
    s['n_history'] = []
    s['TPR_history'] = []
    s['n_history'].append(s['n'][0])


    s['relaxation_factor'] = 0.5 # Smaller values stabilize more but slow down.
                                # Larger values are faster but potentially unstable.


    #region Preallocating Variables

    i_st = s['i_st']
    s['D_S1'] = [0.0] * i_st
    s['D_S2'] = [0.0] * i_st
    s['D_S3'] = [0.0] * i_st
    s['D_M1'] = [0.0] * i_st
    s['D_M2'] = [0.0] * i_st
    s['D_M3'] = [0.0] * i_st
    s['D_H1'] = [0.0] * i_st
    s['D_H2'] = [0.0] * i_st
    s['D_H3'] = [0.0] * i_st

    s['D_m_initial_guess'] = 0.508


    # This will hold the *iterating* mean diameter guess for each 'i'
    s['next_guess1'] = [s['D_m_initial_guess']]*i_st
    s['next_guess2'] = [s['D_m_initial_guess']]*i_st
    s['next_guess3'] = [s['D_m_initial_guess']]*i_st

    s['q'] = [0]*i_st



    s['alpha_1'] = [90]*i_st
    s['alpha_3'] = [90]*i_st

    # --- Pre-allocate lists for calculated flow properties ---
    # These will be populated stage by stage in the main loop
    s['u1'], s['u2'], s['u3'], s['u1_u2'], s['u2_u2']= [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['h_R_l_R'], s['t_R'], s['l_R_t_R'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['t_S'], s['l_S_t_S'], s['h_S_l_S'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['c1_u2'], s['cu1_u2'], s['c3_u2'], s['cu2_u2'], s['c2_u2'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['alpha_2'], s['delta_alpha'] = [0.0]*i_st, [0.0]*i_st
    s['c1'], s['c2'], s['c3'], s['cu3_u2'], s['wu1_u2'], s['wu2_u2'], s['w1_u2'], s['w1'], s['w2_u2'], s['w2'], s['c_m1'], s['c_m2'], s['c_m3'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['cu1'], s['cu2'], s['cu3'], s['cm1'], s['cm2'], s['cm3'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['cu1'], s['cu2'], s['cu3'], s['cm1'], s['cm2'], s['cm3'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['beta_1'], s['beta_2'], s['delta_beta'], s['a'], s['delta_h_t'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st

    # Inlet total temperature for the first stage
    s['T_t1'] = [0.0] * i_st
    s['T_t1'][0] = s['T_t_in']
    s['T_t3'], s['T_t2'], s['T_1'], s['T_2'], s['T_3'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st

    # Inlet total pressure for the first stage
    s['p_t1'] = [0.0] * i_st
    s['p_t1'][0] = s['p_t_in']
    s['p_1'], s['p_2'], s['p_3'], s['p_t3'], s['p_t2'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['roh_1'], s['roh_2'], s['roh_3'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st

    s['Re_l_R'], s['Re_l_S'] = [0.0]*i_st, [0.0]*i_st

    s['beta_blade_1'], s['beta_blade_2'], s['delta_beta_in'], s['delta_beta_out'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['xi_R_pro'], s['xi_R_cl'], s['xi_R_sec'], s['xi_R_inc'], s['xi_R_ma'], s['xi_R_te'], s['xi_R'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['Ma_w1'], s['Ma_w2'], s['Ma_c1'], s['Ma_c2'], s['Ma_c3'], s['Ma_m1'], s['Ma_m2'], s['Ma_m3'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['alpha_blade_2'], s['alpha_blade_3'], s['delta_alpha_in'], s['delta_alpha_out'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['w2_w1'], s['B_R'], s['c_L_R'], s['D_R'] = [0.0]*i_st, [00]*i_st, [0.0]*i_st, [0.0]*i_st
    s['c3_c2'], s['B_S'], s['c_L_S'], s['D_S_diff'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st # Renamed D_S to D_S_diff to avoid conflict with D_S1, D_S2, D_S3
    s['T_2is'] = [0.0]*i_st
    s['xi_S_pro'], s['xi_S_cl'], s['xi_S_sec'], s['xi_S_inc'], s['xi_S_ma'], s['xi_S_te'], s['xi_S'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['eta_s'] = [0.0]*i_st
    s['TPR'], s['roh_h_des'] = [0.0]*i_st, [0.0]*i_st
    s['delta_h'], s['delta_h_R'], s['delta_h_S'], s['delta_h_loss'], s['delta_h_loss_R'], s['delta_h_loss_S'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['eta_sC_tt'], s['eta_pC_tt'] = [0.0]*i_st, [0.0]*i_st

    # Stage geometry related lists (some might be filled later)
    # b1, b2, b3 represent span at various stations - if used in formula they also need to be pre-allocated.
    s['b1'], s['b2'], s['b3'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st
    s['nue_in'], s['delta_D_target_12'], s['delta_D_target_23'] = [0.0]*i_st, [0.0]*i_st, [0.0]*i_st

    #endregion

    return s
