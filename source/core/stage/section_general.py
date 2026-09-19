# ------------------------------------------------------------------
# File:    source/core/stage/section_general.py
# Author:  Luca De Francesco (based on Marco Wiens)
# Purpose: General spanwise blade-section calculation (any rel_h).
# ------------------------------------------------------------------

# Verbatim move from stage_calculation.py (calculation_of_section :1582-1943).
# Only indentation, the base. prefix for module state and translated comments
# differ. Dead print/plot blocks were kept (user decision for this split).

import math

from source.logging import debug_log
from source.core.geometry.bezier import bezier
from source.core.geometry.cubic_spline import cubspline
from source.core.geometry.interpolation import intpol
from source.core.stage.blade_profiles import blade_metal_BP, overall_values
from source.core.stage.section_midspan import mLE_TE_cntr
import source.core.stage.stage_calculation as base

Pi = math.pi


def calculation_of_section(rel_h, row):

    '''
    Defining coordinates for all stages
    '''
    stage = (row - 1) // 2 + 1
    r_values = base.channel_data[stage]['r_values']
    m_prime_values = base.channel_data[stage]['m_prime_values']

    m_LE_0_5, m_TE_0_5, m_cntr_0_5, m_prime_cntr = mLE_TE_cntr(row)
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

    debug_log.debug(f"  calc_section [row={row}, rel_h={rel_h:.2f}]: beta_BP (interpolated) = {[round(v, 2) for v in beta_BP]}", context="camber_angles")

    d_l_BP =[]
    d_l_BP.append(cubspline(3, rel_h, base.h_H, d_l_e)/100)
    d_l_BP.append(cubspline(3, rel_h, base.h_H, d_l_2)/100)
    d_l_BP.append(cubspline(3, rel_h, base.h_H, d_l_3)/100)
    d_l_BP.append(cubspline(3, rel_h, base.h_H, d_l_a)/100)


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
        m_prime.append(float(bezier(4, t[i], m_BP)))

    beta_S = []
    for i in range(len(t)):
        beta_S.append(bezier(4, m_prime[i], beta_BP))

    R_theta_s_prime = [0.0]
    for i in range(len(t)-1):
        R_theta_s_prime.append(R_theta_s_prime[-1]+base._dtan_div(m_prime[i+1]-m_prime[i], (beta_S[i] + beta_S[i+1])/2))

    debug_log.debug(f"  calc_section [row={row}, rel_h={rel_h:.2f}]: R_theta_s_prime[0]={R_theta_s_prime[0]:.6f} (LE), R_theta_s_prime[124]={R_theta_s_prime[124]:.6f} (TE)", context="Rtheta_integration")
    debug_log.debug(f"  calc_section [row={row}, rel_h={rel_h:.2f}]: beta_S[0]={beta_S[0]:.2f} deg (LE), beta_S[124]={beta_S[124]:.2f} deg (TE)", context="Rtheta_integration")

    #Chordlength
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
    for i in range(len(m_prime)):
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
    #print(pos_m_prime_min_u, pos_m_prime_max_u)
    #plt.scatter(m_prime_u[pos_m_prime_min_u], R_theta_s_prime_u[pos_m_prime_min_u], s = 50)
    #plt.scatter(m_prime_u[pos_m_prime_max_u], R_theta_s_prime_u[pos_m_prime_max_u], s = 50)

    pos_m_prime_min_l, pos_m_prime_max_l = min_max(m_prime_l)
    #print(pos_m_prime_min_l, pos_m_prime_max_l)
    #plt.scatter(m_prime_l[pos_m_prime_min_l], R_theta_s_prime_l[pos_m_prime_min_l], s = 50)
    #plt.scatter(m_prime_l[pos_m_prime_max_l], R_theta_s_prime_l[pos_m_prime_max_l], s = 50)

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

    if m_prime_l[0]!=m_prime_u[0]:
        debug_log.debug("first coordinates of upper/lower side not equal (stator)", context="blade_geometry")

    # activate for plotting of blade geometry
    """
    plt.scatter(m_prime_u, R_theta_s_prime_u, s = 3)
    plt.plot(m_prime_u, R_theta_s_prime_u)
    plt.scatter(m_prime, R_theta_s_prime, s = 3)
    plt.plot(m_prime_l, R_theta_s_prime_l)
    plt.scatter(m_prime_l, R_theta_s_prime_l, s = 3)
    plt.plot(m_prime, R_theta_s_prime)
    plt.xlabel("m' [-]")
    plt.ylabel("Rθ [-]")
    plt.xlim(-0.005,0.015)
    plt.ylim(-0.01,0.0025)
    plt.axis('equal')
    plt.show()
    """

    dif_list_len_u = len(m_prime_u)-125

    if dif_list_len_u > 0:
        for i in range(dif_list_len_u):
            k = 20+i*5
            del m_prime_u[k]
            del R_theta_s_prime_u[k]

    elif dif_list_len_u < 0:
        for i in range(abs(dif_list_len_u)):
            k = 20+i*5
            new_m_value = m_prime_u[k]+(m_prime_u[k+1]-m_prime_u[k])/2
            m_prime_u.insert(k+1, new_m_value)
            new_Rtheta_value = R_theta_s_prime_u[k]+(R_theta_s_prime_u[k+1]-R_theta_s_prime_u[k])/2
            R_theta_s_prime_u.insert(k+1, new_Rtheta_value)

    dif_list_len_l = len(m_prime_l)-125

    if dif_list_len_l > 0:
        for i in range(dif_list_len_l):
            k = 20+i*5
            del m_prime_l[k]
            del R_theta_s_prime_l[k]

    elif dif_list_len_l < 0:
        for i in range(abs(dif_list_len_l)):
            k = 20+i*5
            new_m_value = m_prime_l[k]+(m_prime_l[k+1]-m_prime_l[k])/2
            m_prime_l.insert(k+1, new_m_value)
            new_Rtheta_value = R_theta_s_prime_l[k]+(R_theta_s_prime_l[k+1]-R_theta_s_prime_l[k])/2
            R_theta_s_prime_l.insert(k+1, new_Rtheta_value)

    # calculation of the second blade row
    m_LE = m_cntr_0_5-(m_cntr_0_5-m_LE_0_5)*(1+cubspline(3, rel_h, base.h_H, x_LE))
    m_TE = m_cntr_0_5+(m_cntr_0_5-m_LE)*(1-m_prime_cntr)/m_prime_cntr

    s = (m_TE-m_LE)*s_star

    R_LE = intpol(m_LE, len(m_prime_values[0]), m_prime_values[0], r_values[0]) + 0.5*(intpol(m_LE,len(m_prime_values[4]), m_prime_values[4], r_values[4]) -intpol(m_LE, len(m_prime_values[0]), m_prime_values[0], r_values[0]))
    t_s_s_star = s_star*2*Pi*R_LE/(z[0]*s)
    m_star, m_star_u, m_star_l, R_theta_s_star, R_theta_s_star_u, R_theta_s_star_l = [], [], [], [], [], []
    for i in range(len(m_prime)):
        m_star.append((m_prime[i]-m_prime_cntr)*s/s_star+m_cntr_0_5)
        m_star_u.append((m_prime_u[i]-m_prime[i])*s/s_star+m_star[i])
        m_star_l.append((m_prime_l[i]-m_prime[i])*s/s_star+m_star[i])
        R_theta_s_star.append((R_theta_s_prime[i]-Rtet_prime_cntr)*s/s_star)
        R_theta_s_star_u.append((R_theta_s_prime_u[i]-Rtet_prime_cntr)*s/s_star)
        R_theta_s_star_l.append((R_theta_s_prime_l[i]-Rtet_prime_cntr)*s/s_star)

    chord = math.sqrt((m_TE-m_LE)**2+(R_theta_s_star[0]-R_theta_s_star[-1])**2)

    R_theta_s_prime_2, R_theta_s_prime_2_u, R_theta_s_prime_2_l = [], [], []
    for i in range(len(R_theta_s_prime_u)):
        R_theta_s_prime_2.append(R_theta_s_prime[i]-t_s_s_star)
        R_theta_s_prime_2_u.append(R_theta_s_prime_u[i]-t_s_s_star)
        R_theta_s_prime_2_l.append(R_theta_s_prime_l[i]-t_s_s_star)

    R_theta_s_star_2, R_theta_s_star_u_2, R_theta_s_star_l_2 = [], [], []
    for i in range(len(m_prime)):
        R_theta_s_star_2.append((R_theta_s_prime_2[i]-Rtet_prime_cntr)*s/s_star)
        R_theta_s_star_u_2.append((R_theta_s_prime_2_u[i]-Rtet_prime_cntr)*s/s_star)
        R_theta_s_star_l_2.append((R_theta_s_prime_2_l[i]-Rtet_prime_cntr)*s/s_star)

    return chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2
