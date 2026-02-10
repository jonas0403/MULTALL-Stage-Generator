import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import filedialog



def render_gui():
    
    window = tk.Tk()
    window.title("GUI Example")
    
    main_frame = ttk.Frame(window, padding="10")
    main_frame.pack(fill="both", expand=True)

        
    # Fügt Tab listen ein
    notebook = ttk.Notebook(main_frame)  
    notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
    zeroD = ttk.Frame(notebook, padding=10)
    oneD = ttk.Frame(notebook, padding=10)
    geometry = ttk.Frame(notebook, padding=10)
    grid = ttk.Frame(notebook, padding=10)
    other = ttk.Frame(notebook, padding=10)
        
    notebook.add(zeroD, text="0D-Settings")
    notebook.add(oneD, text="1D-Settings")
    notebook.add(geometry, text="Geometry-Settings")
    notebook.add(grid, text="Grid-Settings")
    notebook.add(other, text="Other-Settings")
    
def oneD_Gui():
    global entries



    root = tk.Tk()
    root.title("Thermodynamic Initial Values")

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)

    entries = {}

    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Thermodynamic Parameters")

    params = ['p_t_in', 'T_t_in', 'mflow', 'R', 'cp', 'TPR']
    gui_names = ['p_t_in [Pa]', 'T_t_in [K]', 'mflow [kg/s]', 'R [J/kg*K]', 'cp [J/kg*K]', 'TPR [-]']
    path = os.getcwd()
    print(path)
    for i, param in enumerate(params):
        ttk.Label(frame, text=f"{gui_names[i]}:").grid(row=i, column=0, padx=5, pady=5, sticky='w')
        entries[param] = []
        entry = ttk.Entry(frame, width=15)
        entry.insert(0, str(globals()[param]))
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries[param].append(entry)

    def save_and_initialize():
        try:
            for var_name in entries.keys():
                globals()[var_name] = float(entries[var_name][0].get())
            
            with open('Thermo_Initial_Values.txt', 'w') as file:
                file.write(f"p_t_in = {p_t_in}\n")
                file.write(f"T_t_in = {T_t_in}\n")
                file.write(f"mflow = {mflow}\n")
                file.write(f"R = {R}\n")
                file.write(f"cp = {cp}\n")
                file.write(f"TPR = {TPR}\n")

            print("Parameters saved and initialized.")
        except ValueError:
            print("Please enter valid numbers for all conditions.")

    ttk.Button(root, text="Save and Initialize Parameters", command=save_and_initialize).pack(pady=10)

    root.mainloop()
    
    
    