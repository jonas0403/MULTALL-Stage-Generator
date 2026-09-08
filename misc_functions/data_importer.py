import argparse
import os
import glob
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def main():
    """
    Translates a MATLAB script to Python for reading and processing
    complex .dat/.csv files with multiple data blocks and headers.
    """
    parser = argparse.ArgumentParser(
        description="Read and merge MULTALL output .csv files into a single file."
    )
    parser.add_argument("--folder", default=os.getcwd(),
                        help="Folder containing the input files (default: current directory)")
    parser.add_argument("--pattern", default='global-fixed_mean06_09xRPM_*hPa.csv',
                        help="Search pattern for the input files (default: %(default)s)")
    parser.add_argument("--search-pattern", default=None,
                        help="Alias for --pattern")
    parser.add_argument("--output", default='data_global.csv',
                        help="Output filename, saved in the input folder (default: %(default)s)")
    args = parser.parse_args()

    # ## Step 0: Find files
    # Define the folder and search pattern to find the input files.
    folder_path = os.path.abspath(args.folder)
    search_pattern = args.search_pattern or args.pattern

    # Define the output filename
    output_filename = args.output

    # Create the full path for the output file to save it in the same folder
    # as the input files. 
    output_filepath = os.path.join(folder_path, output_filename)

    
    # Use glob to find all matching files
    full_search_path = os.path.join(folder_path, search_pattern)
    file_list = glob.glob(full_search_path)
    
    # Filter out files containing '_NaN.csv'
    filenames = [f for f in file_list if '_NaN.csv' not in os.path.basename(f)]
    
    # Initialize a list to store data for the final plot from the last file
    all_circ_data_final = np.array([])
    CP_final, KAPPA_final = 0, 0
    
    # ## Main Loop: Iterate through each file found
    for i, current_full_path in enumerate(filenames):
        try:
            # ## Step 1: Open the file for reading
            current_filename = os.path.basename(current_full_path)
            print(f"Opening file: {current_filename}")

            with open(current_full_path, 'r') as f:
                
                # ## Step 2: Read initial parameters
                # Read single-value parameters from the top of the file.
                NSTEP = int(f.readline().split(',')[0])
                CP = float(f.readline().split(',')[0])
                CP_final = CP # Store for final plot
                KAPPA = float(f.readline().split(',')[0])
                KAPPA_final = KAPPA # Store for final plot
                
                IM = int(f.readline().split(',')[0])
                JM = int(f.readline().split(',')[0])
                KM = int(f.readline().split(',')[0])
                NROW = int(f.readline().split(',')[0])
                
                print('\n--- Initial Parameters ---')
                print(f'NSTEP = {NSTEP}')
                print(f'CP = {CP:.4f}')
                print(f'KAPPA = {KAPPA:.4f}')
                print(f'IM = {IM}')
                print(f'JM = {JM}')
                print(f'KM = {KM}')
                print(f'NROW = {NROW}')
                
                # ## Step 3: Read 'NR, JS...' table
                f.readline()  # Skip header line
                blade_data_rows = [next(f) for _ in range(2)]
                blade_table = np.loadtxt(blade_data_rows, delimiter=',')
                
                print('\n--- Blade Table Data ---')
                print(blade_table)

                # Helper function to find and read data tables using pandas
                def find_and_read_table(file_handle, start_text, num_rows):
                    """Skips lines until start_text is found, then reads the table."""
                    for line in file_handle:
                        if start_text in line:
                            break
                    
                    file_handle.readline() # Skip blank line after header
                    header_line = file_handle.readline().strip()
                    headers = [h.strip() for h in header_line.split(',')]
                    
                    df = pd.read_csv(file_handle, header=None, names=headers, nrows=num_rows)
                    return df

                # ## Step 4: Read 'massflow averaged values' table
                massflow_df = find_and_read_table(f, 'massflow averaged values', 3)
                print('\n--- Massflow Averaged Data ---')
                print(massflow_df)

                # ## Step 5: Read 'area averaged values' table
                area_df = find_and_read_table(f, 'area averaged values', 3)
                print('\n--- Area Averaged Data ---')
                print(area_df)

                # ## Step 5.5: Write data to a single output file
                file_mode = 'w' if i == 0 else 'a'
                # MODIFIED: Use the full output filepath
                with open(output_filepath, file_mode, newline='') as f_out:
                    if i > 0:
                        f_out.write('\n\n========================================\n\n')
                    f_out.write(f'Data from: {current_filename}\n\n')
                    
                    # Write massflow data
                    f_out.write('massflow averaged values\n')
                    massflow_df.to_csv(f_out, index=False)
                    f_out.write('\n')
                    
                    # Write area data
                    f_out.write('area averaged values\n')
                    area_df.to_csv(f_out, index=False)

                # MODIFIED: Use the full output filepath in the confirmation message
                print(f'Data from {current_filename} successfully written to {output_filepath}.')
                
                # ## Step 6: Read 'circumferentially averaged values' tables
                all_circ_data_rows = []
                line = f.readline()
                
                # Loop through the rest of the file to find all relevant data blocks
                while line:
                    if 'circumferentially averaged values' in line:
                        # Found a block, now skip headers
                        next(f)  # Skip empty line
                        next(f)  # Skip 'ROW i inlet/outlet' line
                        next(f)  # Skip empty line
                        next(f)  # Skip the header line (e.g., 'K, ETA...')
                        
                        # Read data lines until an empty line is found
                        while True:
                            data_line = f.readline()
                            if not data_line or not data_line.strip():
                                break # End of table block
                            
                            # Sanitize line by splitting on any whitespace or comma
                            values_str = re.split(r'[\s,]+', data_line.strip())
                            
                            # Filter out empty strings that may result from splitting
                            values_str = [v for v in values_str if v]
                            
                            if len(values_str) == 14:
                                all_circ_data_rows.append([float(v) for v in values_str])
                    
                    if 'MASS FLOW ALONG THE FLOW PATH' in line:
                        break # Stop reading if we hit the next major section
                        
                    line = f.readline()

                all_circ_data = np.array(all_circ_data_rows)
                all_circ_data_final = all_circ_data # Save data from the last file for plotting
                
                if all_circ_data.size > 0:
                    print(f'\n--- Combined Circumferentially Averaged Data ({len(all_circ_data)} rows) ---')
                    print(all_circ_data)

        except FileNotFoundError:
            print(f"Error: Could not open file {current_full_path}. Please check the path.")
        except Exception as e:
            print(f"An error occurred while processing {current_filename}: {e}")

# ## Step 7 is commented out in MATLAB, so it is skipped here.
    print('\nAll files have been successfully processed.')

if __name__ == '__main__':
    main()