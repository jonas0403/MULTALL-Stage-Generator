# ------------------------------------------------------------------
# File:    source/core/stage/duct_coordinates.py
# Author:  Jonas Scholz
# Purpose: Inlet and outlet duct coordinate builders per blade row.
# ------------------------------------------------------------------

# Verbatim moves from stage_calculation.py (inlet_coordinates :2077-2176,
# outlet_coordinates :2179-2300). Only indentation, the base. prefix for
# module state and translated comments differ.

import math

from source.logging import debug_log
from source.core.geometry.bezier import bezier
from source.core.geometry.interpolation import intpol
import source.core.stage.stage_calculation as base

Pi = math.pi


# calculation of inlet coordinates
def inlet_coordinates(row, num_planes, n_max_in, l_inlet, x_sec, d_sec, R_sec, Rtheta_sec, beta_S, j_prime_max):

    '''
    Defining coordinates for all stages
    '''
    stage = (row - 1) // 2 + 1
    x0 = base.channel_data[stage]['x0']
    x_values = base.channel_data[stage]['x_values']
    r_values = base.channel_data[stage]['r_values']


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

    if  row % 2 != 0:
        k = 0
    elif row % 2 == 0:
        k = 3

    # First pass: compute raw DX_in
    for i in range(num_planes):
        DX_in.append(x0[k]/1000 - x_sec[i][0])
        DX1_in.append(x_sec[i][1] - x_sec[i][0])

    # Clamp DX_in for internal stages where x0[0]=x0[1] (no inlet duct).
    # Without this, DX_in ≈ 0 causes division by zero in a_in and
    # Rtheta_prime_in_BP. The clamped value guarantees the cosine-bunching
    # formula works while keeping the overlap negligible (~5 mm per stage).
    for i in range(num_planes):
        chord_approx = abs(x_sec[i][-1] - x_sec[i][0])  # blade chord in meters
        min_inlet = max(chord_approx * 0.05, 0.005)     # at least 5 mm or 5% chord
        if abs(DX_in[i]) < min_inlet:
            DX_in[i] = -min_inlet   # negative = upstream of LE

    # Second pass: compute Rtheta_prime_in_BP using adjusted DX_in
    for i in range(num_planes):
        x = max(Rtheta_sec[0][0], Rtheta_sec[4][0])*2.2
        Rtheta_in_BP[i].append(x)
        Rtheta_in_BP[i].append(x)
        Rtheta_in_BP[i].append(Rtheta_sec[i][0])
        Rtheta_prime_in_BP[i].append(Rtheta_in_BP[i][0]/abs(DX_in[i]))
        Rtheta_prime_in_BP[i].append(Rtheta_in_BP[i][0]/abs(DX_in[i]))
        y = Rtheta_in_BP[i][2]/abs(DX_in[i])
        Rtheta_prime_in_BP[i].append(y+base._dtan_div(-1.0/3.0, beta_S[0+125*i]))
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

    for i in range(num_planes):
        dx_val = DX_in[i] if i < len(DX_in) else 0
        debug_log.debug(f"  TRACE inlet_coords [{row}] plane {i}: DX_in={dx_val:.6f}  x_in[0]={x_in[i][0]:.6f} x_in[-1]={x_in[i][-1]:.6f}  R_in[0]={R_in[i][0]:.6f} R_in[-1]={R_in[i][-1]:.6f}  Rtheta_in[0]={Rtheta_in[i][0]:.6f} Rtheta_in[-1]={Rtheta_in[i][-1]:.6f}  d_in all zero={all(v==0.0 for v in d_in[i])}")

    return x_in, d_in, R_in, Rtheta_in

# calculation of outlet coordinates
def outlet_coordinates(row, n_max_out, l_outlet, num_planes, x_sec, Rtheta_sec, beta_S):
    '''
    Defining coordinates for all stages
    '''
    stage = (row - 1) // 2 + 1
    x0 = base.channel_data[stage]['x0']
    x_values = base.channel_data[stage]['x_values']
    r_values = base.channel_data[stage]['r_values']


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

    if row % 2 != 0:
        k = 3
    elif row % 2 == 0:
        k = 6

    # Full x0 array for channel geometry overview
    debug_log.debug(
        f"DX_out row={row} stage={stage} k={k}: "
        f"x0={[round(v,1) for v in x0]}  "
        f"x0[{k}]={x0[k]:.1f}mm  "
        f"n_max_out={n_max_out}  l_outlet={l_outlet}",
        context="outlet_debug")

    # DIAGNOSTIC: compare blade chord vs channel chord for stators
    if row % 2 == 0:
        _l_S = base.radial_data_S[stage]['l_S']
        debug_log.debug(
            f"  CHORD DIAG row={row}: l_S[10]={_l_S[10]:.3f}mm  "
            f"x0[5]={x0[5]:.1f} x0[6]={x0[6]:.1f}  "
            f"channel_axial={x0[6]-x0[5]:.1f}mm  "
            f"blade_TE_midspan={x0[5]+_l_S[10]:.1f}mm  "
            f"overshoot={x0[5]+_l_S[10]-x0[6]:+.1f}mm",
            context="outlet_debug")
    elif row % 2 != 0:
        _l_R = base.radial_data_R[stage]['l_R']
        debug_log.debug(
            f"  CHORD DIAG row={row}: l_R[10]={_l_R[10]:.3f}mm  "
            f"x0[2]={x0[2]:.1f} x0[3]={x0[3]:.1f}  "
            f"channel_axial={x0[3]-x0[2]:.1f}mm  "
            f"blade_TE_midspan={x0[2]+_l_R[10]:.1f}mm  "
            f"overshoot={x0[2]+_l_R[10]-x0[3]:+.1f}mm",
            context="outlet_debug")

    for i in range(num_planes):
        s = len(x_sec[i])-1

        DX_out.append(x0[k]/1000-x_sec[i][s])
        DX1_out.append(x_sec[i][s]-x_sec[i][s-1])

        d_val = DX_out[-1]
        x_sec_last_mm = x_sec[i][s] * 1000
        status = ""
        if d_val < 0:
            status = " *** NEGATIVE: blade TE past channel exit ***"
        elif d_val < 0.005:
            status = f" *** VERY SMALL: only {d_val*1000:.1f}mm for {n_max_out} outlet points ***"
        debug_log.debug(
            f"DX_out row={row} sec={i}: "
            f"x0[{k}]={x0[k]:.1f}mm  x_sec_TE={x_sec_last_mm:.3f}mm  "
            f"DX_out={d_val*1000:.3f}mm  n_max_out={n_max_out}{status}",
            context="outlet_debug")
        x = Rtheta_sec[i][s]
        Rtheta_out_BP[i].append(x)
        Rtheta_out_BP[i].append(x+base._dtan_div(DX_out[i], beta_S[124+125*i]))
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

    for i in range(num_planes):
        debug_log.debug(f"  TRACE outlet_coords [{row}] plane {i}: DX_out={DX_out[i]:.6f}  x_out[0]={x_out[i][0]:.6f} x_out[-1]={x_out[i][-1]:.6f}  R_out[0]={R_out[i][0]:.6f} R_out[-1]={R_out[i][-1]:.6f}  Rtheta_out[0]={Rtheta_out[i][0]:.6f} Rtheta_out[-1]={Rtheta_out[i][-1]:.6f}")

    return x_out, d_out, R_out, Rtheta_out
