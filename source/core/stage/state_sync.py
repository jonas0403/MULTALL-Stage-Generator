# ------------------------------------------------------------------
# File:    source/core/stage/state_sync.py
# Author:  Jonas Scholz
# Purpose: Mirror meanline results into stage module state (with cleanup).
# ------------------------------------------------------------------

# Verbatim move of the run_main_logic unpack block (stage_calculation.py
# :590-733): meanline-dict echo into module state plus the standardization
# block. Bare-name globals became base. attributes (same single home, so all
# Stage.* readers keep working); dead comment blocks were kept per user
# decision. No logic edits.

import source.core.stage.stage_calculation as base


def sync_meanline_state(meanline):
    """Copy the meanline result dict into module state and standardize lists."""
    '''
    writing the Meanline-data out of the compact Dict into the already in use variable names

    '''

    # Process- & Fluidparameter
    base.mflow = meanline['mflow']
    base.n = meanline['n']
    base.kappa = meanline['kappa']
    base.R = meanline['R']
    base.cp = meanline['cp']
    base.i_st = meanline['i_st']

    # Temperatures (Static & Total)
    base.T_t1 = meanline['T_t1']
    base.T_t2 = meanline['T_t2']
    base.T_t3 = meanline['T_t3']
    base.T_1 = meanline['T_1']
    base.T_2 = meanline['T_2']
    base.T_3 = meanline['T_3']

    # Pressures (Static & Total)
    base.p_1 = meanline['p_1']
    base.p_2 = meanline['p_2']
    base.p_3 = meanline['p_3']
    base.p_t1 = meanline['p_t1']
    base.p_t2 = meanline['p_t2']
    base.p_t3 = meanline['p_t3']

    # Gemoetrydiameters in Meters(Shroud, Hub, Mean)
    base.D_S1 = meanline['D_S1']
    base.D_S2 = meanline['D_S2']
    base.D_S3 = meanline['D_S3']
    base.D_H1 = meanline['D_H1']
    base.D_H2 = meanline['D_H2']
    base.D_H3 = meanline['D_H3']
    base.D_m1 = meanline['D_M1'] # Values are in meters nomenclature is wrong here
    base.D_m2 = meanline['D_M2'] # Values are in meters nomenclature is wrong here
    base.D_m3 = meanline['D_M3'] # Values are in meters nomenclature is wrong here

    # Velocity triangles & widths
    base.b1 = meanline['b1']
    base.b2 = meanline['b2']
    base.b3 = meanline['b3']
    base.cu1 = meanline['cu1']
    base.cu2 = meanline['cu2']
    base.cu3 = meanline['cu3']
    base.u1 = meanline['u1']
    base.u2 = meanline['u2']
    base.u3 = meanline['u3']
    base.cm1 = meanline['cm1']
    base.cm2 = meanline['cm2']
    base.cm3 = meanline['cm3']

    # Energetics- & Bladeparameters
    base.delta_h_t = meanline['delta_h_t']
    base.l_R = meanline['l_R']
    base.l_S = meanline['l_S']
    base.l_R_t_R = meanline['l_R_t_R']
    base.l_S_t_S = meanline['l_S_t_S']
    base.d_R_l_R = meanline['d_R_l_R']
    base.d_S_l_S = meanline['d_S_l_S']
    base.incidence_R = meanline['incidence_R']
    base.incidence_S = meanline['incidence_S']
    base.z_R = meanline['z_R']
    base.z_S = meanline['z_S']

    # Angles & Efficienties
    base.beta_blade_1 = meanline['beta_blade_1']
    base.beta_blade_2 = meanline['beta_blade_2']
    base.alpha_blade_2 = meanline['alpha_blade_2']
    base.alpha_blade_3 = meanline['alpha_blade_3']
    base.TPR_M = meanline['TPR_M']
    base.eta_sC_tt_M = meanline['eta_sC_tt_M']
    base.eta_pC_tt_M = meanline['eta_pC_tt_M']

    # Configurations
    base.fixed_radius_type = meanline['fixed_radius_type']
    base.plot_channel_contour = meanline['plot_channel_contour']


    ##### Hugh error dimension of all variables to short because they are defined as one stage and for one stage only

    to_check = [
        'D_S1', 'D_S2', 'D_S3', 'D_H1', 'D_H2', 'D_H3', 'D_m1', 'D_m2', 'D_m3',
        'b1', 'b2', 'b3', 'cu1', 'cu2', 'cu3', 'u1', 'u2', 'u3', 'cm1', 'cm2', 'cm3',
        'delta_h_t', 'T_t1', 'T_t2', 'T_t3', 'p_t1', 'p_t2', 'p_t3'
    ]
    """
    for var_name in to_check:
        # Get the value from the local variables
        val = locals()[var_name]
        # If it's a single number, turn it into a list
        if isinstance(val, (int, float)):
            locals()[var_name] = [val]
    """
    '''
    Defining the values calculated by the radial equilibrium function

    '''
    ### New logic for radial equilibrium because it needs to calculated all stages ###

    # --- STANDARDIZATION BLOCK ---
    # Explicitly check and wrap variables in lists if they are single floats.
    # This ensures the [s-1] indexing in the loop below never fails.

    # 1. Geometry
    base.D_S1 = [base.D_S1] if isinstance(base.D_S1, (int, float)) else base.D_S1
    base.D_S2 = [base.D_S2] if isinstance(base.D_S2, (int, float)) else base.D_S2
    base.D_S3 = [base.D_S3] if isinstance(base.D_S3, (int, float)) else base.D_S3
    base.D_H1 = [base.D_H1] if isinstance(base.D_H1, (int, float)) else base.D_H1
    base.D_H2 = [base.D_H2] if isinstance(base.D_H2, (int, float)) else base.D_H2
    base.D_H3 = [base.D_H3] if isinstance(base.D_H3, (int, float)) else base.D_H3
    base.D_m1 = [base.D_m1] if isinstance(base.D_m1, (int, float)) else base.D_m1
    base.D_m2 = [base.D_m2] if isinstance(base.D_m2, (int, float)) else base.D_m2
    base.D_m3 = [base.D_m3] if isinstance(base.D_m3, (int, float)) else base.D_m3
    base.b1 = [base.b1] if isinstance(base.b1, (int, float)) else base.b1
    base.b2 = [base.b2] if isinstance(base.b2, (int, float)) else base.b2
    base.b3 = [base.b3] if isinstance(base.b3, (int, float)) else base.b3

    # 2. Velocities
    base.cu1 = [base.cu1] if isinstance(base.cu1, (int, float)) else base.cu1
    base.cu2 = [base.cu2] if isinstance(base.cu2, (int, float)) else base.cu2
    base.cu3 = [base.cu3] if isinstance(base.cu3, (int, float)) else base.cu3
    base.u1  = [base.u1]  if isinstance(base.u1,  (int, float)) else base.u1
    base.u2  = [base.u2]  if isinstance(base.u2,  (int, float)) else base.u2
    base.u3  = [base.u3]  if isinstance(base.u3,  (int, float)) else base.u3
    base.cm1 = [base.cm1] if isinstance(base.cm1, (int, float)) else base.cm1
    base.cm2 = [base.cm2] if isinstance(base.cm2, (int, float)) else base.cm2
    base.cm3 = [base.cm3] if isinstance(base.cm3, (int, float)) else base.cm3

    # 3. Thermo & Energetics
    base.delta_h_t = [base.delta_h_t] if isinstance(base.delta_h_t, (int, float)) else base.delta_h_t
    base.T_t1 = [base.T_t1] if isinstance(base.T_t1, (int, float)) else base.T_t1
    base.T_t2 = [base.T_t2] if isinstance(base.T_t2, (int, float)) else base.T_t2
    base.T_t3 = [base.T_t3] if isinstance(base.T_t3, (int, float)) else base.T_t3
    base.p_t1 = [base.p_t1] if isinstance(base.p_t1, (int, float)) else base.p_t1
    base.p_t2 = [base.p_t2] if isinstance(base.p_t2, (int, float)) else base.p_t2
    base.p_t3 = [base.p_t3] if isinstance(base.p_t3, (int, float)) else base.p_t3
