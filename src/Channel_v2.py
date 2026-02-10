# Author: Marco Wiens
# Version: 12.12.2024
# Channel
# Programm for calculation of channel geometry of the first stage


import math 
import numpy as np
import matplotlib.pyplot as plt
from Fixed_radii_Meanline_GUI_v4 import meanline 
from Cubspline_function import cubspline

Pi = math.pi


# values from meanline calculations
mflow, n, kappa, R, cp, i_st, T_t1, T_t2, T_t3,  T_1, T_2, T_3, p_1, p_2, p_3, p_t1, p_t2, p_t3, D_S1, D_S2, D_S3, D_H1, D_H2, D_H3, D_m1, D_m2, D_m3, b1, b2, b3, cu1, cu2, cu3, u1, u2, u3, cm1, cm2, cm3, delta_h_t, l_R, l_S, l_R_t_R, l_S_t_S, d_R_l_R, d_S_l_S, incidence_R, incidence_S, z_R, z_S, beta_blade_1, beta_blade_2, alpha_blade_2, alpha_blade_3, TPR_M, eta_sC_tt_M, eta_pC_tt_M, fixed_radius_type = meanline(GUI_On = 0)

#To generate a plot of the channel, set the value of channelPlot to 1.
channelPlot = 1



def channel(h_H, stage, inlet_area, inlet_dist, outlet_area, outlet_dist, fixed_radius_type):
    # N: Nabe = Hub 
    # G: Gehäuse = Shroud

    # Adjust stage index
    
    stg = stage - 1

    print(f"{l_R}")

    # factors for space between the rows    
    Rotor = [0.4, 0.15, 0.2]
    Stator = [0.3, 0.15, 0.4]
    
    t0 = np.arange(-1.0, 8.0, 1.0)
    print(f"alkskashdk {inlet_dist}")

    x0 = np.full_like(t0, 0)
    x0[1] = 0
    x0[2] = round(Rotor[0]*l_R[stg], 1)
    if stage == 1:
        x0[0] = -inlet_dist * l_R[0]
    else:
        x0[0] = -1*round((x0[2]-x0[1])/(1-Rotor[0]), 0)
    x0[3] = x0[2] + round((1+Rotor[1]) * l_R[stg] *(math.sin((beta_blade_1[stg]+beta_blade_2[stg])/(2*180)*Pi)),1)
    x0[4] = x0[3] + round(Rotor[2]*l_R[stg],1)
    x0[5] = x0[4] + round((Stator[0]+Stator[1]/2)*l_S[stg], 1)
    x0[6] = x0[5] + round((1+Stator[1]) * l_S[stg] *(math.sin((alpha_blade_2[stg]+alpha_blade_3[stg])/(2*180)*Pi)),1)
    x0[7] = x0[6] + round((Stator[2]+Stator[1]/2)*l_S[stg], 1)
    if stage == len(D_m1):
        x0[8] = x0[7] + outlet_dist * l_S[8]
    else:
        x0[8] = x0[7] + round((x0[7]-x0[6])/(1-Stator[2]))
    
    t1 = np.arange(-1, 1.05, 0.05)
    t2 = np.arange(1.025, 2.025, 0.025)
    t3 = np.arange(2.05, 4.05, 0.05)
    t4 = np.arange(4.025, 5.025, 0.025)
    t5 = np.arange(5.05, 7.05, 0.05)
    t = np.concatenate((t1, t2, t3, t4, t5))
        
    # radii of shroud and hub old:
    r0_N = np.full_like(x0, 0)
    r0_N[1] = round(D_H1[stg]/2, 1)
    r0_N[2] = r0_N[1] + round((D_H2[stg]-D_H1[stg])/2*(x0[2]-x0[1])/(x0[4]-x0[1]), 1)
    r0_N[0] = round((r0_N[2]-r0_N[1])/(x0[2]-x0[1])*x0[0]+r0_N[1], 1)
    r0_N[3] = r0_N[1]+ round((D_H2[stg]-D_H1[stg])/2*(x0[3]-x0[1])/(x0[4]-x0[1]), 1)
    r0_N[5] = round(D_H2[stg]/2, 1) + round((D_H3[stg]-D_H2[stg])/2*(x0[5]-x0[4])/(x0[7]-x0[4]), 1)
    r0_N[4] = round((D_H2[stg]/2 + (r0_N[3]+(r0_N[5]-r0_N[3])*(x0[4]-x0[3])/(x0[5]-x0[3])))/2 ,1)
    r0_N[6] = round(D_H2[stg]/2, 1) + round((D_H3[stg]-D_H2[stg])/2*(x0[6]-x0[4])/(x0[7]-x0[4]), 1)
    r0_N[7] = round(D_H3[stg]/2, 1)
    r0_N[8] = round((r0_N[7] - r0_N[6])/(x0[7] - x0[6])*(x0[8] - x0[7]) + r0_N[7], 1)
      

    r0_G = np.full_like(x0, 0)
    r0_G[1] = round(D_S1[stg]/2, 1)
    r0_G[2] = r0_G[1] + round((D_S2[stg]-D_S1[stg])/2*(x0[2]-x0[1])/(x0[4]-x0[1]), 1)
    r0_G[0] = round((r0_G[2]-r0_G[1])/(x0[2]-x0[1])*x0[0]+r0_G[1], 1)
    r0_G[3] = r0_G[1]+ round((D_S2[stg]-D_S1[stg])/2*(x0[3]-x0[1])/(x0[4]-x0[1]), 1)
    r0_G[5] = round(D_S2[stg]/2, 1) + round((D_S3[stg]-D_S2[stg])/2*(x0[5]-x0[4])/(x0[7]-x0[4]), 1)
    r0_G[4] = round((D_S2[stg]/2 + (r0_G[3]+(r0_G[5]-r0_G[3])*(x0[4]-x0[3])/(x0[5]-x0[3])))/2 ,1)
    r0_G[6] = round(D_S2[stg]/2, 1) + round((D_S3[stg]-D_S2[stg])/2*(x0[6]-x0[4])/(x0[7]-x0[4]), 1)
    r0_G[7] = round(D_S3[stg]/2, 1)
    r0_G[8] = round((r0_G[7] - r0_G[6])/(x0[7] - x0[6])*(x0[8] - x0[7]) + r0_G[7], 1)   
    
    
    if stage == 1:
        # Einlass Geometrie
        r_S1_in = D_S1[0] / 2
        r_H1_in = D_H1[0] / 2
        old_area = math.pi * (r_S1_in**2 - r_H1_in**2)
        new_area = old_area * inlet_area
        
        if fixed_radius_type == 'mean':
            delta_r = (new_area - old_area) / (2 * math.pi * (r_H1_in + r_S1_in))
            
            r0_N[0] = (r_H1_in) - delta_r
            r0_G[0] = (r_S1_in) + delta_r
            
        elif fixed_radius_type == 'shroud':
            
            if r_S1_in**2 - new_area / math.pi <= 0:
                raise ValueError("The calculated expanded area is too large for the given outer radius, resulting in an impossible inner radius. Please check your are expansion factor and dimensions")
            else:
                r0_N[0] = math.sqrt(r_S1_in**2 - new_area / math.pi)
                
        elif fixed_radius_type == 'hub':
            r0_G[0] = math.sqrt(r_H1_in**2 + new_area / math.pi)
    elif stage == len(D_H1):
        # Auslass Geometry
        r_S3_in = D_S3[8] / 2
        r_H3_in = D_H3[8] / 2
        old_area = math.pi * (r_S3_in**2 - r_H3_in**2)
        new_area = old_area * inlet_area
        
        if fixed_radius_type == 'mean':
            delta_r = (new_area - old_area) / (2 * math.pi * (r_H3_in + r_S3_in))
            
            r0_N[8] = (r_H3_in) - delta_r
            r0_G[8] = (r_S3_in) + delta_r        
        elif fixed_radius_type == 'shroud':
            
            if r_S3_in**2 - new_area / math.pi <= 0:
                raise ValueError("The calculated expanded area is too large for the given outer radius, resulting in an impossible inner radius. Please check your are expansion factor and dimensions")
            else:
                r0_N[8] = math.sqrt(r_S3_in**2 - new_area / math.pi)
        elif fixed_radius_type == 'hub':
            r0_G[8] = math.sqrt(r_H3_in**2 + new_area / math.pi)
                   
  

    for i, element in enumerate(r0_G):
        r0_G[i] = r0_G[i]*1.08 
    
    for i, element in enumerate(r0_N):
        r0_N[i] = r0_N[i]*0.95 

    #Hub and Shroud
    x_N = []
    for i in range(len(t)):
        s1 = (x0[1]-x0[0])/(t0[1]-t0[0])
        s2 = (x0[8]-x0[7])/(t0[8]-t0[7])
        if t[i] < 0.0:
            x_N.append(s1*t[i]+x0[1])
        elif t[i] >= 0 and t[i] <=6:
            x_N.append(cubspline(3,t[i], t0[1:8], x0[1:8]))           
        elif t[i] > 6:
            x_N.append(s2*(t[i]-t0[8]) + x0[8])

    x_G = x_N 

    r_N = []
    for i in range(len(t)):
        s1 = (r0_N[1]-r0_N[0])/(t0[1]-t0[0])
        s2 = (r0_N[8]-r0_N[7])/(t0[8]-t0[7])
        if t[i] < 0.0:
            r_N.append(s1*t[i]+r0_N[1])
        elif t[i] >= 0 and t[i] <=6:
            r_N.append(cubspline(3,t[i], t0[1:8], r0_N[1:8]))           
        elif t[i] > 6:
            r_N.append(s2*(t[i]-t0[8]) + r0_N[8])

    r_G = []
    for i in range(len(t)):
        s1 = (r0_G[1]-r0_G[0])/(t0[1]-t0[0])
        s2 = (r0_G[8]-r0_G[7])/(t0[8]-t0[7])
        if t[i] < 0.0:
            r_G.append(s1*t[i]+r0_G[1])
        elif t[i] >= 0 and t[i] <=6:
            r_G.append(cubspline(3,t[i], t0[1:8], r0_G[1:8]))           
        elif t[i] > 6:
            r_G.append(s2*(t[i]-t0[8]) + r0_G[8])

    R_G = []
    R_N = []
    for i in range(len(t)):
        R_G.append(-r_G[i])
        R_N.append(-r_N[i])

    channelHeight = []
    for i in range(9):
        channelHeight.append(r0_G[i] - r0_N[i]) 

    # for plotting of channel geometry, please activate
    if channelPlot == 1:
        plt.scatter(x0, r0_N)

        plt.scatter(x0, channelHeight)
        plt.plot(x0, channelHeight)
        
        plt.plot(x_N, r_N, label = 'Hub')
        #plt.plot(x_N, R_N)
        plt.scatter(x0, r0_G)
        plt.plot(x_G, r_G, label = 'Shroud')
        #plt.plot(x_G, R_G)
        plt.axis('equal')
        plt.legend()
        plt.ylabel('radii [mm]')
        plt.xlabel('axial length [mm]')

        for i in range(len(x0)):
            plt.text(round(x0[i],1), round(channelHeight[i],1), f"({round(channelHeight[i],1)})", fontsize=10, ha='right', va='bottom') 
            
        plt.show()
    

    m_prime_N = []
    m_prime_N.append(0.0)
    for i in range(len(t)-1):
        if t[i] < 0.0: 
            m_neu = m_prime_N[0] - math.sqrt((x_N[i+1]-x_N[i])**2 + (r_N[i+1]-r_N[i])**2)
            m_prime_N.insert(0,m_neu)
        elif t[i] > 0.0:
            m_neu = m_prime_N[i] + math.sqrt((x_N[i+1]-x_N[i])**2 + (r_N[i+1]-r_N[i])**2)
            m_prime_N.append(m_neu)

    m_prime_G = []
    m_prime_G.append(0.0)
    for i in range(len(t)-1):
        if t[i] < 0.0: 
            m_neu = m_prime_G[0]-math.sqrt((x_G[i+1]-x_G[i])**2+(r_G[i+1]-r_G[i])**2)
            m_prime_G.insert(0,m_neu)
        elif t[i] > 0.0:
            m_neu = m_prime_G[i] + math.sqrt((x_G[i+1]-x_G[i])**2+(r_G[i+1]-r_G[i])**2)
            m_prime_G.append(m_neu)
    
    x_values, r_values, m_prime_values = [], [], []
    for _ in range(len(h_H)):
        x_values.append([])
        r_values.append([])
        m_prime_values.append([])

    for k, element in enumerate(h_H):
        for i in range(len(t)):
            x_values[k].append(x_N[i]+element*(x_G[i]-x_N[i]))
            r_values[k].append(r_N[i]+element*(r_G[i]-r_N[i]))
            m_prime_values[k].append(m_prime_N[i]+element*(m_prime_G[i]-m_prime_N[i]))
    
    #print(r0_N)
    return x_values, r_values, m_prime_values, x0

if __name__ == "__main__":
    h_H = [0.0, 0.2, 0.5, 0.8, 1.0]
    x_values, r_values, m_prime_values, x0 = channel(h_H,stage=1)
    #print(x0)
    
