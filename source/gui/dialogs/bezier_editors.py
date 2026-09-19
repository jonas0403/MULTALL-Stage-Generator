# ------------------------------------------------------------------
# File:    source/gui/dialogs/bezier_editors.py
# Author:  Luca De Francesco
# Purpose: Interactive Bezier profile editors (sliders).
# ------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from source.core.geometry.bezier import bezier
from source.logging import debug_log


def read_parameters_from_file(filename):
    global use_default_rotor_bezier, use_default_stator_bezier
    global adjust_rotor_thickness, adjust_rotor_angle
    global adjust_stator_thickness, adjust_stator_angle
    global output_folder, levels, nrow
    global show_section_plot, show_angle_distribution_plots
    global enable_bleed_air, rotor_patches_data, stator_patches_data
    global inlet_area, inlet_dist, outlet_area, outlet_dist

    # Initialize default values
    use_default_rotor_bezier = 0
    use_default_stator_bezier = 0
    adjust_rotor_thickness = 0
    adjust_rotor_angle = 0
    adjust_stator_thickness = 0
    adjust_stator_angle = 0
    output_folder = ""
    levels = []
    nrow = 2
    show_section_plot = 0
    show_angle_distribution_plots = 0
    enable_bleed_air = False
    rotor_patches_data = []
    stator_patches_data = []
    inlet_area = 0 
    inlet_dist = 0
    outlet_area = 0
    outlet_dist = 0

    try:
        with open(filename, 'r') as file:
            # Read all lines simultaneously to handle patches easily
            lines = file.readlines()
            # Use a state machine to parse bleed air patches
        is_reading_rotor = False
        is_reading_stator = False
        for line in lines:
            line = line.strip()
            if line.startswith('use_default_rotor_bezier'):
                is_reading_rotor = False
                is_reading_stator = False
                use_default_rotor_bezier = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('use_default_stator_bezier'):
                is_reading_rotor = False
                is_reading_stator = False
                use_default_stator_bezier = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('adjust_rotor_thickness'):
                is_reading_rotor = False
                is_reading_stator = False
                adjust_rotor_thickness = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('adjust_rotor_angle'):
                is_reading_rotor = False
                is_reading_stator = False
                adjust_rotor_angle = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('adjust_stator_thickness'):
                is_reading_rotor = False
                is_reading_stator = False
                adjust_stator_thickness = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('adjust_stator_angle'):
                is_reading_rotor = False
                is_reading_stator = False
                adjust_stator_angle = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('output_folder'):
                is_reading_rotor = False
                is_reading_stator = False
                output_folder = line.split('=')[1].strip()
            elif line.startswith('levels'):
                is_reading_rotor = False
                is_reading_stator = False
                levels_input = line.split('=')[1].strip()
                levels = [float(x) for x in levels_input.split(',')]  # Convert levels to list of floats
            elif line.startswith('nrow'):
                is_reading_rotor = False
                is_reading_stator = False
                nrow = int(line.split('=')[1].strip())
            elif line.startswith('show_section_plot'):
                is_reading_rotor = False
                is_reading_stator = False
                show_section_plot = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('show_angle_distribution_plots'):
                is_reading_rotor = False
                is_reading_stator = False
                show_angle_distribution_plots = 1 if line.split('=')[1].strip() == 'True' else 0
            elif line.startswith('enable_bleed_air'):
                enable_bleed_air = line.split('=')[1].strip() == 'True'
            elif line.startswith('rotor_patches = '):
                is_reading_rotor = True
            elif line.startswith('stator_patches = '):
                is_reading_rotor = False
                is_reading_stator = True
            elif is_reading_rotor and line.startswith('rotor_patch_'):
                values_str = line.split('=')[1].strip().split(',')
                rotor_patches_data.append([v.strip() for v in values_str])
            elif is_reading_stator and line.startswith('stator_patch_'):
                values_str = line.split('=')[1].strip().split(',')
                stator_patches_data.append([v.strip() for v in values_str])
            elif line.startswith('inlet_area = '):
                is_reading_rotor = False
                is_reading_stator = False
                inlet_area = line.split('=')[1].strip()
            elif line.startswith('inlet_dist = '):
                is_reading_rotor = False
                is_reading_stator = False
                inlet_dist = line.split('=')[1].strip()
            elif line.startswith('outlet_area = '):
                is_reading_rotor = False
                is_reading_stator = False
                outlet_area = line.split('=')[1].strip()
            elif line.startswith('outlet_dist = '):
                is_reading_rotor = False
                is_reading_stator = False
                outlet_dist = line.split('=')[1].strip()
                   
            print(f"Levels = {levels}")
            print(f"Folder = {output_folder}")
            
        return use_default_rotor_bezier, use_default_stator_bezier, adjust_rotor_thickness, adjust_rotor_angle, adjust_stator_thickness, adjust_stator_angle, \
        output_folder, levels, nrow, show_section_plot, show_angle_distribution_plots, enable_bleed_air, rotor_patches_data, stator_patches_data, \
        inlet_area, inlet_dist, outlet_area, outlet_dist   

    except FileNotFoundError:
        print("File not found. Please ensure the Setting.txt exists.")



def adjustBezierCurve_d_l(BezierPoints):

    d_lB = BezierPoints
    mB = [0.0, 0.3, 0.7, 1.0] 
    t = np.arange(0, 1.01, 0.01)

    x = bezier(4, t, mB)
    y = bezier(4, t, d_lB)

    # Create the plot
    fig, ax = plt.subplots(num='Thickness Distribution')
    plt.subplots_adjust(bottom=0.5)  # Leave more space for the sliders

    # Plot the points
    points, = plt.plot(mB, d_lB, 'o-', label="Points")
    curve, = plt.plot(x,y)
    plt.title("Thickness Distribution - Béziercurve")
    plt.xlabel("x/l [-]")
    plt.ylabel("d/l [%]")


    # Set axis limits
    ax.set_xlim(0, 1)

    d_l_min = 0.0
    d_l_max = 10.0

    ax.set_ylim(d_l_min, d_l_max)

    # Add sliders for each point
    sliders = []  # Store slider objects
    slider_axes = []  # Store axes for sliders

    for i in range(4):  # Create one slider for each point
        ax_slider = plt.axes([0.2, 0.25 - i * 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        slider = Slider(ax_slider, f'Point {i + 1}', d_l_min, d_l_max, valinit=d_lB[i])
        sliders.append(slider)
        slider_axes.append(ax_slider)

    # Define update function for sliders
    def update(val):
        for i, slider in enumerate(sliders):
            d_lB[i] = slider.val  # Update y-coordinate for each point
        
        y = bezier(4, t, d_lB)
        curve.set_ydata(y)
        points.set_ydata(d_lB)  # Update the plot
        fig.canvas.draw_idle()

    # Connect sliders to the update function
    for slider in sliders:
        slider.on_changed(update)

    # Show the interactive plot
    plt.show()
    for i in range(len(d_lB)):
        d_lB[i] = round(d_lB[i], 2)

    debug_log.debug(f"New Bézier Point: {d_lB}", context="adjustBezierCurve_beta")
    
    return BezierPoints

def adjustBezierCurve_d(BezierPoints, cordlenght):

    d_lB = [point * cordlenght / 100 for point in BezierPoints]
    mB = [0.0, 0.3, 0.7, 1.0] 
    t = np.arange(0, 1.01, 0.01)

    x = bezier(4, t, mB)
    y = bezier(4, t, d_lB)

    # Create the plot
    fig, ax = plt.subplots(num='Thickness Distribution')
    plt.subplots_adjust(bottom=0.5)  # Leave more space for the sliders

    # Plot the points
    points, = plt.plot(mB, d_lB, 'o-', label="Points")
    curve, = plt.plot(x,y)
   # plt.figure(num='This is the title');
    plt.title("Thickness Distribution - Béziercurve")
    plt.xlabel("x/l [-]")
    plt.ylabel("d [mm]")
    plt.grid('on')


    # Set axis limits
    ax.set_xlim(0, 1)

    dmin = 0.0
    dmax = 5.0

    ax.set_ylim(dmin, dmax)

    # Add sliders for each point
    sliders = []  # Store slider objects
    slider_axes = []  # Store axes for sliders

    for i in range(4):  # Create one slider for each point
        ax_slider = plt.axes([0.2, 0.25 - i * 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        slider = Slider(ax_slider, f'Point {i + 1}', dmin, dmax, valinit=d_lB[i])
        sliders.append(slider)
        slider_axes.append(ax_slider)

    # Define update function for sliders
    def update(val):
        for i, slider in enumerate(sliders):
            d_lB[i] = slider.val  # Update y-coordinate for each point
        
        y = bezier(4, t, d_lB)
        curve.set_ydata(y)
        points.set_ydata(d_lB)  # Update the plot
        fig.canvas.draw_idle()

    # Connect sliders to the update function
    for slider in sliders:
        slider.on_changed(update)

    # Show the interactive plot
    plt.show()
    for i in range(len(d_lB)):
        d_lB[i] = round(d_lB[i]*100/cordlenght, 2)

    
    debug_log.debug(f"New Bézier Point: {d_lB}", context="adjustBezierCurve_d")
    return d_lB

def adjustBezierCurve_beta(BezierPoints):

    beta = BezierPoints

    mB = [0.0, 0.3, 0.7, 1.0] 
    t = np.arange(0, 1.01, 0.01)

    x = bezier(4, t, mB)
    y = bezier(4, t, beta)

    # Create the plot
    fig, ax = plt.subplots(num='Blade Angle Distribution')
    plt.subplots_adjust(bottom=0.5)  # Leave more space for the sliders

    # Plot the points
    points, = plt.plot(mB, beta, 'o-', label="Points")
    curve, = plt.plot(x,y)
    plt.title("Blade Angle Distribution - Béziercurve")
    plt.xlabel("x/l [-]")
    plt.ylabel("blade angle [°]")


    # Set axis limits
    ax.set_xlim(0, 1)

    beta_min = 0.0
    beta_max = 170

    ax.set_ylim(beta_min, beta_max)

    # Add sliders for each point
    sliders = []  # Store slider objects
    slider_axes = []  # Store axes for sliders

    for i in range(4):  # Create one slider for each point
        ax_slider = plt.axes([0.2, 0.25 - i * 0.05, 0.65, 0.03], facecolor='lightgoldenrodyellow')
        slider = Slider(ax_slider, f'Point {i + 1}', beta_min, beta_max, valinit=beta[i])
        sliders.append(slider)
        slider_axes.append(ax_slider)

    # Define update function for sliders
    def update(val):
        for i, slider in enumerate(sliders):
            beta[i] = slider.val  # Update y-coordinate for each point
        
        y = bezier(4, t, beta)
        curve.set_ydata(y)
        points.set_ydata(beta)  # Update the plot
        fig.canvas.draw_idle()

    # Connect sliders to the update function
    for slider in sliders:
        slider.on_changed(update)

    # Show the interactive plot
    plt.show()
    for i in range(len(beta)):
        beta[i] = round(beta[i], 2)

    debug_log.debug(f"New Bézier Point: {beta}", context="adjustBezierCurve_beta")
    return BezierPoints
