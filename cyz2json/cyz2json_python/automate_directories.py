import subprocess
import os
import pathlib

# List of directories to be analyzed
directories = [

    r'Spring 2023\51',
    r'Spring 2023\130',
    r'Spring 2023\W08'
    # Add more directories here
]

# List of directories to be analyzed
directories = [
    r'FCM data\Datafiles\Jens\testing'
]

# Path to config file
config_file_path = pathlib.Path(r"flowcytometer_utils\cyz2json\cyz2json_python\config.txt") # be carefull if you have raw .cyz files in your directory you need to skip these!

# Path to python script to be used
script_path_conversion = 'conversion_json.py'
script_path_extraction = 'extraction_image.py'

# Read the original config file
with open(config_file_path, 'r') as file:
    config_lines = file.readlines()

# Function to update the directory_path in the config file
def update_config(directory):
    with open(config_file_path, 'w') as file:
        for line in config_lines:
            if line.strip().startswith('directory_path='):
                file.write(f'directory_path={directory}\n')
            else:
                file.write(line)

# Loop over each directory, update the config file, and run the script
for directory in directories:
    # Update the config file with the current directory
    update_config(directory)
    print("runnning conversion")
    # Run the convertion script
    result_conversion = subprocess.run(['python', script_path_conversion], check=True, capture_output=True, text=True)
    print("run extraction")
    # Run the extracting script
    result_extraction = subprocess.run(['python', script_path_extraction], check=True, capture_output=True, text=True)

    # Print the output of the script
    print(f"Output for directory {directory}:")
    print(result_conversion.stdout)
    if result_conversion.stderr:
        print("Errors:")
        print(result_conversion.stderr)

    # Print the output of the script
    print(f"Output for directory {directory}:")
    print(result_extraction.stdout)
    if result_extraction.stderr:
        print("Errors:")
        print(result_extraction.stderr)

print("Finished processing all directories.")