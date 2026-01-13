import json
import pandas as pd
import re
import os 
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import pathlib
import numpy as np
 
### HANDELING SAMPLE METADATA ###


# MIDAS
def get_data_MIDAS(TA):
    return()

def query_sample_MIDAS(station, yyyymmdd):
    return()

#### HANDELING JSON DATATYPE -> PROCESSING DATA####

import json
import re
import pandas as pd
from datetime import datetime
import json
import re
import pandas as pd
from datetime import datetime

def flatten_dict(d, parent_key='', sep='_'):
    """Recursively flatten a nested dictionary."""
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

def read_json(json_file, separate_concentration_measurement="checked",
              flowcytometer_version="CytoSense", remote_file_server="Do nothing"):
    """
    Parse a CytoSense .json file and extract particle metadata and instrument settings.
    
    :param json_file: Path to *.json file as obtained with extraction script
    :param separate_concentration_measurement: Optional metadata flag
    :param flowcytometer_version: Optional metadata flag
    :param remote_file_server: Optional metadata flag
    :return: (DataFrame, excel_file_name)
    """
    # Load JSON
    with open(json_file, 'r', errors='ignore') as f:
        data = json.load(f)
    print("JSON loaded")

    instr = data['instrument']
    ms = instr.get('measurementSettings', {})
    mr = instr.get('measurementResults', {})

    # Base repeated metadata
    repeated_data = {
        "instrument_name": instr.get("name"),
        "serial_number": instr.get("serialNumber"),
        "sample_core_speed": instr.get("sampleCoreSpeed"),
        "laser_beam_width": instr.get("laserBeamWidth"),
        "flowcytometer_version": flowcytometer_version,
        "remote_file_server": remote_file_server,
        "separate_concentration_measurement": separate_concentration_measurement
    }
    flat_ms = flatten_dict(ms, parent_key='ms')
    flat_mr = flatten_dict(mr, parent_key='mr')

    # Flatten measurementSettings and measurementResults
    repeated_data.update(dict(list(flat_ms.items())[:25]))
    repeated_data.update(dict(list(flat_mr.items())[:25]))
    # Parse start datetime
    datetime_str = mr.get('start')
    if datetime_str:
        try:
            parsed_datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            repeated_data["fcm_datetime"] = parsed_datetime.replace(microsecond=0)
        except Exception as e:
            print(f"Error parsing datetime: {e}")
            repeated_data["fcm_datetime"] = None

    # Extract channels
    for ch in instr.get("channels", []):
        repeated_data[f"channel_{ch['id']}_desc"] = ch.get("description")

    # # Extract Cytoclus easy display
    # cytoclus_mapping = {
    #     "FWS_R": r"FWS R: (\d+)",
    #     "FWS_L": r"FWS L: (\d+)",
    #     "SWS": r"SWS: (\d+)",
    #     "FL_Yellow": r"FL Yellow: (\d+)",
    #     "FL_Orange": r"FL Orange: (\d+)",
    #     "FL_Red": r"FL Red: (\d+)",
    #     "FL_Red2": r"FL Red 2: (\d+)"
    # }
    # easy_display = ms.get("easy_display_cytoclus", "")
    # for key, pattern in cytoclus_mapping.items():
    #     match = re.search(pattern, easy_display)
    #     repeated_data[key] = match.group(1) if match else None

    # # SmartGrid
    # smartgrid_mapping = {
    #     "smartgrid_mode_SWS": "SWS",
    #     "smartgrid_mode_FL_Yellow": "FL Yellow",
    #     "smartgrid_mode_FL_Orange": "FL Orange",
    #     "smartgrid_mode_FL_Red": "FL Red"
    # }
    # smartgrid_str = ms.get("SmartGrid_str", "")
    # for key, val in smartgrid_mapping.items():
    #     repeated_data[key] = val in smartgrid_str

    # Prepare per-particle rows
    rows = []
    filename_without_extension = data.get('filename', '').replace(".cyz", "")
    excel_file_name = f"{filename_without_extension}_sample_processing_data.csv"
    repeated_data["excel_file_name"] = excel_file_name

    for particle in data.get('images', []):
        if particle.get('base64'):
            unique_id = f"{filename_without_extension}_cropped_{particle['particleId']}.png"
            row = {"file": unique_id, "particle_id": particle['particleId'], **repeated_data}
            rows.append(row)

    df = pd.DataFrame(rows)
    return df, excel_file_name

# def read_json(json_file, separate_concentration_measurement="checked",
    #           flowcytometer_version="CytoSense", remote_file_server="Do nothing"):
    # """
    # Parse a CytoSense .json file and extract particle metadata and instrument settings.
    
    # :param json_file: Path to *.json file as obtained with extraction script
    # :param separate_concentration_measurement: Optional metadata flag
    # :param flowcytometer_version: Optional metadata flag
    # :param remote_file_server: Optional metadata flag
    # :return: (DataFrame, excel_file_name)
    # """
    # # Load JSON
    # with open(json_file, 'r', errors='ignore') as f:
    #     data = json.load(f)
    # print("JSON loaded")

    # instr = data['instrument']
    # ms = instr['measurementSettings']
    # mr = instr['measurementResults']

    # # Repeated metadata
    # repeated_data = {
    #     "instrument_name": instr.get("name"),
    #     "serial_number": instr.get("serialNumber"),
    #     "sample_core_speed": instr.get("sampleCoreSpeed"),
    #     "laser_beam_width": instr.get("laserBeamWidth"),
    #     "flowcytometer_version": flowcytometer_version,
    #     "remote_file_server": remote_file_server,
    #     "separate_concentration_measurement": separate_concentration_measurement,
    #     # Measurement settings
    # }

    # # Parse start datetime
    # datetime_str = mr.get('start')
    # if datetime_str:
    #     # Some JSONs include fractional seconds and timezone
    #     try:
    #         parsed_datetime = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    #         repeated_data["fcm_datetime"] = parsed_datetime.replace(microsecond=0)
    #     except Exception as e:
    #         print(f"Error parsing datetime: {e}")
    #         repeated_data["fcm_datetime"] = None

    # # Extract channels
    # for ch in instr.get("channels", []):
    #     repeated_data[f"channel_{ch['id']}_desc"] = ch.get("description")

    # # Extract Cytoclus easy display
    # cytoclus_mapping = {
    #     "FWS_R": r"FWS R: (\d+)",
    #     "FWS_L": r"FWS L: (\d+)",
    #     "SWS": r"SWS: (\d+)",
    #     "FL_Yellow": r"FL Yellow: (\d+)",
    #     "FL_Orange": r"FL Orange: (\d+)",
    #     "FL_Red": r"FL Red: (\d+)",
    #     "FL_Red2": r"FL Red 2: (\d+)"
    # }
    # easy_display = ms.get("easy_display_cytoclus", "")
    # for key, pattern in cytoclus_mapping.items():
    #     match = re.search(pattern, easy_display)
    #     repeated_data[key] = match.group(1) if match else None

    # # SmartGrid
    # smartgrid_mapping = {
    #     "smartgrid_mode_SWS": "SWS",
    #     "smartgrid_mode_FL_Yellow": "FL Yellow",
    #     "smartgrid_mode_FL_Orange": "FL Orange",
    #     "smartgrid_mode_FL_Red": "FL Red"
    # }
    # smartgrid_str = ms.get("SmartGrid_str", "")
    # for key, val in smartgrid_mapping.items():
    #     repeated_data[key] = val in smartgrid_str

    # # Prepare per-particle rows
    # rows = []
    # filename_without_extension = data.get('filename', '').replace(".cyz", "")
    # excel_file_name = f"{filename_without_extension}_sample_processing_data.csv"
    # repeated_data["excel_file_name"] = excel_file_name

    # for particle in data.get('crop_images', []):
    #     if particle.get('base64'):
    #         unique_id = f"{filename_without_extension}_cropped_{particle['particleId']}.png"
    #         row = {"file": unique_id, "particle_id": particle['particleId'], **repeated_data}
    #         rows.append(row)

    # df = pd.DataFrame(rows)
    # return df, excel_file_name

# def read_json(json_file, separate_concentration_measurement="checked", flowcytometer_version="CytoSense", remote_file_server="Do nothing"):
    """
    :param json_file: *.json file as obtained with extraction script
    :param extra_data: dict, additional information to include in repeated data
    :return: pandas dataframe with parsed *.json info
    """

    # Read the JSON file
    with open(json_file, 'r', errors='ignore') as f:
        data = json.load(f)

    print('json loaded')

    # Extract repeated data
    repeated_data = {"sampling_time_s": data['instrument']['measurementSettings']['sampling_time_s'],
                     "sample_pump_ul_s": data['instrument']['measurementSettings']['sample_pump_ul_s'],
                     "limit_particle_rate_s": data['instrument']['measurementSettings']['limit_particle_rate_s'],
                     "minimum_speed_ul_s": data['instrument']['measurementSettings']['minimum_speed_ul_s'],
                     "flush": data['instrument']['measurementSettings']['flush'],
                     "beads_measurement": data['instrument']['measurementSettings']['beads_measurement_2'],
                     "smart_trigger": data['instrument']['measurementSettings']['smart_trigger'],
                     "maximum_measurement_time_s": data['instrument']['measurementResults']['maximum_measurement_time_s'],
                     "analysed_volume": data['instrument']['measurementResults']['analysed_volume'],
                     "pumped_volume": data['instrument']['measurementResults']['pumped_volume'],
                     "images_in_flow": data['instrument']['measurementSettings']['images_in_flow'],
                     "speak_when_finished": data['instrument']['measurementSettings']['speak_when_finished'],
                     "enable_images_in_flow": data['instrument']['measurementSettings']['enable_images_in_flow'],
                     "maximum_images_in_flow": data['instrument']['measurementSettings']['maximum_images_in_flow'],
                     "ROI": data['instrument']['measurementSettings']['ROI'],
                     "restrict_FWS_min": data['instrument']['measurementSettings']['restrict_FWS_min'],
                     "restrict_FWS_max": data['instrument']['measurementSettings']['restrict_FWS_max'],
                     "target_mode": data['instrument']['measurementSettings']['target_mode'],
                     "measurement_noise_levels": data['instrument']['measurementSettings']['measurement_noise_levels'],
                     "adaptive_MaxTimeOut": data['instrument']['measurementSettings']['adaptive_MaxTimeOut'],
                     "adaptive_MaxTimeOut_method": data['instrument']['measurementSettings']['adaptive_MaxTimeOut3'],
                     "enable_export": data['instrument']['measurementSettings']['enable_export'],
                     "flowcytometer_version": flowcytometer_version, "remote_file_server": remote_file_server,
                     "separate_concentration_measurement": separate_concentration_measurement}

    # Add specific extra data directly

    # Modification needed to get fcm_datetime
    datetime_str = data['instrument']['measurementResults']['start']
    datetime_part, timezone_part = datetime_str.rsplit('+', 1)
    # Truncate the fractional seconds part to 6 digits (microseconds)
    datetime_part = datetime_part[:26]  # Keep only the first 6 digits of the fractional part
    # Reassemble the datetime string
    datetime_str_truncated = datetime_part + '+' + timezone_part
    # Specific time format from flowcytometer
    format_str = '%Y-%m-%dT%H:%M:%S.%f%z'
    parsed_datetime = datetime.strptime(datetime_str_truncated, format_str)
    # Convert to naive datetime by removing the timezone and fractional seconds
    # Removing the timezone
    naive_datetime = parsed_datetime.replace(tzinfo=None)
    # Truncate fractional seconds
    naive_datetime = naive_datetime.replace(microsecond=0)
    repeated_data["fcm_datetime"] = naive_datetime

    # Split easy_display_cytoclus into separate columns
    cytoclus_mapping = {
        "FWS_R": r"FWS R: (\d+)",
        "FWS_L": r"FWS L: (\d+)",
        "SWS": r"SWS: (\d+)",
        "FL_Yellow": r"FL Yellow: (\d+)",
        "FL_Orange": r"FL Orange: (\d+)",
        "FL_Red": r"FL Red: (\d+)",
        "FL_Red2": r"FL Red 2: (\d+)"
    }

    # Split SmartGrid_str into separate boolean columns
    smartgrid_mapping = {
        "smartgrid_mode_SWS": "SWS",
        "smartgrid_mode_FL_Yellow": "FL Yellow",
        "smartgrid_mode_FL_Orange": "FL Orange",
        "smartgrid_mode_FL_Red": "FL Red"
    }

    # Extract easy_display_cytoclus values into columns
    cytoclus_values = {}
    for column, pattern in cytoclus_mapping.items():
        match = re.search(pattern, data['instrument']['measurementSettings']['easy_display_cytoclus'])
        cytoclus_values[column] = match.group(1) if match else None
    
    # Extract SmartGrid_str into boolean columns
    smartgrid_values = {}
    for column, term in smartgrid_mapping.items():
        smartgrid_values[column] = term in data['instrument']['measurementSettings']['SmartGrid_str']
    
    # Combine repeated data with extracted values
    repeated_data.update(cytoclus_values)
    repeated_data.update(smartgrid_values)
    
    # Extract unique data from crop_images
    rows = []
    # Remove .cyz from filename
    filename_without_extension = data['filename'].replace(".cyz", "")
    excel_file_name = f"{filename_without_extension}_sample_processing_data.csv"
    repeated_data["excel_file_name"] = excel_file_name
    for particle in data['crop_images']:
        if particle['base64']:  # Check if base64 is not empty
            unique_id = f"{filename_without_extension}_cropped_{particle['particleId']}.png"
            repeated_data["particle_id"] = particle['particleId']
            row_file = {"file": unique_id, **repeated_data}
            rows.append(row_file)


    
     # Create a DataFrame
    df = pd.DataFrame(rows)
    return df, excel_file_name

def concat_csv(pathdir, out=None):
    """
    concats sample data csv files from directory structure
    :param pathdir: path to top level directory containing individual processed fcm outputs
    :return: concatenated csv
    """
    csv_files = []
    for file in os.listdir(pathdir):
        if file.endswith('.csv') and "processing" not in file:
            csv_files.append(os.path.join(pathdir, file))

    print(csv_files)
    
    dataframes = []
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
            dataframes.append(df)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    # Concatenate all DataFrames, matching on columns
    combined_csv = pd.concat([df.reindex(sorted(df.columns), axis=1) for df in dataframes])

    print(combined_csv)
    if out:
        combined_csv.to_csv(out, index=False)
    else:
        combined_csv.to_csv(os.path.join(pathdir, "combined_sample_data.csv"), index=False)
        print('Done!')


