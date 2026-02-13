import os
import pyautogui
import time
import tkinter as tk
from tkinter import ttk, filedialog

 
def choose_file():
    file_path = tk.filedialog.askopenfilename(title="Select a file", filetypes=[("All files", "*.*")])
    if file_path:
        print(f"Selected file: {file_path}")
    
    return file_path

def cmd_control(multall_executable_path):


    os.system('start cmd /k "Multall Strömungssimulation for TMDA"')

    time.sleep(1) 

    pyautogui.write('cd "{multall_executable_path}")', interval=0.1)
    pyautogui.press('enter')

class MultallSimulation:
    def __init__(self):
        self.data_path = ""
        self.data_name = ""
        
    def choose_file(self):
        self.multall_executable_path = tk.filedialog.askopenfilename(title="Select a file", filetypes=[("All files", "*.*")])
        
        if self.multall_executable_path:
            print(f"Selected file: {self.multall_executable_path}")
            print(f"Multall executable path: {self.data_path}")
            print(f"Data name: {self.data_name}")
        
        self.data_path, self.data_name = os.path.split(self.multall_executable_path)      

    def cmd_control(self):

        os.system('start cmd /k "Multall Strömungssimulation for TMDA"')

        time.sleep(1) 

        command_path = f'cd /d "{self.data_path}"'
        pyautogui.write(command_path, interval=0.05)
        pyautogui.press('enter')
        
        pyautogui.write('multall.exe', interval=0.05)
        
        root = tk.Tk()
        root.withdraw() 
        root.clipboard_clear()
        root.clipboard_append('<')
        root.update() 
        root.destroy()
        
        pyautogui.hotkey('ctrl', 'v')
        
        pyautogui.write(f'{self.data_name}', interval=0.1)

        pyautogui.press('enter')
        
        window.destroy()

if __name__ == "__main__":
    sim = MultallSimulation()
    
    window = tk.Tk()
    window.title("Multall Strömungssimulation for TMDA")
    tk.Label(window, text="Multall Strömungssimulation for TMDA", font=("Arial", 16)).pack(pady=10)

    main_frame = ttk.Frame(window, padding="10")
    main_frame.pack(fill="both", expand=True)

    tk.Button(main_frame, text="Select File to calculate", command=sim.choose_file).pack(pady=10)
    tk.Button(main_frame, text="Start Multall", command=sim.cmd_control).pack(pady=10)

    window.mainloop()
        