import subprocess
import glob
import os


# Read the paths from the config file
config = {}
with open(r'C:\Users\wout.decrop\environments\Imagine\flowcytometer\flowcytometer_utils\cyz2json\cyz2json_python\config.txt', 'r') as file:
    for line in file:
        # Skip empty lines and comments
        if line.strip() == '' or line.strip().startswith('#'):
            continue
        # Split the line by the first occurrence of '='
        parts = line.split('=', 1)
        # Check if the line follows the key=value format
        if len(parts) != 2:
            print(f"Ignoring invalid line in config file: {line.strip()}")
            continue
        key, value = parts
        # Remove leading/trailing whitespace from key and value
        key = key.strip()
        value = value.strip()
        config[key] = value

# Extract directory and dotnet program paths from the config dictionary
directory = config.get('directory_path', None)
dotnet_program = config.get('dotnet_program_path', None)

# Ensure the directory and dotnet program paths exist
if not directory or not os.path.isdir(directory):
    print("Error: Directory path not provided or does not exist.")
    exit(1)

if not dotnet_program or not os.path.isfile(dotnet_program):
    print("Error: Dotnet program path not provided or does not exist.")
    exit(1)



# Get the list of all .cyz files in the current directory
cyz_files = glob.glob(os.path.join(directory, '*.cyz'))

# Loop through each file and run the dotnet command
for file in cyz_files:
    output_file = f"{file}.json"
    # Construct the command
    command = [
        'dotnet',
        dotnet_program,
        file,
        '--output',
        output_file
    ]
    print(command)
    try:
        # Run the command
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully processed {file}")
        print(f"Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {file}")
        print(f"Error: {e.stderr}")

# Make sure to handle potential errors
print("Finished processing all files.")