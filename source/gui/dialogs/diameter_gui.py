# ------------------------------------------------------------------
# File:    source/gui/dialogs/diameter_gui.py
# Author:  Jonas Scholz
# Purpose: Channel-contour diameter dialog (sliders + preview).
# ------------------------------------------------------------------

import json
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from source.io.paths import JSON_PATH as json_path
from source.gui.widgets.helpers import create_scrollable_frame
from source.core.geometry.cubic_spline import cubspline
from source.core.meanline.meanline import meanline
from source.logging import debug_log


class diameter_gui:
    def __init__(self, root, i_st_val, on_close_callback, initial_diamter_data):
        
        debug_log.debug(f"initial_data: {initial_diamter_data}", context="diameter_gui")
        
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
        self.initial_type = initial_diamter_data.get("fixed_radius_type", "mean")
        self.initial_D_f1 = initial_diamter_data.get("D_f1", [])
        self.initial_D_f2 = initial_diamter_data.get("D_f2", [])
        self.initial_D_f3 = initial_diamter_data.get("D_f3", [])
        self.initial_plot_contour = initial_diamter_data.get("plot_channel_contour", False)
        debug_log.debug(f"plot_channel_contour={self.initial_plot_contour}", context="diameter_gui")
        
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
        debug_log.debug(f"self.cubspline_points={self.cubspline_points}", context="diameter_gui")
        
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
        # [FIX bug #1] the dialog runs on its own tk.Tk() root, but a master-less
        # BooleanVar binds to the *first* (app) root interpreter, so clicks on this
        # Checkbutton never reached the variable (flag stayed False). Bind to dialog root.
        self.plot_channel_var = tk.BooleanVar(self.root, value=self.initial_plot_contour)
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
        self.entry_vars = []
                        
        for i in range(self.num_points):
            row_frame = tk.Frame(self.slider_frame)
            row_frame.pack(padx=5, pady=5, fill='x')
            
            # Label
            label = tk.Label(row_frame, text=f"Points {i+1}")
            label.pack(side='left', padx=(0, 5))
            
            # Entrybox
            # [FIX bug #9] DoubleVar needs the dialog root as master (two-Tk-roots trap:
            # master-less vars bind to the app root interpreter, so entries stayed empty).
            entry_var = tk.DoubleVar(self.root, value=self.cubspline_points[i])
            entry = tk.Entry(row_frame, width=8, textvariable=entry_var)
            entry.pack(side='right')
            entry.bind('<Return>', lambda event, idx=i: self.update_from_box(idx))
            self.entries.append(entry)
            self.entry_vars.append(entry_var)
            
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
        # [FIX] idempotent close: double-clicks / X-during-plot re-enter here;
        # a second pass must not rerun the save or destroy a dead root (TclError).
        if getattr(self, "_closing_done", False):
            return
        self._closing_done = True
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
        
        self.changed_channel_contour_data = {
            
            "D_f1": D_f1,
            "D_f2": D_f2,
            "D_f3": D_f3,
            "fixed_radius_type": fixed_radius_type,
            "plot_channel_contour": plot_channel_contour
        }
        debug_log.debug(f"self.changed_channel_contour_data: {self.changed_channel_contour_data}", context="diameter_gui")
        
        #self.save_and_initialize_meanline(plot_channel_contour) 
        self.on_close_callback(self.changed_channel_contour_data)
        try:
            self.root.destroy()
        except tk.TclError:
            pass  # already destroyed (e.g. double close) - nothing left to do
        try:
            plt.close(self.fig)
        except Exception:
            pass


def run_diameter_gui(self, i_st, initial_data, save_callback = None):
    root = tk.Tk()
    D_f1, D_f2, D_f3 = [],  [],  []
    fixed_radius_type = ""
    plot_channel_contour = False
    
    def on_close(changed_diamtere_data):
        # FIX (2026-09-08): without `nonlocal` the assignments below created
        # local variables inside on_close(), so the outer run_diameter_gui()
        # variables kept their initial values (empty lists / "" / False). After
        # root.mainloop() returned, that reset self.prepop_diameter_data to the
        # empty defaults (GUI.py:759-763): the edited diameters were discarded
        # in memory and the "Plot the channel contour" checkbox never reached
        # meanline() -> plot_channel(). Declaring nonlocal forwards the values
        # to the enclosing function so they survive past the dialog close.
        nonlocal D_f1, D_f2, D_f3, fixed_radius_type, plot_channel_contour
        D_f1 = changed_diamtere_data["D_f1"]
        D_f2 = changed_diamtere_data["D_f2"]
        D_f3 = changed_diamtere_data["D_f3"]

        fixed_radius_type = changed_diamtere_data["fixed_radius_type"]
        plot_channel_contour = changed_diamtere_data["plot_channel_contour"]
        
        try:
            with open(json_path, 'r') as file:
                all_json_data = json.load(file)
            new_diameter_data = {}
            '''
            if self.meanline_data["fixed_radius_type"] == "shroud":
                new_diameter_data["D_f1"] = self.meanline_data["D_S1"]
                new_diameter_data["D_f2"] = self.meanline_data["D_S2"]
                new_diameter_data["D_f3"] = self.meanline_data["D_S3"]
            elif self.meanline_data["fixed_radius_type"] == "mean":
                new_diameter_data["D_f1"] = self.meanline_data["D_M1"]
                new_diameter_data["D_f2"] = self.meanline_data["D_M2"]
                new_diameter_data["D_f3"] = self.meanline_data["D_M3"]
            elif self.meanline_data["fixed_radius_type"] == "hub":
                new_diameter_data["D_f1"] = self.meanline_data["D_H1"]
                new_diameter_data["D_f2"] = self.meanline_data["D_H2"]
                new_diameter_data["D_f3"] = self.meanline_data["D_H3"]   
            '''
            new_diameter_data["D_f1"] = D_f1
            new_diameter_data["D_f2"] = D_f2
            new_diameter_data["D_f3"] = D_f3
            
            debug_log.debug(f"Debug plot_chanel_contour: {plot_channel_contour}", context="diameter_gui")
                
            new_diameter_data["fixed_radius_type"] = fixed_radius_type
            new_diameter_data["plot_channel_contour"] = plot_channel_contour
            
            all_json_data['Diameter_data'] = new_diameter_data
                
            
            # The data to be saved is already in self.prepop_diameter_data,
            # which was updated by run_diameter_gui.

            with open(json_path, 'w') as file:
                json.dump(all_json_data, file, indent=4)
            status_msg = "Diameter data saved to JSON successfully."
            print(status_msg)
            debug_log.debug(status_msg, context="diameter_gui")
            
            self.prepop_diameter_data = new_diameter_data
            debug_log.debug(f"D_f1={D_f1}, D_f2={D_f2}, D_f3={D_f3}, fixed_radius_type = {fixed_radius_type}, plot_channel_contour = {plot_channel_contour}", context="diameter_gui")
            self.meanline_data = meanline(self.Thermodata, self.prepop_meanline_input_data, self.prepop_diameter_data, plot_channel_contour)
        except Exception as e:
            err_msg = f"Error during JSON write in write_diameters: {e}"
            print(err_msg)
            debug_log.debug(err_msg, context="diameter_gui")
        
        
    # Read Initial Data from File   
    diameter_gui(root, i_st, on_close, initial_data)
    root.mainloop()
    debug_log.debug(f"D_f1={D_f1}, D_f2={D_f2}, D_f3={D_f3}, fixed_radius_type={fixed_radius_type}, plot_channel_contour={plot_channel_contour}", context="diameter_gui")
    
    self.prepop_diameter_data["D_f1"] = D_f1
    self.prepop_diameter_data["D_f2"] = D_f2
    self.prepop_diameter_data["D_f3"] = D_f3
    self.prepop_diameter_data["fixed_radius_type"] = fixed_radius_type  
    self.prepop_diameter_data["plot_channel_contour"] = plot_channel_contour
    
    debug_log.debug(f"UPDATED prepop_diameter_data: {self.prepop_diameter_data}", context="diameter_gui")
    
    if save_callback:
        debug_log.debug("Calling save_callback...", context="diameter_gui")
        save_callback()#save_callback(show_plot=plot_channel_contour)
    
    return D_f1, D_f2, D_f3, fixed_radius_type, plot_channel_contour


def write_diameters(self):
    debug_log.debug("Writing using the write_diameters function", context="diameter_gui")
    debug_log.debug("Writing diameter data to JSON...", context="diameter_gui")
    plot_channel_contour=False
    self.meanline_data = meanline(self.Thermodata, self.prepop_meanline_input_data, self.prepop_diameter_data, plot_channel_contour)
    '''
    try: 
       
def write_diameters(**kwargs):
    """
    Writes the diameter data, which has been updated in self.prepop_diameter_data,
    to the JSON file. This function is called as a callback after the diameter GUI is closed.
    """
    '''
    
    try:
        with open(json_path, 'r') as file:
            all_json_data = json.load(file)
        new_diameter_data = {}
        
        if self.meanline_data["fixed_radius_type"] == "shroud":
            new_diameter_data["D_f1"] = self.meanline_data["D_S1"]
            new_diameter_data["D_f2"] = self.meanline_data["D_S2"]
            new_diameter_data["D_f3"] = self.meanline_data["D_S3"]
        elif self.meanline_data["fixed_radius_type"] == "mean":
            new_diameter_data["D_f1"] = self.meanline_data["D_M1"]
            new_diameter_data["D_f2"] = self.meanline_data["D_M2"]
            new_diameter_data["D_f3"] = self.meanline_data["D_M3"]
        elif self.meanline_data["fixed_radius_type"] == "hub":
            new_diameter_data["D_f1"] = self.meanline_data["D_H1"]
            new_diameter_data["D_f2"] = self.meanline_data["D_H2"]
            new_diameter_data["D_f3"] = self.meanline_data["D_H3"]   
            
        new_diameter_data["fixed_radius_type"] = self.meanline_data["fixed_radius_type"]
        new_diameter_data["plot_channel_contour"] = self.meanline_data["plot_channel_contour"]
        
        all_json_data['Diameter_data'] = new_diameter_data
            

        # The data to be saved is already in self.prepop_diameter_data,
        # which was updated by run_diameter_gui.
        all_json_data['Diameter_data'] = self.prepop_diameter_data

        with open(json_path, 'w') as file:
            json.dump(all_json_data, file, indent=4)
        status_msg = "Diameter data saved to JSON successfully."
        print(status_msg)
        debug_log.debug(status_msg, context="diameter_gui")
    except Exception as e:
        err_msg = f"Error during JSON write in write_diameters: {e}"
        print(err_msg)
        debug_log.debug(err_msg, context="diameter_gui")
        
        self.prepop_diameter_data = new_diameter_data
        
        status_msg = "Parameters saved and initialized."
        print(status_msg)
        debug_log.debug(status_msg, context="oneD_tab")
    
    except ValueError as e: 
        err_msg = f"Error: {e}"
        print(err_msg)
        debug_log.debug(err_msg, context="oneD_tab")  

