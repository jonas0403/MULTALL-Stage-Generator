# ------------------------------------------------------------------
# File:    source/gui/tabs/zero_d.py
# Author:  Jonas Scholz, Luca De Francesco
# Purpose: 0D settings tab.
# ------------------------------------------------------------------

import json
import tkinter as tk
from tkinter import ttk
from source.io.paths import JSON_PATH as json_path
from source.core.meanline.thermodynamics import Thermo
from source.logging import debug_log


def build_zero_d_tab(self, window):
    '''
    Thermodynamic Parameters Tab
    '''
    ttk.Label(window, text="This is the 0D Settings tab").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')

    # old not used
    #read_initial_values(static_folder/ "Thermo_Initial_Values.txt") 
    #params = ['p_t_in', 'T_t_in', 'mflow', 'R', 'cp', 'TPR'] 
    #window.add(window, text="Thermodynamic Parameters")  
    #path = os.getcwd()
    #print(path)

    entries = {}
    params = list(self.prepop_thermo_data.keys())
    gui_names = ['p_t_in [Pa]', 'T_t_in [K]', 'mflow [kg/s]', 'R [J/kg*K]', 'cp [J/kg*K]', 'TPR [-]']
    
    for i, param in enumerate(params):
        ttk.Label(window, text=f"{gui_names[i]}:").grid(row=i+1, column=0, padx=5, pady=5, sticky='w')
        
        entry = ttk.Entry(window, width=15)
        entry.insert(0, str(self.prepop_thermo_data[param]))
        entry.grid(row=i+1, column=1, padx=5, pady=5)
        entries[param]= entry

    def save_and_initialize():
        try:
            with open(json_path, 'r') as file:
                all_json_data = json.load(file)
                                
            new_thermo_values = {}
            for param in params:
                new_thermo_values[param] = float(entries[param].get())

            all_json_data['Thermodynamic_input_data'] = new_thermo_values
            
            with open(json_path, 'w') as file:
                json.dump(all_json_data, file, indent=4)
             
            self.prepop_thermo_data = new_thermo_values
                
            thermo_msg = "Thermodynamic Parameters saved and initialized."
            print(thermo_msg)
            debug_log.debug(thermo_msg, context="zeroD_tab")

            
            self.Thermodata =  Thermo(
                new_thermo_values['p_t_in'],
                new_thermo_values['T_t_in'],
                new_thermo_values['mflow'],
                new_thermo_values['R'],
                new_thermo_values['cp'],
                new_thermo_values['TPR'],
                self.stage
            )
            calc_msg = "Calculation of Thermodynamic Data completed."
            print(calc_msg)
            debug_log.debug(calc_msg, context="zeroD_tab")
        except ValueError:
            val_err = "Please enter valid numbers for all conditions."
            print(val_err)
            debug_log.debug(val_err, context="zeroD_tab")
            
        
        

    save_button = ttk.Button(window, text="Save and Initialize Parameters", command=save_and_initialize)
    save_button.grid(row=len(params)+1, column=0, columnspan=2, pady=10)
    save_and_initialize()   
        
        
'''
Function and population of second tab
Here meanline calculation values can be entered through boxes or through the reading of the json file
Creating an extra gui for the entry and definition of the channel contours. Can also be read through json file  
'''
