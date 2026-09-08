import argparse
import os

# --- 1. CONFIGURATION ---
# Override any value via command line; defaults are relative to the current
# working directory.

# Specify the folder where your template file is located.
SOURCE_FOLDER = os.getcwd()

# Specify the folder where you want to save the new files.
OUTPUT_FOLDER = SOURCE_FOLDER

# The name of the master input file to use as a template.
BASE_FILENAME = 'stage_1_11.dat'

# The exact line number you want to change in the file.
TARGET_LINE_NUMBER = 1762

# The string template for the new output filenames.
OUTPUT_FILENAME_TEMPLATE = 'aspirated_stators_08xRPM_5mflow_{}hPa.dat'

# --- Define the overall range and the STANDARD step size ---
START_VALUE = 100000.0
END_VALUE = 150000.0
STEP_VALUE = 5000.0

# --- Define the SPECIAL interval and its step size ---
# This interval starts at START_VALUE and goes up to the value specified here.
# For values *after* this point, the standard STEP_VALUE will be used.
SPECIAL_INTERVAL_END = 120000.0
SPECIAL_STEP_VALUE = 2500.0


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate multiple .dat files with varying pressure values."
    )
    parser.add_argument("--source-folder", default=SOURCE_FOLDER,
                        help="Folder containing the template .dat file (default: current directory)")
    parser.add_argument("--output-folder", default=None,
                        help="Folder to write generated files (default: same as source folder)")
    parser.add_argument("--base-filename", default=BASE_FILENAME,
                        help="Template file to modify (default: %(default)s)")
    parser.add_argument("--target-line", type=int, default=TARGET_LINE_NUMBER,
                        help="Line number to modify (1-based, default: %(default)s)")
    parser.add_argument("--filename-template", default=OUTPUT_FILENAME_TEMPLATE,
                        help="Output filename template using {} as pressure placeholder (default: %(default)s)")
    parser.add_argument("--start", type=float, default=START_VALUE,
                        help="Start pressure value (default: %(default)s)")
    parser.add_argument("--end", type=float, default=END_VALUE,
                        help="End pressure value (default: %(default)s)")
    parser.add_argument("--step", type=float, default=STEP_VALUE,
                        help="Standard pressure step (default: %(default)s)")
    parser.add_argument("--special-end", type=float, default=SPECIAL_INTERVAL_END,
                        help="End value of the special (finer-step) interval (default: %(default)s)")
    parser.add_argument("--special-step", type=float, default=SPECIAL_STEP_VALUE,
                        help="Step size inside the special interval (default: %(default)s)")
    return parser.parse_args()


# --- 2. SCRIPT LOGIC (No need to edit below this line) ---

def generate_files(args=None):
    """
    Reads a base file, modifies a specific line with a range of values
    using different step sizes for different intervals, and saves new files.
    """
    args = args or parse_args()
    print("--- Starting File Generation ---")

    source_folder = os.path.abspath(args.source_folder)
    output_folder = os.path.abspath(args.output_folder or source_folder)
    base_filename = args.base_filename
    target_line = args.target_line

    full_base_path = os.path.join(source_folder, base_filename)

    # --- Read the base template file into memory ---
    try:
        with open(full_base_path, 'r') as f:
            lines = f.readlines()
        print(f"Successfully read base file: '{full_base_path}'")
    except FileNotFoundError:
        print(f"Error: The base file '{full_base_path}' was not found.")
        print("Please check the source folder and --base-filename arguments.")
        return

    # --- Validate the file length ---
    if len(lines) < target_line:
        print(f"Error: The file '{base_filename}' has only {len(lines)} lines, but the script needs to modify line {target_line}.")
        return

    # --- Create the output directory if it doesn't exist ---
    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
            print(f"Created output directory: '{output_folder}'")
        except OSError as e:
            print(f"Error: Could not create output directory '{output_folder}'. Reason: {e}")
            return

    # --- Loop through the specified range using a while loop for flexibility ---
    current_value = args.start
    file_counter = 0

    print("\n--- Generating Files ---")
    while current_value <= args.end:
        # Create the new line content and filename
        # The formatting ensures the value has one decimal place, e.g., 100000.0
        new_line = f"  {current_value:.1f}  {current_value:.1f}\n"
        
        # Format the pressure code for the filename (e.g., 1000hPa, 1025hPa)
        # It takes the integer part of the value and divides by 100
        pressure_code = int(current_value / 100)
        new_filename = args.filename_template.format(pressure_code)
        
        full_output_path = os.path.join(output_folder, new_filename)

        # Create a new list of lines with the modification
        new_lines = list(lines)
        new_lines[target_line - 1] = new_line

        # Write the new file to disk
        try:
            with open(full_output_path, 'w') as f:
                f.writelines(new_lines)
            print(f"-> Created: {new_filename} with value {current_value:.1f}")
            file_counter += 1
        except IOError as e:
            print(f"Error: Could not write file '{full_output_path}'. Reason: {e}")

        # --- Logic to determine the next step size ---
        # If the current value is within the special interval, use the special step.
        if current_value < args.special_end:
            current_value += args.special_step
        # Otherwise, use the standard step.
        else:
            current_value += args.step

    print(f"\n--- File Generation Complete ---")
    print(f"Total files created: {file_counter}")


if __name__ == "__main__":
    generate_files()