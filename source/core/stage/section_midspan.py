# ------------------------------------------------------------------
# File:    source/core/stage/section_midspan.py
# Author:  Luca De Francesco, Jonas Scholz (based on Marco Wiens)
# Purpose: Midspan (rel_h = 0.5) blade-section calculation + LE/TE center.
# ------------------------------------------------------------------

# Verbatim moves from stage_calculation.py (calculation_of_section_0_5
# :1245-1558, mLE_TE_cntr :1561-1579). Only indentation, the base. prefix
# for module state and translated comments differ. Dead print blocks were
# kept (user decision for this split).

import math

from source.logging import debug_log
from source.core.geometry.bezier import bezier
from source.core.geometry.cubic_spline import cubspline
from source.core.stage.blade_profiles import blade_metal_BP, overall_values
import source.core.stage.stage_calculation as base

Pi = math.pi


def calculation_of_section_0_5(row):
    rel_h = 0.5

    '''
    Defining coordinates for all stages
    '''
    stage_to_calc = (row - 1) // 2 + 1
    x0 = base.channel_data[stage_to_calc]['x0']

    #print(f"  VERIFY calc_0_5 [row={row}, stage={stage}]: x0[2]={x0[2]:.4f}") # Debug to see if stage per stage calls are working

    beta_M_a, beta_M_2, beta_M_3,  beta_M_e, d_l_a, d_l_2, d_l_3, d_l_e, m_star_BP= blade_metal_BP(row)


    '''
    ### Chaning the calling for the calculation of the overall values from scalar first stage values to values that are depending on the current stage.
    For that using the row numbering to calcualte the current stage to be calculated and accesing the correct values of the current stage
    '''
    stage = (row - 1) // 2 + 1
    _l_R = base.radial_data_R[stage]['l_R']
    _l_S = base.radial_data_S[stage]['l_S']
    _z_R = base.radial_data_R[stage].get('z_R', base.z_R)  # fallback to global if not in dict
    _z_S = base.radial_data_S[stage].get('z_S', base.z_S)
    z, s_1D, s_0_5, x_LE, elipse_LE, elipse_TE = overall_values(row, _z_R, _l_R, _l_S)
    debug_log.debug(f"  VERIFY overall_values [row={row}]: s_1D={s_1D:.4f}") # Temporary Debug call


    # Old logic z, s_1D, s_0_5, x_LE, elipse_LE, elipse_TE = overall_values(row, z_R, l_R, l_S)

    LE_TE_fac_1 = [0.0, 2.0, 5.0, 9.0, 15.0, 22.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0]
    LE_TE_fac_2 = LE_TE_fac_1.copy()
    LE_TE_fac_2.reverse()

    k = 125-2*len(LE_TE_fac_1)
    Nulls = [0.0]*k
    LE_TE_fac = LE_TE_fac_1 + Nulls + LE_TE_fac_2

    m_BP = []
    for i in range(4):
        m_BP.append(cubspline(3, rel_h, base.h_H, m_star_BP[i]))

    beta_BP = []
    beta_BP.append(cubspline(3, rel_h, base.h_H, beta_M_e))
    beta_BP.append(cubspline(3, rel_h, base.h_H, beta_M_2))
    beta_BP.append(cubspline(3, rel_h, base.h_H, beta_M_3))
    beta_BP.append(cubspline(3, rel_h, base.h_H, beta_M_a))

    debug_log.debug(f"  calc_section_0_5 [row={row}, rel_h={rel_h}]: beta_BP (interpolated) = {[round(v, 2) for v in beta_BP]}", context="camber_angles")

    d_l_BP =[]
    d_l_BP.append(cubspline(3, rel_h, base.h_H, d_l_e)/200)
    d_l_BP.append(cubspline(3, rel_h, base.h_H, d_l_2)/200)
    d_l_BP.append(cubspline(3, rel_h, base.h_H, d_l_3)/200)
    d_l_BP.append(cubspline(3, rel_h, base.h_H, d_l_a)/200)

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
        R_theta_s_prime.append(R_theta_s_prime[-1]+base._dtan_div(m_prime[i+1]-m_prime[i], (beta_S[i] + beta_S[i+1])/2))

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
            m_prime_u.append(m_prime[i]-d_l[i]*base._seg_unit(R_theta_s_prime[i+1]-R_theta_s_prime[i], m_prime[i+1]-m_prime[i])[0])
            m_prime_l.append(m_prime[i]+d_l[i]*base._seg_unit(R_theta_s_prime[i+1]-R_theta_s_prime[i], m_prime[i+1]-m_prime[i])[0])
        elif i>0 and i<124:
            m_prime_u.append(m_prime[i]-d_l[i]*base._seg_unit(R_theta_s_prime[i+1]-R_theta_s_prime[i-1], m_prime[i+1]-m_prime[i-1])[0])
            m_prime_l.append(m_prime[i]+d_l[i]*base._seg_unit(R_theta_s_prime[i+1]-R_theta_s_prime[i-1], m_prime[i+1]-m_prime[i-1])[0])
        elif i == 124:
            m_prime_u.append(m_prime[i]-d_l[i]*base._seg_unit(R_theta_s_prime[i]-R_theta_s_prime[i-1], m_prime[i]-m_prime[i-1])[0])
            m_prime_l.append(m_prime[i]+d_l[i]*base._seg_unit(R_theta_s_prime[i]-R_theta_s_prime[i-1], m_prime[i]-m_prime[i-1])[0])

    R_theta_s_prime_u, R_theta_s_prime_l = [], []
    for i in range(len(m_prime)):
        if i == 0:
            R_theta_s_prime_u.append(R_theta_s_prime[i]+s_star*d_l[i]*base._seg_unit(R_theta_s_prime[i+1]-R_theta_s_prime[i], m_prime[i+1]-m_prime[i])[1])
            R_theta_s_prime_l.append(R_theta_s_prime[i]-s_star*d_l[i]*base._seg_unit(R_theta_s_prime[i+1]-R_theta_s_prime[i], m_prime[i+1]-m_prime[i])[1])
        elif i>0 and i<124:
            R_theta_s_prime_u.append(R_theta_s_prime[i]+s_star*d_l[i]*base._seg_unit(R_theta_s_prime[i+1]-R_theta_s_prime[i-1], m_prime[i+1]-m_prime[i-1])[1])
            R_theta_s_prime_l.append(R_theta_s_prime[i]-s_star*d_l[i]*base._seg_unit(R_theta_s_prime[i+1]-R_theta_s_prime[i-1], m_prime[i+1]-m_prime[i-1])[1])
        elif i == 124:
            R_theta_s_prime_u.append(R_theta_s_prime[i]+s_star*d_l[i]*base._seg_unit(R_theta_s_prime[i]-R_theta_s_prime[i-1], m_prime[i]-m_prime[i-1])[1])
            R_theta_s_prime_l.append(R_theta_s_prime[i]-s_star*d_l[i]*base._seg_unit(R_theta_s_prime[i]-R_theta_s_prime[i-1], m_prime[i]-m_prime[i-1])[1])

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
            debug_log.debug("blade section 2 selected (upper side)", context="blade_geometry")

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
        debug_log.debug("first coordinates of upper/lower side not equal", context="blade_geometry")

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

    if row % 2 != 0:
        k = 2
    elif row % 2 == 0:
        k = 5

    m_cntr_0_5 = m_prime_cntr*s_0_5/s_star*1000+x0[k]                               #m*cntr

    return  m_cntr_0_5, m_prime_cntr

# calculation of LE and TE coordinates
def mLE_TE_cntr(row):
    '''
    Defining coordinates for all stages
    '''
    stage_to_calc = (row - 1) // 2 + 1
    x0 = base.channel_data[stage_to_calc]['x0']
    debug_log.debug(f"  VERIFY mLE_TE_cntr [row={row}, stage={stage_to_calc}]: x0[2]={x0[2]:.4f}, m_LE_0_5 will be={x0[2 if row%2!=0 else 5]:.4f}") # Same verification for correct implemntation of stage by stage calling

    if row % 2 != 0:
        k = 2
    elif row % 2 == 0:
        k = 5

    m_cntr_0_5, m_prime_cntr = calculation_of_section_0_5(row)

    m_LE_0_5 = x0[k]
    m_TE_0_5 = m_cntr_0_5 + (m_cntr_0_5-m_LE_0_5)*(1-m_prime_cntr)/m_prime_cntr

    return m_LE_0_5, m_TE_0_5, m_cntr_0_5, m_prime_cntr
