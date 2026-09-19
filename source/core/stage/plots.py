# ------------------------------------------------------------------
# File:    source/core/stage/plots.py
# Author:  Jonas Scholz, Luca De Francesco (based on Marco Wiens)
# Purpose: Uncalled blade-geometry plot helpers (future GUI integration).
# ------------------------------------------------------------------

# Verbatim moves from stage_calculation.py (plot_temp_alpha_beta :76-101,
# xRtheta_plot :2450-2460). Only indentation, the base. prefix for module
# state and translated comments differ. NOTE (user, 2026-09-19): integrate
# these into the GUI later; kept uncalled for now.

import matplotlib.pyplot as plt
import numpy as np

import source.core.stage.stage_calculation as base


def plot_temp_alpha_beta(T_Plot, beta_R_Plot, alpha_S_Plot):
    #Temp plot
    if T_Plot == 1:
        plt.plot(base.T_S_out, base.h_rel, label = "T_out'")
        plt.plot(base.T_R_in, base.h_rel, label = 'T_in"')
        plt.plot(base.T_R_out, base.h_rel, label = "T_out'' = T_in'")
        plt.legend()
        plt.show()

    #Beta plot
    if beta_R_Plot == 1:
        plt.plot(base.beta_blade_R_in, base.h_rel, label = "beta_blade_R_in'")
        plt.plot(base.beta_blade_R_out, base.h_rel, label = "beta_blade_R_out'")
        plt.plot(base.beta_R_in, base.h_rel, label = "beta_R_in'")
        plt.plot(base.beta_R_out, base.h_rel, label = "beta_R_out''")
        plt.legend()
        plt.show()

    # Alpha plot
    if alpha_S_Plot == 1:
        plt.plot(base.alpha_S_in, base.h_rel, label = "alpha_S_in'")
        plt.plot(base.alpha_S_out, base.h_rel, label = "alpha_S_out'")
        plt.plot(base.beta_blade_S_in, base.h_rel, label = "beta_blade_S_in''")
        plt.plot(base.beta_blade_S_out, base.h_rel, label = "beta_blade_S_out''")
        plt.legend()
        plt.show()


def xRtheta_plot(Rtheta_new, R_new, x_new):
    fig = plt.figure(figsize=(10, 8))
    theta_radians = np.deg2rad(Rtheta_new)
    y_values = [r * np.cos(theta) for r, theta in zip(R_new, Rtheta_new)]
    z_values = [r * np.sin(theta) for r, theta in zip(R_new, Rtheta_new)]
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x_new, y_values, z_values, c='r', marker='o')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()
