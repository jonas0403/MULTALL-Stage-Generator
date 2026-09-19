# ------------------------------------------------------------------
# File:    source/core/meanline/stage_iteration.py
# Author:  Jonas Scholz
# Purpose: Per-stage inner diameter iteration of the meanline solver.
# ------------------------------------------------------------------

# Verbatim move of meanline.py:154-184 (per-stage setup) and :186-596 (inner
# diameter iteration + next-stage guess seeding). Only indentation, the
# state-dict prefix, translated German comments and deleted dead print blocks
# differ. Inner-loop scalars stay function locals.

import math

from source.logging import debug_log
from source.core.meanline.losses import (
    xi_ac_pro, xi_ac_te, xi_a_cl, xi_ac_inc, xi_a_sec, xi_ac_ma, diffusion,
    angle_blade_in, angle_blade_out, Re,
)

Pi = math.pi


def iterate_stage(s, i):
    """Run the full inner diameter iteration for stage i (mutates s)."""
    current_D_M1_guess=s['next_guess1'][i]
    current_D_M2_guess=s['next_guess2'][i]
    current_D_M3_guess=s['next_guess3'][i]

    iteration_count=0
    max_iteration_steps=1000
    tolerance=0.0005

    stage_msg = f"\n--- Starting calculation for Stage {i+1}/{s['i_st']} ---"
    print(stage_msg)
    debug_log.debug(stage_msg, context="meanline")

    if s['fixed_radius_type'] == "hub":
        s['D_H1'][i]=s['D_f1'][i]
        s['D_H2'][i]=s['D_f2'][i]
        s['D_H3'][i]=s['D_f3'][i]

    elif s['fixed_radius_type'] == "shroud":
        s['D_S1'][i]=s['D_f1'][i]
        s['D_S2'][i]=s['D_f2'][i]
        s['D_S3'][i]=s['D_f3'][i]
    elif s['fixed_radius_type'] == "mean":
        s['D_M1'][i]=s['D_f1'][i]
        s['D_M2'][i]=s['D_f2'][i]
        s['D_M3'][i]=s['D_f3'][i]
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
        s['u1'][i]=(2*Pi*s['n'][i])/60*current_D_M1_guess/2
        s['u2'][i]=(2*Pi*s['n'][i])/60*current_D_M2_guess/2



        if i > 0 :
            s['u3'][i-1]=s['u2'][i]
        else:
            s['u3'][i] = 0

        s['u1_u2'][i]=s['u1'][i]/s['u2'][i]
        s['u2_u2'][i]=s['u2'][i]/s['u2'][i]
        #u3_u2[i]=u3[i]/u2[i] # Stators dont move


        #region Calculates the flow Properties

        #Rotor
        s['h_R_l_R'][i]=s['h_R'][i]/s['l_R'][i]
        s['t_R'][i]=round(Pi*current_D_M2_guess/s['z_R'][i]*1000,2)
        s['l_R_t_R'][i]=s['l_R'][i]/s['t_R'][i]

        #Stator
        s['h_S_l_S'][i]=s['h_S'][i]/s['l_S'][i]
        s['t_S'][i]=round(Pi*current_D_M2_guess/s['z_S'][i]*1000,2)
        s['l_S_t_S'][i]=s['l_S'][i]/s['t_S'][i]

        # Non Dimensinal Velocities
        s['c1_u2'][i]=s['phi_1'][i]/math.sin(math.radians(s['alpha_1'][i])) if math.sin(math.radians(s['alpha_1'][i]))!=0 else float('inf')
        s['cu1_u2'][i]=s['c1_u2'][i]*math.cos(math.radians(s['alpha_1'][i]))
        s['c3_u2'][i]=s['phi_3'][i]/math.sin(math.radians(s['alpha_3'][i])) if math.sin(math.radians(s['alpha_3'][i]))!=0 else float('inf')
        s['cu2_u2'][i]=s['u1_u2'][i]*s['cu1_u2'][i]+s['psi_h'][i]/2-s['q'][i]/s['u2'][i]**2+s['c3_u2'][i]**2/2-s['c1_u2'][i]**2/2
        s['c2_u2'][i]=math.sqrt(s['phi_2'][i]**2+s['cu2_u2'][i]**2)

        s['alpha_2'][i]=math.degrees(math.acos(s['cu2_u2'][i]/s['c2_u2'][i]))
        s['delta_alpha'][i]=s['alpha_2'][i]-s['alpha_3'][i]


        # Absolut and Relative Velocities
        s['c1'][i]=s['c1_u2'][i]*s['u2'][i]
        s['c2'][i]=s['c2_u2'][i]*s['u2'][i]
        s['c3'][i]=s['c3_u2'][i]*s['u2'][i]
        s['cu3_u2'][i]=s['c3_u2'][i]*math.cos(math.radians(s['alpha_3'][i]))
        s['wu1_u2'][i]=s['cu1_u2'][i]-s['u1_u2'][i]
        s['wu2_u2'][i]=s['cu2_u2'][i]-s['u2_u2'][i]
        s['w1_u2'][i]=math.sqrt(s['phi_1'][i]**2+s['wu1_u2'][i]**2)
        s['w1'][i]=s['w1_u2'][i]*s['u2'][i]
        s['w2_u2'][i]=math.sqrt(s['phi_2'][i]**2+s['wu2_u2'][i]**2)
        s['w2'][i]=s['w2_u2'][i]*s['u2'][i]

        # Angles and Enthalpy
        # Check math.acos arguments to avoid domain errors (-1 <= x <= 1)

        s['beta_1'][i]=math.degrees(math.acos(s['wu1_u2'][i]/s['w1_u2'][i]))
        s['beta_2'][i]=math.degrees(math.acos(s['wu2_u2'][i]/s['w2_u2'][i]))
        s['delta_beta'][i]=s['beta_2'][i]-s['beta_1'][i]

        s['a'][i]=(s['cu2_u2'][i]-s['u1_u2'][i]*s['cu1_u2'][i])*s['u2'][i]**2
        s['delta_h_t'][i]=s['a'][i]+s['q'][i]

        # Total and Static Temperatures
        if i>0:
            s['T_t1'][i]=s['T_t3'][i-1]# Rotor Inlet temperature is equal to stator exit Temperatur
            s['p_t1'][i]=s['p_t3'][i-1]# Rotor Inlet pressure is equal to stator exit Temperatur

        s['T_t3'][i]=s['T_t1'][i]+s['delta_h_t'][i]/s['cp']
        s['T_t2'][i]=s['T_t3'][i]# For stator inlet

        s['T_1'][i]=s['T_t1'][i]-s['c1'][i]**2/(2*s['cp'])

        s['T_2'][i]=s['T_t2'][i]-s['c2'][i]**2/(2*s['cp'])

        s['T_3'][i]=s['T_t3'][i]-s['c3'][i]**2/(2*s['cp'])


        # Static and Total pressure and Density
        s['p_1'][i]=s['p_t1'][i]*(s['T_1'][i]/s['T_t1'][i])**(s['kappa']/(s['kappa']-1))
        if i > 0:
            s['roh_1'][i]=s['roh_3'][i-1]
        else:
            s['roh_1'][i]=s['p_1'][i]/(s['R']*s['T_1'][i])

        # Blade Angles, Reynoldsnumbers, Machnumbers and Losses


        debug_log.debug(f"beta_blade_1[i]={s['beta_blade_1'][i]}=angle_blade_in(...)", context="meanline")

        s['Re_l_R'][i]=Re(s['roh_1'][i],s['w1'][i],s['l_R'][i],s['T_1'][i])
        s['beta_blade_1'][i]=angle_blade_in(s['beta_1'][i], s['beta_2'][i], s['w1'][i], s['w2'][i], s['T_1'][i], s['T_2'][i], s['l_R_t_R'][i], s['d_R_l_R'][i], s['incidence_R'][i], s['R'], s['kappa'])
        s['beta_blade_2'][i]=angle_blade_out(s['beta_1'][i], s['beta_2'][i], s['w1'][i], s['w2'][i], s['T_1'][i], s['T_2'][i], s['l_R_t_R'][i], s['d_R_l_R'][i], s['incidence_R'][i], s['R'], s['kappa'])
        s['delta_beta_in'][i]=s['beta_blade_1'][i]-s['beta_1'][i]
        s['delta_beta_out'][i]=s['beta_2'][i]-s['beta_blade_2'][i]

        # Rotor Losses

        s['xi_R_pro'][i]=xi_ac_pro(s['beta_1'][i],s['beta_2'][i], s['l_R_t_R'][i])
        s['xi_R_cl'][i]=xi_a_cl(s['beta_1'][i], s['beta_2'][i], s['l_R_t_R'][i], s['d_Cl_R'][i], s['h_R'][i])
        s['xi_R_sec'][i]=xi_a_sec(s['beta_1'][i], s['beta_2'][i], s['l_R_t_R'][i], s['t_R'][i], s['h_R'][i])
        s['xi_R_inc'][i]=xi_ac_inc(s['beta_1'][i], s['beta_2'][i],s['incidence_R'][i])
        s['xi_R_ma'][i]=xi_ac_ma(s['w1'][i], s['T_1'][i])
        s['xi_R_te'][i]=xi_ac_te(s['beta_1'][i], s['beta_2'][i], s['l_R_t_R'][i], s['t_R'][i], s['d_TE_R'][i], s['Re_l_R'][i])
        s['xi_R'][i]=s['xi_R_pro'][i] + s['xi_R_te'][i] + s['xi_R_cl'][i] + s['xi_R_sec'][i] + s['xi_R_inc'][i] + s['xi_R_ma'][i]

        # Machnumbers

        s['Ma_w1'][i]=s['w1'][i]/math.sqrt(s['kappa']*s['R']*s['T_1'][i])
        s['Ma_w2'][i]=s['w2'][i]/math.sqrt(s['kappa']*s['R']*s['T_2'][i])
        s['Ma_c1'][i]=s['c1'][i]/math.sqrt(s['kappa']*s['R']*s['T_1'][i])
        s['Ma_c2'][i]=s['c2'][i]/math.sqrt(s['kappa']*s['R']*s['T_2'][i])
        s['Ma_c3'][i]=s['c3'][i]/math.sqrt(s['kappa']*s['R']*s['T_3'][i])
        s['Ma_m1'][i]=s['phi_1'][i]*s['u2'][i]/math.sqrt(s['kappa']*s['R']*s['T_1'][i])
        s['Ma_m2'][i]=s['phi_2'][i]*s['u2'][i]/math.sqrt(s['kappa']*s['R']*s['T_2'][i])
        s['Ma_m3'][i]=s['phi_3'][i]*s['u2'][i]/math.sqrt(s['kappa']*s['R']*s['T_3'][i])


        s['alpha_blade_2'][i]=angle_blade_in(s['alpha_2'][i], s['alpha_3'][i], s['c2'][i], s['c3'][i], s['T_2'][i], s['T_3'][i], s['l_S_t_S'][i], s['d_S_l_S'][i], s['incidence_S'][i], s['R'], s['kappa'])
        s['alpha_blade_3'][i]=angle_blade_out(s['alpha_2'][i], s['alpha_3'][i], s['c2'][i], s['c3'][i], s['T_2'][i], s['T_3'][i], s['l_S_t_S'][i], s['d_S_l_S'][i], s['incidence_S'][i], s['R'], s['kappa'])
        s['delta_alpha_in'][i]=s['alpha_2'][i]-s['alpha_blade_2'][i]
        s['delta_alpha_out'][i]=s['alpha_blade_3'][i]-s['alpha_3'][i]


        # Rotor design Parameters

        s['w2_w1'][i]=s['w2_u2'][i]/s['w1_u2'][i]
        s['B_R'][i]=2*abs(s['wu2_u2'][i]-s['wu1_u2'][i])/((s['w2_u2'][i]+s['w1_u2'][i])/2)
        s['c_L_R'][i]=s['B_R'][i]/s['l_R_t_R'][i]
        s['D_R'][i]=diffusion(s['beta_1'][i], s['beta_2'][i], s['w1'][i], s['w2'][i], s['l_R_t_R'][i])


        # Stator deign parameters

        s['c3_c2'][i]=s['c3_u2'][i]/s['c2_u2'][i]
        s['B_S'][i]=2*abs(s['cu3_u2'][i] - s['cu2_u2'][i])/((s['c3_u2'][i] + s['c2_u2'][i])/2)
        s['c_L_S'][i]=s['B_S'][i]/s['l_S_t_S'][i]
        s['D_S_diff'][i]=diffusion(s['alpha_2'][i], s['alpha_3'][i], s['c2'][i], s['c3'][i], s['l_R_t_R'][i]) # ????? diffusion has to be calculated with l_S_t_S



        # Pressures, Densities and losses continued

        s['T_2is'][i]=s['T_2'][i]-s['xi_R'][i]*s['w1'][i]**2/(2*s['cp'])
        s['p_2'][i]=s['p_1'][i]*(s['T_2is'][i]/s['T_1'][i])**(s['kappa']/(s['kappa']-1))
        s['roh_2'][i]=s['p_2'][i]/(s['T_2'][i]*s['R'])

        s['Re_l_S'][i]=Re(s['roh_2'][i], s['c2'][i], s['l_S'][i], s['T_2'][i])

        s['xi_S_pro'][i]=xi_ac_pro(s['alpha_2'][i],s['alpha_3'][i], s['l_S_t_S'][i])
        s['xi_S_cl'][i]=xi_a_cl(s['alpha_2'][i], s['alpha_3'][i], s['l_S_t_S'][i], s['d_CL_S'][i], s['h_S'][i])
        s['xi_S_sec'][i]=xi_a_sec(s['alpha_2'][i], s['alpha_3'][i], s['l_S_t_S'][i], s['t_S'][i], s['h_S'][i])
        s['xi_S_inc'][i]=xi_ac_inc(s['alpha_2'][i], s['alpha_3'][i] ,s['incidence_S'][i])
        s['xi_S_ma'][i]=xi_ac_ma(s['c2'][i], s['T_2'][i])
        s['xi_S_te'][i]=xi_ac_te(s['alpha_2'][i], s['alpha_3'][i], s['l_S_t_S'][i], s['t_S'][i], s['d_TE_S'][i], s['Re_l_S'][i])
        s['xi_S'][i]=s['xi_S_pro'][i] + s['xi_S_te'][i] + s['xi_S_cl'][i] + s['xi_S_sec'][i] + s['xi_S_inc'][i] + s['xi_S_ma'][i]

        s['eta_s'][i]=(s['psi_h'][i]-s['xi_R'][i]*s['w1_u2'][i]**2-s['xi_S'][i]*s['c2_u2'][i]**2)/s['psi_h'][i]
        s['p_t3'][i]=s['p_t1'][i]*(s['eta_s'][i]*(s['T_t3'][i]/s['T_t1'][i]-1)+1)**(s['kappa']/(s['kappa']-1))
        s['p_3'][i]=s['p_t3'][i]*(s['T_3'][i]/s['T_t3'][i])**(s['kappa']/(s['kappa']-1))
        s['roh_3'][i]=s['p_3'][i]/(s['T_3'][i]*s['R'])

        s['TPR'][i]=s['p_t3'][i]/s['p_t1'][i]
        s['p_t2'][i]=s['p_2'][i]*(s['T_t2'][i]/s['T_2'][i])**(s['kappa']/(s['kappa']-1))
        s['roh_h_des'][i]=(2*(s['cu2_u2'][i]-s['u1_u2'][i]*s['cu1_u2'][i])-(s['cu2_u2'][i]**2-s['cu1_u2'][i]**2))/(2*(s['cu2_u2'][i]-s['u1_u2'][i]*s['cu1_u2'][i])-(s['c3_u2'][i]**2-s['c1_u2'][i]**2))

        s['delta_h'][i]=s['psi_h'][i]*s['u2'][i]**2/2
        s['delta_h_R'][i]=s['delta_h'][i]*s['roh_h_des'][i]
        s['delta_h_S'][i]=s['delta_h'][i]-s['delta_h_R'][i]
        s['delta_h_loss_R'][i]=s['xi_R'][i]*s['w1'][i]**2/2
        s['delta_h_loss_S'][i]=s['xi_S'][i]*s['c2'][i]**2/2
        s['delta_h_loss'][i]=s['delta_h_loss_R'][i]+s['delta_h_loss_S'][i]

        s['eta_sC_tt'][i]=s['eta_s'][i]
        s['eta_pC_tt'][i]=s['R']*math.log(s['TPR'][i],math.e)/(s['cp']*math.log(s['T_t3'][i]/s['T_t1'][i],math.e))

        # endregion

        # Calculating C_m for the Diameter Calculation to Gurantee Continuity
        if i > 0:
            s['c_m1'][i] = s['c_m3'][i-1]
        else:
            s['c_m1'][i] = s['phi_1'][i]*s['u2'][i]

        s['c_m2'][i] = s['phi_2'][i]*s['u2'][i]
        s['c_m3'][i] = s['phi_3'][i]*s['u2'][i]

        # Calculates the new Diameter based on massflow
        if s['fixed_radius_type'] == "hub":
            # D_H1[i] is fixed
            under_sqrt1=s['D_H1'][i]**2+(4*s['mflow'])/(Pi*s['roh_1'][i]*s['c_m1'][i])
            under_sqrt2=s['D_H2'][i]**2+(4*s['mflow'])/(Pi*s['roh_2'][i]*s['c_m2'][i])
            under_sqrt3=s['D_H3'][i]**2+(4*s['mflow'])/(Pi*s['roh_3'][i]*s['c_m3'][i])

            if under_sqrt1 < 0:
                warn_msg = f"Warning: Term under sqrt for D_S1 at stage {i} is negative. Setting D_S1[i] = D_H1[i]."
                print(warn_msg)
                debug_log.debug(warn_msg, context="meanline")
                s['D_S1'][i]=s['D_H1'][i]
            else:
                s['D_S1'][i]=math.sqrt(under_sqrt1)
            new_D_M1_guess=(s['D_H1'][i]+s['D_S1'][i])/2

            if under_sqrt2 < 0:
                warn_msg = f"Warning: Term under sqrt for D_S2 at stage {i} is negative. Setting D_S2[i] = D_H2[i]."
                print(warn_msg)
                debug_log.debug(warn_msg, context="meanline")
                s['D_S2'][i]=s['D_H2'][i]
            else:
                s['D_S2'][i]=math.sqrt(under_sqrt2)
            new_D_M2_guess=(s['D_H2'][i]+s['D_S2'][i])/2

            if under_sqrt3 < 0:
                warn_msg = f"Warning: Term under sqrt for D_S3 at stage {i} is negative. Setting D_S3[i] = D_H3[i]."
                print(warn_msg)
                debug_log.debug(warn_msg, context="meanline")
                s['D_S3'][i]=s['D_H3'][i]
            else:
                s['D_S3'][i]=math.sqrt(under_sqrt3)
            new_D_M3_guess=(s['D_H3'][i]+s['D_S3'][i])/2

            # Update next_guess with the current converged Values
            s['D_M1'][i]=new_D_M1_guess
            s['D_M2'][i]=new_D_M2_guess
            s['D_M3'][i]=new_D_M3_guess

        if s['fixed_radius_type'] == "shroud":
            # D_S1[i] is fixed

            under_sqrt1=s['D_S1'][i]**2-(4*s['mflow'])/(Pi*s['roh_1'][i]*s['c_m1'][i])
            under_sqrt2=s['D_S2'][i]**2-(4*s['mflow'])/(Pi*s['roh_2'][i]*s['c_m2'][i])
            under_sqrt3=s['D_S3'][i]**2-(4*s['mflow'])/(Pi*s['roh_3'][i]*s['c_m3'][i])

            if under_sqrt1 < 0:
                warn_msg = f"Warning: Term under sqrt for D_H1 at stage {i} is negative. Setting D_H1[i] = D_S1[i]."
                print(warn_msg)
                debug_log.debug(warn_msg, context="meanline")
                s['D_H1'][i]=s['D_S1'][i]
            else:
                s['D_H1'][i]=math.sqrt(under_sqrt1)
            new_D_M1_guess=(s['D_H1'][i]+s['D_S1'][i])/2

            if under_sqrt2 < 0:
                warn_msg = f"Warning: Term under sqrt for D_H2 at stage {i} is negative. Setting D_H2[i] = D_S2[i]."
                print(warn_msg)
                debug_log.debug(warn_msg, context="meanline")
                s['D_H2'][i]=s['D_S2'][i]
            else:
                s['D_H2'][i]=math.sqrt(under_sqrt2)
            new_D_M2_guess=(s['D_H2'][i]+s['D_S2'][i])/2

            if under_sqrt3 < 0:
                warn_msg = f"Warning: Term under sqrt for D_H3 at stage {i} is negative. Setting D_H3[i] = D_S3[i]."
                print(warn_msg)
                debug_log.debug(warn_msg, context="meanline")
                s['D_H3'][i]=s['D_S3'][i]
            else:
                s['D_H3'][i]=math.sqrt(under_sqrt3)
            new_D_M3_guess=(s['D_H3'][i]+s['D_S3'][i])/2

            # Update next_guess with the current converged Values
            s['D_M1'][i]=new_D_M1_guess
            s['D_M2'][i]=new_D_M2_guess
            s['D_M3'][i]=new_D_M3_guess

        if s['fixed_radius_type'] == "mean":
            # D_M1[i] is fixed
            # Calculate Channel height
            s['b1'][i]=s['mflow']/(s['roh_1'][i]*s['phi_1'][i]*s['u2'][i]*Pi*s['D_M1'][i])
            s['b2'][i]=s['mflow']/(s['roh_2'][i]*s['phi_2'][i]*s['u2'][i]*Pi*s['D_M2'][i])
            s['b3'][i]=s['mflow']/(s['roh_3'][i]*s['phi_3'][i]*s['u2'][i]*Pi*s['D_M3'][i])

            # Calculate Shroud Diameter
            s['D_S1'][i]=s['D_M1'][i]+s['b1'][i]
            s['D_S2'][i]=s['D_M2'][i]+s['b2'][i]
            s['D_S3'][i]=s['D_M3'][i]+s['b3'][i]

            # Calculate Hub Diameter
            s['D_H1'][i]=s['D_M1'][i]-s['b1'][i]
            s['D_H2'][i]=s['D_M2'][i]-s['b2'][i]
            s['D_H3'][i]=s['D_M3'][i]-s['b3'][i]

            # Overwrite D_M guesses to check for convergence
            new_D_M1_guess=s['D_M1'][i]
            new_D_M2_guess=s['D_M2'][i]
            new_D_M3_guess=s['D_M3'][i]

            # Set converged to True because fixed mean line does not need to be iteratated
            converged = True



        # Applying relaxation factor
        # Used for the stability of an non-linear system
        # Only use when not in meanline fixed design

        if s['fixed_radius_type'] != "mean":
            current_D_M1_guess=old_D_M1_guess*(1-s['relaxation_factor'])+new_D_M1_guess*s['relaxation_factor']
            current_D_M2_guess=old_D_M2_guess*(1-s['relaxation_factor'])+new_D_M2_guess*s['relaxation_factor']
            current_D_M3_guess=old_D_M3_guess*(1-s['relaxation_factor'])+new_D_M3_guess*s['relaxation_factor']
        else:
            # With fixed_radius_type "mean", adopt the fixed values
            current_D_M1_guess=s['D_M1'][i]
            current_D_M2_guess=s['D_M2'][i]
            current_D_M3_guess=s['D_M3'][i]


        # Update the meanline diameters

        s['D_M1'][i]=current_D_M1_guess
        s['D_M2'][i]=current_D_M2_guess
        s['D_M3'][i]=current_D_M3_guess


        if s['fixed_radius_type'] == "hub":
            # D_H is fixed, D_S adapts
            s['D_S1'][i]=2*s['D_M1'][i]-s['D_H1'][i]
            s['D_S2'][i]=2*s['D_M2'][i]-s['D_H2'][i]
            s['D_S3'][i]=2*s['D_M3'][i]-s['D_H3'][i]
        elif s['fixed_radius_type'] == "shroud":
            # D_S is fixed, D_H adapts
            s['D_H1'][i]=2*s['D_M1'][i]-s['D_S1'][i]
            s['D_H2'][i]=2*s['D_M2'][i]-s['D_S2'][i]
            s['D_H3'][i]=2*s['D_M3'][i]-s['D_S3'][i]


        # Update the Rotor and Stator Height
        s['h_S'][i]=((s['D_S2'][i]-s['D_H2'][i])+(s['D_S3'][i]-s['D_H3'][i]))/4*1000
        s['h_R'][i]=((s['D_S1'][i]-s['D_H1'][i])+(s['D_S2'][i]-s['D_H2'][i]))/4*1000

        # Check for Convergence
        converged=(abs(new_D_M1_guess-old_D_M1_guess)<tolerance and abs(new_D_M2_guess-old_D_M2_guess)<tolerance and abs(new_D_M3_guess-old_D_M3_guess)<tolerance)

        # Debug prints
        if iteration_count % 10 == 0 or converged: # Every 10 iterations or at convergence
            debug_log.debug(f"Stage {i+1}, Iteration {iteration_count+1}: D_M1={current_D_M1_guess:.4f}, D_M2={current_D_M2_guess:.4f}, D_M3={current_D_M3_guess:.4f}", context="meanline")
            debug_log.debug(f"Changes: dD_M1={abs(current_D_M1_guess - old_D_M1_guess):.6f}, dD_M2={abs(current_D_M2_guess - old_D_M2_guess):.6f}, dD_M3={abs(current_D_M3_guess - old_D_M3_guess):.6f} (Tol: {tolerance})", context="meanline")
            debug_log.debug(f"Diameters: D_S1={s['D_S1'][i]:.4f} D_M1={s['D_M1'][i]:.4f} D_H1={s['D_H1'][i]:.4f}  D_S2={s['D_S2'][i]:.4f} D_M2={s['D_M2'][i]:.4f} D_H2={s['D_H2'][i]:.4f}  D_S3={s['D_S3'][i]:.4f} D_M3={s['D_M3'][i]:.4f} D_H3={s['D_H3'][i]:.4f}", context="meanline")
            debug_log.debug(f"T_t1={s['T_t1'][i]:.2f}K p_t1={s['p_t1'][i]:.2f}Pa roh_1={s['roh_1'][i]:.4f}  Ma_w1={s['Ma_w1'][i]:.3f} Ma_c1={s['Ma_c1'][i]:.3f}  eta_s={s['eta_s'][i]:.3f} TPR={s['TPR'][i]:.3f}", context="meanline")


        if converged:
            conv_msg = f"Stage {i+1}: Converged in {iteration_count+1} iterations."
            print(conv_msg)
            debug_log.debug(conv_msg, context="meanline")
            if s['fixed_radius_type'] == "hub" and i < s['i_st']:
                current_D_M1_guess = current_D_M3_guess
            elif s['fixed_radius_type'] == "shroud" and i < s['i_st']:
                current_D_M1_guess = current_D_M3_guess
            break # Exit the iteration loop for this stage


        # Update Iteration Count
        iteration_count += 1



    else: # This 'else' block executes if the while loop completes WITHOUT a 'break'
        nonconv_msg = f"Warning: Diameters for stage {i} did not converge after {max_iteration_steps} iterations."
        print(nonconv_msg)
        debug_log.debug(nonconv_msg, context="meanline")
        # The last calculated values are stored in D_M1[i], D_S1[i] etc.


    # Guarantee the continuity of the diameters between stages


    # Important: The initial guess for the next stage (i+1) has to be the converged D_M of the current stage (i)

    if i < s['i_st'] - 1: # Only do this if it is not the last stage
        s['next_guess1'][i+1] = s['D_M1'][i]
        s['next_guess2'][i+1] = s['D_M2'][i]
        s['next_guess3'][i+1] = s['D_M3'][i]
