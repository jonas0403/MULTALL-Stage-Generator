# ------------------------------------------------------------------
# File:    source/gui/tabs/three_d.py
# Author:  Jonas Scholz, Luca De Francesco
# Purpose: 3D settings tab (inlet/outlet subtabs).
# ------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, filedialog
from source.gui.widgets.tooltip import Tooltip
from source.logging import debug_log


def build_three_d_tab(self, parent_frame):

    # Add a dictionary for storing bleedair data  
    self.bleed_air_data = {
        'rotor': {'patches': [], 'count': 0},
        'stator': {'patches': [], 'count': 0}
    }
    
    # Potential error fix for attribute error
    self.rotor_patch_entries = []
    self.stator_patch_entries = []
    
    # Variables for Inlet and Outlet Adjustment
    self.inlet_area_var = tk.DoubleVar()
    self.inlet_dist_var = tk.DoubleVar()
    self.outlet_area_var = tk.DoubleVar()
    self.outlet_dist_var = tk.DoubleVar()
    
    # Misc Variable s
    self.output_folder_entry = tk.Entry()
    self.show_angle_dist_plot_var = tk.BooleanVar()
    

    
    self.main_choice = tk.StringVar(value="default")
    self.specs = {
    "section_idx": tk.StringVar(),
    "row": tk.StringVar(),
    "parameter": tk.StringVar(),
    "stage": tk.StringVar(value="1")
    }
    
    self.show_section_plot_var = tk.BooleanVar(value=False) 
    self.show_angle_dist_plot_var = tk.BooleanVar(value=False) 
    
    self.use_default_rotor_bezier_var = tk.BooleanVar(value=False)
    self.use_default_stator_bezier_var = tk.BooleanVar(value=False)
    self.adjust_rotor_thickness_var = tk.BooleanVar(value=False)
    self.adjust_rotor_angle_var = tk.BooleanVar(value=False)
    self.adjust_stator_thickness_var = tk.BooleanVar(value=False)
    self.adjust_stator_angle_var = tk.BooleanVar(value=False)
    
    self.enable_bleed_air_var = tk.BooleanVar(value=False)
    self.enable_bleed_air_var.trace_add("write", self.update_bleed_air_display)
    
    ttk.Label(parent_frame, text="3D Profile Generation and Visualization").pack(pady=10)
    self.sub_notebook = ttk.Notebook(parent_frame)
    self.sub_notebook.pack(fill='both', expand=True, padx=10, pady=5)
    
    self.parameters_frame = ttk.Frame(self.sub_notebook, padding=10)
    self.plot_options_frame = ttk.Frame(self.sub_notebook, padding=10)
    self.bleed_air_frame = ttk.Frame(self.sub_notebook, padding=10)
    self.inlet_outlet_frame = ttk.Frame(self.sub_notebook, padding=10)
    self.output_frame = ttk.Frame(self.sub_notebook, padding=10)
    
    self.sub_notebook.add(self.parameters_frame, text="Profile Parameters")
    self.sub_notebook.add(self.plot_options_frame, text="Plot Options")
    self.sub_notebook.add(self.bleed_air_frame, text="Bleed Air")
    self.sub_notebook.add(self.inlet_outlet_frame, text="Inlet/Outlet")
    #self.sub_notebook.add(self.output_frame, text="Output Settings")
    
    # Creat container frame for inputs for the bleed air
    self.bleed_input_container = ttk.Frame(self.bleed_air_frame)
    self.bleed_input_container.pack(fill='both', expand=True, padx=10, pady=10)
    
    
    # Loading Data for the bleed air and the variable Intake and Outtake Area 
    self.load_bleed_air_and_area_change() 
    
    
    self.setup_parameters_tab()
    self.setup_plot_options_tab()
    self.create_bleed_input_widget()
    self.setup_inlet_outlet_tab()
    
    # Save button for the whole of the 3D-Tab, saving all entered data in these tabs
    # Sits below all of the four tabs
    self.save_button_inlet_outlet = ttk.Button(parent_frame, text="Save", command=self.save_and_initialize_3D_tab)
    self.save_button_inlet_outlet.pack(pady=10, side='bottom')
    
    
    # --- Can Not be ignored ---
    # --- Must be under her (I think) ---
    # Initial call to set up the Bleed AIr Tab based on loaded values
    parent_frame.after(100, lambda: self.update_bleed_air_display())

    
    
    # We dont need this button there is nothing to save there
    # self.save_button = ttk.Button(self.parameters_frame, text="Save and Initialize", command=self.run_action_and_stay_open) 
    # self.save_button.pack(pady=10, padx=10, fill='x')
    
    #self.load_settings()
    
    #self.check_button_states()

def setup_inlet_outlet_tab(self):
    self.inlet_outlet_title_frame = ttk.Frame(self.inlet_outlet_frame)
    self.inlet_outlet_title_frame.pack(fill='x', padx=10, pady=10)
    
    self.inlet_outlet_title_label = ttk.Label (self.inlet_outlet_title_frame, text="Inlet and Outlet Geometry Definition")
    self.inlet_outlet_title_label.pack(side='left', padx= (0, 5))
    
    self.inlet_outlet_help = ttk.Label(self.inlet_outlet_title_frame, text= "?", cursor="question_arrow")
    self.inlet_outlet_help.pack(side='left', padx=(5, 0))
    self.inlet_outlet_help_text = "Define the geometry parameters of the Inlet and Outlet Area"
    Tooltip(self.inlet_outlet_help, self.inlet_outlet_help_text)
    
    self.inlet_frame = ttk.LabelFrame(self.inlet_outlet_frame, text="Inlet Area Definition")
    self.inlet_frame.pack(fill='x', padx=10, pady=10)
    
    # Inlet 
    self.inlet_area_label = ttk.Label(self.inlet_frame, text="Inlet Area")
    self.inlet_area_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
    
    # Area
    self.inlet_area_help = ttk.Label(self.inlet_frame, text= "?", cursor="question_arrow")
    self.inlet_area_help.grid(row=0, column=2, padx=(5, 0))
    self.inlet_area_help_text = "Enter the Size of the Inlet as a factor of the Diameter of the first Blade Row. Default = 1 (same Size as the Diameter of the first Blade Row)"
    Tooltip(self.inlet_area_help, self.inlet_area_help_text)
    
    self.inlet_area_entry = ttk.Entry(self.inlet_frame, width=10, textvariable=self.inlet_area_var)
    self.inlet_area_entry.grid(row=0, column=1, padx=5, pady=5)
    
    # Distance
    self.inlet_dist_label = ttk.Label(self.inlet_frame, text="Inlet Distance")
    self.inlet_dist_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
    
    self.inlet_dist_help = ttk.Label(self.inlet_frame, text= "?", cursor="question_arrow")
    self.inlet_dist_help.grid(row=1, column=2, padx=(5, 0))
    self.inlet_dist_help_text = "Enter the Distanz of the Inlet to the first stage as a factor of the first Blade length. Default = 2 (length between the Inlet and the first Blade Row is equal to two times the Blade length) "
    Tooltip(self.inlet_dist_help, self.inlet_dist_help_text)
    
    self.inlet_dist_entry = ttk.Entry(self.inlet_frame, width=10, textvariable=self.inlet_dist_var)
    self.inlet_dist_entry.grid(row=1, column=1, padx=5, pady=5)
    
    # Outlet        
    self.outlet_frame = ttk.LabelFrame(self.inlet_outlet_frame, text="Outlet Area Definition")
    self.outlet_frame.pack(fill='x', padx=10, pady=10)
    
    # Area
    self.outlet_area_label = ttk.Label(self.outlet_frame, text="Outlet Area")
    self.outlet_area_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
    
    self.outlet_area_help = ttk.Label(self.outlet_frame, text= "?", cursor="question_arrow")
    self.outlet_area_help.grid(row=0, column=2, padx=(5, 0))
    self.outlet_area_help_text = "Enter the Size of the Outlet as a factor of the Diameter of the last Blade Row. Default = 1 (same Size as the Diameter of the last Blade Row)"
    Tooltip(self.outlet_area_help, self.outlet_area_help_text)
    
    debug_log.debug(f"self.outlet_area_var: {self.outlet_area_var.get()}", context="threeD_tab")
    self.outlet_area_entry = ttk.Entry(self.outlet_frame, width=10, textvariable=self.outlet_area_var)
    self.outlet_area_entry.grid(row=0, column=1, padx=5, pady=5)
    
    # Distanz
    self.outlet_dist_label = ttk.Label(self.outlet_frame, text="Outlet Distance")
    self.outlet_dist_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
    
    self.outlet_dist_help = ttk.Label(self.outlet_frame, text= "?", cursor="question_arrow")
    self.outlet_dist_help.grid(row=1, column=2, padx=(5, 0))
    outlet_dist_help_text = "Enter the Distanz of the last Blade row to the Outlet as a factor of the last Blade length. Default = 2 (length between the last Blade Row and the Output is equal to two times the Blade length) "
    Tooltip(self.outlet_dist_help, outlet_dist_help_text)
    
    self.outlet_dist_entry = ttk.Entry(self.outlet_frame, width=10, textvariable=self.outlet_dist_var)
    self.outlet_dist_entry.grid(row=1, column=1, padx=5, pady=5)
    
    # Save Button
    '''
    # Save button moves to below all tabs
    self.save_button_inlet_outlet = ttk.Button(self.inlet_outlet_frame, text="Save", command=self.save_and_initialize_3D_tab)
    self.save_button_inlet_outlet.pack(pady=10, side='bottom')
    '''
    
    
def browse_output_folder(self):
    path = filedialog.askdirectory()
    if path:  
        # Glaube das sollte nicht klappen weil du hast dein outputfolder anders genannt in deiner gui als in der originalen GUI          
        self.output_folder_entry.delete(0, tk.END) # Deletes old contents
        self.output_folder_entry.insert(0, path) # Neuer Pfad

