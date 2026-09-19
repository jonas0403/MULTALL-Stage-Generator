# ------------------------------------------------------------------
# File:    source/gui/tabs/other.py
# Author:  Jonas Scholz, Luca De Francesco
# Purpose: Other-settings tab (DAT variants, batch, solver run).
# ------------------------------------------------------------------

import json
import os
import shutil
import subprocess
import sys
import tkinter as tk
from datetime import datetime
from tkinter import ttk, filedialog, messagebox
from source.io.paths import (JSON_PATH as json_path, REPO_ROOT as current_dir)
from source.gui.widgets.tooltip import Tooltip
from misc_functions.generate_dat_files_multiple import generate_multiple_dat_files
from misc_functions.generate_run_batch import create_run_batch


def build_other_tab(self, parent_frame):
    settings_frame = ttk.LabelFrame(parent_frame, text="Compressor Map Generation", padding=10)
    settings_frame.pack(fill='x', padx=5, pady=5)

    self.dat_enabled_var = tk.BooleanVar(value=False)
    self.dat_start_var = tk.DoubleVar(value=100000.0)
    self.dat_end_var = tk.DoubleVar(value=150000.0)
    self.dat_step_var = tk.DoubleVar(value=5000.0)
    self.dat_template_var = tk.StringVar(value="multall_output_{}.dat")
    self.dat_batch_title_var = tk.StringVar(value="multall_compressor_map")

    ttk.Checkbutton(
        settings_frame,
        text="Create multiple DAT files for compressor map",
        variable=self.dat_enabled_var,
        command=self._toggle_dat_inputs
    ).grid(row=0, column=0, columnspan=3, sticky='w', pady=5)

    ttk.Label(settings_frame, text="Start value:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
    self.dat_start_entry = ttk.Entry(settings_frame, textvariable=self.dat_start_var, width=15)
    self.dat_start_entry.grid(row=1, column=1, sticky='w', padx=5, pady=2)
    start_help = ttk.Label(settings_frame, text="?", cursor="question_arrow")
    start_help.grid(row=1, column=2, padx=(5, 0))
    Tooltip(start_help, "The first pressure value to use for the generated DAT files.")

    ttk.Label(settings_frame, text="End value:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
    self.dat_end_entry = ttk.Entry(settings_frame, textvariable=self.dat_end_var, width=15)
    self.dat_end_entry.grid(row=2, column=1, sticky='w', padx=5, pady=2)
    end_help = ttk.Label(settings_frame, text="?", cursor="question_arrow")
    end_help.grid(row=2, column=2, padx=(5, 0))
    Tooltip(end_help, "The last pressure value to use for the generated DAT files.")

    ttk.Label(settings_frame, text="Step value:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
    self.dat_step_entry = ttk.Entry(settings_frame, textvariable=self.dat_step_var, width=15)
    self.dat_step_entry.grid(row=3, column=1, sticky='w', padx=5, pady=2)
    step_help = ttk.Label(settings_frame, text="?", cursor="question_arrow")
    step_help.grid(row=3, column=2, padx=(5, 0))
    Tooltip(step_help, "Increment between consecutive pressure values.")

    ttk.Label(settings_frame, text="Filename template:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
    self.dat_template_entry = ttk.Entry(settings_frame, textvariable=self.dat_template_var, width=40)
    self.dat_template_entry.grid(row=4, column=1, columnspan=2, sticky='ew', padx=5, pady=2)
    template_help = ttk.Label(settings_frame, text="?", cursor="question_arrow")
    template_help.grid(row=4, column=3, padx=(5, 0))
    Tooltip(template_help, "Use {} as placeholder, e.g. output_{}.dat becomes output_100000.dat")

    ttk.Label(settings_frame, text="Batch title:").grid(row=5, column=0, sticky='w', padx=5, pady=2)
    self.dat_batch_title_entry = ttk.Entry(settings_frame, textvariable=self.dat_batch_title_var, width=40)
    self.dat_batch_title_entry.grid(row=5, column=1, columnspan=2, sticky='ew', padx=5, pady=2)
    title_help = ttk.Label(settings_frame, text="?", cursor="question_arrow")
    title_help.grid(row=5, column=3, padx=(5, 0))
    Tooltip(title_help, "Window title for the batch script that runs all DAT files through MULTALL.")

    info_text = "These settings are used when pressing the Generate Output File button below."
    ttk.Label(settings_frame, text=info_text, font=("TkDefaultFont", 8), wraplength=500).grid(
        row=6, column=0, columnspan=4, pady=(10, 0)
    )

    self._toggle_dat_inputs()
    
    hist_frame = ttk.LabelFrame(parent_frame, text="Configuration History", padding=10)
    hist_frame.pack(fill='x', padx=5, pady=5)
    
    ttk.Label(hist_frame, text="Saved configurations:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
    self.history_combo = ttk.Combobox(hist_frame, state="readonly", width=45)
    self.history_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
    self.history_combo['postcommand'] = self._refresh_history_list
    self._refresh_history_list()
    hist_help = ttk.Label(hist_frame, text="?", cursor="question_arrow")
    hist_help.grid(row=0, column=2, padx=(5, 0))
    Tooltip(hist_help, "Snapshots saved on every successful Generate Output File (latest 25). Import reloads one into all fields.")
    
    ttk.Button(hist_frame, text="Import Selected", command=self._import_history_selection).grid(row=1, column=0, padx=5, pady=5, sticky='w')
    ttk.Button(hist_frame, text="Browse File\u2026", command=self._import_history_browse).grid(row=1, column=1, padx=5, pady=5, sticky='w')
    

def _toggle_dat_inputs(self):
    state = tk.NORMAL if self.dat_enabled_var.get() else tk.DISABLED
    self.dat_start_entry.config(state=state)
    self.dat_end_entry.config(state=state)
    self.dat_step_entry.config(state=state)
    self.dat_template_entry.config(state=state)
    self.dat_batch_title_entry.config(state=state)

def _find_source_dat_file(self, output_folder):
    dat_files = [os.path.join(output_folder, f) for f in os.listdir(output_folder)
                 if f.endswith('.dat') and os.path.isfile(os.path.join(output_folder, f))]
    if not dat_files:
        return None
    return max(dat_files, key=os.path.getmtime)

def _generate_dat_files(self, target_folder=None):
    if target_folder is None:
        target_folder = self.prepop_metadata.get('output_folder', 'Run_Multall')
        if not os.path.isabs(target_folder):
            target_folder = os.path.join(current_dir, target_folder)

    source_file = self._find_source_dat_file(target_folder)
    if not source_file:
        messagebox.showerror("Error", "No .dat file found in target folder. Generate a grid first.")
        return

    try:
        start = self.dat_start_var.get()
        end = self.dat_end_var.get()
        step = self.dat_step_var.get()
        template = self.dat_template_var.get()

        if start > end:
            messagebox.showerror("Error", "Start value must be less than or equal to end value.")
            return
        if step <= 0:
            messagebox.showerror("Error", "Step value must be positive.")
            return

        count = generate_multiple_dat_files(source_file, target_folder, start, end, step, template)
        messagebox.showinfo("Success", f"Created {count} DAT files in:\n{target_folder}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def _create_run_batch(self, target_folder=None, exclude_source=None, results_dir=None):
    if target_folder is None:
        target_folder = self.prepop_metadata.get('output_folder', 'Run_Multall')
        if not os.path.isabs(target_folder):
            target_folder = os.path.join(current_dir, target_folder)

    batch_title = self.dat_batch_title_var.get()

    exclude = []
    if exclude_source:
        exclude.append(os.path.basename(exclude_source))

    try:
        count = create_run_batch(target_folder, batch_title=batch_title, exclude_files=exclude, results_dir=results_dir)
        if count == 0:
            messagebox.showwarning("Warning", f"No .dat files found (excluding source) in:\n{target_folder}")
        else:
            messagebox.showinfo("Success", f"Created batch file for {count} files in:\n{target_folder}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# endregion

def _generate_all_and_exit(self):
    if hasattr(self, '_generate_grid_callback') and self._generate_grid_callback:
        # [FIX] stay open on grid failure (e.g. failed blade check) instead of exiting.
        grid_ok = self._generate_grid_callback()
        if grid_ok is False:
            return
        
        # [History] snapshot live settings (grid just generated successfully).
        # Title/Date go FIRST in the file; readers use key access (order-safe).
        try:
            _hist_dir = os.path.join(os.path.dirname(os.path.abspath(str(json_path))), "history")
            os.makedirs(_hist_dir, exist_ok=True)
            _nst = int(getattr(self, "stages_to_calc", 0) or 0)
            _gd = getattr(self, "prepop_grid_data", {}) or {}
            def _clean(v, default="x"):
                t = str(v) if v is not None else default
                t = "".join(c for c in t if c.isalnum() or c in ("_", "-"))
                return t or default
            _im = _clean(_gd.get("im_selection", 37))
            _km = _clean(_gd.get("km_selection", 37))
            _now = datetime.now()
            _stamp = _now.strftime("%Y%m%d_%H%M%S")
            _datestr = _now.strftime("%Y-%m-%d %H:%M")
            with open(json_path, "r", encoding="utf-8") as _jf:
                _snap = json.load(_jf)
            _snap.pop("Title", None)
            _snap.pop("Date", None)
            _snap = {"Title": f"{_nst}-stage compressor config - {_datestr}",
                     "Date": _now.strftime("%Y-%m-%d %H:%M:%S"), **_snap}
            _hist_name = f"config_{_nst}stg_IM{_im}_KM{_km}_{_stamp}.json"
            with open(os.path.join(_hist_dir, _hist_name), "w", encoding="utf-8") as _jf:
                json.dump(_snap, _jf, indent=4)
            print(f"Configuration snapshot saved: {_hist_name}")
        except Exception as e:
            messagebox.showwarning("History snapshot", f"Grid was generated, but the history snapshot failed:\n{e}")
        

    output_folder = self.prepop_metadata.get('output_folder', 'Run_Multall')
    if not os.path.isabs(output_folder):
        output_folder = os.path.join(current_dir, output_folder)

    multall_dir = os.path.join(current_dir, 'Run_Multall')

    source_file = self._find_source_dat_file(output_folder)

    if self.dat_enabled_var.get():
        if source_file:
            import shutil
            shutil.copy2(source_file, multall_dir)
        self._generate_dat_files(target_folder=multall_dir)
        results_dir = os.path.join(output_folder, self.dat_batch_title_var.get())
        self._create_run_batch(target_folder=multall_dir, exclude_source=source_file, results_dir=results_dir)

    if self.run_multall_var.get():
        if self.dat_enabled_var.get():
            batch_path = os.path.join(multall_dir, 'run_multall_files.bat')
            if os.path.isfile(batch_path):
                subprocess.Popen(
                    ['cmd', '/k', 'run_multall_files.bat'],
                    cwd=multall_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
        else:
            if source_file:
                import shutil
                shutil.copy2(source_file, multall_dir)
                basename = os.path.basename(source_file)
                subprocess.Popen(
                    ['cmd', '/k', f'multall.exe<{basename}'],
                    cwd=multall_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )

    self.root.destroy()
    sys.exit()


def _history_dir():
    d = os.path.join(os.path.dirname(os.path.abspath(str(json_path))), "history")
    os.makedirs(d, exist_ok=True)
    return d


def _history_display_name(filename):
    """Readable dropdown label for a history snapshot. Plain function (no GUI
    needed) so it stays testable. Unknown shapes fall back to the filename."""
    import re
    m = re.match(r"^config_(\d+)stg_IM(.+?)_KM(.+?)_(\d{8})_(\d{6})\.json$", filename or "")
    if not m:
        return filename
    nst, im, km, date, time = m.groups()
    try:
        stamp = f"{date[6:8]}.{date[4:6]}.{date[0:4]} at {time[0:2]}:{time[2:4]}:{time[4:6]}"
        int(date)
        int(time)
    except (ValueError, IndexError):
        return filename
    stage = "1 Stage" if nst == "1" else f"{nst} Stage"
    return f"{stage} \u00b7 IM {im} \u00b7 KM {km} \u00b7 {stamp}"


def _refresh_history_list(self):
    # Latest 25 snapshots by file time (any name qualifies), newest first.
    # The dropdown shows readable labels; _history_name_map resolves them back.
    try:
        files = [f for f in os.listdir(_history_dir())
                 if f.endswith(".json") and os.path.isfile(os.path.join(_history_dir(), f))]
        files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(_history_dir(), f)), reverse=True)[:25]
    except OSError:
        files = []
    self._history_name_map = {}
    seen = {}
    labels = []
    for f in files:
        label = _history_display_name(f)
        if label in seen:  # same-second snapshots would collide
            seen[label] += 1
            label = f"{label} ({seen[label]})"
        else:
            seen[label] = 1
        self._history_name_map[label] = f
        labels.append(label)
    current = self.history_combo.get()
    if labels:
        self.history_combo["values"] = labels
        self.history_combo.set(current if current in labels else labels[0])
    else:
        self.history_combo["values"] = ["(no history yet)"]
        self.history_combo.set("(no history yet)")


def _import_history_selection(self):
    label = self.history_combo.get()
    if not label or label == "(no history yet)":
        messagebox.showwarning("Import history", "No history file selected.")
        return
    name = getattr(self, "_history_name_map", {}).get(label, label)
    _import_history_file(self, os.path.join(_history_dir(), name))


def _import_history_browse(self):
    path = filedialog.askopenfilename(title="Select configuration JSON",
                                      filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if path:
        _import_history_file(self, path)


def _import_history_file(self, path):
    # [History] copy over the live JSON, reload memory, rebuild the whole GUI so every
    # visible field shows the imported values (same destroy-then-render sequence as startup).
    if not os.path.isfile(path):
        messagebox.showerror("Import history", f"File not found:\n{path}")
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        messagebox.showerror("Import history", f"Cannot read JSON:\n{e}")
        return
    # [FIX] validate every section loading_prepopulated_data hard-indexes BEFORE copying:
    # a partial file must never clobber the live configuration.
    _required = ("Thermodynamic_input_data", "Meanline_input_data", "Diameter_data",
                 "Metadata", "Grid_data", "Bleed_air_data", "Intake_Outtake_area")
    _missing = [k for k in _required if not isinstance(data.get(k), dict)]
    if _missing:
        messagebox.showerror("Import history",
                             "Not a complete compressor configuration, missing: "
                             + ", ".join(_missing) + ". Live configuration left untouched.")
        return
    try:
        n_stages = len(data["Meanline_input_data"]["n"])
    except (KeyError, TypeError):
        messagebox.showerror("Import history", "Not a compressor configuration (missing Meanline_input_data.n).")
        return
    if n_stages != getattr(self, "stage", n_stages):
        messagebox.showerror("Import history",
                             f"History is for {n_stages} stage(s), GUI runs {self.stage}. "
                             "Restart the GUI with a matching stage count first.")
        return
    try:
        shutil.copy2(path, json_path)
    except Exception as e:
        messagebox.showerror("Import history", f"Cannot write live configuration:\n{e}")
        return
    self.loading_prepopulated_data()
    messagebox.showinfo("Import history", f"Imported {os.path.basename(path)} into all fields.")
    self.root.destroy()
    self.render_gui()


