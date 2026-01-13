import json
import pandas as pd
import re
import os 
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import pathlib
import numpy as np    


from functions import add_image_properties_to_data


json_file=rf"C:\Users\wout.decrop\Documents\environments\flowcytometer_utils_public\data\test\LW2019protocol1_20240306_ZG02_2 2024-05-07 13h57.cyz.json"


with open(json_file, 'r', errors='ignore') as f:
    data = json.load(f)

json_filename = os.path.splitext(os.path.basename(json_file))[0]
json_filename_cleaned = json_filename.replace('.cyz', '')
csv_file= json_file.replace('.cyz.json', '.csv')


# Extract particles with hasImage == True
particles_with_images = [p for p in data.get('particles', []) if p.get('hasImage')]

# Define possible parameter keys
parameters_keys = ['asymmetry', 'average', 'centreOfGravity', 'description', 'fillFactor', 'first', 
                   'inertia', 'last', 'length', 'maximum', 'minimum', 'numberOfCells', 'sampleLength', 
                   'swscov', 'timeOfArrival', 'total', 'variableLength']

flattened_particles = []

for particle in particles_with_images:
    flat_particle = {
        'particleId': particle.get('particleId'),
        'hasImage': particle.get('hasImage')
    }
    
    # Flatten pulseShapes
    for ps in particle.get('pulseShapes', []):
        desc = ps['description'].replace(" ", "_")  # e.g., "Fl Orange" -> "Fl_Orange"
        flat_particle[f'{desc}_values'] = ps['values']
    
    # Flatten parameters (first element only if exists)
    parameters = particle.get('parameters', [])
    if parameters:
        param = parameters[0]
        for key in parameters_keys:
            flat_particle[f'parameters_{key}'] = param.get(key)
    else:
        for key in parameters_keys:
            flat_particle[f'parameters_{key}'] = None
    
    flattened_particles.append(flat_particle)

# Convert to DataFrame
df = pd.DataFrame(flattened_particles)

# Show DataFrame
pd.set_option('display.max_columns', None)  # display all columns
print(df.head())

image_folder = json_file + "_images" #=rf"C:\Users\wout.decrop\Documents\environments\flowcytometer_utils_public\data\test\LW2019protocol1_20240306_ZG02_2 2024-05-07 13h57.cyz.json"

# image_folder = r"data\STATION\SWS250-ST-FLRmax50-1000im-PMTlow 2025-03-04 18h10.cyz.json_images"
df['object_id'] = json_filename_cleaned + '_full_' + df['particleId'].astype(str) + ".jpg"

# Add the image properties to the DataFrame
data_with_image_props = add_image_properties_to_data(df, image_folder)
# json_file=rf"C:\Users\wout.decrop\Documents\environments\flowcytometer_utils_public\data\test\LW2019protocol1_20240306_ZG02_2 2024-05-07 13h57.cyz.json"

data_cleaned = data_with_image_props.drop(columns=['particleId', 'hasImage','parameters_description'], errors='ignore')

# Rename 'object_id' to 'image_location'
data_cleaned = data_cleaned.rename(columns={'object_id': 'image'})

# Reorder columns to make 'image_location' first
cols = data_cleaned.columns.tolist()
if 'image' in cols:
    cols.remove('image')
    cols = ['image']+ ['image_location'] + cols

data_cleaned['image_location'] = data_cleaned["image"].apply(lambda x: os.path.join(image_folder, str(x)))


data_cleaned = data_cleaned[cols]
# Save the DataFrame
data_cleaned.to_csv(csv_file, index=False)

print(f"Saved CSV to: {csv_file}")