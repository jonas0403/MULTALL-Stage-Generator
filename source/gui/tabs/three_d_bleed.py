# ------------------------------------------------------------------
# File:    source/gui/tabs/three_d_bleed.py
# Author:  Jonas Scholz, Luca De Francesco
# Purpose: Bleed-air and area-change tab + save.
# ------------------------------------------------------------------

import json
import tkinter as tk
from tkinter import ttk
from source.io.paths import JSON_PATH as json_path
from source.gui.widgets.tooltip import Tooltip
from source.logging import debug_log


def load_bleed_air_and_area_change(self):
    # Load settings from JSON
    debug_log.debug("Loading settings from json bleed air and co gets called", context="threeD_tab")
    
    try:
        with open(json_path, 'r') as file:
            all_json_data = json.load(file)
        
        # Load Metadata
        if 'Metadata' in all_json_data:
            metadata = all_json_data['Metadata']
            
            
            # [FIX] output_folder_entry is unpacked legacy (never visible); touching it here
            # broke re-render loads with TclError and aborted the whole load. The value lives
            # in prepop_metadata (owned by the Grid tab entry); save below uses that.
            
            '''
            # Not needed gets read in in grid defintion function
            if 'levels' in metadata:
                # Convert list back to comma-separated string
                
                levels_str = ', '.join(str(x) for x in metadata['levels'])
                self.levels_entry.delete(0, tk.END)
                self.levels_entry.insert(0, levels_str)
            
            if 'levels' in metadata:
                # Convert list back to comma-separated string
                levels_str = ', '.join(str(x) for x in metadata['levels'])
                
                print(f"[DEBUG] levels_str = {levels_str}")
                print(f"[DEBUG] self = {self}")
                print(f"[DEBUG] hasattr levels_entry: {hasattr(self, 'levels_entry')}")
                print(f"[DEBUG] self.__dict__ keys: {list(self.__dict__.keys())}")
                
                if hasattr(self, 'levels_entry'):
                    print(f"[DEBUG] levels_entry widget: {self.levels_entry}")
                    print(f"[DEBUG] levels_entry type: {type(self.levels_entry)}")
                    self.levels_entry.delete(0, tk.END)
                    self.levels_entry.insert(0, levels_str)
                else:
                    print("[DEBUG] ERROR: levels_entry does not exist on self!")
                    print("[DEBUG] This means the widget was never created or was created on a different instance.")
                   
                    
            if 'levels' in metadata:
                levels_str = ', '.join(str(x) for x in metadata['levels'])
                
                # Debug: check if you have a list of bleed row objects
                print(f"[DEBUG] dir(self) levels-related: {[x for x in dir(self) if 'level' in x.lower() or 'bleed' in x.lower() or 'row' in x.lower() or 'patch' in x.lower()]}")
                
                # Check rotor/stator patch entries since those exist on self
                print(f"[DEBUG] rotor_patch_entries: {self.rotor_patch_entries}")
                print(f"[DEBUG] stator_patch_entries: {self.stator_patch_entries}")
                for i, entry in enumerate(self.rotor_patch_entries):
                    print(f"[DEBUG] rotor_patch_entries[{i}] type: {type(entry)}, attrs: {[x for x in dir(entry) if 'level' in x.lower()]}")
                for i, entry in enumerate(self.stator_patch_entries):
                    print(f"[DEBUG] stator_patch_entries[{i}] type: {type(entry)}, attrs: {[x for x in dir(entry) if 'level' in x.lower()]}")
            
            ''' 
            
                    
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
                self.show_angle_dist_plot_var.set(metadata['show_angle_distribution_plots'])
        
        # Load Grid_data
        if 'Grid_data' in all_json_data:
            grid_data_not_in_use_yet = all_json_data['Grid_data']
            '''
            # Potential Addition to Prepopulted Grid Gui Tab with the last used values
            if 'nrow' in grid_data:
                self.nrow_entry.delete(0, tk.END)
                self.nrow_entry.insert(0, str(grid_data['nrow']))
            '''
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
        debug_log.debug(f"self.bleed_air_data: {self.bleed_air_data}", context="threeD_tab")
        
        # Load Intake_Outtake_area
        if 'Intake_Outtake_area' in all_json_data:
            intake_data = all_json_data['Intake_Outtake_area']
            
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
        self.prepop_intake_outtake = all_json_data.get('Intake_Outtake_area', {})
        # [FIX bugs #10/#18] push loaded counts/patches into the widgets (if built).
        self.refresh_bleed_widgets_from_data()
        
        status_msg = "Settings loaded successfully from JSON."
        print(status_msg)
        debug_log.debug(status_msg, context="load_settings")
        debug_log.debug("", context="load_settings")
    except FileNotFoundError:
        status_msg = "No previous parameters found. Starting with defaults."
        print(status_msg)
        debug_log.debug(status_msg, context="load_settings")
    except json.JSONDecodeError as e:
        err_msg = f"Error parsing JSON file: {e}"
        print(err_msg)
        debug_log.debug(err_msg, context="load_settings")
    except Exception as e:
        err_msg = f"Error loading settings: {e}"
        print(err_msg)
        debug_log.debug(err_msg, context="load_settings")

    
def update_bleed_air_display(self, *args):
    # 1. Safety Check: Does the widget exist in the Tcl interpreter?
    try:
        if not self.bleed_input_container.winfo_exists():
            return
    except (AttributeError, tk.TclError):
        # If the attribute isn't set yet or Tcl can't find the path, stop here
        return

    # 2. Logic to show or hide the container
    if self.enable_bleed_air_var.get():
        # Check if it's already visible to avoid redundant 'packing'
        if not self.bleed_input_container.winfo_ismapped():
            self.bleed_input_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Call your widget creation/update logic
        self.create_bleed_input_widget()
    else:
        # Safely hide it if it's currently visible
        if self.bleed_input_container.winfo_ismapped():
            self.bleed_input_container.pack_forget()    
    

def _widget_alive(widget):
    # [FIX] hasattr is not enough across GUI rebuilds: attributes persist on self while
    # their widgets belong to a destroyed Tcl interpreter (or a same-path different widget).
    # Only touch widgets that are alive in the current tree.
    try:
        return bool(widget.winfo_exists())
    except Exception:
        return False


def refresh_bleed_widgets_from_data(self):
    # [FIX bugs #10/#18] load_bleed_air_and_area_change() fills self.bleed_air_data only;
    # without this refresh the count boxes keep showing 0 and no patch widgets are built,
    # and a later save would write the zeros back (wiping a good stored config).
    # Safe before widgets exist (hasattr guards) and after; covers load-then-create,
    # create-then-load, and trace-triggered mid-load rebuild orders.
    data = getattr(self, "bleed_air_data", None)
    if not data:
        return
    if not (hasattr(self, "rotor_patches_entry") and hasattr(self, "rotor_frame")):
        return
    if not _widget_alive(self.rotor_patches_entry) or not _widget_alive(self.rotor_frame):
        return
    for blade_type, entry_name in (("rotor", "rotor_patches_entry"), ("stator", "stator_patches_entry")):
        try:
            count = int(data.get(blade_type, {}).get("count", 0) or 0)
        except (TypeError, ValueError):
            count = 0
        entry = getattr(self, entry_name)
        entry.delete(0, tk.END)
        entry.insert(0, str(count))
    self.update_patches("rotor")
    self.update_patches("stator")

# Old: newone above to fix timing issue of rendering children  
def create_bleed_input_widget(self):
        # Clear existing Widgets
        for widget in self.bleed_air_frame.winfo_children():
            widget.destroy()
            
        # Split window into two sides for Rotor and Stator
        self.rotor_frame = ttk.Frame(self.bleed_air_frame)
        self.rotor_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        self.stator_frame = ttk.Frame(self.bleed_air_frame)
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
        num_patches_entry = self.rotor_patches_entry
        #num_patches_str = self.rotor_patches_entry.get()
        parent_frame = self.rotor_frame
        # Save patches data in dedicated list
        self.rotor_patch_entries.clear()
        patches_data = self.bleed_air_data['rotor']['patches']
    else:
        num_patches_entry = self.stator_patches_entry
        #num_patches_str = self.stator_patches_entry.get()
        parent_frame = self.stator_frame
        # Save patches data in dedicated list
        self.stator_patch_entries.clear()
        patches_data = self.bleed_air_data['stator']['patches']
    
    # [FIX] trust the entry box (user intent): a typed 0 must stay 0. Stale-display sync
    # is handled by refresh_bleed_widgets_from_data() at load time, not here.
    num_patches_str = num_patches_entry.get()
     
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
    
    # Building stage list from self.stage  for the dropdown to choose which stage 
    stage_options = [f"Stage {i+1}" for i in range(self.stage)] if hasattr(self, 'stage') and self.stage > 0 else ["Stage 1"]
    
    # Creat new Input widget for each Patch
    for i in range(num_patches):
        patch_frame = ttk.LabelFrame(parent_frame, text=f"Bleed Air Patch {i+1}")
        patch_frame.pack(fill='x',padx=5, pady=5)
        
        patch_entries = []
        
        
        # Stage selection Dropdown menu at the top of each patch
        stage_label = ttk.Label(patch_frame, text="Stage:")
        stage_label.grid(row=0,column=0,padx=5, pady=2, sticky='w')
        stage_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
        stage_q_label.grid(row=0, column=3, padx=2, pady=2, sticky='w')
        Tooltip(stage_q_label, "Select which stage this bleed air patch applies to")
        stage_var = tk.StringVar(value=stage_options[0])
        stage_dropdown = ttk.Combobox(patch_frame, textvariable=stage_var, values=stage_options, state="readonly", width=10)
        stage_dropdown.grid(row=0, column=1, columnspan=2, padx=5, pady=2)
        

        
        # I coordinates
        i_label = ttk.Label(patch_frame, text="I start/end:")
        i_label.grid(row=1,column=0,padx=5, pady=2, sticky='w')
        i_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
        i_q_label.grid(row=1, column=3, padx=2, pady=2, sticky='w')
        Tooltip(i_q_label, " The I-Coordinates define the Spanwise direction. If using standard Grid and Blade settings, choose Values between 1 and 37. If you want to have bleed air over the whole spane enter 1 and 37")
        i_start_entry = ttk.Entry(patch_frame, width=5)
        i_start_entry.grid(row=1, column=1, padx=5, pady=2)
        i_end_entry = ttk.Entry(patch_frame, width=5)
        i_end_entry.grid(row=1, column=2, padx=5, pady=2)
        
        # J coordinates
        j_label = ttk.Label(patch_frame, text="J start/end:")
        j_label.grid(row=2,column=0,padx=5, pady=2, sticky='w')
        j_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
        j_q_label.grid(row=2, column=3, padx=2, pady=2, sticky='w')
        Tooltip(j_q_label, f"The J-Coordinates define the Axial direction. With default Gird and Bladevalues 1 is defined as the start of the Blade while 96 is defined as the End of the blade")
        j_start_entry = ttk.Entry(patch_frame, width=5)
        j_start_entry.grid(row=2, column=1, padx=5, pady=2)
        j_end_entry = ttk.Entry(patch_frame, width=5)
        j_end_entry.grid(row=2, column=2, padx=5, pady=2)
        
        # K coordinates
        k_label = ttk.Label(patch_frame, text="K start/end:")
        k_label.grid(row=3,column=0,padx=5, pady=2, sticky='w')
        k_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
        k_q_label.grid(row=3, column=3, padx=2, pady=2, sticky='w')
        Tooltip(k_q_label, "The K-Coordinate is defined as the Radial direction with 1 being the Hub wall and 37 being the Shroud wall (for the standard Grid and channel Settings). If you only want Bleed air to be extracted from one of the wall enter 1 and 1 or 37 and 37. It is also possible to extract Bleed air from the Stators and Rotors")
        k_start_entry = ttk.Entry(patch_frame, width=5)
        k_start_entry.grid(row=3, column=1, padx=5, pady=2)
        k_end_entry = ttk.Entry(patch_frame, width=5)
        k_end_entry.grid(row=3, column=2, padx=5, pady=2)
        
        # Massflow
        mflow_label = ttk.Label(patch_frame, text="Extraced Bleed Air (kg/s):")
        mflow_label.grid(row=4, column=0, padx=5, pady=2, sticky='w')
        mflow_q_label = ttk.Label(patch_frame, text="?", cursor="question_arrow")
        mflow_q_label.grid(row=4, column=3, padx=2, pady=2, sticky='w')
        Tooltip(mflow_q_label, "The massflow rate is defined in kg/s. Specify how much Bleed air you want to be extracted in this Bleed air patch")
        massflow_entry = ttk.Entry(patch_frame, width=10)
        massflow_entry.grid(row=4, column=1, columnspan=2, padx=5, pady=2)
        
        # Store Enter entries
        patch_entries.extend([stage_var, i_start_entry, i_end_entry, j_start_entry, j_end_entry, k_start_entry, k_end_entry, massflow_entry])
        
        
        debug_log.debug(f"patch_entries: {patch_entries}", context="threeD_tab")
        # Insert loaded values if exisiting
        if i < len(patches_data):
            saved_patch = patches_data[i]
            # Load stage (index 0)
            if len(saved_patch) > 0 and saved_patch[0] in stage_options:
                stage_var.set(saved_patch[0])
            # Load remaining entries (indices 1-7 in saved data into entries index 1-7)
            for idx, entry in enumerate(patch_entries[1:], start=1):
                if idx < len(saved_patch):
                    entry.insert(0, saved_patch[idx])
                    
        if blade_type == 'rotor':
            self.rotor_patch_entries.append(patch_entries)
        else: 
            self.stator_patch_entries.append(patch_entries)
        

def save_and_initialize_3D_tab(self):
    try:
        # Read existing JSON data
        with open(json_path, 'r') as file:
            all_json_data = json.load(file)
        
        # Parse levels string to list of floats
        levels_str = self.levels_entry.get()
        levels_list = [float(x.strip()) for x in levels_str.split(',')]
        
        # Save Metadata
        new_metadata = {
            "output_folder": self.prepop_metadata.get('output_folder', ''),
            "main_choice": "default",
            "levels": levels_list,
            "use_default_rotor_bezier": self.use_default_rotor_bezier_var.get(),
            "use_default_stator_bezier": self.use_default_stator_bezier_var.get(),
            "adjust_rotor_thickness": self.adjust_rotor_thickness_var.get(),
            "adjust_rotor_angle": self.adjust_rotor_angle_var.get(),
            "adjust_stator_thickness": self.adjust_stator_thickness_var.get(),
            "adjust_stator_angle": self.adjust_stator_angle_var.get(),
            "show_section_plot": self.show_section_plot_var.get(),
            "show_angle_distribution_plots": self.show_angle_dist_plot_var.get()
        }
        all_json_data['Metadata'] = new_metadata
        
        '''
        # Grid data can be ignored here
        # Save Grid_data
        new_grid_data = {
            "nrow": int(self.nrow_entry.get())
        }
        
        all_json_data['Grid_data'] = new_grid_data
        '''
        
        # Save Bleed_air_data
        enable_bleed_air = self.enable_bleed_air_var.get()
        n_rotor = len(self.rotor_patch_entries) if enable_bleed_air else 0
        n_stator = len(self.stator_patch_entries) if enable_bleed_air else 0
        # [FIX] no patches -> disabled (a stale checked box must not persist or emit cards).
        if n_rotor == 0 and n_stator == 0:
            enable_bleed_air = False
        new_bleed_air_data = {
            "enable_bleed_air": enable_bleed_air,
            "rotor_patches": n_rotor,
            "stator_patches": n_stator
        }
        
        if enable_bleed_air:
            # Save rotor patches
            for i, entries in enumerate(self.rotor_patch_entries):
                patch_data = [
                    entries[0].get(),
                    int(entries[1].get()),
                    int(entries[2].get()),
                    int(entries[3].get()),
                    int(entries[4].get()),
                    int(entries[5].get()),
                    int(entries[6].get()),
                    float(entries[7].get())
                ]
                new_bleed_air_data[f"rotor_patch_{i+1}"] = patch_data
            
            # Save stator patches
            for i, entries in enumerate(self.stator_patch_entries):
                patch_data = [
                    entries[0].get(),
                    int(entries[1].get()),
                    int(entries[2].get()),
                    int(entries[3].get()),
                    int(entries[4].get()),
                    int(entries[5].get()),
                    int(entries[6].get()),
                    float(entries[7].get())
                ]
                new_bleed_air_data[f"stator_patch_{i+1}"] = patch_data
        
        all_json_data['Bleed_air_data'] = new_bleed_air_data
        
        # Save Intake_Outtake_area
        new_intake_outtake = {
            "inlet_area": float(self.inlet_area_var.get()),
            "inlet_dist": float(self.inlet_dist_var.get()),
            "outlet_area": float(self.outlet_area_var.get()),
            "outlet_dist": float(self.outlet_dist_var.get())
        }
        all_json_data['Intake_Outtake_area'] = new_intake_outtake
        
        # Write back to JSON
        with open(json_path, 'w') as file:
            json.dump(all_json_data, file, indent=4)
        
        # Update prepopulated data 
        self.prepop_metadata = new_metadata
        #self.prepop_grid_data = new_grid_data not saving grid data here
        self.prepop_bleed_air_data = new_bleed_air_data
        self.prepop_intake_outtake = new_intake_outtake
        
        status_msg = "3D-Parameters saved and initialized."
        print(status_msg)
        debug_log.debug(status_msg, context="threeD_tab")
        
    except ValueError as e:
        err_msg = f"Error: Please enter valid numbers. {e}"
        print(err_msg)
        debug_log.debug(err_msg, context="threeD_tab")
    except Exception as e:
        err_msg = f"Error saving settings: {e}"
        print(err_msg)
        debug_log.debug(err_msg, context="threeD_tab")
    
