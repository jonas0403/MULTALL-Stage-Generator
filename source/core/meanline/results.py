# ------------------------------------------------------------------
# File:    source/core/meanline/results.py
# Author:  Jonas Scholz
# Purpose: Post-processing and result-dict assembly for meanline.
# ------------------------------------------------------------------

# Verbatim move of meanline.py:686-840 (mm conversion, efficiencies, span
# prep, plot gate, result dict). Only indentation, the state-dict prefix,
# translated comments and deleted dead print blocks differ.

import math

from source.logging import debug_log
from source.core.geometry.plot_channel import plot_channel

Pi = math.pi


def build_results(s, plot_channel_contour):
    """Finalize units/derived values and assemble the result dict."""
    i_st = s['i_st']

    # --- Calculation after all Diameters converged ---


    # Convert all Diameters to mm

    D_H1_mm=[val*1000 for val in s['D_H1']]
    D_H2_mm=[val*1000 for val in s['D_H2']]
    D_H3_mm=[val*1000 for val in s['D_H3']]
    D_M1_mm=[val*1000 for val in s['D_M1']]
    D_M2_mm=[val*1000 for val in s['D_M2']]
    D_M3_mm=[val*1000 for val in s['D_M3']]
    D_S1_mm=[val*1000 for val in s['D_S1']]
    D_S2_mm=[val*1000 for val in s['D_S2']]
    D_S3_mm=[val*1000 for val in s['D_S3']]



    # Check for T_t3[i_st-1] - T_t_in > 0 to avoid division by zero
    if (s['T_t3'][i_st-1] - s['T_t_in']) != 0:
        eta_sC_tt_M=(s['TPR_M']**((s['kappa']-1)/s['kappa'])-1)/((s['T_t3'][i_st-1]/s['T_t_in'])-1)
        eta_pC_tt_M=s['R']*math.log(s['TPR_M'], math.e)/(s['cp']*math.log((s['T_t3'][i_st-1]/s['T_t_in']), math.e))
    else:
        eta_sC_tt_M=0.0 # Or handle as an error
        eta_pC_tt_M=0.0 # Or handle as an error


    eta_sC_tt, eta_pC_tt = [], []
    for i in range(i_st):
        eta_sC_tt.append(s['eta_s'][i])
        eta_pC_tt.append(s['R']*math.log(s['TPR'][i], math.e)/(s['cp']*math.log((s['T_t3'][i]/s['T_t1'][i]), math.e)))

    #Stage geometry
    # Calculating Span (b) based on channel geometry

    for i in range(i_st):
        # Only calculate Channel hight if meanline is not fixed because it was calculated earlier
        if s['fixed_radius_type'] != "mean":
            # Using the actual D_M values from calculation
            s['b1'][i]=s['mflow']/(s['roh_1'][i]*s['phi_1'][i]*s['u2'][i]*Pi*s['D_M1'][i])*1000
            s['b2'][i]=s['mflow']/(s['roh_2'][i]*s['phi_2'][i]*s['u2'][i]*Pi*s['D_M2'][i])*1000
            s['b3'][i]=s['mflow']/(s['roh_3'][i]*s['phi_3'][i]*s['u2'][i]*Pi*s['D_M3'][i])*1000

    for i in range(i_st):
        s['nue_in'].append(s['D_H1'][i]/s['D_S1'][i])
        s['delta_D_target_12'].append(s['D_S1'][i]-s['D_S2'][i])
        s['delta_D_target_23'].append(s['D_S2'][i]-s['D_S3'][i])


        # Specific Values for the radial Equlibrium
        s['cu1'][i]=s['cu1_u2'][i]*s['u2'][i]
        s['cu2'][i]=s['cu2_u2'][i]*s['u2'][i]
        s['cu3'][i]=s['cu3_u2'][i]*s['u2'][i]
        s['cm1'][i]=s['phi_1'][i]*s['u2'][i]
        s['cm2'][i]=s['phi_2'][i]*s['u2'][i]
        s['cm3'][i]=s['phi_3'][i]*s['u2'][i]


    # Add last T_t3 value onto the T_t1
    s['T_t1'].append(s['T_t3'][i_st-1])



    # Convert Span to mm
    b1=[val*1000 for val in s['b1']]
    b2=[val*1000 for val in s['b2']]
    b3=[val*1000 for val in s['b3']]


    if plot_channel_contour == True:
        debug_log.debug("plot incoming", context="meanline")
        plot_channel(s['D_S1'], s['D_S2'], s['D_S3'], s['D_H1'], s['D_H2'], s['D_H3'], s['D_M1'], s['D_M2'], s['D_M3'], i_st, s['l_R'], s['l_S'], s['beta_blade_1'], s['beta_blade_2'], s['alpha_blade_2'], s['alpha_blade_3'])


    for i in range(i_st):
        debug_log.debug(f"Stg:{i} D_S3={s['D_S3'][i]} D_M3={s['D_M3'][i]} D_H3={s['D_H3'][i]}", context="meanline")
        if i < i_st:
            debug_log.debug(f"Stg:{i+1} D_S1={s['D_S1'][i]} D_M1={s['D_M1'][i]} D_H1={s['D_H1'][i]}", context="meanline")


    result = {
        # Process- & Fluidparameter
        'mflow': s['mflow'],
        'n': s['n'],
        'kappa': s['kappa'],
        'R': s['R'],
        'cp': s['cp'],
        'i_st': s['i_st'],

        # Temperatures (Static & Total)
        'T_t1': s['T_t1'],
        'T_t2': s['T_t2'],
        'T_t3': s['T_t3'],
        'T_1': s['T_1'],
        'T_2': s['T_2'],
        'T_3': s['T_3'],

        # Pressures (Static & Total)
        'p_1': s['p_1'],
        'p_2': s['p_2'],
        'p_3': s['p_3'],
        'p_t1': s['p_t1'],
        'p_t2': s['p_t2'],
        'p_t3': s['p_t3'],

        # Gemoetrydiameters in Milimeters(Shroud, Hub, Mean)
        'D_S1_mm': D_S1_mm, 'D_S2_mm': D_S2_mm, 'D_S3_mm': D_S3_mm,
        'D_H1_mm': D_H1_mm, 'D_H2_mm': D_H2_mm, 'D_H3_mm': D_H3_mm,
        'D_M1_mm': D_M1_mm, 'D_M2_mm': D_M2_mm, 'D_M3_mm': D_M3_mm,

        # Gemoetrydiameters in Meters(Shroud, Hub, Mean)
        'D_S1': s['D_S1'], 'D_S2': s['D_S2'], 'D_S3': s['D_S3'],
        'D_H1': s['D_H1'], 'D_H2': s['D_H2'], 'D_H3': s['D_H3'],
        'D_M1': s['D_M1'], 'D_M2': s['D_M2'], 'D_M3': s['D_M3'],

        # Velocity triangles & widths
        'b1': b1, 'b2': b2, 'b3': b3,
        'cu1': s['cu1'], 'cu2': s['cu2'], 'cu3': s['cu3'],
        'u1': s['u1'], 'u2': s['u2'], 'u3': s['u3'],
        'cm1': s['cm1'], 'cm2': s['cm2'], 'cm3': s['cm3'],

        # Energetics- & Bladeparameters
        'delta_h_t': s['delta_h_t'],
        'l_R': s['l_R'],
        'l_S': s['l_S'],
        'l_R_t_R': s['l_R_t_R'],
        'l_S_t_S': s['l_S_t_S'],
        'd_R_l_R': s['d_R_l_R'],
        'd_S_l_S': s['d_S_l_S'],
        'incidence_R': s['incidence_R'],
        'incidence_S': s['incidence_S'],
        'z_R': s['z_R'],
        'z_S': s['z_S'],

        # Angles & Efficienties
        'beta_blade_1': s['beta_blade_1'],
        'beta_blade_2': s['beta_blade_2'],
        'alpha_blade_2': s['alpha_blade_2'],
        'alpha_blade_3': s['alpha_blade_3'],
        'TPR_M': s['TPR_M'],
        'eta_sC_tt_M': eta_sC_tt_M,
        'eta_pC_tt_M': eta_pC_tt_M,

        # Configurations
        'fixed_radius_type': s['fixed_radius_type'],
        'plot_channel_contour': plot_channel_contour

    }

    return result
