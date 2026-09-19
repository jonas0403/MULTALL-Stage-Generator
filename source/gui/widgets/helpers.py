# ------------------------------------------------------------------
# File:    source/gui/widgets/helpers.py
# Author:  Jonas Scholz
# Purpose: Shared GUI helpers (scrollable frame).
# ------------------------------------------------------------------

import tkinter as tk


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
