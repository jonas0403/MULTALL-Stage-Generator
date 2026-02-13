import tkinter as tk
import numpy as np
import matplotlib as plt
import matplotlib.pyplot as plt
import os 
import shutil
import json
#from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, filedialog, Label, Toplevel
from pathlib import Path
#from matplotlib.widgets import Slider

from Stage_v3_working_with_bleedair import create_default_profiles, calculation_of_section, run_main_logic
from Cubspline_function_v2 import cubspline
from Thermodynamic_calc_GUI import Thermo

current_dir = Path(__file__).parent.parent
static_folder = current_dir/ "static"
json_file = 'Populated_data.json'


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
        json_path = static_folder / json_file
        
        with open(json_path, 'r') as file:
            data = json.load(file)

            self.perpop_thermo_data = data['Thermodynamic_input_data']
            self.prepop_meanline_input_data = data['Meanline_input_data']
            self.prepop_diameter_data = data['Diameter_data']
            self.prepop_bezier_point_stator = data['Bezier_point_data']['stator']
            self.prepop_bezier_point_rotor = data['Bezier_point_data']['rotor']
            self.prepop_metadata = data['Metadata']
        

        
    
                
    ## Tab_Entrys
    def zeroD_tab(self, window):
            ttk.Label(window, text="This is the 0D Settings tab").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')
            ### Thermodynamic Parameters Tab
           

            read_initial_values(static_folder/ "Thermo_Initial_Values.txt")

            entries = {}

            #window.add(window, text="Thermodynamic Parameters")

            params = ['p_t_in', 'T_t_in', 'mflow', 'R', 'cp', 'TPR']
            gui_names = ['p_t_in [Pa]', 'T_t_in [K]', 'mflow [kg/s]', 'R [J/kg*K]', 'cp [J/kg*K]', 'TPR [-]']
            path = os.getcwd()
            print(path)
            for i, param in enumerate(params):
                ttk.Label(window, text=f"{gui_names[i]}:").grid(row=i+1, column=0, padx=5, pady=5, sticky='w')
                entries[param] = []
                entry = ttk.Entry(window, width=15)
                entry.insert(0, str(globals()[param]))
                entry.grid(row=i+1, column=1, padx=5, pady=5)
                entries[param].append(entry)

            def save_and_initialize():
                try:
                    current_values_thermo = {}
                    for var_name in entries.keys():
                        val = float(entries[var_name][0].get())
                        globals()[var_name] = val
                        current_values_thermo[var_name] = val
                
                    with open('Thermo_Initial_Values.txt', 'w') as file:
                        file.write(f"p_t_in = {current_values_thermo['p_t_in']}\n")
                        file.write(f"T_t_in = {current_values_thermo['T_t_in']}\n")
                        file.write(f"mflow = {current_values_thermo['mflow']}\n")
                        file.write(f"R = {current_values_thermo['R']}\n")
                        file.write(f"cp = {current_values_thermo['cp']}\n")
                        file.write(f"TPR = {current_values_thermo['TPR']}\n")
                        
                    print("Parameters saved and initialized.")
                    
                    self.Thermodata =  Thermo(
                        current_values_thermo['p_t_in'],
                        current_values_thermo['T_t_in'],
                        current_values_thermo['mflow'],
                        current_values_thermo['R'],
                        current_values_thermo['cp'],
                        current_values_thermo['TPR']
                    )
                    print("Calculation of Thermodynamic Data completed.") 
                except ValueError:
                    print("Please enter valid numbers for all conditions.")
                    
                
                

            ttk.Button(window, text="Save and Initialize Parameters", command=save_and_initialize).grid(row=len(params)+1, column=0, columnspan=2, pady=10)
            save_and_initialize()       
            

    def oneD_tab(self, parent_frame, i_st_val):
            
        '''
        Define Names for Settings.json and Lockfile
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
        # Create reverse mapping
        gui_to_var_map = {v: k for k, v in var_name_to_gui_map.items()}
        
        LOCK_FILE = static_folder/"settings.lock"
        SETTINGS_FILE = static_folder/"Diameter_Values.txt"       
        
    
        '''
        Not in use
        '''    
        def create_input_window(i_st_val):
            # Creates Gui to Input the fixed Diameters and the type of fixed Diameters

            # Initialize Variables
            D_f1_result = [0.508]*i_st_val 
            D_f2_result = [0.508]*i_st_val
            D_f3_result = [0.508]*i_st_val
            fixed_radius_type = "none"# "shroud" , "mean" , "hub" , "none"
            
            plot_channel_contour = False # Default to False
            
            # List to hold StringVar objexts for each diameter entry
            D_f1_entry_vars = [] 
            D_f2_entry_vars = []
            D_f3_entry_vars = []
            
            def on_save():
                nonlocal fixed_radius_type, D_f1_result, D_f2_result, D_f3_result, plot_channel_contour

                selected_type = type_var.get()
                if not selected_type:
                    if os.path.exists(LOCK_FILE):
                        os.remove(LOCK_FILE)
                    messagebox.showerror("Input Error", "Please select a fixed radius type.")
                    return

                # Validate and parse D_f entries
                try:
                    # Iterate through D_f_entry_vars to get values for each stage
                    temp_D_f1 = []
                    temp_D_f2 = []
                    temp_D_f3 = []
                    
                    for i in range(i_st_val):
                        temp_D_f1.append(float(D_f1_entry_vars[i].get().strip()))
                        temp_D_f2.append(float(D_f2_entry_vars[i].get().strip()))
                        temp_D_f3.append(float(D_f3_entry_vars[i].get().strip()))
                    
                    D_f1_result = temp_D_f1
                    D_f2_result = temp_D_f2
                    D_f3_result = temp_D_f3
                    
                    fixed_radius_type = selected_type
                    plot_channel_contour = plot_var.get() # Get checkbox value
                    root.destroy() # Close the window
                except ValueError:
                    messagebox.showerror("Input Error", "Please enter numerical values for D_f, separated by commas.")
                except Exception as e:
                    if os.path.exists(LOCK_FILE):
                        os.remove(LOCK_FILE)
                    messagebox.showerror("Error", f"An unexpected error occurred: {e}")
                
                
            def update_default_diameters(args):
                # This function is called when the fixed_radius_type changes
                current_type = type_var.get()
                default_val = "0.508" # Default for shroud/hub, adjust as needed

                if current_type == "shroud":
                    default_val = "0.740"
                elif current_type == "hub":
                    default_val = "0.274" # Example: different default for hub
                elif current_type == "mean":
                    default_val = "0.508" # Example: different default for mean
                elif current_type == "none":
                    default_val = "0.0" # Example: default to zero if 'none' fixed
                
                # Update the entry fields with the new default values
                for i in range(i_st_val):
                    D_f1_entry_vars[i].set(default_val)
                    D_f2_entry_vars[i].set(default_val)
                    D_f3_entry_vars[i].set(default_val)    
                    
            #Function to toggle entry state
            def toggle_diameter_entries():
                state = "disabled" if use_default_var.get() else "normal"
                for i in range(i_st_val):
                    D_f1_entries[i].config(state=state)
                    D_f2_entries[i].config(state=state)
                    D_f3_entries[i].config(state=state)

                # If default is selected, apply default values
                if use_default_var.get():
                    update_default_diameters()
            
            def on_closing():
                root.destroy()
                if os.path.exists(LOCK_FILE):
                        os.remove(LOCK_FILE)
        
            root = tk.Tk()
            root.title("Channel Contour Window")
            
            # Select Fixed Radius Type
            tk.Label(root, text="Select Fixed Radius Type:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            type_var = tk.StringVar(root)
            type_options = ["shroud", "mean", "hub", "none"]
            type_var.set(type_options[0]) # default value
            type_menu = tk.OptionMenu(root, type_var, *type_options)
            type_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew", columnspan=i_st_val)
            
            # Bind the update function to the type_var
            type_var.trace_add("write", update_default_diameters)
            
            # Add text Window 
            message_frame = tk.LabelFrame(root, text="Important Note", padx=10, pady=10, relief="groove", borderwidth=2)
            message_frame.grid(row=1, column=0, columnspan=1+i_st_val, padx=10, pady=10, sticky="ew")
            
            tk.Label(message_frame, 
                    text="D_f3 of each but the last stage must be equal to D_f1 of the following stage", 
                    font=("TkDefaultFont", 10, "bold"), 
                    fg="blue", # Optional: make text blue for emphasis
                    wraplength=400, # Wrap text if it's too long
                    justify="center").grid(row=0, column=0, padx=5, pady=5)
            
            
            # StringVars for entry fields
            D_f1_entries = []
            D_f2_entries = []
            D_f3_entries = []
            
            # Dynamic creation of D_f input fileds
            # Start row for D_f inputs, adjusted for new checkbox and message frame
            current_row = 2
            
            # Add column headers for each stage
            tk.Label(root, text="").grid(row=current_row,column=0) # Empty label for alligning over the text boxes
            
            for i in range(i_st_val):
                tk.Label(root,text=f"Stage {i+1}", font=("TkDefaultFont",10, "bold")).grid(row=current_row, column=1+i, padx=5, pady=2, sticky="ew")
                
            current_row += 1
            
            tk.Label(root, text=f"Enter D_f1 ").grid(row=current_row, column=0, padx=10, pady=2, sticky="w")
            tk.Label(root, text=f"Enter D_f2 ").grid(row=current_row+1, column=0, padx=10, pady=2, sticky="w")
            tk.Label(root, text=f"Enter D_f3 ").grid(row=current_row+2, column=0, padx=10, pady=2, sticky="w")
            
            for i in range(i_st_val):
                # D_f1 Input
                D_f1_var=tk.StringVar(root)
                entry_D_f1 = tk.Entry(root, width=15, textvariable=D_f1_var)
                entry_D_f1.grid(row=current_row, column=1+i, padx=5, pady=2, sticky="ew")
                D_f1_entry_vars.append(D_f1_var)
                D_f1_entries.append(entry_D_f1) 
                
                # D_f2 Input
                D_f2_var=tk.StringVar(root)
                entry_D_f2 = tk.Entry(root, width=15, textvariable=D_f2_var)
                entry_D_f2.grid(row=current_row+1, column=1+i, padx=5, pady=2, sticky="ew")
                D_f2_entry_vars.append(D_f2_var)
                D_f2_entries.append(entry_D_f2) 
                
                # D_f3 Input
                D_f3_var=tk.StringVar(root)
                entry_D_f3 = tk.Entry(root, width=15, textvariable=D_f3_var)
                entry_D_f3.grid(row=current_row+2, column=1+i, padx=5, pady=2, sticky="ew")
                D_f3_entry_vars.append(D_f3_var)
                D_f3_entries.append(entry_D_f3) 


            # Initialize entry fields with default values based on the initial type_var
            update_default_diameters() # Call once to set initial defaults
            
            
            
            # Checkbox for the "Use default Diameters"
            use_default_var = tk.BooleanVar(root)
            use_default_var.set(False) # Defaults to unchecked
            checkbutton_use_default = tk.Checkbutton(root, text= "Use default Diameters for the fixed radius type", variable=use_default_var, command=toggle_diameter_entries)
            checkbutton_use_default.grid(row=current_row+3, column=0, columnspan=1+i_st_val, pady=5)
        
            # Checkbutton for plotting channel contour
            plot_var = tk.BooleanVar(root)
            plot_var.set(True) # Default to checked (True)
            checkbutton_plot = tk.Checkbutton(root, text="Plot Channel Contour", variable=plot_var)
            checkbutton_plot.grid(row=current_row +4, column=0, columnspan=1+i_st_val, pady=5)

            # Delete LOCK-File on closing of the window
            root.protocol("WM_DELETE_WINDOW", on_closing)

            # Save Button
            save_button = tk.Button(root, text="Save and Continue", command=on_save)
            save_button.grid(row=current_row+5, column=0, columnspan=1+i_st_val, pady=10)

            # Make the window modal (optional, but good practice for input dialogs)
            root.grab_set()
            
            toggle_diameter_entries()
            
            root.wait_window()
            
            write_diameters(SETTINGS_FILE,fixed_radius_type, D_f1_result, D_f2_result, D_f3_result, plot_channel_contour)
            return fixed_radius_type, D_f1_result, D_f2_result, D_f3_result, plot_channel_contour


            '''
        Not in use
        ''' 
        

        '''
        ' Helping functions for the meanline gui creation.
        ' 
        '''
        def create_scrollable_frame(container):
            canvas = tk.Canvas(container)
            scrollbar = tk.Scrollbar(container, orient='vertical', command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            
            scrollable_frame.pack(fill='both', expand=True)
            
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            
            frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
            
            canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width))
            
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Bind Mouswheel
            def _on_mousewheel(event):
                if event.num == 4 or event.delta > 0:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5 or event.delta < 0:
                    canvas.yview_scroll(1, "units")
                    
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            return canvas, scrollbar, scrollable_frame

        class diameter_gui:
            def __init__(self, root, i_st_val, on_close_callback, initial_data):
                self.root = root
                self.on_close_callback = on_close_callback
                self.num_stages = i_st_val
                self.num_points = 2 * i_st_val + 1
                
                # Standard values for the different fixed radius types
                self.default_values = {
                    "shroud": [0.800] * self.num_points,
                    "mean": [0.508] * self.num_points,
                    "hub": [0.274] * self.num_points
                }
                
                # Initial slider Values loaded out of the settings file 
                self.initial_type, self.initial_D_f1, self.initial_D_f2, self.initial_D_f3, self.initial_plot_contour = initial_data
                
                # Initialize this data
                self.cubspline_points = []
                if self.initial_D_f1 and self.initial_D_f2:
                    for i in range(len(self.initial_D_f1)):
                        if i == 0:
                            self.cubspline_points.append(self.initial_D_f1[0])
                            self.cubspline_points.append(self.initial_D_f2[0])
                            self.cubspline_points.append(self.initial_D_f3[0])
                        else:   #if i == len(self.initial_D_f1)-1: 
                            self.cubspline_points.append(self.initial_D_f2[i])
                            self.cubspline_points.append(self.initial_D_f3[i])
                else: 
                    self.cubspline_points = [1] * self.num_points
                
                self.t = np.arange(0, 1.01, 0.01)
                print(f"self.cubspline_points={self.cubspline_points}")
                
                # Define x-cood for Bezier-Points
                self.mB = np.linspace(0.0, 1.0, self.num_points)
                
                # Define slider limits based on fixed Radius type 
                self.limits = {
                    "shroud": (0.4, 1.2),
                    "mean": (0.25, 0.8),
                    "hub": (0.05, 0.6)
                }
                
                self.root.title("Choose Channel Contour Diameter")
                self.root.geometry("600x800")
                
                # Create main Frames
                self.top_frame = tk.Frame(root)
                self.top_frame.pack(side='top', fill='x', padx=10, pady=10)
                
                self.plot_frame = tk.Frame(root)
                self.plot_frame.pack(side='top', fill='both', expand=True)
                
                self.bottom_frame = tk.Frame(root)
                self.bottom_frame.pack(side='bottom', fill='both', expand=True)
                
                # Dropdown Menu 
                tk.Label(self.top_frame, text="Select fixed Radius type: ").pack(padx=10, pady=5, anchor='w')
                self.type_var = tk.StringVar(root)
                self.type_options = list(self.limits.keys())
                self.type_var.set(self.initial_type)
                self.type_menu = tk.OptionMenu(self.top_frame, self.type_var, *self.type_options, command=self.update_slider_limit)
                self.type_menu.pack(padx=10, pady=5, fill='x', expand=True)
                
                # Checkbox for Plot Contour Channel
                self.plot_channel_var = tk.BooleanVar(value=self.initial_plot_contour)
                self.plot_channel_checkbox = tk.Checkbutton(self.top_frame, text="Plot the channel contour", variable=self.plot_channel_var)
                self.plot_channel_checkbox.pack(padx=10, pady=5, anchor='w')
                
                # Plot
                self.fig, self.ax = plt.subplots(figsize=(5,4))
                self.ax.set_title("Fixed Diameter Contour")
                self.ax.set_xlabel("x / channel length")
                self.ax.set_ylabel("D [m]")
                self.ax.set_xlim(0, 1)
                self.ax.set_ylim(self.limits[self.type_var.get()])
                self.curve, = self.ax.plot([], [], 'b-')
                self.points, = self.ax.plot([], [], 'o', color='red', label="Control Points")
                
                self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(fill='both', expand=True)
                
                # Use Scrollable Frame 
                self.slider_canvas, self.slider_scrollbar, self.slider_frame = create_scrollable_frame(self.bottom_frame)
                self.slider_scrollbar.pack(side='right', fill= 'y')
                self.slider_canvas.pack(side='left', fill='both', expand=True)
                
                # Frame for Sliders
                #self.sliders_frame = tk.Frame(self.bottom_frame)
                #self.sliders_frame.pack(side='top', fill='both', expand=True)
                
                # SLiders and the Enrtybox
                self.sliders = []
                self.entries = []
                
                for i in range(self.num_points):
                    row_frame = tk.Frame(self.slider_frame)
                    row_frame.pack(padx=5, pady=5, fill='x')
                    
                    # Label
                    label = tk.Label(row_frame, text=f"Points {i+1}")
                    label.pack(side='left', padx=(0, 5))
                    
                    # Entrybox
                    entry_var = tk.DoubleVar(value=self.cubspline_points[i])
                    entry = tk.Entry(row_frame, width=8, textvariable=entry_var)
                    entry.pack(side='right')
                    entry.bind('<Return>', lambda event, idx=i: self.update_from_box(idx))
                    self.entries.append(entry)
                    
                    # SLiders
                    min_val, max_val = self.limits[self.type_var.get()]
                    slider = tk.Scale(row_frame, from_=min_val, to=max_val, orient='horizontal', resolution=0.01)
                    slider.set(self.cubspline_points[i])
                    slider.configure(command=lambda val, idx=i: self.update_from_slider(float(val), idx))
                    slider.pack(side='left', fill='x', expand=True)
                    self.sliders.append(slider)
                
                # Button Frame   
                self.button_frame = tk.Frame(self.slider_frame)
                self.button_frame.pack(side='top', fill='x', padx= 5, pady=10)
                
                self.save_button = tk.Button(self.button_frame, text="Save and Exit", command=self.save_and_exit)
                self.save_button.pack(side='left', padx=5, expand=True, fill='x')
                
                self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
                
                # Initial plot setup
                self.update_plot()
                
            def update_plot(self):
                # Updates Plot and the curve in it
                x_points = self.mB.tolist()
                y_points = self.cubspline_points
                
                y = [cubspline(1, xi, x_points, y_points) for xi in self.t.tolist()]
                self.curve.set_xdata(self.t)
                self.curve.set_ydata(y)
                self.points.set_xdata(self.mB)
                self.points.set_ydata(self.cubspline_points)
                self.fig.canvas.draw_idle()
                
            def update_slider_limit(self, selected_type):
                # Updates Slider Range base on the fixed Radius type
                min_val, max_val = self.limits[selected_type]
                self.ax.set_ylim(min_val, max_val)
                
                new_val = self.default_values.get(selected_type, [])
                
                for i, slider in enumerate(self.sliders):
                    slider.configure(from_=min_val, to=max_val)
                    # Update slider position on fixed radius type change
                    if i < len(new_val):
                        slider.set(new_val[i])
                        self.cubspline_points[i] = new_val[i]
                        self.entries[i].delete(0, tk.END)
                        self.entries[i].insert(0, f"{new_val[i]:.4f}")
                
                # Update Plot to change Plot
                self.update_plot()
            
            def update_from_slider(self, val, idx):
                # Updates sliders and synchronizes entryboxes
                self.cubspline_points[idx] = val
                self.entries[idx].delete(0, tk.END)
                self.entries[idx].insert(0, f"{val:.4f}")
                self.update_plot()
                
            def update_from_box(self, idx):
                # Updates Entrybox and synchonizes slider
                try:
                    val = float(self.entries[idx].get())
                    min_val = self.sliders[idx].cget("from")
                    max_val = self.sliders[idx].cget("to")
                    
                    if min_val <= val <= max_val:
                        self.sliders[idx].set(val)
                        self.cubspline_points[idx] = val
                        self.update_plot()
                    else:
                        messagebox.showerror("Invalid Input", f"Value must be between {min_val:.4f} and {max_val:.4f}")
                        self.entries[idx].delete(0, tk.END)
                        self.entries[idx].insert(0, f"{self.sliders[idx].get():.4f}")
                
                except:
                    messagebox.showerror("Invalid Input", "Please enter a Valid Number")
                    self.entries[idx].delete(0, tk.END)
                    self.entries[idx].insert(0, f"{self.sliders[idx].get():.4f}")
                    
            def save_and_exit(self):
                self.on_closing()
                    
            def on_closing(self):
                # Called when window is closed
                # Returns all points
                
                # Saving all Data
                D_f1, D_f2, D_f3 = [0] * self.num_stages,  [0] * self.num_stages,  [0] * self.num_stages
                
                
                
                for i in range(self.num_stages):
                    if i == 0:
                        D_f1[i] = self.cubspline_points[0]
                        D_f2[i] = self.cubspline_points[1]
                        D_f3[i] = self.cubspline_points[2]
                    elif i == self.num_stages - 1:
                        D_f1[i] = self.cubspline_points[len(self.cubspline_points)-3]
                        D_f2[i] = self.cubspline_points[len(self.cubspline_points)-2]
                        D_f3[i] = self.cubspline_points[len(self.cubspline_points)-1]
                    else:
                        D_f1[i] = self.cubspline_points[i*2]
                        D_f2[i] = self.cubspline_points[i*2+1]
                        D_f3[i] = self.cubspline_points[i*2+2]
                        
                    
                # Call writing function
                fixed_radius_type = self.type_var.get()
                plot_channel_contour = self.plot_channel_var.get()
                #write_diameters(SETTINGS_FILE, fixed_radius_type, D_f1, D_f2, D_f3, plot_channel_contour)    
                
                self.on_close_callback(D_f1, D_f2, D_f3, fixed_radius_type, plot_channel_contour)
                self.root.destroy()
                plt.close(self.fig)
                
        def run_diameter_gui(i_st):
            root = tk.Tk()
            D_f1, D_f2, D_f3 = [],  [],  []
            fixed_radius_type = ""
            plot_channel_contour = False
            
            def on_close(d1, d2, d3, type_var, plot_var):
                nonlocal D_f1, D_f2, D_f3, fixed_radius_type, plot_channel_contour
                D_f1 = d1
                D_f2 = d2
                D_f3 = d3
                fixed_radius_type = type_var
                plot_channel_contour = plot_var
                
            # Read Initial Data from File
            initial_data = read_diameter(SETTINGS_FILE)    
            diameter_gui(root, i_st, on_close, initial_data)
            root.mainloop()
            print(f"D_f1={D_f1}, D_f2={D_f2}, D_f3={D_f3}, fixed_radius_type={fixed_radius_type}, plot_channel_contour={plot_channel_contour}")
            return D_f1, D_f2, D_f3, fixed_radius_type, plot_channel_contour
                    
            
        def read_diameter(filename):
            
            fixed_radius_typ = None
            D_f1 = None
            D_f2 = None
            D_f3 = None
            plot_channel_contour = None

            with open(filename,'r') as file:
                for line in file:
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    if line.startswith('Fixed Radius Typ ='):
                        fixed_radius_typ = line.split('=')[1].strip(" '[]\n").replace("'","") 
                    elif line.startswith('D_f1 ='):
                        D_f1 = [float(x) for x in line.split('=')[1].strip('[] ').split(',')]
                    elif line.startswith('D_f2 ='):
                        D_f2 = [float(x) for x in line.split('=')[1].strip('[] ').split(',')]
                    elif line.startswith('D_f3 ='):
                        D_f3 = [float(x) for x in line.split('=')[1].strip('[] ').split(',')]
                    elif line.startswith('Plot Channel Contour ='):
                        plot_channel_contour = line.split('=')[1].strip(" '[]\n").replace("'","") 

            return fixed_radius_typ, D_f1, D_f2, D_f3, plot_channel_contour

        def write_diameters(filename,fixed_radius_typ, D_f1, D_f2, D_f3, plot_channel_contour):
            # Check if there is a Lock File. Lock file is created to signal that the GUI and Diameters_values.txt was writen/modified 
            if os.path.exists(LOCK_FILE):
                print("Lock File was found. Reading Diameters_Values.txt")
                return
            # If no Lock File exists create one
            try:
                with open(LOCK_FILE,'w') as f:
                    f.write("running")
                # Registers a function to delete the Lock File if Programm is exited normally

                print(f"D_f1={D_f1}, D_f2={D_f2}, D_f3={D_f3}, fixed_radius_type={fixed_radius_typ}, plot_channel_contour={plot_channel_contour}")
                with open(filename, 'w') as file:
                    file.write(f'Fixed Radius Typ = {fixed_radius_typ}\n')
                    file.write(f'D_f1 = {D_f1}\n')
                    file.write(f'D_f2 = {D_f2}\n')
                    file.write(f'D_f3 = {D_f3}\n')
                    file.write(f'Plot Channel Contour = {plot_channel_contour}')
                print("Settings were written succesfully ")

            except Exception as e:
                print(f"Error dring writting of the Diameters_Values.txt: {e}")
                # Delete Lock File in case of an error
                if os.path.exists(LOCK_FILE):
                    os.remove(LOCK_FILE)

        def read_initial_values(filename):
            global n, psi_h, phi_1, phi_2, phi_3
            global z_R, l_R, d_R_l_R, d_Cl_R, d_TE_R, incidence_R
            global z_S, l_S, d_S_l_S, d_TE_S, d_CL_S, incidence_S

            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('n = '):
                        n = [float(x) for x in line[4:].strip('[]').split(',')]
                    elif line.startswith('psi_h = '):
                        psi_h = [float(x) for x in line[8:].strip('[]').split(',')]
                    elif line.startswith('phi_1 = '):
                        phi_1 = [float(x) for x in line[8:].strip('[]').split(',')]
                    elif line.startswith('phi_2 = '):
                        phi_2 = [float(x) for x in line[8:].strip('[]').split(',')]
                    elif line.startswith('phi_3 = '):
                        phi_3 = [float(x) for x in line[8:].strip('[]').split(',')]
                    elif line.startswith('z_R = '):
                        z_R = [int(x) for x in line[6:].strip('[]').split(',')]
                    elif line.startswith('l_R = '):
                        l_R = [float(x) for x in line[6:].strip('[]').split(',')]
                    elif line.startswith('d_R_l_R = '):
                        d_R_l_R = [float(x) for x in line[11:].strip('[]').split(',')]
                    elif line.startswith('d_Cl_R = '):
                        d_Cl_R = [float(x) for x in line[10:].strip('[]').split(',')]
                    elif line.startswith('d_TE_R = '):
                        d_TE_R = [float(x) for x in line[10:].strip('[]').split(',')]
                    elif line.startswith('incidence_R = '):
                        incidence_R = [float(x) for x in line[14:].strip('[]').split(',')]
                    elif line.startswith('z_S = '):
                        z_S = [int(x) for x in line[6:].strip('[]').split(',')]
                    elif line.startswith('l_S = '):
                        l_S = [float(x) for x in line[6:].strip('[]').split(',')]
                    elif line.startswith('d_S_l_S = '):
                        d_S_l_S = [float(x) for x in line[11:].strip('[]').split(',')]
                    elif line.startswith('d_TE_S = '):
                        d_TE_S = [float(x) for x in line[10:].strip('[]').split(',')]
                    elif line.startswith('d_CL_S = '):
                        d_CL_S = [float(x) for x in line[10:].strip('[]').split(',')]
                    elif line.startswith('incidence_S = '):
                        incidence_S = [float(x) for x in line[14:].strip('[]').split(',')]

        def create_gui():
            global entries
            read_initial_values(static_folder/ "Meanline_Initial_Values.txt")

            root = parent_frame
            
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
                    entries[param] = []  # Use param as the key
                    for j, value in enumerate(globals()[param]):
                        entry = ttk.Entry(frame, width=10)
                        entry.insert(0, str(value))
                        entry.grid(row=i, column=j+1, padx=5, pady=5)
                        entries[param].append(entry)

            def save_and_initialize():
                try:
                    for var_name in entries.keys():  # Iterate over the keys in entries
                        if var_name in ['z_R', 'z_S']:
                            globals()[var_name] = [int(entry.get()) for entry in entries[var_name]]
                        else:
                            globals()[var_name] = [float(entry.get()) for entry in entries[var_name]]

                    with open('Meanline_Initial_Values.txt', 'w') as file:
                        file.write(f"n = {n}\n")
                        file.write(f"psi_h = {psi_h}\n")
                        file.write(f"phi_1 = {phi_1}\n")
                        file.write(f"phi_2 = {phi_2}\n")
                        file.write(f"phi_3 = {phi_3}\n")
                        file.write(f"z_R = {z_R}\n")
                        file.write(f"l_R = {l_R}\n")
                        file.write(f"d_R_l_R = {d_R_l_R}\n")
                        file.write(f"d_Cl_R = {d_Cl_R}\n")
                        file.write(f"d_TE_R = {d_TE_R}\n")
                        file.write(f"incidence_R = {incidence_R}\n")
                        file.write(f"z_S = {z_S}\n")
                        file.write(f"l_S = {l_S}\n")
                        file.write(f"d_S_l_S = {d_S_l_S}\n")
                        file.write(f"d_TE_S = {d_TE_S}\n")
                        file.write(f"d_CL_S = {d_CL_S}\n")
                        file.write(f"incidence_S = {incidence_S}\n")

                    print("Parameters saved and initialized.")
                except ValueError:
                    print("Please enter valid numbers for all conditions. z_R and z_S must be integers.")

            ttk.Button(root, text="Save and Initialize Parameters", command=save_and_initialize).pack(pady=10)
            ttk.Button(root, text="Change the Channelcontour", command=lambda: run_diameter_gui(i_st_val)).pack(pady=10)

        
        
        # Starts and creates the meanline gui inside of the window
        create_gui()
                
    def threeD_tab(self, window):
        ttk.Label(window, text="Stage-Settings").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')
        
        self.bleed_air_data = {
            'rotor': {'patches': [], 'count': 0},
            'stator': {'patches': [], 'count': 0}
        }
        self.rotor_patch_entries = []
        self.stator_patch_entries = []
        
        self.inlet_area_var = tk.DoubleVar()
        self.inlet_dist_var = tk.DoubleVar()
        self.outlet_area_var = tk.DoubleVar()
        self.outlet_dist_var = tk.DoubleVar()

        self.main_choice = tk.StringVar(value="default")
        self.specs = {
        "section_idx": tk.StringVar(),
        "row": tk.StringVar(),
        "parameter": tk.StringVar()
        }
        
        # Variablen für die Eingabefelder
        self.show_section_plot_var = tk.BooleanVar(value=False) # Neue Variable für Abschnittsverteilung
        self.show_angle_dist_plot_var = tk.BooleanVar(value=False) # Neue Variable für Winkelverteilung
        
        # Fügt Tab listen ein
        self.notebook = ttk.Notebook(self.window)  
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.parameters_frame = ttk.Frame(self.notebook, padding=10)
        self.plot_options_frame = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.parameters_frame, text="Parameters")
        self.notebook.add(self.plot_options_frame, text="Plot Options")
        
        # Füllt die Tabs mit Inhalt
        self.setup_parameters_tab()
        self.setup_plot_options_tab()
        
        ttk.Button(self.root, text="Save and Initialize", command=self.run_action_and_stay_open)
        self.save_button = ttk.Button(self.window, text="Save and Initialize", command=self.run_action_and_stay_open) # Button zum Speichern und Initialisieren
        self.save_button.pack(pady=10, padx=10, fill='x')
        
        self.load_settings()
        
        self.check_button_states() # Initialer Check der Button-Zustände

    def check_button_states(self):
        rotor_exists = os.path.exists("bezier_control_points_R.txt")
        stator_exists = os.path.exists("bezier_control_points_S.txt")
    
        # Enable or disable buttons based on file existence
        if rotor_exists and stator_exists:
            self.create_profiles_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.NORMAL)
        else:
            self.create_profiles_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.DISABLED)
        
    def create_profiles_and_update_gui(self):
        create_default_profiles(self)
        self.check_button_states()

    
    def setup_parameters_tab(self):
    
        # main_frame = ttk.Frame(self.root, padding="10")
        # main_frame.pack(fill="both", expand=True) # Gruppierungscontainer
    
        choice_frame = ttk.LabelFrame(self.parameters_frame, text="Profile Choice")
        choice_frame.pack(fill='x', padx=5, pady=5)
        ttk.Radiobutton(choice_frame, text="Use Default or Loaded Profiles", variable=self.main_choice, value="default").pack(anchor='w', padx=10, pady=2)
        ttk.Radiobutton(choice_frame, text="Make a specific adjustment", variable=self.main_choice, value="adjust", command=self.open_specification_window).pack(anchor='w', padx=10, pady=2)
        
        self.create_profiles_button = ttk.Button(choice_frame, text="Create Default Profile(s)", command=self.create_profiles_and_update_gui) # Button zum Erstellen der Profile
        self.create_profiles_button.pack(pady=5, padx=10, fill='x')
    
        load_frame = ttk.LabelFrame(self.parameters_frame, text="Profiles")
        load_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(load_frame, text="Load Rotor Profile", command=self.load_rotor_settings).pack(fill='x', padx=10, pady=5) # Auswahl für Profil Laden
        ttk.Button(load_frame, text="Load Stator Profile", command=self.load_stator_settings).pack(fill='x', padx=10, pady=5)
        
        nrow_frame = ttk.LabelFrame(self.parameters_frame, text="Blade Rows")
        nrow_frame.pack(fill='x', padx=5, pady=5, anchor='n')
        
        inner_nrow_frame = ttk.Frame(nrow_frame)
        inner_nrow_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(inner_nrow_frame, text="Number of Blade Rows:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nrow_combo = ttk.Combobox(inner_nrow_frame, values=["Complete Stage (Rotor & Stator)", "Rotor Only"], state="readonly")
        self.nrow_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(inner_nrow_frame, text= "Levels for Output:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        # self.levels_entry.insert(0, "0.0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 0.95, 1.00") # Default Werte
        self.levels_entry = ttk.Entry(inner_nrow_frame)
        self.levels_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        inner_nrow_frame.grid_columnconfigure(1, weight=1)

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
        
        

        
    
    def open_specification_window(self):

        def apply_adjustments():
            settings = {
                'main_choice': 'adjust',
                'adjust_section_idx': self.specs["section_idx"].get().split(" ")[0],
                'adjust_row': self.specs["row"].get(),
                'adjust_parameter': self.specs["parameter"].get(),
                'levels': self.levels_entry.get(),
                'nrow': 1 if self.nrow_combo.get() == "Rotor Only" else 2
            }
            run_main_logic(settings)
        
        spec_window = tk.Toplevel(self.root)
        spec_window.title("Adjustments")
        spec_window.transient(self.root) # Fenster bleibt im Vordergrund
        spec_window.grab_set() # Lässt keine Änderungen am Unterfenster zu
    
        frame = ttk.Frame(spec_window, padding="15")
        frame.pack(expand=True, fill="both")
    
        # Erstellt ein DropDown Menü 
        ttk.Label(frame, text="Section Plan to change:").grid(row=0, column=0, sticky='w', pady=5)
        section_combo = ttk.Combobox(frame, textvariable=self.specs["section_idx"], values=1, state="readonly")
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
    
        ttk.Button(frame, text="Adjust Profile", command=apply_adjustments).grid(row=3, column=0, columnspan=2, pady=15)
        ttk.Button(frame, text="Close", command=spec_window.destroy).grid(row=4, column=0, columnspan=2, pady=15)
        
    def browse_output_folder(self):
        path = filedialog.askdirectory()
        if path:            
            self.output_folder_entry.delete(0, tk.END) # Löscht alte Inhalte
            self.output_folder_entry.insert(0, path) # Neuer Pfad

    def load_rotor_settings(self):
    
        filepath = filedialog.askopenfilename(title="Select Rotor Bezier Points File", filetypes=[("Text Files", "*.txt")])
        if filepath:
            
            try:
                if os.path.samefile(filepath, "bezier_control_points_R.txt"):
                    print("Diese Datei existiert bereits")
                    return
            except FileNotFoundError:
                pass
            
            shutil.copy(filepath, "bezier_control_points_R.txt") # Kopiert die ausgewählte Datei in das Arbeitsverzeichnis 
            print(f"Rotor Profile loaded: {filepath}")

        
    def load_stator_settings(self):
        filepath = filedialog.askopenfilename(title="Select Stator Bezier Points File", filetypes=[("Text Files", "*.txt")])
        if filepath:
                        
            try:
                if os.path.samefile(filepath, "bezier_control_points_S.txt"):
                    print("Diese Datei existiert bereits")
                    return
            except FileNotFoundError:
                pass
            
            shutil.copy(filepath, "bezier_control_points_S.txt")
            print(f"Stator Profile loaded: {filepath}")

    def save_settings(self):
        with open('Settings.txt', 'w') as file:
            file.write(f"main_choice = {self.main_choice.get()}\n") # Holt sich die User Auswahl aus dem Radiobutton
        
            if self.main_choice.get() == 'adjust': # nur wenn Adjust gewählt wurde
                section_str = self.specs["section_idx"].get().split(" ")[0] ############
                section_map = {'0.0': 0, '0.2': 1, '0.5': 2, '0.8': 3, '1.0': 4}
                file.write(f"adjust_section_idx = {section_map.get(section_str, 2)}\n")
                file.write(f"adjust_row = {self.specs['row'].get()}\n")
                file.write(f"adjust_parameter = {self.specs['parameter'].get()}\n")
            
            file.write(f"levels = {self.levels_entry.get()}\n")
        print("Settings saved")
    
    def load_settings(self):
        try:
            settings = {}
            with open('Settings.txt', 'r') as file:
                for line in file:
                    line = line.strip()
                    if ' = ' in line:
                        try:
                            key, value = line.split(' = ', 1)
                            settings[key] = value
                        except ValueError:
                            continue    
                
            self.show_section_plot_var.set(settings.get('show_section_plot', "False"))
            self.show_angle_dist_plot_var.set(settings.get('show_angle_dist_plot', "False")) # Holt die gespeicherten Einstellungen wenn keine vorhanden sind -> False
            
            self.levels_entry.insert(0, settings.get('levels', '0.0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 0.95, 1.00'))
            nrow_value = int(settings.get('nrow', 2))
            self.nrow_combo.set("Rotor Only" if nrow_value == 1 else "Complete Stage (Rotor & Stator)")
        except FileNotFoundError:
            self.levels_entry.insert(0, '0.0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.6, 0.8, 0.9, 0.95, 1.00')
            self.nrow_combo.set("Complete Stage (Rotor & Stator)")

    def run_action_and_stay_open(self): # Speichert alles und schließt das Fesnter nicht
        settings = {
            "main_choice": self.main_choice.get(),
        }

        nrow_choice = self.nrow_combo.get()
        settings["nrow"] = 1 if nrow_choice == "Rotor Only" else 2
        
        settings["levels"] = self.levels_entry.get()
        
        if settings["main_choice"] == "adjust":
            section_str = self.specs["section_idx"].get()
            section_map = {'0.0': 0, '0.1':1, '0.2': 2, '0.3': 3, '0.4': 4, '0.5': 5, '0.6': 6, '0.7': 7, '0.8': 8, '0.9': 9, '1.0': 10}
            settings["adjust_section_idx"] = section_map.get(section_str, 2)
            settings["adjust_row"] = self.specs['row'].get()
            settings["adjust_parameter"] = self.specs['parameter'].get()
            
        
        run_main_logic(settings)
        
        self.save_settings() # Speichert die Einstellungen in der Settings.txt
        
        self.root.destroy() # Schließt das Fenster
        
    def show_plots_section_rotor(self):
        NROW = 1
        
        h = [0.0 , 0.2, 0.5, 0.8, 1.0]
        
        if not os.path.exists("bezier_control_points_R.txt") or not os.path.exists("bezier_control_points_S.txt"):
            print("Bezier control point files are missing. Please load or create them first.")
            return

        length = []
        row = 1
        for k in range(len(h)):
            h = [0.0 , 0.2, 0.5, 0.8, 1.0]
            farben = ["pink", "blue", "green", "red", "black"]
            i = h[k]
            chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
            plt.plot(m_star_u, R_theta_s_star_u, color = farben[k], label = f"{h[k]*100}%")
            plt.plot(m_star_l, R_theta_s_star_l, color = farben[k])
            plt.legend()
            plt.title("Rotor Geometry")
        
        plt.xlabel("x [mm]")
        plt.ylabel("R\u03b8 [mm]") 
            
        plt.show()
    

        
    def show_plots_section_stator(self):
        NROW = 2   
        h = [0.0 , 0.2, 0.5, 0.8, 1.0]
        
        if not os.path.exists("bezier_control_points_R.txt") or not os.path.exists("bezier_control_points_S.txt"):
            print("Bezier control point files are missing. Please load or create them first.")
            
        length = []
        row = 2
        for k in range(len(h)):
            h = [0.0 , 0.2, 0.5, 0.8, 1.0]
            farben = ["pink", "blue", "green", "red", "black"]
            i = h[k]
            chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
            #length.append(chord)
            plt.plot(m_star_u, R_theta_s_star_u, color = farben[k], label = f"{h[k]*100}%")
            plt.plot(m_star_l, R_theta_s_star_l, color = farben[k])
            plt.legend()
            plt.title("Stator Geometry")
            
        plt.xlabel("x [mm]")
        plt.ylabel("R\u03b8 [mm]") 
            
        plt.show()

    def show_plots_angle_rotor(self):
        NROW = 1
        h = [0.0 , 0.2, 0.5, 0.8, 1.0]
        
        if not os.path.exists("bezier_control_points_R.txt") or not os.path.exists("bezier_control_points_S.txt"):
            print("Bezier control point files are missing. Please load or create them first.")
            return

        row = 1
        for k in range(len(h)):
            h = [0.0 , 0.2, 0.5, 0.8, 1.0]
            farben = ["pink", "blue", "green", "red", "black"]
            i = h[k]
            chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
            plt.plot(m_prime, beta_S, label = f"{h[k]*100}%", color = farben[k])
            plt.scatter(m_BP, beta_BP, color = farben[k])
            plt.legend()
            plt.title("Blade Angle Distribution Rotor")
            
        plt.xlabel('x/s [%]')
        plt.ylabel("blade angle [°]")           
        plt.show() 
    
    def show_plots_angle_stator(self):
        NROW = 2
        h = [0.0 , 0.2, 0.5, 0.8, 1.0]
        
        if not os.path.exists("bezier_control_points_R.txt") or not os.path.exists("bezier_control_points_S.txt"):
            print("Bezier control point files are missing. Please load or create them first.")
            return

        length = []
        row = 2
        for k in range(len(h)):
            h = [0.0 , 0.2, 0.5, 0.8, 1.0]
            farben = ["pink", "blue", "green", "red", "black"]
            i = h[k]
            chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
            plt.plot(m_prime, beta_S, label = f"{h[k]*100}%", color = farben[k])
            plt.scatter(m_BP, beta_BP, color = farben[k])
            plt.legend()
            plt.title("Blade Angle Distribution Stator")
            
        plt.xlabel('x/s [%]')
        plt.ylabel("blade angle [°]")           
        plt.show()

    def show_plots_thickness_rotor(self):
        h = [0.0 , 0.2, 0.5, 0.8, 1.0]
        
        if not os.path.exists("bezier_control_points_R.txt") or not os.path.exists("bezier_control_points_S.txt"):
            print("Bezier control point files are missing. Please load or create them first.")
            return

        row = 1
        for k in range(len(h)):
            h = [0.0 , 0.2, 0.5, 0.8, 1.0]
            farben = ["pink", "blue", "green", "red", "black"]
            i = h[k]
            chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
            plt.plot(m_prime, d_l, label = f"{h[k]*100}%", color = farben[k])
            plt.scatter(m_BP, d_l_BP, color = farben[k])
            plt.legend()
            plt.title("Thickness Distribution Rotor")
        
        plt.xlabel('x/s [%]')
        plt.ylabel("thickness d [mm]")           
        plt.show() 
    
    def show_plots_thickness_stator(self):
        h = [0.0 , 0.2, 0.5, 0.8, 1.0]
        if not os.path.exists("bezier_control_points_R.txt") or not os.path.exists("bezier_control_points_S.txt"):
            print("Bezier control point files are missing. Please load or create them first.")
            return
        
        NROW = 2 
        length = []
        row = 2
        for k in range(len(h)):
            h = [0.0 , 0.2, 0.5, 0.8, 1.0]
            farben = ["pink", "blue", "green", "red", "black"]
            i = h[k]
            chord, m_star, R_theta_s_star, m_star_u, R_theta_s_star_u, m_star_l, R_theta_s_star_l, m_prime, m_prime_u, m_prime_l, m_BP, beta_S, beta_BP, d_l, d_l_BP, R_theta_s_prime, R_theta_s_prime_u, R_theta_s_prime_l, Rtet_prime_cntr, R_theta_s_prime_2, R_theta_s_prime_2_l, R_theta_s_prime_2_u, R_theta_s_star_2, R_theta_s_star_l_2, R_theta_s_star_u_2 = calculation_of_section(i, row)
            plt.plot(m_prime, d_l, label = f"{h[k]*100}%", color = farben[k])
            plt.scatter(m_BP, d_l_BP, color = farben[k])
            plt.legend()
            plt.title("Thickness Distribution Stator")

        plt.xlabel('x/s [%]')
        plt.ylabel("thickness d [mm]")           
        plt.show()
                
    def render_gui(self):
                
        window = tk.Tk()
        window.title("GUI Example")
                
        main_frame = ttk.Frame(window, padding="10")
        main_frame.pack(fill="both", expand=True)

                    
        # Fügt Tab listen ein
        notebook = ttk.Notebook(main_frame)  
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
                    
        zeroD = ttk.Frame(notebook, padding=10)
        oneD = ttk.Frame(notebook, padding=10)
        threeD = ttk.Frame(notebook, padding=10)
        grid = ttk.Frame(notebook, padding=10)
        other = ttk.Frame(notebook, padding=10)
                    
        notebook.add(zeroD, text="0D-Settings")
        notebook.add(oneD, text="1D-Settings")
        notebook.add(threeD, text="3D-Settings")
        notebook.add(grid, text="Grid-Settings")
        notebook.add(other, text="Other-Settings")
                
        self.zeroD_tab(zeroD)
        self.oneD_tab(oneD, i_st_val = 3)
        #self.threeD_tab(threeD)
                
                
                

        main_frame.mainloop()




'''
Class to help render Tooltips for the Gui 

logic as follow:
        name_help = ttk.Label(where_questionmark_will_be_renderd_frame, text= "?", cursor="question_arrow")
        name_help.pack(side='left', padx=(5, 0))
        name_help_text = "Text to appear when hovering over tooltip"
        Tooltip(name_help, name_help_text)
'''
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        
    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25  
        y += self.widget.winfo_rooty() + 25     
        
        self.tooltip_window = Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = Label(self.tooltip_window, text = self.text, background = '#ffffe0', relief = 'solid', borderwidth = 1, font=("tahoma", '11', 'normal'), wraplength=500)
        label.pack(ipadx=1) 
        
    def hide_tooltip(self, event = None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None
    
if __name__ == "__main__":
    my_gui = CompressorGui()
    my_gui.loading_prepopulated_data(my_gui)
    my_gui.render_gui()