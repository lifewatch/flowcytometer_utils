import json
import base64
from pathlib import Path
import glob
import os

# Read the paths from the config file
config = {}
with open('./cyz2json/cyz2json_python/config.txt', 'r') as file:
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

# Extract directory paths from the config dictionary
directory = config.get('directory_path', None)

# Ensure the directory paths exist
if not directory or not os.path.isdir(directory):
    print("Error: Directory path not provided or does not exist.")
    exit(1)

# Get the list of all .json files in the current directory
json_files = glob.glob(os.path.join(directory, '*.json'))

for file in json_files:
    # Extract the base name of the JSON file (without the extension)
    json_filename = os.path.splitext(os.path.basename(file))[0]
    # Remove the `.cyz` pattern from the filename
    json_filename_cleaned = json_filename.replace('.cyz', '')
    # Define the directory where to save the images
    output_directory = f'{file}_images'
    # Create the output directory if it doesn't exist
    Path(output_directory).mkdir(parents=True, exist_ok=True)

    # Remove any existing files in the output directory
    for old_file in Path(output_directory).glob('*'):
        try:
            old_file.unlink()  # Delete the file
        except Exception as e:
            print(f"Error deleting file {old_file}: {e}")


    # Load the JSON file
    with open(file, 'r') as file_data:
        json_data = json.load(file_data)
    
    # Extract the image data (stored under a key 'images')
    image_data = json_data.get('images', [])

    # Loop through each item in the image data
    for item in image_data:
        # Extract the base64 string
        base64_string = item.get('base64')
        
        # Extract the particleId
        particle_id = item.get('particleId')
        
        # Decode the base64 string to raw binary data
        raw_image_data = base64.b64decode(base64_string)
        
        # Create a unique filename for each image using the particleId
        filename = f"{json_filename_cleaned}_full_{particle_id}.jpg"
        
        # Define the full path to save the image
        file_path = Path(output_directory) / filename
        
        # Write the raw image data to a file
        with open(file_path, 'wb') as image_file:
            image_file.write(raw_image_data)

        print(f"Saved image {filename}")

    # File to store particleIDs with empty base64 strings
    empty_base64_file = Path(output_directory) / "no_cropped_image_particle_ids.txt"

    # List to store particle IDs with empty base64 strings
    empty_particle_ids = []

    # Extract the image data (stored under a key 'crop_images')
    crop_image_data = json_data.get('crop_images', [])

    # Loop through each item in the image data
    for imgcr in crop_image_data:
        # Extract the base64 string
        base64_stringcr = imgcr.get('base64')
        
        # Extract the particleId
        particle_idcr = imgcr.get('particleId')
        
        # Check if there is a cropped image
        if not base64_stringcr:
            # Add particleId to the list if no cropped image
            empty_particle_ids.append(particle_idcr)
            continue  # Skip to the next item 
        
        # Decode the base64 string to raw binary data
        raw_imagecr_data = base64.b64decode(base64_stringcr)
        
        # Create a unique filename for each image using the particleId
        filenamecr = f"{json_filename_cleaned}_cropped_{particle_idcr}.jpg"
        
        # Define the full path to save the image
        file_path = Path(output_directory) / filenamecr
        
        # Write the raw image data to a file
        with open(file_path, 'wb') as imagecr_file:
            imagecr_file.write(raw_imagecr_data)

        print(f"Saved cropped image {filenamecr}")

    # Write the particle IDs with empty base64 strings to a file
    if empty_particle_ids:
        with open(empty_base64_file, 'w') as empty_file:
            for particle_id in empty_particle_ids:
                empty_file.write(f"{particle_id}\n")

    print(f"Saved particle IDs with empty base64 strings to {empty_base64_file}")