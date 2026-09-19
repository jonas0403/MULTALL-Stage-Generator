# ------------------------------------------------------------------
# File:    source/gui/tabs/three_d_profiles.py
# Author:  Jonas Scholz, Luca De Francesco
# Purpose: Blade-profile import/export, settings and adjustment window.
# ------------------------------------------------------------------

import json
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from source.io.paths import JSON_PATH as json_path
from source.gui.widgets.tooltip import Tooltip
from source.core.stage.blade_profiles import create_default_profiles
from source.core.stage.orchestration import run_main_logic
from source.logging import debug_log


def create_profiles_and_update_gui(self):
    create_default_profiles(self, json_path)
    #self.check_button_states()


def setup_parameters_tab(self):

    # main_frame = ttk.Frame(self.root, padding="10")
    # main_frame.pack(fill="both", expand=True) # Gruppierungscontainer

    choice_frame = ttk.LabelFrame(self.parameters_frame, text="Bezier Profile Import / Export")
    choice_frame.pack(fill='x', padx=5, pady=5)
    
    self.create_profiles_button = ttk.Button(choice_frame, text="Create Default Profile(s)", command=self.create_profiles_and_update_gui) # Button zum Erstellen der Profile
    self.create_profiles_button.pack(pady=5, padx=10, fill='x')
    
    self.load_rotor_button = ttk.Button(choice_frame, text="Load Rotor Profile", command=lambda: self.import_bezier_from_txt('rotor')) # Selection for loading profile
    self.load_rotor_button.pack(fill='x', padx=10, pady=5)
    self.load_stator_button = ttk.Button(choice_frame, text="Load Stator Profile", command=lambda: self.import_bezier_from_txt('stator')) # Selection for loading profile
    self.load_stator_button.pack(fill='x', padx=10, pady=5)
    
    ttk.Button(choice_frame, text="Export Profiles to TXT", command=self.export_bezier_to_txt).pack(fill='x', padx=10, pady=5)

    adjust_frame = ttk.LabelFrame(self.parameters_frame, text="Adjust Profiles")
    adjust_frame.pack(fill='x', padx=5, pady=5)
    self.adjust_profiles_button = ttk.Button(adjust_frame, text="Make a specific adjustment", command= self.open_specification_window)
    self.adjust_profiles_button.pack(pady=5, padx=10, fill='x')

    
    # Is this needed?
    def save_adjustments_to_json(self, new_adjust_values):
    
        try:
            with open(json_path, 'r') as file:
                all_json_data = json.load(file)
                
            new_adjust_values = {}
            all_json_data['Adjust_Settings'] = new_adjust_values
            
            with open(json_path, 'w') as file:
                json.dump(all_json_data, file, indent=4)
                
            status_msg = "Adjust settings successfully saved to JSON."
            print(status_msg)
            debug_log.debug(status_msg, context="threeD_tab")
            
            self.prepop_adjust_data = new_adjust_values
            
        except Exception as e:
            err_msg = f"Error saving adjust settings to JSON: {e}"
            print(err_msg)
            debug_log.debug(err_msg, context="threeD_tab")
            

def setup_plot_options_tab(self):
    rotor_frame = ttk.LabelFrame(self.plot_options_frame, text="Rotor Profile")
    rotor_frame.pack(fill='x', padx=5, pady=5)
    
    stator_frame = ttk.LabelFrame(self.plot_options_frame, text="Stator Profile")
    stator_frame.pack(fill='x', padx=5, pady=5)
    
    ttk.Button(rotor_frame, text="Show geometry plot", command=self.show_plots_section_rotor).pack(fill='x', padx=10, pady=10)
    ttk.Button(rotor_frame, text="Show angle distribution plot", command=self.show_plots_angle_rotor).pack(fill='x', padx=10, pady=10)
    ttk.Button(rotor_frame, text="Show thickness distribution plot", command=self.show_plots_thickness_rotor).pack(fill='x', padx=10, pady=10)
    
    ttk.Button(stator_frame, text="Show geometry plot", command=self.show_plots_section_stator).pack(fill='x', padx=10, pady=10)
    ttk.Button(stator_frame, text="Show angle distribution plot", command=self.show_plots_angle_stator).pack(fill='x', padx=10, pady=10)
    ttk.Button(stator_frame, text="Show thickness distribution plot", command=self.show_plots_thickness_stator).pack(fill='x', padx=10, pady=10)
    
    
def export_bezier_to_txt(self):
    import json
    import os
    from tkinter import filedialog, messagebox

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        
        bezier_data = data.get("Bezier_point_data", {})
        if not bezier_data:
            messagebox.showerror("Error", "No Bezier data found in JSON! Please generate profiles first.")
            return
            
        export_dir = filedialog.askdirectory(title="Select the folder to save the TXT files")
        if not export_dir:
            return
            
        # Writes both files (Rotor and Stator) into the selected directory
        for blade_type in ["rotor", "stator"]:
            if blade_type in bezier_data:
                b_data = bezier_data[blade_type]
                angle_key = "beta_S" if blade_type == "rotor" else "alpha_S"
                filename = f"bezier_control_points_{'R' if blade_type == 'rotor' else 'S'}.txt"
                filepath = os.path.join(export_dir, filename)
                
                with open(filepath, "w") as f:
                    f.write(f"For each level h/H = [0, 0.2, 0.5, 0.8, 1.0]\n\n")
                    f.write(f"1st to 4th control points for {angle_key} for all levels:\n")
                    
                    angles = b_data.get(angle_key, [0]*20)
                    for i in range(4):
                        row_vals = angles[i*5:(i+1)*5]
                        f.write(", ".join(map(str, row_vals)) + "\n")
                        
                    f.write("\n1st to 4th control points for d/l for all levels:\n")
                    thicks = b_data.get("d/l", [0]*20)
                    for i in range(4):
                        row_vals = thicks[i*5:(i+1)*5]
                        f.write(", ".join(map(str, row_vals)) + "\n")
                        
                    f.write("\nm* for all levels:\n")
                    mstars = b_data.get("m*", [0.0]*5 + [0.3]*5 + [0.7]*5 + [1.0]*5)
                    for i in range(4):
                        row_vals = mstars[i*5:(i+1)*5]
                        f.write(", ".join(map(str, row_vals)) + "\n")
                        
        messagebox.showinfo("Success", f"Profiles successfully exported to:\n{export_dir}")
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Error", f"Export failed: {e}")

def import_bezier_from_txt(self, blade_type):
    import json
    from tkinter import filedialog, messagebox

    # Opens the file dialog to select the .txt file
    filepath = filedialog.askopenfilename(title=f"Select the {blade_type.capitalize()} TXT file", filetypes=[("Text files", "*.txt")])
    if not filepath:
        return
        
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            
        angle_key = "beta_S" if blade_type == "rotor" else "alpha_S"
        
        # Helper function to extract exactly the 4 lines below a specific header
        def extract_block(header_text):
            block = []
            idx = -1
            for i, line in enumerate(lines):
                if header_text in line:
                    idx = i
                    break
            if idx != -1:
                for i in range(1, 5):
                    vals = [float(v.strip()) for v in lines[idx+i].split(",")]
                    block.extend(vals)
            return block
            
        angles = extract_block(f"1st to 4th control points for {angle_key}")
        thicks = extract_block("1st to 4th control points for d/l")
        mstars = extract_block("m* for all levels")
        
        if len(angles) != 20 or len(thicks) != 20:
            messagebox.showerror("Error", "The file does not have the expected format! Values are missing.")
            return
            
        # Silently saves the newly extracted TXT data into the JSON
        with open(json_path, "r") as f:
            data = json.load(f)
            
        if "Bezier_point_data" not in data:
            data["Bezier_point_data"] = {}
        if blade_type not in data["Bezier_point_data"]:
            data["Bezier_point_data"][blade_type] = {}
            
        data["Bezier_point_data"][blade_type]["h/H"] = [0.0, 0.2, 0.5, 0.8, 1.0]
        data["Bezier_point_data"][blade_type][angle_key] = angles
        data["Bezier_point_data"][blade_type]["d/l"] = thicks
        data["Bezier_point_data"][blade_type]["m*"] = mstars
        
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)
            
        # Update the GUI instance memory so the program knows about the new values immediately
        if blade_type == "rotor":
            self.prepop_bezier_point_rotor = data["Bezier_point_data"][blade_type]
        else:
            self.prepop_bezier_point_stator = data["Bezier_point_data"][blade_type]
            
        messagebox.showinfo("Success", f"The {blade_type.capitalize()} profile was successfully imported into the JSON! The script will now use these values for calculation.")
        
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Error", f"Import failed: {e}")
    

def open_specification_window(self):

    def apply_adjustments():
        settings_adjustments = {
            'main_choice': 'adjust',
            'adjust_section_idx': self.specs["section_idx"].get().split(" ")[0],
            'adjust_row': self.specs["row"].get(),
            'adjust_parameter': self.specs["parameter"].get(),
            'adjust_stage': self.specs["stage"].get(),
            'levels': self.levels_entry.get(),
            'nrow': 1 if self.nrow_combo.get() == "Rotor Only" else 2
        }
        run_main_logic(settings_adjustments, self, json_path)
    
    spec_window = tk.Toplevel(self.root)
    spec_window.title("Adjustments")
    spec_window.transient(self.root) # Fenster bleibt im Vordergrund
    spec_window.grab_set() # Prevents changes to the sub-window

    frame = ttk.Frame(spec_window, padding="15")
    frame.pack(expand=True, fill="both")

    # Creates a dropdown menu 
    ttk.Label(frame, text="Section Plan to change:").grid(row=0, column=0, sticky='w', pady=5)
    
    section_combo = ttk.Combobox(frame, textvariable=self.specs["section_idx"], values=['0.0', '0.2', '0.5', '0.8', '1.0'], state="readonly")
    section_combo.grid(row=0, column=1, pady=5)
    section_combo.current(2)

    ttk.Label(frame, text="Blade Row:").grid(row=1, column=0, sticky='w', pady=5)
    row_combo = ttk.Combobox(frame, textvariable=self.specs["row"], value=['Rotor', 'Stator'], state="readonly")
    row_combo.grid(row=1, column=1, pady=5)
    row_combo.current(0)

    ttk.Label(frame, text="Parameter to Adjust:").grid(row=2, column=0, sticky='w', pady=5)
    parameter_combo = ttk.Combobox(frame, textvariable=self.specs["parameter"], value=['Angle', 'Thickness'], state="readonly")
    parameter_combo.grid(row=2, column=1, pady=5)
    parameter_combo.current(0)

    ttk.Label(frame, text="Stage:").grid(row=3, column=0, sticky='w', pady=5)
    stage_vals = [str(i + 1) for i in range(self.stage)] if hasattr(self, 'stage') and self.stage > 0 else ['1']
    stage_combo = ttk.Combobox(frame, textvariable=self.specs["stage"], values=stage_vals, state="readonly")
    stage_combo.grid(row=3, column=1, pady=5)
    stage_combo.current(0)

    ttk.Button(frame, text="Adjust Profile", command=apply_adjustments).grid(row=4, column=0, columnspan=2, pady=15)
    ttk.Button(frame, text="Close", command=spec_window.destroy).grid(row=5, column=0, columnspan=2, pady=15)
    
def load_rotor_settings(self):

    filepath = filedialog.askopenfilename(title="Select Rotor Bezier Points File", filetypes=[("Text Files", "*.txt")])
    if filepath:
        
        try:
            if os.path.samefile(filepath, "bezier_control_points_R.txt"):
                msg = "This file already exists."
                print(msg)
                debug_log.debug(msg, context="threeD_tab")
                return
        except FileNotFoundError:
            pass
        
        shutil.copy(filepath, "bezier_control_points_R.txt")
        msg = f"Rotor Profile loaded: {filepath}"
        print(msg)
        debug_log.debug(msg, context="threeD_tab")

    
def load_stator_settings(self):
    filepath = filedialog.askopenfilename(title="Select Stator Bezier Points File", filetypes=[("Text Files", "*.txt")])
    if filepath:
                    
        try:
            if os.path.samefile(filepath, "bezier_control_points_S.txt"):
                msg = "This file already exists."
                print(msg)
                debug_log.debug(msg, context="threeD_tab")
                return
        except FileNotFoundError:
            pass
        
        shutil.copy(filepath, "bezier_control_points_S.txt")
        msg = f"Stator Profile loaded: {filepath}"
        print(msg)
        debug_log.debug(msg, context="threeD_tab")

# not in use anymore
def save_settings(self):
    with open('Settings.txt', 'w') as file:
        file.write(f"main_choice = {self.main_choice.get()}\n") # Holt sich die User Auswahl aus dem Radiobutton
    
        if self.main_choice.get() == 'adjust': # only if Adjust was selected
            section_str = self.specs["section_idx"].get().split(" ")[0] 
            section_map = {'0.0': 0, '0.2': 1, '0.5': 2, '0.8': 3, '1.0': 4}
            file.write(f"adjust_section_idx = {section_map.get(section_str, 2)}\n")
            file.write(f"adjust_row = {self.specs['row'].get()}\n")
            file.write(f"adjust_parameter = {self.specs['parameter'].get()}\n")
        
        file.write(f"levels = {self.levels_entry.get()}\n")
    print("Settings saved")
    debug_log.debug("Settings saved", context="save_settings")

# def load_settings(self):
#     try:
#         settings = {}
#         with open('Settings.txt', 'r') as file:
#             for line in file:
#                 line = line.strip()
#                 if ' = ' in line:
#                     try:
#                         key, value = line.split(' = ', 1)
#                         settings[key] = value
#                     except ValueError:
#                         continue    
            
#         self.show_section_plot_var.set(settings.get('show_section_plot', "False"))
#         self.show_angle_dist_plot_var.set(settings.get('show_angle_dist_plot', "False")) 
        
#         self.levels_entry.insert(0, settings.get('levels', '0.0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 0.95, 1.00'))
#         nrow_value = int(settings.get('nrow', 2))
#         self.nrow_combo.set("Rotor Only" if nrow_value == 1 else "Complete Stage (Rotor & Stator)")
#     except FileNotFoundError:
#         self.levels_entry.insert(0, '0.0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 0.95, 1.00')
#         self.nrow_combo.set("Complete Stage (Rotor & Stator)")
### Everything above still needs to be replaced by a load method. Copied here only for functionality

# def run_action_and_stay_open(self): # Saves everything and does not close the window
#     settings = {
#         "main_choice": self.main_choice.get(),
#     }

#     nrow_choice = self.nrow_combo.get()
#     settings["nrow"] = 1 if nrow_choice == "Rotor Only" else 2
    
#     settings["levels"] = self.levels_entry.get()
    
#     if settings["main_choice"] == "adjust":
#         section_str = self.specs["section_idx"].get()
#         section_map = {'0.0': 0, '0.1':1, '0.2': 2, '0.3': 3, '0.4': 4, '0.5': 5, '0.6': 6, '0.7': 7, '0.8': 8, '0.9': 9, '1.0': 10}
#         settings["adjust_section_idx"] = section_map.get(section_str, 2)
#         settings["adjust_row"] = self.specs['row'].get()
#         settings["adjust_parameter"] = self.specs['parameter'].get()
        
    
#     run_main_logic_result = run_main_logic(settings, self)
#     if run_main_logic_result is not None:
#         self.stage_data = run_main_logic_result
#         print("stage_data saved sucessfully")
    
#     self.save_settings() # Speichert die Einstellungen in der Settings.txt

def _bezier_data_ready(self) -> bool:
    """Return True when at least stage-1 bezier data exists in the JSON."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        store = data.get("Bezier_point_data", {})
        has_new    = "rotor_stage_1" in store and "stator_stage_1" in store
        has_legacy = "rotor" in store and "stator" in store
        return has_new or has_legacy
    except Exception:
        return False  

