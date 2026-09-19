# ------------------------------------------------------------------
# File:    source/gui/tabs/one_d.py
# Author:  Jonas Scholz, Luca De Francesco
# Purpose: 1D meanline settings tab.
# ------------------------------------------------------------------

import json
import os
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog  # noqa: F401 — ttk used throughout
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pathlib import Path
from source.io.paths import JSON_PATH as json_path
from source.core.geometry.cubic_spline import cubspline
from source.core.meanline.thermodynamics import Thermo
from source.core.meanline.meanline import meanline
from source.logging import debug_log
from source.gui.dialogs import diameter_gui as _diameter_gui_mod
from source.gui.widgets import helpers as _helpers_mod


def build_one_d_tab(self, parent_frame, i_st_val):
        
    '''
    Define Names for Settings json 
    Defines Variable Mapping and GUI Names for reading of setting file
    '''
    parameters_sections = {
    'General Parameters': ['n', 'psi_h', 'phi_1', 'phi_2', 'phi_3'],
    'Rotor Parameters': ['z_R', 'l_R', 'd_R_l_R', 'd_Cl_R', 'd_TE_R', 'incidence_R'],
    'Stator Parameters': ['z_S', 'l_S', 'd_S_l_S', 'd_TE_S', 'd_CL_S', 'incidence_S']}
    # Define mapping between variable names and GUI names
    var_name_to_gui_map = {
        'n': 'n [rpm]',
        'psi_h': 'psi_h [-]',
        'phi_1': 'phi_1 [-]',
        'phi_2': 'phi_2 [-]',
        'phi_3': 'phi_3 [-]',
        'z_R': 'z" [-]',
        'l_R': 'l" [mm]',
        'd_R_l_R': 'd"/l" [-]',
        'd_Cl_R': 'd_cl" [mm]',
        'd_TE_R': 'd_TE" [mm]',
        'incidence_R': 'i" [°]',
        'z_S': "z' [-]",
        'l_S': "l' [mm]",
        'd_S_l_S': "d'/l' [-]",
        'd_TE_S': "d_TE' [mm]",
        'd_CL_S': "d_CL' [mm]",
        'incidence_S': "i' [°]"}
          
    
    '''
    Not in use
    '''
    #region not in used/obsolet functions and variables
    # Create reverse mapping 
    # currently not needed
    #gui_to_var_map = {v: k for k, v in var_name_to_gui_map.items()}
    
    # Obsolet
    #LOCK_FILE = static_folder/"settings.lock"
    #SETTINGS_FILE = static_folder/"Diameter_Values.txt"  
      
    def create_input_window(i_st_val):
        return _diameter_gui_mod.create_input_window(i_st_val)


    '''
    Maybe in use
    Not in use
    ''' 
    #endregion

    '''
    ' Helping functions for the meanline gui creation.
    ' 
    '''
    def create_scrollable_frame(container):
        return _helpers_mod.create_scrollable_frame(container)

    # NOTE (Session 17d): class diameter_gui moved to
    # source.gui.dialogs.diameter_gui (only used by run_diameter_gui, moved along).
            
    def run_diameter_gui(i_st, initial_data, save_callback = None):
        return _diameter_gui_mod.run_diameter_gui(self, i_st, initial_data, save_callback)
                        
    

    def write_diameters(**kwargs):
        return _diameter_gui_mod.write_diameters(self, **kwargs)

    def create_gui():
        
        global entries
        root = parent_frame
        '''
        Reading and saveing dict data from perpopulated data json
        '''
        entries = {}
        params = list(self.prepop_meanline_input_data.keys())

        #ttk.Label(root, text="Meanline Parameter Initialization").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')
        #root.Label(self, text="Meanline Parameter Initialization").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')
        #root.label("Meanline Parameters Initialization")

        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        entries = {}

        for section, params in parameters_sections.items():
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=section)

            for i, param in enumerate(params):
                gui_name = var_name_to_gui_map[param]
                ttk.Label(frame, text=f"{gui_name}:").grid(row=i, column=0, padx=5, pady=5, sticky='w')
                entries[param] = []
                values = self.prepop_meanline_input_data[param]
                
                if param == 'n':
                    entry = ttk.Entry(frame, width=10)
                    entry.insert(0, str(values[0]))  # asks for only one RPM value
                    entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
                    num_stages = self.stage 
                    for _ in range(num_stages):
                        entries[param].append(entry)
                else:
                    for j, value in enumerate(values):
                        entry = ttk.Entry(frame, width=10)
                        entry.insert(0, str(value))
                        entry.grid(row=i, column=j+1, padx=5, pady=5)
                        entries[param].append(entry)
                '''
                # Old. RPM should only be one input box because the value is const over that whole compressor
                for j, value in enumerate(values):
                    entry = ttk.Entry(frame, width=10)
                    entry.insert(0, str(value))
                    entry.grid(row=i, column=j+1, padx=5, pady=5)
                    entries[param].append(entry)
                '''
        def save_and_initialize_meanline(show_plot):
            debug_log.debug(f"Writing using the save_and_initialize function. Show_plot = {show_plot}", context="oneD_tab")
            
            ''' 
            Run meanline function to calculate channelcontour   
            ''' 
            self.meanline_data = meanline(self.Thermodata, self.prepop_meanline_input_data, self.prepop_diameter_data, show_plot)

            '''  
            # Load settings from JSON
            try:
                with open(json_path, 'r') as file:
                    all_json_data = json.load(file)
                
                # Load Metadata
                if 'Metadata' in all_json_data:
                    metadata = all_json_data['Metadata']
                    
                    if 'output_folder' in metadata:
                        self.output_folder_entry.delete(0, tk.END)
                        self.output_folder_entry.insert(0, metadata['output_folder'])
                    
                    if 'levels' in metadata:
                        # Convert list back to comma-separated string
                        levels_str = ', '.join(str(x) for x in metadata['levels'])
                        self.levels_entry.delete(0, tk.END)
                        self.levels_entry.insert(0, levels_str)
                    
                    if 'use_default_rotor_bezier' in metadata:
                        self.use_default_rotor_bezier_var.set(metadata['use_default_rotor_bezier'])
                    
                    if 'use_default_stator_bezier' in metadata:
                        self.use_default_stator_bezier_var.set(metadata['use_default_stator_bezier'])
                    
                    if 'adjust_rotor_thickness' in metadata:
                        self.adjust_rotor_thickness_var.set(metadata['adjust_rotor_thickness'])
                    
                    if 'adjust_rotor_angle' in metadata:
                        self.adjust_rotor_angle_var.set(metadata['adjust_rotor_angle'])
                    
                    if 'adjust_stator_thickness' in metadata:
                        self.adjust_stator_thickness_var.set(metadata['adjust_stator_thickness'])
                    
                    if 'adjust_stator_angle' in metadata:
                        self.adjust_stator_angle_var.set(metadata['adjust_stator_angle'])
                    
                    if 'show_section_plot' in metadata:
                        self.show_section_plot_var.set(metadata['show_section_plot'])
                    
                    if 'show_angle_distribution_plots' in metadata:
                        self.show_angle_distribution_plots_var.set(metadata['show_angle_distribution_plots'])
                
                # Load Grid_data
                if 'Grid_data' in all_json_data:
                    grid_data = all_json_data['Grid_data']
                    
                    if 'nrow' in grid_data:
                        self.nrow_entry.delete(0, tk.END)
                        self.nrow_entry.insert(0, str(grid_data['nrow']))
                
                # Load Bleed_air_data
                if 'Bleed_air_data' in all_json_data:
                    bleed_data = all_json_data['Bleed_air_data']
                    
                    if 'enable_bleed_air' in bleed_data:
                        self.enable_bleed_air_var.set(bleed_data['enable_bleed_air'])
                    
                    if 'rotor_patches' in bleed_data:
                        self.bleed_air_data['rotor']['count'] = bleed_data['rotor_patches']
                    
                    if 'stator_patches' in bleed_data:
                        self.bleed_air_data['stator']['count'] = bleed_data['stator_patches']
                    
                    # Load rotor patches
                    for i in range(bleed_data.get('rotor_patches', 0)):
                        patch_key = f'rotor_patch_{i+1}'
                        if patch_key in bleed_data:
                            self.bleed_air_data['rotor']['patches'].append(bleed_data[patch_key])
                    
                    # Load stator patches
                    for i in range(bleed_data.get('stator_patches', 0)):
                        patch_key = f'stator_patch_{i+1}'
                        if patch_key in bleed_data:
                            self.bleed_air_data['stator']['patches'].append(bleed_data[patch_key])
                print(f"self.bleed_air_data: {self.bleed_air_data}")
                
                # Load Intale_Outtake_area
                if 'Intale_Outtake_area' in all_json_data:
                    intake_data = all_json_data['Intale_Outtake_area']
                    
                    if 'inlet_area' in intake_data:
                        self.inlet_area_var.set(intake_data['inlet_area'])
                    
                    if 'inlet_dist' in intake_data:
                        self.inlet_dist_var.set(intake_data['inlet_dist'])
                    
                    if 'outlet_area' in intake_data:
                        self.outlet_area_var.set(intake_data['outlet_area'])
                    
                    if 'outlet_dist' in intake_data:
                        self.outlet_dist_var.set(intake_data['outlet_dist'])
                
                # Store prepopulated data
                self.prepop_metadata = all_json_data.get('Metadata', {})
                self.prepop_grid_data = all_json_data.get('Grid_data', {})
                self.prepop_bleed_air_data = all_json_data.get('Bleed_air_data', {})
                self.prepop_intake_outtake = all_json_data.get('Intale_Outtake_area', {})
                
                print("Settings loaded successfully from JSON.")

            except FileNotFoundError:
                print("No previous parameters found. Starting with defaults.")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON file: {e}")
            except Exception as e:
                print(f"Error loading settings: {e}")

            '''
            try:
                with open(json_path, 'r') as file:
                    all_json_data = json.load(file)
                                    
                new_meanline_input_data = {}
                all_params = [p for params_list in parameters_sections.values() for p in params_list]
                for param in all_params:
                    if param in ['z_R', 'z_S']:
                        new_meanline_input_data[param] = [int(entry.get()) for entry in entries[param]]
                    else:
                        new_meanline_input_data[param] = [float(entry.get()) for entry in entries[param]]
                #new_meanline_input_data[param] = float(entries[param].get())

                all_json_data['Meanline_input_data'] = new_meanline_input_data
                
                with open(json_path, 'w') as file:
                    json.dump(all_json_data, file, indent=4)
                
                self.prepop_meanline_input_data = new_meanline_input_data
                    
                status_msg = "Meanline Parameters saved and initialized."
                print(status_msg)
                debug_log.debug(status_msg, context="oneD_tab")
            except ValueError:
                err_msg = "Please enter valid numbers for all conditions. z_R and z_S must be integers."
                print(err_msg)
                debug_log.debug(err_msg, context="oneD_tab")
            
            '''
            # Not old used in wrong spot???
            try:
                with open(json_path, 'r') as file:
                    all_json_data = json.load(file)
                                    
                new_meanline_input_data = {}
                all_params = [p for params_list in parameters_sections.values() for p in params_list]
                for param in all_params:
                    if param in ['z_R', 'z_S']:
                        new_meanline_input_data[param] = [int(entry.get()) for entry in entries[param]]
                    else:
                        new_meanline_input_data[param] = [float(entry.get()) for entry in entries[param]]
                #new_meanline_input_data[param] = float(entries[param].get())

                all_json_data['Meanline_input_data'] = new_meanline_input_data
                
                with open(json_path, 'w') as file:
                    json.dump(all_json_data, file, indent=4)
                
                self.prepop_meanline_input_data = new_meanline_input_data
                    
                print("Parameters saved and initialized.")
            except ValueError:
                print("Please enter valid numbers for all conditions. z_R and z_S must be integers.")
            '''

        debug_log.debug(f"self.prepop_diameter_data: {self.prepop_diameter_data}", context="oneD_tab")
        ttk.Button(root, text="Save and Initialize Parameters", command=lambda: save_and_initialize_meanline(show_plot=self.prepop_diameter_data["plot_channel_contour"])).pack(pady=10)
        #ttk.Button(root, text="Save and Initialize Parameters", command=save_and_initialize(show_plot=self.prepop_diameter_data["Plot Channel Contour"])).pack(pady=10)
        ttk.Button(root, text="Change the Channelcontour", command=lambda: run_diameter_gui(i_st_val, self.prepop_diameter_data, write_diameters)).pack(pady=10)
        save_and_initialize_meanline(show_plot = False)
    
    
    # Starts and creates the meanline gui inside of the window
    create_gui()

'''
3D-Tab and related functions
'''    
# region 3D Helper Methods (3D-Tab and related functions)

           
