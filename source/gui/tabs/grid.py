# ------------------------------------------------------------------
# File:    source/gui/tabs/grid.py
# Author:  Luca De Francesco
# Purpose: Grid-settings tab and generation trigger.
# ------------------------------------------------------------------

import json
import os
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from source.io.paths import JSON_PATH as json_path, REPO_ROOT
from source.gui.widgets.tooltip import Tooltip
import source.core.grid.grid_generator as VG
from source.core.stage.orchestration import run_main_logic
from source.logging import debug_log


def build_grid_tab(self, parent_frame):


    '''
    # --- Main Grid Settings  ---
    '''    
    
    
    grid_data = { # Loading Default Values
        'nrow': tk.IntVar(value=2),
        'im_selection' : tk.StringVar(value=37),   # Default value for IM
        'km_selection' : tk.StringVar(value=37),   # Default value for KM
        'ref_chord_length': tk.DoubleVar(value=134.4),  # Default value for reference chord length
        'JM_grid_density': tk.IntVar(value=200),  # Default value for reference grid points
        'tip_clearance_rotor': tk.DoubleVar(value=1.3),  # Standardwert von 1.3mm
        'inlet_percentage': tk.DoubleVar(value=0.2),  # Standardwert von 20%
        'outlet_percentage': tk.DoubleVar(value=0.15),  # Standardwert von 15%
        'show_plot': tk.BooleanVar(value=False),  # Default value for showing the plot
        'Q3D_mode': tk.BooleanVar(value=False),  # Default value for Q3D mode
        'ref_chord_length_mode': tk.BooleanVar(value=False),  # Default value for reference chord length mode
        'SA_mode': tk.BooleanVar(value=False)  # Default value for SA turbulence model
    }
    
    km_options = ["5", "21", "25", "29", "33", "37", "41", "45", "49", "53", "57", "61", "65", "69", "73", "77", "81", "89"]
    im_options = ["5", "13", "21", "29", "37", "45", "53", "71", "79", "86", "94"]
    jm_options = [str(i) for i in range(8, 800, 8)]
    
    ui_config = [
        {
            "key": "ref_chord_length",
            "label": "Reference Chord Length [mm]:",
            "type": "entry",
            "help": "Reference value for the chord length...",
            "state_key": "ref_chord_length_mode" 
        },
        {
            "key": "km_selection",
            "label": "Grid Dimension (KM):",
            "type": "combobox",
            "values": km_options,
            "help": "Points of Grid in Radial Direction..."
        },
        {
            "key": "im_selection",
            "label": "Grid Dimension (IM):",
            "type": "combobox",
            "values": im_options,
            "help": "Points of Grid in Circumferential Direction..."
        },
        {
            "key": "JM_grid_density",
            "label": "Fineness (Reference Points):",
            "type": "combobox",
            "values": jm_options,
            "help": "Points of Grid in Axial Direction..."
        },
        {
            "key": "inlet_percentage",
            "label": "Inlet Points (% of JM):",
            "type": "entry",
            "help": "Percentage of points at the inlet..."
        },
        {
            "key": "outlet_percentage",
            "label": "Outlet Points (% of JM):",
            "type": "entry",
            "help": "Percentage of points at the outlet..."
        },
        {
            "key": "tip_clearance_rotor",
            "label": "Tip clearance (mm):",
            "type": "entry",
            "help": "Distance between blade tip and shroud..."
        }
    ]   
       
    main_frame = ttk.Frame(parent_frame, padding="10")
    main_frame.pack(fill="both", expand=True)
    
    nrow_frame = ttk.LabelFrame(main_frame, text="Blade Rows")
    nrow_frame.pack(fill='x', padx=5, pady=5, anchor='n')
    
    inner_nrow_frame = ttk.Frame(nrow_frame)
    inner_nrow_frame.pack(fill='x', padx=10, pady=5)
    
    ttk.Label(inner_nrow_frame, text="Number of Blade Rows:").grid(row=0, column=0, sticky="w", padx=5, pady=5)

    self.nrow_combo = ttk.Combobox(inner_nrow_frame, values=["Complete Stage (Rotor & Stator)", "Rotor Only"], state="readonly")
    self.nrow_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    # CHANGE: question mark label to the right of combobox, same pattern as bleed air tooltips
    nrow_q_label = ttk.Label(inner_nrow_frame, text="?", cursor="question_arrow")
    nrow_q_label.grid(row=0, column=2, padx=2, pady=5, sticky='w')
    Tooltip(nrow_q_label, "Multi-stage analysis requires both Rotor and Stator components for continuity.")

    # [FIX] restore turbulence checkbox from JSON (save already writes it; without this
    # the box always reset to False). Other ui_config defaults intentionally untouched.
    if self.prepop_grid_data.get('SA_mode', False):
        grid_data['SA_mode'].set(True)

    loaded_nrow = self.prepop_grid_data.get('nrow')

    # CHANGE: lock combobox if stages_to_calc > 1
    if self.stages_to_calc > 1:
        self.nrow_combo.set("Complete Stage (Rotor & Stator)")
        self.nrow_combo.config(state="disabled")
    else:
        if loaded_nrow == 1:
            self.nrow_combo.set("Rotor Only")
        else:
            self.nrow_combo.set("Complete Stage (Rotor & Stator)")
    
    '''
    ttk.Label(inner_nrow_frame, text="Number of Blade Rows:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    self.nrow_combo = ttk.Combobox(inner_nrow_frame, values=["Complete Stage (Rotor & Stator)", "Rotor Only"], state="readonly")
    
    loaded_nrow = self.prepop_grid_data.get('nrow')
    
    # locking the combobox to select if only the rotor were to be calculated if sages to calc is larger than one
    if self.stages_to_calc != 1:
        # Force "Complete Stage" regardless of loaded data if stages > 1
        self.nrow_combo.set("Complete Stage (Rotor & Stator)")
        self.nrow_combo.config(state="disabled") # Lock the box
        
        # Add a small Tooltip to explain why it is locked
        row_label = inner_nrow_frame.winfo_children()[-2] # Accessing the Label
        Tooltip(row_label, "Multi-stage analysis requires both Rotor and Stator components for continuity.")
    else:
        # Normal behavior for single stage: use the loaded value
        if loaded_nrow == 1:
            self.nrow_combo.set("Rotor Only")
        else:
            self.nrow_combo.set("Complete Stage (Rotor & Stator)")
    
    if loaded_nrow == 1:
        self.nrow_combo.set("Rotor Only")
    else:
        self.nrow_combo.set("Complete Stage (Rotor & Stator)")
    '''
    self.nrow_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    
    ttk.Label(inner_nrow_frame, text= "Levels for Output:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    self.levels_entry = ttk.Entry(inner_nrow_frame)
    
    loaded_levels = self.prepop_metadata.get('levels', [0.0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 0.95, 1.0])
    levels_str = ", ".join(map(str, loaded_levels))
    self.levels_entry.insert(0, levels_str)
    
    self.levels_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
    
    ttk.Label(inner_nrow_frame, text="Output:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    self.output_entry = ttk.Entry(inner_nrow_frame)

    loaded_output = self.prepop_metadata.get('output_folder', '')
    self.output_entry.insert(0, loaded_output)
    
    self.output_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
    
    def browse_grid_output():
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)
    
    ttk.Button(inner_nrow_frame, text="Browse", command=browse_grid_output).grid(row=2, column=2, padx=5, pady=5)
    
    ttk.Label(inner_nrow_frame, text="Grid file prefix:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    self.grid_prefix_entry = ttk.Entry(inner_nrow_frame)
    self.grid_prefix_entry.insert(0, "grid")
    self.grid_prefix_entry.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
    prefix_tip = ttk.Label(inner_nrow_frame, text="?", cursor="question_arrow")
    prefix_tip.grid(row=3, column=3, padx=2, pady=5, sticky='w')
    Tooltip(prefix_tip, "First part of the grid filename (manual entry, not saved). Rest is added automatically.")
    inner_nrow_frame.grid_columnconfigure(1, weight=1)  
    
    self.settings_frame = ttk.LabelFrame(main_frame, text="Grid Configuration")
    self.settings_frame.pack(side="top" ,fill="x", anchor="n", pady=5)
    
    self.turbulence_model_frame = ttk.LabelFrame(main_frame, text="Turbulence Model")
    self.turbulence_model_frame.pack(side="top", fill="x", pady=5)
    
    self.widgets = {}
    
    def toggle_ref_chord():
        entry_widget = self.widgets['ref_chord_length']
        
        is_acativated = grid_data['ref_chord_length_mode'].get()
        
        if is_acativated:
            # when activated:
            entry_widget.configure(state="normal")
        else:
            # when deactivated:
            entry_widget.configure(state="disabled")
            
            grid_data['ref_chord_length'].set(134.4)  
    
    # --- Helper Funktion for Q3D Logic ---
    def toggle_Q3D():
        KM_combobox = self.widgets['km_selection']
        if grid_data['Q3D_mode'].get():
            grid_data['km_selection'].set(2) 
            KM_combobox.config(state=tk.DISABLED) 
            tip_clearance_entry = self.widgets['tip_clearance_rotor']
            grid_data['tip_clearance_rotor'].set(0.0)
            tip_clearance_entry.config(state=tk.DISABLED)
        else:
            KM_combobox.config(state=tk.NORMAL) 
            grid_data['km_selection'].set(37)  
            
    def toggle_SA():
        if grid_data['SA_mode'].get():
            SA_mode = True #  SA Turbulence Model
            SA_model = 1
        else:
            SA_mode = False #  Standart Turbulence Model
            SA_model =0
        
        debug_log.debug(f"SA_model: {SA_model}", context="grid_tab")
        
    def save_and_initialize_grid():

        debug_log.debug("Saving Parameter...", context="grid_tab")
        grid_data_save = {}
        
        for key, tk_variable in grid_data.items():
            grid_data_save[key] = tk_variable.get()
            
        nrow_choice = self.nrow_combo.get()
        grid_data_save['nrow'] = 1 if nrow_choice == "Rotor Only" else 2
            
        try:
            all_json_data = {}
            
            try:
                with open(json_path, 'r') as file:
                    all_json_data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            
            # [FIX] preserve JSON-only keys (e.g. suppress_blade_check, not in GUI):
            # UI values win, file-only keys survive instead of being wiped on save.
            merged_grid_data = dict(all_json_data.get('Grid_data', {}))
            merged_grid_data.update(grid_data_save)
            # [FIX] seed the JSON-only blade-check opt-out so the option exists;
            # UI values already won above, this only adds the default when absent.
            merged_grid_data.setdefault('suppress_blade_check', False)
            all_json_data['Grid_data'] = merged_grid_data
            
            levels_input = self.levels_entry.get()
            levels_list = [float(x.strip()) for x in levels_input.split(',')]
            output_value = self.output_entry.get()
            
            if 'Metadata' not in all_json_data:
                all_json_data['Metadata'] = {}
                
            all_json_data['Metadata']['levels'] = levels_list
            all_json_data['Metadata']['output_folder'] = output_value
            
            with open(json_path, 'w') as file:
                json.dump(all_json_data, file, indent=4)
                
            status_msg = "Parameters saved successfully to JSON."
            print(status_msg)
            debug_log.debug(status_msg, context="grid_tab")

            self.prepop_grid_data = grid_data_save
            
            if not hasattr(self, 'prepop_metadata'):
                self.prepop_metadata = {}
            self.prepop_metadata['levels'] = levels_list
            self.prepop_metadata['output_folder'] = output_value
            
        except ValueError:
            from tkinter import messagebox
            messagebox.showerror("Eingabefehler", "Bitte überprüfe die Eingabe bei 'Levels'. Die Zahlen müssen mit Komma getrennt sein (z.B. 0.0, 0.5, 1.0).")
        except Exception as e:
            err_msg = f"An error occurred while saving: {e}"
            print(err_msg)
            debug_log.debug(err_msg, context="grid_tab")
    
    def generate_grid():
        
        debug_log.debug("Saving Grid...", context="grid_tab")
        save_and_initialize_grid()
        # current_grid_settings = {}
        # for key, widget in self.widgets.items():
        #     current_grid_settings[key] = widget.get() 

        # try:
        #     gd = self.prepop_grid_data
        #     nrow_wert         = int(gd.get('nrow', 2))
        #     KM_grid_density   = int(gd.get('km_selection', 37))
        #     IM_grid_density   = int(gd.get('im_selection', 37))
        #     JM_grid_density   = int(gd.get('JM_grid_density', 200))
        #     inlet_percentage  = float(gd.get('inlet_percentage', 0.2))
        #     outlet_percentage = float(gd.get('outlet_percentage', 0.15))
        #     ref_chord_length  = float(gd.get('ref_chord_length', 134.4))
        #     tip_clearance_mm  = float(gd.get('tip_clearance_rotor', 1.3))
        #     Q3D_value         = bool(gd.get('Q3D_mode', False))
        #     do_plot           = bool(gd.get('show_plot', False))
        #     output_path       = gd.get('output_folder', '.')
            
        #     if not hasattr(self, 'meanline_results') or not self.meanline_results:
        #         messagebox.showerror("Error", "No Meanline-Data found. Please calculate '1D-Settings' first!")
        #         return
            
        #     if hasattr(self, 'prepop_metadata') and 'levels' in self.prepop_metadata:
        #         stage_levels = self.prepop_metadata['levels']
        #     else:
        #         # Fallback, in case Metadata is empty
        #         stage_levels = [0.0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 0.95, 1.0]

        #     if Q3D_value:
        #         KM_grid_density = 2

        #     D_S1 = self.meanline_results['D_S1']
        #     D_H1 = self.meanline_results['D_H1']
        #     total_height = (D_S1[0] - D_H1[0]) / 2.0 
        #     tip_clearance_multall = tip_clearance_mm / (total_height * 1000)

        #     print("Starting Grid calculations...")
            
        #     grid_data_list, grid_data_list_plot, JM_dynamic, JM = VG.generate_and_plot_grid(
        #         nrow_wert, IM_grid_density, KM_grid_density,
        #         0.5, JM_grid_density,
        #         inlet_percentage, outlet_percentage,
        #         ref_chord_length, stage_levels,
        #         self.meanline_results 
        #     )

        #     if do_plot:
        #         VG.plot_all(grid_data_list_plot, JM_dynamic)

        #     if Q3D_value:
        #         output_name = f"multall_grid_Q3D_IM_{IM_grid_density}_JM_{JM_dynamic}_rows_{nrow_wert}.dat"
        #     else:
        #         output_name = f"multall_grid_IM_{IM_grid_density}_KM_{KM_grid_density}_JM_{JM_dynamic}_rows_{nrow_wert}.dat"

        #     full_output_path = os.path.join(output_path, output_name)
        #     enable_bleed_air = self.meanline_results.get('enable_bleed_air', False)

        #     VG.write_head_file(KM_grid_density, IM_grid_density, full_output_path,
        #                        0, nrow_wert, len(stage_levels), Q3D_value, enable_bleed_air, 
        #                        self.meanline_results)
            
        #     for data in grid_data_list:
        #         self.JTE = data['JTE']
        #         VG.multall_grid_data_head_row(
        #             full_output_path, len(data['x_new']), data['row_num'],
        #             data['JLE'], data['JM'], data['JTE'],
        #             KM_grid_density, tip_clearance_multall, stage_levels,
        #             self.meanline_results
        #         )
        #         VG.write_coordinates(
        #             data['x_new'], data['Rtheta_new'], data['d_new'], data['R_new'],
        #             full_output_path, data['row_num'], 0, len(data['x_new']), data['JM']
        #         )

        #     VG.write_end_file(nrow_wert, full_output_path, 0, KM_grid_density, stage_levels, self.meanline_results)

        #     messagebox.showinfo("Erfolg", f"Gitter generiert:\n{full_output_path}")

        # except Exception as e:
        #     print(e)
        #     messagebox.showerror("Fehler", f"Fehler: {e}")
        '''
        # ============================================================
        # TODO (other branch): The following was an alternative simpler
        # approach from branch b7c0ba - please review and decide if
        # VG.process_grid_data(json_path) should replace the above.
        # ============================================================
          There was a merge conflict. Top not commented out version is 
          the more completed one
          Review lower commented out section to see if this is the correct
          merged version
        # ============================================================
        '''
        debug_log.debug("Grid is saved.", context="grid_tab")
        # [REFACTOR Session 17] old line resolved "..\Docs\Output" relative to src/;
        # from source/gui/tabs/ that would be wrong, so pin it to the repo root.
        debug_log.open_file(str(REPO_ROOT / "Docs" / "Output" / "debug.txt"))
        # Why is this called twice for the same button?
        try:
            run_main_logic({'main_choice': 'default'}, self, json_path)
        except Exception as e:
            import traceback
            err_msg = "\n--- Error Loading the 1-D Data ---"
            print(err_msg)
            debug_log.debug(err_msg, context="grid_tab")
            traceback.print_exc()
            messagebox.showerror("Error", "Please calculate and save the Meanline data first!")
            return False
        
        debug_log.debug("Generating Grid...", context="grid_tab")
        # [FIX output name] manual prefix (not in JSON); core sanitizes + falls back to "grid".
        self.grid_name_prefix = self.grid_prefix_entry.get() if hasattr(self, "grid_prefix_entry") else "grid"
        try:
            VG.process_grid_data(json_path, self)
        except ValueError as e:
            # [Guardrail] surface validation failures as a popup, not just console.
            messagebox.showerror("Blade profile check", str(e))
            print(f"Grid generation stopped: {e}")
            debug_log.debug(f"Grid generation stopped: {e}", context="grid_tab")
            return False
        status_msg = "Grid is generated."
        print(status_msg)
        debug_log.debug(status_msg, context="grid_tab")
        # [FIX] report success so callers (Generate Outputfile) only exit on success.
        return True
        
    
    '''
    GUI Logic
    '''
    
    for row_index, config in enumerate(ui_config):
        
        ttk.Label(self.settings_frame, text=config["label"]).grid(row=row_index, column=0, sticky="w", pady=5)
        
        current_var = grid_data[config["key"]]
        widget = None
        
        if config["type"] == "entry":
            widget = ttk.Entry(self.settings_frame, textvariable=current_var, width=10)
        elif config["type"] == "combobox":
            widget = ttk.Combobox(self.settings_frame, textvariable=current_var, values=config["values"], state="readonly", width=8)   

        if widget:
            widget.grid(row=row_index, column=1, sticky="w", pady=5, padx=5)
            self.widgets[config["key"]] = widget
            
        help_label = ttk.Label(self.settings_frame, text="?", cursor="question_arrow")
        help_label.grid(row=row_index, column=2, padx=(5, 0))
        Tooltip(help_label, config["help"])
    
        if config["key"] == "ref_chord_length":
            ttk.Checkbutton(
                self.settings_frame, 
                text="Change reference Chord length", 
                variable=grid_data['ref_chord_length_mode'], 
                command=toggle_ref_chord
            ).grid(row=row_index, column=3, padx=10) 
            
    last_row = len(ui_config)
    ttk.Checkbutton(
        self.settings_frame,
        text="Activate Q3D Mode (Sets KM to 2)",
        variable=grid_data['Q3D_mode'],
        command=toggle_Q3D
    ).grid(row=last_row, column=0, columnspan=2, sticky="w", pady=10)

    # SA Model Checkbutton
    ttk.Checkbutton(
        self.turbulence_model_frame,
        text="Use Spalart-Allmaras Turbulence Model",
        variable=grid_data['SA_mode'],
        command=toggle_SA
    ).grid(row=0, column=0, sticky="w")

    # Save Button
    #save_button = ttk.Button(main_frame, text="Save and Initialize Parameters", command=save_and_initialize_grid)
    #save_button.pack(pady=20)
    
    self._generate_grid_callback = generate_grid
    #save_button.pack(pady=20)   
        
         

    toggle_ref_chord()
    toggle_Q3D()


   
    
