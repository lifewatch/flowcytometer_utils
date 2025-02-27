# Flow Cytometer Data Reformatting

## Overview
The **Flow Cytometer Data Reformatting** process involves extracting, processing, and transforming flow cytometry data from JSON files and associated metadata into a more interpretable and consistent format. This allows the data to be integrated into internal VLIZ structures, facilitating further analysis. The process is divided into two primary components: the **[flowcytometer.py](flowcytometer.py)** class and the **[flowcytometerOutput.py](flowcytometerOutput.py)** class.

## Key Components

1. **[flowcytometer.py](flowcytometer.py)** Class:
   This class contains the base functionality for:
   - Parsing metadata from the file name.
   - Connecting to the MIDAS database.
   - Querying the MIDAS database.
   - Reading metadata from the JSON file and passing it to a dictionary while reformatting the data.

2. **[flowcytometerOutput.py](flowcytometerOutput.py)** Class:
   This class builds upon the base functionality of the **[flowcytometer.py](flowcytometer.py)** class and performs the following actions:
   - Initializes the **FlowCytometer** object.
   - Adds metadata collected from the file name, MIDAS (coordinates, sampling datetime, trip action, action type), and hardcoded sample metadata (project, device type, etc.) to a dictionary.
   - Calculates processing lag as the difference between sampling and lab processing datetime.

## Steps

### Running the Script
Running the **[reformat.py](reformat.py)** script initializes the **[flowcytometerOutput.py](flowcytometerOutput.py)** class, and the following functions are executed in order:
1. **add_manual_metadata_VLIZ()**: Adds additional hardcoded metadata.
2. **data_MIDAS()**: Fetches metadata from the research vessel's MIDAS system.
3. **write_metadata_csv()**: Writes the sample metadata to a CSV file (`sample_metadata.csv`).
4. **extract_parameters_json()**: Extracts flow cytometer parameters from the JSON file and calculates additional parameters (e.g., processing lag).
5. **add_any_metadata()** *(optional)*: Adds any additional metrics that are available in a dictionary.

### Output Files
At the end of the script execution, two CSV files are generated per sample:
- `sample_metadata.csv`: Contains all metadata related to sampling.
- `sample_processing.csv`: Contains all metadata related to laboratory processing.

Finally, the function `concat_csv()` combines all the `sample_metadata.csv` files into a single `combined_sample_data.csv` file.

### Database Upload
The two CSVs per sample, along with previously extracted images, can be used in the next steps

## What happens within the script

This script harvests sample- and sample-processing-specific metadata from:
- The MIDAS vessel information system.
- The sample file name.
- Some hardcoded metadata 

### Connection to MIDAS
The script connects to an internal **VLIZ** database using credentials (via URI). For security reasons, this script cannot be shared. The script queries the MIDAS database for sample metadata based on sample date and station. It collects real-time coordinates, datetime of sampling, action type (e.g., Niskin bottle samples), and a unique trip action ID (`tripactionID`). This information is stored in a dictionary.

### Handling Missing Data
In cases where the MIDAS database is not accessible (e.g., samples taken with an external vessel), the `add_any_metadata` function is used. This function processes a CSV file with relevant metadata (datetime, coordinates, action type) and outputs it as a dictionary.

If querying MIDAS fails due to human error or incorrect sample dates, the function `find_sample_midas()` uses a two-day time range to find the relevant sample data. For security reasons this script cannot be shared.

### Writing Metadata to CSV
At the end of the reformatting process, the `write_metadata_csv()` function generates the `sample_metadata.csv` file.

### Extracting Processing Data from JSON

The `extract_parameters_json()` function is the most important function for extracting processing data from the **[flowcytometerOutput.py](flowcytometerOutput.py)** class. It reads the JSON file, extracts the necessary information, and writes the `sample_processing_data.csv` file.

The **[flowcytometer.py](flowcytometer.py)** class contains several critical functions for processing flow cytometry data, such as:
- `calculate_processing_lag()`: This function calculates the time lag between sample collection (`datetime_sample`) and measurement initiation (`fcm_datetime`), providing insights into instrument efficiency.
- `read_json()`: This function is used to read all necessary data from the JSON file.

## Conclusion
This systematic approach to data reformatting ensures that all metadata and flow cytometer parameters are properly extracted, reformatted, and saved in CSV files. This makes the data more accessible for integration into downstream workflows, ensuring both reproducibility and interpretability of the flow cytometry experiments.
