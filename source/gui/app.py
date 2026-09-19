# ------------------------------------------------------------------
# File:    source/gui/app.py
# Author:  Jonas Scholz, Luca De Francesco
# Purpose: Main GUI shell: lifecycle, rendering and per-tab delegation.
# ------------------------------------------------------------------

import json
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk

from source.io.paths import JSON_PATH as json_path, STATIC_FOLDER as static_folder, REPO_ROOT as current_dir
from source.gui.widgets.tooltip import Tooltip
from source.logging import debug_log
from source.gui.tabs import (
    zero_d,
    one_d,
    three_d,
    three_d_bleed,
    three_d_profiles,
    three_d_plots,
    grid as grid_tab,
    other,
)

# [REFACTOR Session 17] Kept here at module level for now (parity, Phase A/B).
# Marked obsolete: dead code, was never wired into the GUI.
def read_initial_values(filename):
    global p_t_in, T_t_in, mflow, R, cp, TPR
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('p_t_in = '):
                p_t_in = float(line[9:])
            elif line.startswith('T_t_in = '):
                T_t_in = float(line[9:])
            elif line.startswith('mflow = '):
                mflow = float(line[8:])
            elif line.startswith('R = '):
                R = float(line[4:])
            elif line.startswith('cp = '):
                cp = float(line[5:])
            elif line.startswith('TPR = '):
                TPR = float(line[6:])


class CompressorGui:
    '''
    Load all data once and save into different class data dicts
    Data gets prepopulated with rendering of the gui
    '''
    def loading_prepopulated_data(self):
        with open(json_path, 'r') as file:
            data = json.load(file)

            self.prepop_thermo_data = data['Thermodynamic_input_data']
            self.prepop_meanline_input_data = data['Meanline_input_data']
            self.prepop_diameter_data = data['Diameter_data']
            # self.prepop_bezier_point_stator = data['Bezier_point_data']['stator']
            # self.prepop_bezier_point_rotor = data['Bezier_point_data']['rotor']
            self.prepop_metadata = data['Metadata']
            self.prepop_grid_data = data['Grid_data']
            self.prepop_bleed_air_data = data['Bleed_air_data']
            self.prepop_intake_outtake_area_data = data['Intake_Outtake_area']

        bezier_store = data.get('Bezier_point_data', {})

        # Support both new per-stage keys (rotor_stage_1 …) and the old single keys
        if 'rotor_stage_1' in bezier_store:
            self.prepop_bezier_point_rotor  = bezier_store['rotor_stage_1']
            self.prepop_bezier_point_stator = bezier_store.get('stator_stage_1', {})
        else:
            # Legacy fallback – JSON was written before the multi-stage patch
            self.prepop_bezier_point_rotor  = bezier_store.get('rotor',  {})
            self.prepop_bezier_point_stator = bezier_store.get('stator', {})

    # ------------------------------------------------------------------
    # 0D-Settings tab -> tabs/zero_d.py
    # ------------------------------------------------------------------
    def zeroD_tab(self, window):
        return zero_d.build_zero_d_tab(self, window)

    # ------------------------------------------------------------------
    # 1D-Settings tab -> tabs/one_d.py  (still >500 lines: the nested
    # diameter_gui class & run_diameter_gui extraction is a later pass)
    # ------------------------------------------------------------------
    def oneD_tab(self, parent_frame, i_st_val):
        return one_d.build_one_d_tab(self, parent_frame, i_st_val)

    # ------------------------------------------------------------------
    # 3D-Settings tab -> tabs/three_d{, _bleed, _profiles, _plots}.py
    # ------------------------------------------------------------------
    def threeD_tab(self, parent_frame):
        return three_d.build_three_d_tab(self, parent_frame)

    def setup_inlet_outlet_tab(self):
        return three_d.setup_inlet_outlet_tab(self)

    def browse_output_folder(self):
        return three_d.browse_output_folder(self)

    def load_bleed_air_and_area_change(self):
        return three_d_bleed.load_bleed_air_and_area_change(self)

    def update_bleed_air_display(self, *args):
        return three_d_bleed.update_bleed_air_display(self, *args)

    def refresh_bleed_widgets_from_data(self):
        return three_d_bleed.refresh_bleed_widgets_from_data(self)

    def create_bleed_input_widget(self):
        return three_d_bleed.create_bleed_input_widget(self)

    def update_patches(self, blade_type):
        return three_d_bleed.update_patches(self, blade_type)

    def save_and_initialize_3D_tab(self):
        return three_d_bleed.save_and_initialize_3D_tab(self)

    def create_profiles_and_update_gui(self):
        return three_d_profiles.create_profiles_and_update_gui(self)

    def setup_parameters_tab(self):
        return three_d_profiles.setup_parameters_tab(self)

    def export_bezier_to_txt(self):
        return three_d_profiles.export_bezier_to_txt(self)

    def setup_plot_options_tab(self):
        return three_d_profiles.setup_plot_options_tab(self)

    def import_bezier_from_txt(self, blade_type):
        return three_d_profiles.import_bezier_from_txt(self, blade_type)

    def open_specification_window(self):
        return three_d_profiles.open_specification_window(self)

    def load_rotor_settings(self):
        return three_d_profiles.load_rotor_settings(self)

    def load_stator_settings(self):
        return three_d_profiles.load_stator_settings(self)

    def save_settings(self):
        return three_d_profiles.save_settings(self)

    def _bezier_data_ready(self) -> bool:
        return three_d_profiles._bezier_data_ready(self)

    def show_plots_section_rotor(self):
        return three_d_plots.show_plots_section_rotor(self)

    def show_plots_section_stator(self):
        return three_d_plots.show_plots_section_stator(self)

    def show_plots_angle_rotor(self):
        return three_d_plots.show_plots_angle_rotor(self)

    def show_plots_angle_stator(self):
        return three_d_plots.show_plots_angle_stator(self)

    def show_plots_thickness_rotor(self):
        return three_d_plots.show_plots_thickness_rotor(self)

    def show_plots_thickness_stator(self):
        return three_d_plots.show_plots_thickness_stator(self)

    # ------------------------------------------------------------------
    # Grid-Settings tab -> tabs/grid.py
    # ------------------------------------------------------------------
    def grid_definition_tab(self, parent_frame):
        return grid_tab.build_grid_tab(self, parent_frame)

    # ------------------------------------------------------------------
    # Other-Settings tab + generators -> tabs/other.py
    # ------------------------------------------------------------------
    def other_settings_tab(self, parent_frame):
        return other.build_other_tab(self, parent_frame)

    def _toggle_dat_inputs(self):
        return other._toggle_dat_inputs(self)

    def _find_source_dat_file(self, output_folder):
        return other._find_source_dat_file(self, output_folder)

    def _generate_dat_files(self, target_folder=None):
        return other._generate_dat_files(self, target_folder)

    def _create_run_batch(self, target_folder=None, exclude_source=None, results_dir=None):
        return other._create_run_batch(self, target_folder, exclude_source, results_dir)

    def _generate_all_and_exit(self):
        return other._generate_all_and_exit(self)

    def _refresh_history_list(self):
        return other._refresh_history_list(self)

    def _import_history_selection(self):
        return other._import_history_selection(self)

    def _import_history_browse(self):
        return other._import_history_browse(self)

    # ------------------------------------------------------------------
    # Multall start / startup dialog / main loop (kept inline)
    # ------------------------------------------------------------------
    def start_Multall(self):
        popup_multall = tk.Toplevel()
        popup_multall.title("Do you want to start Multall?")
        popup_multall.geometry("300x150")
        tk.Label(popup_multall, text="Do you want to start Multall with the current settings?", wraplength=280).pack(pady=20)

        def start_multall_and_exit():
            status_msg = "Starting Multall..."
            print(status_msg)
            debug_log.debug(status_msg, context="multall")

            # [REFACTOR Session 17g] solver module now lives in source/: launch it as a
            # module from the repo root so its absolute source.* imports resolve.
            _repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            subprocess.Popen([sys.executable, "-m", "source.solver_run"], cwd=_repo_root)

            popup_multall.destroy()
            self.root.destroy()
            sys.exit()

        def cancel_and_exit():
            status_msg = "Multall start cancelled."
            print(status_msg)
            debug_log.debug(status_msg, context="multall")
            popup_multall.destroy()
            self.root.destroy()
            sys.exit()

        ttk.Button(popup_multall, text="No", command=cancel_and_exit, style="danger.TButton", width=10).pack(side="left", padx=20, pady=10)
        ttk.Button(popup_multall, text="Yes", command=start_multall_and_exit, style="success.TButton", width=10).pack(side="right", padx=20, pady=10)

    def show_startup_dialog(self):
        dialog = tk.Tk()
        dialog.title("Startup")
        dialog.resizable(True, True)

        # Configure grid weights so content stays centered/fills space
        dialog.columnconfigure(0, weight=1)
        dialog.columnconfigure(1, weight=1)
        for i in range(4): dialog.rowconfigure(i, weight=1)

        # Asks for the amount of stages
        ttk.Label(dialog, text="Number of Stages:").grid(row=0, column=0, padx=10, pady=10, sticky='w')

        stage_var = tk.IntVar(value=3)
        stage_entry = ttk.Entry(dialog, textvariable=stage_var, width=5)
        stage_entry.grid(row=0, column=1, padx=10, pady=10)
        stage_entry.config(state='readonly')

        # Asks for the amount of stages to be calculated
        ttk.Label(dialog, text="Stages to Calculate:").grid(row=1, column=0, padx=10, pady=10, sticky='w')

        stages_to_calc_var = tk.IntVar(value=3)
        stages_to_calc_entry = ttk.Entry(dialog, textvariable=stages_to_calc_var, width=5)
        stages_to_calc_entry.grid(row=1, column=1, padx=10, pady=10)

        # error label incase of stages_to_calc_entry > stage_entry
        error_label = ttk.Label(dialog, text="", foreground="red")
        error_label.grid(row=2, columnspan=2)

        def save_and_start():
            try:
                num_stages = int(stage_entry.get())
                num_to_calc = int(stages_to_calc_entry.get())

                if num_to_calc > num_stages:
                    error_label.config(text=f"Stages to calculate ({num_to_calc}) cannot exceed total stages ({num_stages})!")
                    return

                if num_to_calc < 1:
                    error_label.config(text="Stages to calculate must be at least 1!")
                    return

                self.stage = num_stages
                self.stages_to_calc = num_to_calc
                dialog.destroy()
                self.render_gui()
            except ValueError:
                error_label.config(text="Please enter a valid integer!")

        ttk.Button(dialog, text="Save and Start GUI", command=save_and_start).grid(row=3, columnspan=2, pady=10)

        dialog.mainloop()

    def render_gui(self):
        self.root = tk.Tk()
        self.root.title("GUI Example")

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Insert tab list
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        zeroD = ttk.Frame(notebook, padding=10)
        oneD = ttk.Frame(notebook, padding=10)
        threeD = ttk.Frame(notebook, padding=10)
        grid = ttk.Frame(notebook, padding=10)
        multall_data = ttk.Frame(notebook, padding=10)
        other_tab = ttk.Frame(notebook, padding=10)

        notebook.add(zeroD, text="0D-Settings")
        notebook.add(oneD, text="1D-Settings")
        notebook.add(threeD, text="3D-Settings")
        notebook.add(grid, text="Grid-Settings")
        notebook.add(other_tab, text="Other-Settings")

        self.zeroD_tab(zeroD)
        self.oneD_tab(oneD, self.stage)
        self.threeD_tab(threeD)
        self.grid_definition_tab(grid)
        self.other_settings_tab(other_tab)

        ttk.Button(main_frame, text="Generate Output File", command=self._generate_all_and_exit).pack(pady=5)

        self.run_multall_var = tk.BooleanVar(value=False)
        multall_check_frame = ttk.Frame(main_frame)
        multall_check_frame.pack(pady=(0, 10))
        self.run_multall_check = ttk.Checkbutton(
            multall_check_frame,
            text="Run MULTALL after generation",
            variable=self.run_multall_var
        )
        self.run_multall_check.pack(side='left')
        multall_help = ttk.Label(multall_check_frame, text="?", cursor="question_arrow")
        multall_help.pack(side='left', padx=(5, 0))
        Tooltip(multall_help, "If checked, a new command window will open and run MULTALL on the generated file(s). If multiple DAT files were created the batch file is executed, otherwise a single MULTALL run is started.")

        main_frame.mainloop()


if __name__ == "__main__":
    my_gui = CompressorGui()
    my_gui.loading_prepopulated_data()
    my_gui.show_startup_dialog()