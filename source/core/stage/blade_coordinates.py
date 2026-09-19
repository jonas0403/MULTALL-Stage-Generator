# ------------------------------------------------------------------
# File:    source/core/stage/blade_coordinates.py
# Author:  Luca De Francesco, Jonas Scholz (based on Marco Wiens)
# Purpose: Blade-row coordinate assembly (blade/inlet/outlet merge).
# ------------------------------------------------------------------

# Verbatim moves from stage_calculation.py (coordinates :1946-1991,
# calculate_m_prime_new :1994-1996, calculation_blade_coordinates :1999-2074,
# merge_coordinates :2303-2330, additional_section :2333-2382,
# coordinates_levels :2385-2410, calc_blade_row_coordinates :2413-2445).
# Only indentation, the base. prefix for module state and translated
# comments differ.

import math

from source.logging import debug_log
from source.core.geometry.interpolation import intpol, intp_new
from source.core.stage.section_general import calculation_of_section
from source.core.stage.duct_coordinates import inlet_coordinates, outlet_coordinates
import source.core.stage.stage_calculation as base


def coordinates(row):

    '''
    Defining coordinates for all stages
    '''
    stage = (row - 1) // 2 + 1
    x_values = base.channel_data[stage]['x_values']
    r_values = base.channel_data[stage]['r_values']
    m_prime_values = base.channel_data[stage]['m_prime_values']


    R_u, x_u, y_u, z_u, R_l, x_l, y_l, z_l = [], [], [], [], [], [], [], []
    R_theta_s_star_u, R_theta_s_star_l, beta_S, m_star_l,m_star_u = [], [], [], [], []

    for i in range(len(base.h_H)):
        if base.h_H[i] == 0.0:
            k = 0
        elif base.h_H[i] == 0.2:
            k = 1
        elif base.h_H[i] == 0.5:
            k = 2
        elif base.h_H[i] == 0.8:
            k = 3
        elif base.h_H[i] == 1.0:
            k = 4

        chord, m_star_i, R_theta_s_star_i, m_star_u_i, R_theta_s_star_u_i, m_star_l_i, R_theta_s_star_l_i, m_prime, m_prime_u, m_prime_l, m_BP, beta_S_i, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(base.h_H[i], row)
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
    debug_log.debug(f"  TRACE coordinates [{row}]: x_values[0][0]={x_values[0][0]:.4f} x_values[0][-1]={x_values[0][-1]:.4f}  r_values[0][0]={r_values[0][0]:.6f} r_values[0][-1]={r_values[0][-1]:.6f}  r_values[4][0]={r_values[4][0]:.6f} r_values[4][-1]={r_values[4][-1]:.6f}")
    debug_log.debug(f"  TRACE coordinates [{row}]: R_u[0]={R_u[0]:.6f} R_u[124]={R_u[124]:.6f} R_u[125]={R_u[125]:.6f} R_u[499]={R_u[499]:.6f} R_u[500]={R_u[500]:.6f} R_u[624]={R_u[624]:.6f}")
    debug_log.debug(f"  TRACE coordinates [{row}]: x_u[0]={x_u[0]:.4f} x_u[124]={x_u[124]:.4f} x_u[125]={x_u[125]:.4f} x_u[499]={x_u[499]:.4f} x_u[500]={x_u[500]:.4f} x_u[624]={x_u[624]:.4f}")

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
    debug_log.debug(f"  DEBUG calculation_blade_coordinates [{row}]: x_u[0]={x_u[0]:.4f}, x_u[124]={x_u[124]:.4f}, x_u[125]={x_u[125]:.4f}, len(x_u)={len(x_u)}")


    x_sec, Rtheta_sec, d_sec, R_sec = [], [], [], []
    for i in range(len(base.h_H)):
        x_sec.append([])
        Rtheta_sec.append([])
        d_sec.append([])
        R_sec.append([])

    for i in range(len(base.h_H)):
        chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u_, m_star_l, R_theta_s_star_l_, m_prime_0_0, m_prime_u, m_prime_l, m_BP, beta_S_0_0, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2= calculation_of_section(base.h_H[i], row)

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

            # DIAGNOSTIC: check intpol for out-of-range (sentinel -99999)
            if x_sec_value < -99990:
                debug_log.debug(f"  DIAG: intpol x_sec FAIL at i={i} j={j} row={row} m_prime_new={m_prime_new[j]:.6f} range=[{m_prime_upper[0]:.6f},{m_prime_upper[-1]:.6f}]")
                x_sec_value = 0.0  # fallback
            if Rtheta_sec_value < -99990:
                debug_log.debug(f"  DIAG: intpol Rtheta_sec FAIL at i={i} j={j} row={row} m_prime_new={m_prime_new[j]:.6f} range=[{m_prime_upper[0]:.6f},{m_prime_upper[-1]:.6f}]")
                Rtheta_sec_value = 0.0

            x_sec[i].append(x_sec_value)
            Rtheta_sec[i].append(Rtheta_sec_value)

            lower_intpol = intpol(m_prime_new[j], len(m_prime_lower), m_prime_lower, R_theta_s_star_l[a:b])/1000
            if lower_intpol < -99990:
                debug_log.debug(f"  DIAG: intpol Rtheta_lower FAIL at i={i} j={j} row={row} m_prime_new={m_prime_new[j]:.6f} range=[{m_prime_lower[0]:.6f},{m_prime_lower[-1]:.6f}]")
                lower_intpol = Rtheta_sec[i][j]  # fallback => d_sec=0
            d_sec_value = Rtheta_sec[i][j] - lower_intpol

            if d_sec_value < 0:
                debug_log.debug(f"  DIAG: NEGATIVE d_sec at row={row} i={i} j={j} d_sec={d_sec_value:.10f} Rtheta_sec={Rtheta_sec[i][j]:.10f} lower={lower_intpol:.10f} m_prime_new={m_prime_new[j]:.6f}")

            R_sec_value = intpol(m_prime_new[j], len(m_prime_upper), m_prime_upper, R_u[a:b])/1000
            if R_sec_value < -99990:
                debug_log.debug(f"  DIAG: intpol R_sec FAIL at i={i} j={j} row={row} m_prime_new={m_prime_new[j]:.6f} range=[{m_prime_upper[0]:.6f},{m_prime_upper[-1]:.6f}]")
                R_sec_value = 0.0

            d_sec[i].append(d_sec_value)
            R_sec[i].append(R_sec_value)

    for i in range(len(base.h_H)):
        d_max = max(d_sec[i])
        d_max_idx = d_sec[i].index(d_max)
        d_mid = d_sec[i][len(d_sec[i])//2]
        debug_log.debug(f"  TRACE calc_blade_coords [{row}] section {i}: x_sec[0]={x_sec[i][0]:.6f} x_sec[-1]={x_sec[i][-1]:.6f}  d_sec max={d_max:.6f} at idx={d_max_idx} mid={d_mid:.6f}  Rtheta_sec[0]={Rtheta_sec[i][0]:.6f} Rtheta_sec[-1]={Rtheta_sec[i][-1]:.6f}")

    return x_sec, d_sec, R_sec, Rtheta_sec, beta_S, j_prime_max

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
    # Z_H (h=0.05) goes between hub (h=0.0, idx 0) and section 1 (h=0.20, idx 1)
    x.insert(1, X_0_05)
    Rtheta.insert(1, Rtheta_0_05)
    d.insert(1, d_0_05)
    R.insert(1, R_0_05)
    # After the Z_H insert, sections are: [0]=h0.0, [1]=h0.05, [2]=h0.20, [3]=h0.50, [4]=h0.80, [5]=h1.0
    # Z_S (h=0.95) goes between h=0.80 (idx 4) and h=1.0 (idx 5) → insert at index 5
    x.insert(5, X_0_95)
    Rtheta.insert(5, Rtheta_0_95)
    d.insert(5, d_0_95)
    R.insert(5, R_0_95)

    for i in range(len(R)):
        radii_at_inlet = [R[sec][0] for sec in range(len(R))]
        radii_monotonic = all(radii_at_inlet[k] <= radii_at_inlet[k+1] for k in range(len(radii_at_inlet)-1))
        if i == 0:
            debug_log.debug(f"  Section ordering: radii at inlet = {[f'{r:.4f}' for r in radii_at_inlet]}  monotonic={radii_monotonic}")

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
            Z = (R[6][i]-R[0][i])*element + R[0][i]
            A = [x[0][i], x[1][i], x[2][i], x[3][i], x[4][i], x[5][i], x[6][i]]
            B = [Rtheta[0][i], Rtheta[1][i], Rtheta[2][i], Rtheta[3][i], Rtheta[4][i],Rtheta[5][i], Rtheta[6][i]]
            C = [d[0][i], d[1][i], d[2][i], d[3][i], d[4][i], d[5][i], d[6][i]]
            D = [R[0][i], R[1][i], R[2][i], R[3][i], R[4][i], R[5][i], R[6][i]]
            x_new[j].append(intp_new(2, N, XN, A, Z))
            Rtheta_new[j].append(intp_new(2, N, XN, B, Z))
            d_new[j].append(intp_new(2 ,N, XN, C, Z))
            R_new[j].append(intp_new(2, N, XN, D, Z))

    return x_new, d_new, R_new, Rtheta_new

# function for calculation of blade row coordinates. It just activates other functions
def calc_blade_row_coordinates(row, j_prime_max, num_planes, n_max_in, l_inlet, n_max_out, l_outlet, Z_H, Z_S, levels):
    x_sec, d_sec, R_sec, Rtheta_sec, beta_S, j_prime_max = calculation_blade_coordinates(j_prime_max, row)
    x_in, d_in, R_in, Rtheta_in = inlet_coordinates(row, num_planes, n_max_in, l_inlet, x_sec, d_sec, R_sec, Rtheta_sec, beta_S, j_prime_max)
    x_out, d_out, R_out, Rtheta_out = outlet_coordinates(row, n_max_out, l_outlet, num_planes, x_sec, Rtheta_sec, beta_S)
    x, d, R, Rtheta = merge_coordinates(num_planes, j_prime_max, n_max_in, x_in, x_sec, x_out, d_in, d_sec, d_out, R_in, R_sec, R_out, Rtheta_in, Rtheta_sec, Rtheta_out)

    for i in range(num_planes):
        debug_log.debug(f"  TRACE merged [{row}] plane {i}: x[0]={x[i][0]:.6f} x[-1]={x[i][-1]:.6f}  R[0]={R[i][0]:.6f} R[-1]={R[i][-1]:.6f}  d[0]={d[i][0]:.6f} d[-1]={d[i][-1]:.6f}  Rtheta[0]={Rtheta[i][0]:.6f} Rtheta[-1]={Rtheta[i][-1]:.6f}")

    x, d, R, Rtheta = additional_section(Z_H, Z_S, x, d, R, Rtheta)
    x_new, d_new, R_new, Rtheta_new = coordinates_levels(levels, x, d, R, Rtheta )

    for j in range(len(levels)):
        stats = []
        for name, arr in [('x', x_new[j]), ('d', x_new[j]), ('R', R_new[j]), ('Rt', Rtheta_new[j])]:
            n_nan = sum(1 for v in arr if v != v)
            n_inf = sum(1 for v in arr if v == float('inf') or v == -float('inf'))
            if n_nan or n_inf:
                stats.append(f"{name}:{len(arr)}pts nan={n_nan} inf={n_inf}")
            n_neg = sum(1 for v in arr if v < 0)
            if name != 'Rt' and n_neg:
                stats.append(f"{name}:{len(arr)}pts neg={n_neg}")
        if stats:
            debug_log.debug(f"  TRACE final [{row}] level {j}: *** INVALID *** {' | '.join(stats)}", context="INVALID")
        else:
            debug_log.debug(f"  TRACE final [{row}] level {j}: x[0]={x_new[j][0]:.6f} x[-1]={x_new[j][-1]:.6f}  R[0]={R_new[j][0]:.6f} R[-1]={R_new[j][-1]:.6f}  d[0]={d_new[j][0]:.6f} d[-1]={d_new[j][-1]:.6f}  Rtheta[0]={Rtheta_new[j][0]:.6f} Rtheta[-1]={Rtheta_new[j][-1]:.6f}")
            # Log negative Rtheta count as informational (not INVALID) — negative Rtheta
            # is physically correct when the blade turns past the zero-Rtheta reference
            n_neg_rt = sum(1 for v in Rtheta_new[j] if v < 0)
            if n_neg_rt:
                debug_log.debug(f"  TRACE final [{row}] level {j}: Rt negative count={n_neg_rt}/{len(Rtheta_new[j])} (informational — physically correct for blades turning past zero reference)", context="Rt_negative_info")

    return x_new, d_new, R_new, Rtheta_new
