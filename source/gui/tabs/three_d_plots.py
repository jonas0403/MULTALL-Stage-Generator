# ------------------------------------------------------------------
# File:    source/gui/tabs/three_d_plots.py
# Author:  Jonas Scholz, Luca De Francesco
# Purpose: Blade section, angle and thickness plots.
# ------------------------------------------------------------------

import matplotlib.pyplot as plt
from tkinter import messagebox
from source.io.paths import JSON_PATH as json_path
from source.core.stage.section_general import calculation_of_section


def show_plots_section_rotor(self):
    if not self._bezier_data_ready():
        messagebox.showwarning("Missing data",
            "No Bezier profile data found.\n"
            "Please click 'Create Default Profile(s)' first.")
        return
    farben = ["pink", "blue", "green", "red", "black"]
    for stage in range(1, self.stages_to_calc + 1):
        row = 2 * stage - 1          # rotor row for this stage
        for k, h_val in enumerate([0.0, 0.2, 0.5, 0.8, 1.0]):
            _, _, _, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, *_ = \
                calculation_of_section(h_val, row)
            label = f"Stage {stage} – {int(h_val*100)}%" if k == 2 else None
            plt.plot(m_star_u, R_theta_s_star_u, color=farben[k], label=label)
            plt.plot(m_star_l, R_theta_s_star_l, color=farben[k])
    plt.xlabel("x [mm]")
    plt.ylabel("Rθ [mm]")
    plt.title("Rotor Geometry – all stages")
    plt.legend()
    plt.axis('equal')
    plt.show()

def show_plots_section_stator(self):
    if not self._bezier_data_ready():
        messagebox.showwarning("Missing data",
            "No Bezier profile data found.\n"
            "Please click 'Create Default Profile(s)' first.")
        return
    farben = ["pink", "blue", "green", "red", "black"]
    for stage in range(1, self.stages_to_calc + 1):
        row = 2 * stage              # stator row for this stage
        for k, h_val in enumerate([0.0, 0.2, 0.5, 0.8, 1.0]):
            _, _, _, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, *_ = \
                calculation_of_section(h_val, row)
            label = f"Stage {stage} – {int(h_val*100)}%" if k == 2 else None
            plt.plot(m_star_u, R_theta_s_star_u, color=farben[k], label=label)
            plt.plot(m_star_l, R_theta_s_star_l, color=farben[k])
    plt.xlabel("x [mm]")
    plt.ylabel("Rθ [mm]")
    plt.title("Stator Geometry – all stages")
    plt.legend()
    plt.axis('equal')
    plt.show()

# ── angle-distribution plots ──────────────────────────────────────────────────
def show_plots_angle_rotor(self):
    if not self._bezier_data_ready():
        messagebox.showwarning("Missing data",
            "No Bezier profile data found.\n"
            "Please click 'Create Default Profile(s)' first.")
        return
    farben = ["pink", "blue", "green", "red", "black"]
    for stage in range(1, self.stages_to_calc + 1):
        row = 2 * stage - 1
        for k, h_val in enumerate([0.0, 0.2, 0.5, 0.8, 1.0]):
            _, _, _, _, _, _, _, m_prime, _, _, m_BP, beta_S, beta_BP, *_ = \
                calculation_of_section(h_val, row)
            label = f"Stage {stage} – {int(h_val*100)}%" if k == 2 else None
            plt.plot(m_prime, beta_S, color=farben[k], label=label)
            plt.scatter(m_BP, beta_BP, color=farben[k])
    plt.xlabel("x/s [%]")
    plt.ylabel("Blade angle [°]")
    plt.title("Blade Angle Distribution – Rotor, all stages")
    plt.legend()
    plt.show()

def show_plots_angle_stator(self):
    if not self._bezier_data_ready():
        messagebox.showwarning("Missing data",
            "No Bezier profile data found.\n"
            "Please click 'Create Default Profile(s)' first.")
        return
    farben = ["pink", "blue", "green", "red", "black"]
    for stage in range(1, self.stages_to_calc + 1):
        row = 2 * stage
        for k, h_val in enumerate([0.0, 0.2, 0.5, 0.8, 1.0]):
            _, _, _, _, _, _, _, m_prime, _, _, m_BP, beta_S, beta_BP, *_ = \
                calculation_of_section(h_val, row)
            label = f"Stage {stage} – {int(h_val*100)}%" if k == 2 else None
            plt.plot(m_prime, beta_S, color=farben[k], label=label)
            plt.scatter(m_BP, beta_BP, color=farben[k])
    plt.xlabel("x/s [%]")
    plt.ylabel("Blade angle [°]")
    plt.title("Blade Angle Distribution – Stator, all stages")
    plt.legend()
    plt.show()

# ── thickness-distribution plots ──────────────────────────────────────────────
def show_plots_thickness_rotor(self):
    if not self._bezier_data_ready():
        messagebox.showwarning("Missing data",
            "No Bezier profile data found.\n"
            "Please click 'Create Default Profile(s)' first.")
        return
    farben = ["pink", "blue", "green", "red", "black"]
    for stage in range(1, self.stages_to_calc + 1):
        row = 2 * stage - 1
        for k, h_val in enumerate([0.0, 0.2, 0.5, 0.8, 1.0]):
            _, _, _, _, _, _, _, m_prime, _, _, m_BP, _, _, d_l, d_l_BP, *_ = \
                calculation_of_section(h_val, row)
            label = f"Stage {stage} – {int(h_val*100)}%" if k == 2 else None
            plt.plot(m_prime, d_l, color=farben[k], label=label)
            plt.scatter(m_BP, d_l_BP, color=farben[k])
    plt.xlabel("x/s [%]")
    plt.ylabel("Thickness d [mm]")
    plt.title("Thickness Distribution – Rotor, all stages")
    plt.legend()
    plt.show()

def show_plots_thickness_stator(self):
    if not self._bezier_data_ready():
        messagebox.showwarning("Missing data",
            "No Bezier profile data found.\n"
            "Please click 'Create Default Profile(s)' first.")
        return
    farben = ["pink", "blue", "green", "red", "black"]
    for stage in range(1, self.stages_to_calc + 1):
        row = 2 * stage
        for k, h_val in enumerate([0.0, 0.2, 0.5, 0.8, 1.0]):
            _, _, _, _, _, _, _, m_prime, _, _, m_BP, _, _, d_l, d_l_BP, *_ = \
                calculation_of_section(h_val, row)
            label = f"Stage {stage} – {int(h_val*100)}%" if k == 2 else None
            plt.plot(m_prime, d_l, color=farben[k], label=label)
            plt.scatter(m_BP, d_l_BP, color=farben[k])
    plt.xlabel("x/s [%]")
    plt.ylabel("Thickness d [mm]")
    plt.title("Thickness Distribution – Stator, all stages")
    plt.legend()
    plt.show()        
