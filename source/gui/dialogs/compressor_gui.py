# ------------------------------------------------------------------
# File:    source/gui/dialogs/compressor_gui.py
# Author:  Jonas Scholz
# Purpose: Compressor settings dialog (second GUI window).
# ------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, filedialog
from source.gui.widgets.tooltip import Tooltip
from source.logging import debug_log


class CompressorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Settings for MULTALL file")
        self.meanline_data = None
        
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
        
        # Create notebook for multiple pages
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create frames for each section
        self.parameters_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.parameters_frame, text="Parameters")

        self.plot_options_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.plot_options_frame, text="Plot Options")
        
        self.bleed_air_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bleed_air_frame, text="Bleed Air")
        
        # Creat container frame for inputs for the bleed air
        self.bleed_input_container = ttk.Frame(self.bleed_air_frame)
        self.bleed_input_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.inlet_outlet_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inlet_outlet_frame, text="Define Inlet and Outlet")

        self.output_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.output_frame, text="Output")

        # Parameters Page
        self.use_default_rotor_bezier_var = tk.BooleanVar()
        self.use_default_rotor_bezier_var.set(False)
        ttk.Checkbutton(self.parameters_frame, text="Use default Bezier points for rotor", variable=self.use_default_rotor_bezier_var).grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.adjust_rotor_thickness_var = tk.BooleanVar()
        self.adjust_rotor_thickness_var.set(False)
        ttk.Checkbutton(self.parameters_frame, text="Adjust Bezier points of rotor for thickness distribution", variable=self.adjust_rotor_thickness_var).grid(row=1, column=0, padx=5, pady=5, sticky='w')

        self.adjust_rotor_angle_var = tk.BooleanVar()
        self.adjust_rotor_angle_var.set(False)
        ttk.Checkbutton(self.parameters_frame, text="Adjust Bezier points of rotor for blade angle distribution", variable=self.adjust_rotor_angle_var).grid(row=2, column=0, padx=5, pady=5, sticky='w')

        # Add spacing between rotor and stator parameters
        ttk.Label(self.parameters_frame, text="").grid(row=3, column=0, pady=20)

        self.use_default_stator_bezier_var = tk.BooleanVar()
        self.use_default_stator_bezier_var.set(False)
        ttk.Checkbutton(self.parameters_frame, text="Use default Bezier points for stator", variable=self.use_default_stator_bezier_var).grid(row=4, column=0, padx=5, pady=5, sticky='w')

        self.adjust_stator_thickness_var = tk.BooleanVar()
        self.adjust_stator_thickness_var.set(False)
        ttk.Checkbutton(self.parameters_frame, text="Adjust Bezier points of stator for thickness distribution", variable=self.adjust_stator_thickness_var).grid(row=5, column=0, padx=5, pady=5, sticky='w')

        self.adjust_stator_angle_var = tk.BooleanVar()
        self.adjust_stator_angle_var.set(False)
        ttk.Checkbutton(self.parameters_frame, text="Adjust Bezier points of stator for blade angle distribution", variable=self.adjust_stator_angle_var).grid(row=6, column=0, padx=5, pady=5, sticky='w')

        # Plot Options Page
        self.show_section_plot_var = tk.BooleanVar()
        self.show_section_plot_var.set(False)
        ttk.Checkbutton(self.plot_options_frame, text="Show section plot", variable=self.show_section_plot_var).grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.show_angle_distribution_plots_var = tk.BooleanVar()
        self.show_angle_distribution_plots_var.set(False)
        ttk.Checkbutton(self.plot_options_frame, text="Show angle distribution plots", variable=self.show_angle_distribution_plots_var).grid(row=1, column=0, padx=5, pady=5, sticky='w')

        
        # Inlet and Outlet Area Definition Page
        
        
        # Bleed Air Page
        # self.enable_bleed_air_var = tk.BooleanVar(value=False)
        # self.enable_bleed_air_var.trace_add("write", self.update_bleed_air_display)
        # self.enable_bleed_air_checkbox = ttk.Checkbutton(self.bleed_air_frame, text="Enable Bleed Air", variable=self.enable_bleed_air_var)
        # self.enable_bleed_air_checkbox.pack(padx=10, pady=10, anchor='w', side='top')
        
        bleed_air_container = ttk.Frame(self.bleed_air_frame)
        bleed_air_container.pack(padx=10, pady=10, anchor='w', side='top')
        
        self.enable_bleed_air_var = tk.BooleanVar(value=False)
        self.enable_bleed_air_var.trace_add("write", self.update_bleed_air_display)
        self.enable_bleed_air_checkbox = ttk.Checkbutton(bleed_air_container, text="Enable Bleed Air", variable= self.enable_bleed_air_var)
        self.enable_bleed_air_checkbox.pack(side='left')
        
        # Add Tooltip Questionmark
        help_button = ttk.Label(bleed_air_container, text="?", cursor="question_arrow")
        help_button.pack(side='left', padx=(5, 0))
        help_text = "Coordinate Explaination"
        Tooltip(help_button, help_text)
        
        # Output Page
        output_folder_label = ttk.Label(self.output_frame, text="Output Folder Path:")
        output_folder_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.output_folder_entry = ttk.Entry(self.output_frame, width=50)
        self.output_folder_entry.grid(row=0, column=1, padx=5, pady=5)

        output_folder_browse_button = ttk.Button(self.output_frame, text="Browse", command=self.browse_output_folder)
        output_folder_browse_button.grid(row=0, column=2, padx=5, pady=5)

        levels_label = ttk.Label(self.output_frame, text="Levels:")
        levels_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        self.levels_entry = ttk.Entry(self.output_frame, width=50)
        self.levels_entry.grid(row=1, column=1, padx=5, pady=5)

        nrow_label = ttk.Label(self.output_frame, text="Number of Rows [only Rotor: '1' or 1st Stage: '2']")
        nrow_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        self.nrow_entry = ttk.Entry(self.output_frame, width=10)
        self.nrow_entry.insert(0, "2")
        self.nrow_entry.grid(row=2, column=1, padx=5, pady=5)

        save_button_parameters = ttk.Button(self.parameters_frame, text="Save", command=self.save_and_initialize)
        save_button_parameters.grid(row=7, columnspan=2)

        save_button_plot_options = ttk.Button(self.plot_options_frame, text="Save", command=self.save_and_initialize)
        save_button_plot_options.grid(row=2, columnspan=2)
        
        save_button_bleed_air = ttk.Button(self.bleed_air_frame, text="Save", command=self.save_and_initialize)
        save_button_bleed_air.pack(pady=10, side='bottom')

        save_button_output_options = ttk.Button(self.output_frame, text="Save", command=self.save_and_initialize)
        save_button_output_options.grid(row=3, columnspan=3)
        
        # Define Inlet and Outlet Page
        
        inlet_outlet_title_frame = ttk.Frame(self.inlet_outlet_frame)
        inlet_outlet_title_frame.pack(fill='x', padx=10, pady=10)
        
        inlet_outlet_title_label = ttk.Label (inlet_outlet_title_frame, text="Inlet and Outlet Geometry Definition")
        inlet_outlet_title_label.pack(side='left', padx= (0, 5))
        
        inlet_outlet_help = ttk.Label(inlet_outlet_title_frame, text= "?", cursor="question_arrow")
        inlet_outlet_help.pack(side='left', padx=(5, 0))
        inlet_outlet_help_text = "Define the geometry parameters of the Inlet and Outlet Area"
        Tooltip(inlet_outlet_help, inlet_outlet_help_text)
        
        inlet_frame = ttk.LabelFrame(self.inlet_outlet_frame, text="Inlet Area Definition")
        inlet_frame.pack(fill='x', padx=10, pady=10)
        
        # Inlet 
        inlet_area_label = ttk.Label(inlet_frame, text="Inlet Area")
        inlet_area_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        # Area
        inlet_area_help = ttk.Label(inlet_frame, text= "?", cursor="question_arrow")
        inlet_area_help.grid(row=0, column=2, padx=(5, 0))
        inlet_area_help_text = "Enter the Size of the Inlet as a factor of the Diameter of the first Blade Row. Default = 1 (same Size as the Diameter of the first Blade Row)"
        Tooltip(inlet_area_help, inlet_area_help_text)
        
        self.inlet_area_entry = ttk.Entry(inlet_frame, width=10, textvariable=self.inlet_area_var)
        self.inlet_area_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Distanz
        inlet_dist_label = ttk.Label(inlet_frame, text="Inlet Distance")
        inlet_dist_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        inlet_dist_help = ttk.Label(inlet_frame, text= "?", cursor="question_arrow")
        inlet_dist_help.grid(row=1, column=2, padx=(5, 0))
        inlet_dist_help_text = "Enter the Distanz of the Inlet to the first stage as a factor of the first Blade length. Default = 2 (length between the Inlet and the first Blade Row is equal to two times the Blade length) "
        Tooltip(inlet_dist_help, inlet_dist_help_text)
        
        self.inlet_dist_entry = ttk.Entry(inlet_frame, width=10, textvariable=self.inlet_dist_var)
        self.inlet_dist_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Outlet        
        outlet_frame = ttk.LabelFrame(self.inlet_outlet_frame, text="Outlet Area Definition")
        outlet_frame.pack(fill='x', padx=10, pady=10)
        
        # Area
        outlet_area_label = ttk.Label(outlet_frame, text="Outlet Area")
        outlet_area_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        outlet_area_help = ttk.Label(outlet_frame, text= "?", cursor="question_arrow")
        outlet_area_help.grid(row=0, column=2, padx=(5, 0))
        outlet_area_help_text = "Enter the Size of the Outlet as a factor of the Diameter of the last Blade Row. Default = 1 (same Size as the Diameter of the last Blade Row)"
        Tooltip(outlet_area_help, outlet_area_help_text)
        
        self.outlet_area_entry = ttk.Entry(outlet_frame, width=10, textvariable=self.outlet_area_var)
        self.outlet_area_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Distanz
        outlet_dist_label = ttk.Label(outlet_frame, text="Outlet Distance")
        outlet_dist_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        outlet_dist_help = ttk.Label(outlet_frame, text= "?", cursor="question_arrow")
        outlet_dist_help.grid(row=1, column=2, padx=(5, 0))
        outlet_dist_help_text = "Enter the Distanz of the last Blade row to the Outlet as a factor of the last Blade length. Default = 2 (length between the last Blade Row and the Output is equal to two times the Blade length) "
        Tooltip(outlet_dist_help, outlet_dist_help_text)
        
        self.outlet_dist_entry = ttk.Entry(outlet_frame, width=10, textvariable=self.outlet_dist_var)
        self.outlet_dist_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Save Button
        save_button_inlet_outlet = ttk.Button(self.inlet_outlet_frame, text="Save", command=self.save_and_initialize)
        save_button_inlet_outlet.pack(pady=10, side='bottom')

        # Load last output folder path and levels if available
        try:
            with open('Setting.txt', 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('output_folder = '):
                        last_output_folder = line[16:].strip()
                        self.output_folder_entry.insert(0, last_output_folder)
                    elif line.startswith('levels = '):
                        last_levels = line[8:].strip()
                        self.levels_entry.delete(0)
                        self.levels_entry.insert(0, last_levels)
                    elif line.startswith('use_default_rotor_bezier'):
                        self.use_default_rotor_bezier_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('use_default_stator_bezier'):
                        self.use_default_stator_bezier_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('adjust_rotor_thickness'):
                        self.adjust_rotor_thickness_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('adjust_rotor_angle'):
                        self.adjust_rotor_angle_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('adjust_stator_thickness'):
                        self.adjust_stator_thickness_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('adjust_stator_angle'):
                        self.adjust_stator_angle_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('show_section_plot'):
                        self.show_section_plot_var.set(line.split('=')[1].strip() == 'True')
                    elif line.startswith('show_angle_distribution_plots'):
                        self.show_angle_distribution_plots_var.set(line.split('=')[1].strip() == 'True')
                    # Read Saved Bleed Air Settings
                    elif line.startswith('enable_bleed_air'):
                        self.enable_bleed_air_var.set(line.split('=')[1].strip()=='True')
                    # Read Number of Patches and its Coordinates
                    elif line.startswith('rotor_patches = '):
                        self.bleed_air_data['rotor']['count'] = int(line.split('=')[1].strip())
                    elif line.startswith('stator_patches = '):
                        self.bleed_air_data['stator']['count'] = int(line.split('=')[1].strip())
                    elif line.startswith('rotor_patches_'):
                        try:
                            values = [v.strip() for v in line.split('=')[1].strip().split(',')]
                            self.bleed_air_data['rotor']['patches'].append(values)
                        except (ValueError, IndexError) as e:
                            err_msg = f"Error parsing Rotor patchline: line={line}. Error: {e}"
                            print(err_msg)
                            debug_log.debug(err_msg, context="load_parameters")
                    elif line.startswith('stator_patches_'):
                        try:
                            values = [v.strip() for v in line.split('=')[1].strip().split(',')]
                            self.bleed_air_data['stator']['patches'].append(values)
                        except (ValueError, IndexError) as e:
                            err_msg = f"Error parsing Stator patchline: line={line}. Error: {e}"
                            print(err_msg)
                            debug_log.debug(err_msg, context="load_parameters")    
                    elif line.startswith('inlet_area = '):
                        self.inlet_area_var.set(float(line.split('=')[1].strip()))
                    elif line.startswith('inlet_dist = '):
                        self.inlet_dist_var.set(float(line.split('=')[1].strip()))
                    elif line.startswith('outlet_area = '):
                        self.outlet_area_var.set(float(line.split('=')[1].strip()))
                    elif line.startswith('outlet_dist = '):
                        self.outlet_dist_var.set(float(line.split('=')[1].strip()))



        except FileNotFoundError:
            info_msg = "No previous parameters found. Starting with defaults."
            print(info_msg)
            debug_log.debug(info_msg, context="load_parameters")
        
        # Initial call to set up the Bleed AIr Tab based on loaded values
        self.update_bleed_air_display()
        
    def update_bleed_air_display(self, *args):
        if self.enable_bleed_air_var.get():
            self.bleed_input_container.pack(fill='both', expand=True, padx=10, pady=10)
            self.create_bleed_input_widget()
        else:
            self.bleed_input_container.pack_forget()
            
    def create_bleed_input_widget(self):
        # Clear existing Widgets
        for widget in self.bleed_input_container.winfo_children():
            widget.destroy()
            
        # Split window into two sides for Rotor and Stator
        self.rotor_frame = ttk.Frame(self.bleed_input_container)
        self.rotor_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        self.stator_frame = ttk.Frame(self.bleed_input_container)
        self.stator_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
        
        # Add lables for both Rows
        ttk.Label(self.rotor_frame, text="Rotor Bleed Air", style="Bold.TLabel").pack(anchor='w')
        ttk.Label(self.stator_frame, text="Stator Bleed Air", style="Bold.TLabel").pack(anchor='w')
        
        # Add input for number of patches
        self.rotor_patches_frame = ttk.Frame(self.rotor_frame)
        self.rotor_patches_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(self.rotor_patches_frame, text="Number of Bleed Air Patches").pack(side='left')
        q_label_patches_rotor = ttk.Label(self.rotor_patches_frame, text="?", cursor="question_arrow")
        q_label_patches_rotor.pack(side='left', padx=(5, 5))
        Tooltip(q_label_patches_rotor, " Enter the number of Bleed air patches. Each patch is an area where a specific amout of air is bled from")
        self.rotor_patches_entry = ttk.Entry(self.rotor_patches_frame, width=5)
        self.rotor_patches_entry.pack(side='left')
        self.rotor_patches_entry.bind('<Return>', lambda event: self.update_patches('rotor'))
        # Insert loaded Patches
        self.rotor_patches_entry.insert(0, str(self.bleed_air_data['rotor']['count']))
        
        self.stator_patches_frame = ttk.Frame(self.stator_frame)
        self.stator_patches_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(self.stator_patches_frame, text="Number of Bleed Air Patches").pack(side='left')
        q_label_patches_stator = ttk.Label(self.stator_patches_frame, text="?", cursor="question_arrow")
        q_label_patches_stator.pack(side='left', padx=(5, 5))
        Tooltip(q_label_patches_stator, " Enter the number of Bleed air patches. Each patch is an area where a specific amout of air is bled from")
        self.stator_patches_entry = ttk.Entry(self.stator_patches_frame, width=5)
        self.stator_patches_entry.pack(side='left')
        self.stator_patches_entry.bind('<Return>', lambda event: self.update_patches('stator'))
        # Insert loaded Patches
        self.stator_patches_entry.insert(0, str(self.bleed_air_data['stator']['count']))
        
        # Call update_patches to create coordinates in fields upon loading
        self.update_patches('rotor')
        self.update_patches('stator')
        
    def update_patches(self, blade_type):
        if blade_type == 'rotor':
            num_patches_str = self.rotor_patches_entry.get()
            parent_frame = self.rotor_frame
            # Save patches data in dedicated list
            self.rotor_patch_entries.clear()
            patches_data = self.bleed_air_data['rotor']['patches']
        else:
            num_patches_str = self.stator_patches_entry.get()
            parent_frame = self.stator_frame
            # Save patches data in dedicated list
            self.stator_patch_entries.clear()
            patches_data = self.bleed_air_data['stator']['patches']
            
        try:
            num_patches = int(num_patches_str)
            if num_patches < 0:
                raise ValueError
        except (ValueError, IndexError):
            num_patches = 0
            
        # Remove previouse Patch Frames
        for widget in parent_frame.winfo_children():
            # Check if widget is in a patch inputframe
            if isinstance(widget, ttk.LabelFrame):
                widget.destroy()
        
        # Creat new Input widget for each Patch
        for i in range(num_patches):
            patch_frame = ttk.LabelFrame(parent_frame, text=f"Bleed Air Patch {i+1}")
            patch_frame.pack(fill='x',padx=5, pady=5)
            
            patch_entries = []
            
            # I coordinates
            i_label = ttk.Label(patch_frame, text="I start/end:")
            i_label.grid(row=0,column=0,padx=5, pady=2, sticky='w')
            i_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
            i_q_label.grid(row=0, column=3, padx=2, pady=2, sticky='w')
            Tooltip(i_q_label, " The I-Coordinates define the Spanwise direction. Choose Values between 1 and 37. If you want to have bleed air over the whole spane enter 1 and 37")
            i_start_entry = ttk.Entry(patch_frame, width=5)
            i_start_entry.grid(row=0, column=1, padx=5, pady=2)
            i_end_entry = ttk.Entry(patch_frame, width=5)
            i_end_entry.grid(row=0, column=2, padx=5, pady=2)
            
            # J coordinates
            j_label = ttk.Label(patch_frame, text="J start/end:")
            j_label.grid(row=1,column=0,padx=5, pady=2, sticky='w')
            j_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
            j_q_label.grid(row=1, column=3, padx=2, pady=2, sticky='w')
            Tooltip(j_q_label, f"The J-Coordinates define the Axial direction. 1 is defined as the start of the Blade while {JTE} is defined as the End of the blade")
            j_start_entry = ttk.Entry(patch_frame, width=5)
            j_start_entry.grid(row=1, column=1, padx=5, pady=2)
            j_end_entry = ttk.Entry(patch_frame, width=5)
            j_end_entry.grid(row=1, column=2, padx=5, pady=2)
            
            # K coordinates
            k_label = ttk.Label(patch_frame, text="K start/end:")
            k_label.grid(row=2,column=0,padx=5, pady=2, sticky='w')
            k_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
            k_q_label.grid(row=2, column=3, padx=2, pady=2, sticky='w')
            Tooltip(k_q_label, "The K-Coordinate is defined as the Radial direction with 1 being the Hub wall and 37 being the Shroud wall. If you only want Bleed air to be extracted from one of the wall enter 1 and 1 or 37 and 37. It is also possible to extract Bleed air from the Stators and Rotors")
            k_start_entry = ttk.Entry(patch_frame, width=5)
            k_start_entry.grid(row=2, column=1, padx=5, pady=2)
            k_end_entry = ttk.Entry(patch_frame, width=5)
            k_end_entry.grid(row=2, column=2, padx=5, pady=2)
            
            # Massflow
            mflow_label = ttk.Label(patch_frame, text="Extraced Bleed Air (kg/s):")
            mflow_label.grid(row=3, column=0, padx=5, pady=2, sticky='w')
            mflow_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
            mflow_q_label.grid(row=3, column=3, padx=2, pady=2, sticky='w')
            Tooltip(mflow_q_label, "The massflow rate is defined in kg/s. Specify how much Bleed air you want to be extracted in this Bleed air patch")
            massflow_entry = ttk.Entry(patch_frame, width=10)
            massflow_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=2)
            
            # Store Enter entries
            patch_entries.extend([i_start_entry, i_end_entry, j_start_entry, j_end_entry, k_start_entry, k_end_entry, massflow_entry])
            
            # Insert loaded values if exisiting
            if i < len(patches_data):
                for idx, entry in enumerate(patch_entries):
                    if idx < len(patches_data[i]):
                        entry.insert(0,patches_data[i][idx])
                        
            if blade_type == 'rotor':
                self.rotor_patch_entries.append(patch_entries)
            else: 
                self.stator_patch_entries.append(patch_entries)
            

    def browse_output_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, path)

    def save_and_initialize(self):
        use_default_rotor_bezier = self.use_default_rotor_bezier_var.get()
        use_default_stator_bezier = self.use_default_stator_bezier_var.get()
        adjust_rotor_thickness = self.adjust_rotor_thickness_var.get()
        adjust_rotor_angle = self.adjust_rotor_angle_var.get()
        adjust_stator_thickness = self.adjust_stator_thickness_var.get()
        adjust_stator_angle = self.adjust_stator_angle_var.get()
        output_folder = self.output_folder_entry.get()
        
        levels = self.levels_entry.get()
        nrow = self.nrow_entry.get()
        
        show_section_plot = self.show_section_plot_var.get()
        show_angle_distribution_plots = self.show_angle_distribution_plots_var.get()
        
        inlet_area = self.inlet_area_var.get()
        inlet_dist = self.inlet_dist_var.get()
        outlet_area = self.outlet_area_var.get()
        outlet_dist = self.outlet_dist_var.get()
        
        # Get bleed Air Settings
        enable_bleed_air = self.enable_bleed_air_var.get()

        with open('Setting.txt', 'w') as file:
            file.write(f"use_default_rotor_bezier = {use_default_rotor_bezier}\n")
            file.write(f"use_default_stator_bezier = {use_default_stator_bezier}\n")
            file.write(f"adjust_rotor_thickness = {adjust_rotor_thickness}\n")
            file.write(f"adjust_rotor_angle = {adjust_rotor_angle}\n")
            file.write(f"adjust_stator_thickness = {adjust_stator_thickness}\n")
            file.write(f"adjust_stator_angle = {adjust_stator_angle}\n")
            file.write(f"output_folder = {output_folder}\n")
            file.write(f"levels = {levels}\n")
            file.write(f"nrow = {nrow}\n")
            file.write(f"show_section_plot = {show_section_plot}\n")
            file.write(f"show_angle_distribution_plots = {show_angle_distribution_plots}\n")
            # Save Bleed Air data
            file.write(f"enable_bleed_air = {enable_bleed_air}\n")
            if enable_bleed_air:
                file.write(f"rotor_patches = {len(self.rotor_patch_entries)}\n")
                for i, entries in enumerate(self.rotor_patch_entries):
                    i_start = entries[0].get()
                    i_end= entries[1].get()
                    j_start = entries[2].get()
                    j_end= entries[3].get()
                    k_start = entries[4].get()
                    k_end= entries[5].get()
                    massflow = entries[6].get()
                    file.write(f"rotor_patch_{i+1} = {i_start}, {i_end}, {j_start}, {j_end}, {k_start}, {k_end}, {massflow}\n")
                    
                file.write(f"stator_patches = {len(self.stator_patch_entries)}\n")
                for i, entries in enumerate(self.stator_patch_entries):
                    i_start = entries[0].get()
                    i_end= entries[1].get()
                    j_start = entries[2].get()
                    j_end= entries[3].get()
                    k_start = entries[4].get()
                    k_end= entries[5].get()
                    massflow = entries[6].get()
                    file.write(f"stator_patch_{i+1} = {i_start}, {i_end}, {j_start}, {j_end}, {k_start}, {k_end}, {massflow}\n")
                    
            file.write(f"inlet_area = {inlet_area}\n")
            file.write(f"inlet_dist = {inlet_dist}\n")
            file.write(f"outlet_area = {outlet_area}\n")
            file.write(f"outlet_dist = {outlet_dist}\n")

        save_msg = "Parameters saved successfully."
        print(save_msg)
        debug_log.debug(save_msg, context="save_parameters")


if __name__ == "__main__":
    
    root = tk.Tk() 
    app = CompressorGUI(root) 
    root.mainloop()
