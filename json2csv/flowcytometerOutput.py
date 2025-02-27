import os
import pandas as pd
from PIL import Image
import io
import flowcytometer
import re
import datetime


class FlowcytometerOutput: 
    # INIT
    def __init__(self, path, csv_check):
        self.sample_metadata = {}
        self.csv_file = ''
        self.processing_data_file = ''
        self.json_file = path
        self.dir_path = os.path.dirname(self.json_file)
        output_directory = f'{path}_images'
        self.image_path = output_directory
        self.sample_metadata_file = ''
        self.csv_check = csv_check #give to subfunctions of class


        # check for csv and remove if found to reset directory after for reprocessing
        if csv_check:
            csv_files = [file for file in self.dir_path if file.endswith('.csv')]
            if csv_files:
                for csv_file in csv_files:
                    file_path = os.path.join(self.dir_path, csv_file)
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                if not csv_files:
                    print("No .csv files found to delete.")

    #wrapper to process LifeWatch/ Simon Stevin data
    def add_data_MIDAS(self, parse_dirname=True):
        if parse_dirname:
            self.collect_directory_name()
        self.find_sample_MIDAS()
        # Finally add some ease of use fields
        self.add_any_metadata({"month": self.sample_metadata["sample_datetime"].month,
                               "year": self.sample_metadata["sample_datetime"].year})
        print('Sample metadata updated!')

    def add_manual_metadata_VLIZ(self,
                                 project="LW",
                                 flowcytometer_version="CytoSense",
                                 comments=""
                                 ):
        # REQUIRES USER INPUT
        self.sample_metadata["project"] = project
        self.sample_metadata["flowcytometer_version"] = flowcytometer_version
        self.sample_metadata["comments"] = comments

        print('hardcoded metadata updated')

    #pass any metadata from other functions
    def add_any_metadata(self, data):
        assert type(data) == dict, "Provide data in dictionary"
        # Shallow merge, values in data replace self.sample_metadata if same key
        self.sample_metadata = {**self.sample_metadata, **data}

    # Get metadata from directory
    def collect_directory_name(self):
        """
        Extracts protocol, sample_date, station, and replicate from the filename and returns dictionary.
        :param json_file_path: str, the full path to the JSON file
        :return: dict, extracted metadata
        """
        # Extract the JSON file name without the directory
        json_file_name = os.path.basename(self.json_file)
        # Regular expression to extract the required fields from the filename
        match = re.match(r"(.*?)_(\d{8})_(\w+)_([\d]+)", json_file_name)
        if not match:
            raise ValueError(f"Filename {json_file_name} does not match the expected pattern.")

        # Extract components
        metadata = {
            "protocol": match.group(1),
            "sample_date": match.group(2),
            "station": match.group(3),
            "replicate": match.group(4),
        }

        self.add_any_metadata(metadata)


    # Get metadata from MIDAS
    def find_sample_MIDAS(self):
        return

    def collect_MIDAS_result(self, res):
        return

    def ask_tripactionid(self, suggestions=None):

        ask_text = "Please enter correct tripactionid:"
        if suggestions:
            ask_text = "Please enter correct tripactionid. Suggestions are {}:".format(suggestions)

        tripaction_input = input(ask_text)

        self.add_any_metadata({"tripactionid": int(tripaction_input)})
        self.find_sample_MIDAS()
        print("TripActionID {} found! -> {}, datetime: {}, station: {}".format(tripaction_input,
                                                                self.sample_metadata["action_type"],
                                                                self.sample_metadata["sample_datetime"],
                                                                self.sample_metadata["station"]))

    def calculate_processing_lag(self):
        assert self.sample_metadata["sample_datetime"] and self.sample_metadata[
            'fcm_datetime'], "Make sure Sample & lab processing datetime exist in sample_metadata!!"

        lag = self.sample_metadata['fcm_datetime'] - self.sample_metadata["sample_datetime"]
        self.add_any_metadata({"processing_lag_s": int(lag.total_seconds())})

    def extract_parameters_json(self):
        # Extract info from json file
        print('opening json')
        json_data, excel_file_name = flowcytometer.read_json(self.json_file)
        print('json data read successfully')
        # Append the directory to the excel_file_name
        excel_file_name_with_path = os.path.join(self.dir_path, os.path.basename(excel_file_name))
        self.processing_data_file = excel_file_name_with_path
        #pass info from sample_metdata

        print("calculating processing lag")
        fcm_datetime = json_data["fcm_datetime"][0].to_pydatetime()
        self.add_any_metadata({'fcm_datetime': fcm_datetime})
        self.calculate_processing_lag()
        #transfer between sample and processing dict so written to rigth csv file
        json_data["fcm_datetime"] = fcm_datetime
        json_data["processing_lag_s"] = self.sample_metadata['processing_lag_s']
        json_data["replicate"] = self.sample_metadata['replicate']
        json_data["protocol"] = self.sample_metadata['protocol']
        json_data["flowcytometer_version"] = self.sample_metadata['flowcytometer_version']

        # Save the DataFrame to the CSV file
        json_data.to_csv(excel_file_name_with_path, index=False)
        print('processing csv created!')

    def write_metadata_csv(self):
        df = pd.DataFrame([self.sample_metadata])
        # Select the columns you want and rearrange them (if needed)
        required_columns = ['action_type', 'comments', 'sample_datetime', 'month', 'project', 'sample_date', 'station', 'latitude', 'longitude', 'tripactionid', 'year']  # list of columns you need
        df = df[required_columns]  # Select only the required columns
        target_name_file = os.path.basename(self.json_file).replace(".cyz.json", "")
        sample_metadata_file_name = f"{target_name_file}_sample_metadata.csv"
        # Append the directory to the excel_file_name
        sample_metadata_file_name_with_path = os.path.join(self.dir_path, os.path.basename(sample_metadata_file_name))
        self.sample_metadata_file = sample_metadata_file_name_with_path
        df.to_csv(sample_metadata_file_name_with_path, index=False)
        print('sample metadata.csv written')



    def read_processed_sample(self):
        self.initLogger.info("Re-initialization of previously processed output!")
        # Read file into dict; this should be only 1 line of data
        df = pd.read_csv(self.sample_metadata_file, parse_dates=["datetime"])
        self.sample_metadata = flowcytometer.correct_encoding(df.iloc[0].to_dict()) #to add to script

        self.processing_data = pd.read_csv(self.processing_data_file, parse_dates=["fcm_datetime"])

        #Find dir with cropped images
        if not os.path.exists(self.image_path):
            self.initLogger.info("Can't find cropped images directory: {}!".format(self.image_path))
            self.image_path = None




