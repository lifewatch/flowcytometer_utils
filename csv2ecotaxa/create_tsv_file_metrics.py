import os
import pandas as pd
import zipfile
import shutil
from skimage.io import imread
from skimage import measure, morphology
from skimage.color import rgb2gray
import numpy as np



# Define the base with cyz files (we need their name to find the csv files)
base_path1 = r"location\to\folder"

def getImageRegionList(filename):
    # Read the image
    image = imread(filename)

    # If the image is colored (RGB), convert it to grayscale
    if image.ndim == 3:
        image = rgb2gray(image)

    # Threshold the image
    image_threshold = np.where(image > np.mean(image), 0., 1.0)

    # Perform dilation
    image_dilated = morphology.dilation(image_threshold, np.ones((4, 4)))

    # Label the regions
    label_list = measure.label(image_dilated)

    # Combine the thresholded image and labels
    label_list = (image_threshold * label_list).astype(int)

    # Return region properties
    return measure.regionprops(label_list)


# Find the region with the largest area
def getMaxArea(filename):
    region_list = getImageRegionList(filename)

    maxArea = None
    for property in region_list:
        if maxArea is None:
            maxArea = property
        else:
            if property.area > maxArea.area:
                maxArea = property
    return maxArea

def getMaxAreaDict(filename):
    property = getMaxArea(filename)

    if property is None:
        maxAreaDict = {'area': 0}
    else:
        maxAreaDict = {

            # Location of centroid (Unknown table prefix → Add "object_additional_")
            'object_additional_centroid_row': property.centroid[0],
            'object_additional_centroid_col': property.centroid[1],

            # Equivalent diameter (Unknown table prefix → Add "object_additional_")
            'object_additional_diameter_equivalent': property.equivalent_diameter,

            # Axis lengths (Unknown table prefix → Add "object_additional_")
            'object_additional_length_minor_axis': property.minor_axis_length,
            'object_additional_length_major_axis': property.major_axis_length,

            # Shape properties (Format must be Table_Field → Keep normal)
            'object_additional_eccentricity': property.eccentricity,
            'object_additional_area': property.area,
            'object_additional_perimeter': property.perimeter,
            'object_additional_orientation': property.orientation,

            # Additional area-related properties (Unknown table prefix → Add "object_additional_")
            'object_additional_area_convex': property.convex_area,
            'object_additional_area_filled': property.filled_area,

            # Bounding box (Unknown table prefix → Add "object_additional_")
            'object_additional_box_min_row': property.bbox[0],
            'object_additional_box_max_row': property.bbox[2],
            'object_additional_box_min_col': property.bbox[1],
            'object_additional_box_max_col': property.bbox[3],

            # Ratio properties (Unknown table prefix → Add "object_additional_")
            'object_additional_ratio_extent': property.extent,
            'object_additional_ratio_solidity': property.solidity,

            # Inertia tensor eigenvalues (Unknown table prefix → Add "object_additional_")
            'object_additional_inertia_tensor_eigenvalue1': property.inertia_tensor_eigvals[0],
            'object_additional_inertia_tensor_eigenvalue2': property.inertia_tensor_eigvals[1],

            # Hu moments (Unknown table prefix → Add "object_additional_")
            'object_additional_moments_hu1': property.moments_hu[0],
            'object_additional_moments_hu2': property.moments_hu[1],
            'object_additional_moments_hu3': property.moments_hu[2],
            'object_additional_moments_hu4': property.moments_hu[3],
            'object_additional_moments_hu5': property.moments_hu[4],
            'object_additional_moments_hu6': property.moments_hu[5],
            'object_additional_moments_hu7': property.moments_hu[6],

            # Euler number (Unknown table prefix → Add "object_additional_")
            'object_additional_euler_number': property.euler_number,

            # Count coordinates (Format must be Table_Field → Keep normal)
            'object_additional_countcoords': len(property.coords)
        }

    return maxAreaDict



# Function to add image properties to the dataset
def add_image_properties_to_data(data, image_folder):
    image_properties = []

    # Get all possible keys from getMaxAreaDict
    all_keys = [
        # Unknown table prefix → Add "object_additional_"
        'object_additional_centroid_row', 'object_additional_centroid_col', 'object_additional_diameter_equivalent',
        'object_additional_length_minor_axis', 'object_additional_length_major_axis', 'object_additional_area_convex',
        'object_additional_area_filled', 'object_additional_box_min_row', 'object_additional_box_max_row',
        'object_additional_box_min_col', 'object_additional_box_max_col', 'object_additional_ratio_extent',
        'object_additional_ratio_solidity', 'object_additional_inertia_tensor_eigenvalue1',
        'object_additional_inertia_tensor_eigenvalue2', 'object_additional_moments_hu1', 'object_additional_moments_hu2',
        'object_additional_moments_hu3', 'object_additional_moments_hu4', 'object_additional_moments_hu5',
        'object_additional_moments_hu6', 'object_additional_moments_hu7', 'object_additional_euler_number',
        'object_additional_eccentricity', 'object_additional_perimeter', 'object_additional_orientation', 'object_additional_area', 'object_additional_countcoords']
        # Format must be Table_Field → Keep normal
    #     'eccentricity', 'perim.', 'orientation', 'area', 'countcoords'
    # ]

    for _, row in data.iterrows():
        img_file = os.path.join(image_folder, str(row['object_id']))
        if os.path.exists(img_file):
            props = getMaxAreaDict(img_file)
        else:
            props = {key: None for key in all_keys}  # Assign None to all properties if file is missing

        image_properties.append(props)

    # Convert to DataFrame and merge
    properties_df = pd.DataFrame(image_properties)
    data = pd.concat([data, properties_df], axis=1)

    return data



def open_files(base_path, search_term1, search_term2):
    """
    Opens files based on search terms and ensures file extensions match.

    :param base_path: Directory where the files are located.
    :param search_term1: Partial name of the first file.
    :param search_term2: Partial name of the second file.
    """
    # Ensure the search terms have the correct extension
    if not search_term1.endswith('.csv'):
        search_term1 += '.csv'
    if not search_term2.endswith('.csv'):
        search_term2 += '.csv'

    # List files in the directory
    files = os.listdir(base_path)

    file1 = None
    file2 = None

    for file in files:
        if search_term1 in file:
            file1 = os.path.join(base_path, file)
        elif search_term2 in file:
            file2 = os.path.join(base_path, file)

    if file1:
        print(f"Opening {file1}...")
        data1 = pd.read_csv(file1)
        print(data1.head())
    else:
        print(f"File matching '{search_term1}' not found.")

    if file2:
        print(f"Opening {file2}...")
        data2 = pd.read_csv(file2)
        print(data2.head())
    else:
        print(f"File matching '{search_term2}' not found.")

    return data1,data2
def open_additional_file(file_path):
    """
    Opens an Excel file from a direct path.

    :param file_path: The exact path to the Excel file.
    :return: None
    """
    if os.path.exists(file_path):
        print(f"Opening {file_path}...")
        data = pd.read_excel(file_path)
        print(data.head())  # Display the first rows of the file
    else:
        print(f"File {file_path} does not exist.")

    return data




# Get all .cyz.json files in the folder
cyz_json_files = [f for f in os.listdir(base_path1) if f.endswith('.cyz.json')]

# Loop through each .cyz file
for cyz_json_file in cyz_json_files:
    # break
    # Extract the term from the .cyz file name (without the extension)
    term =cyz_json_file.split(".")[0]

    # Define search terms based on the current term
    search_term1 = f"{term}_sample_processing_data"
    search_term2 = f"{term}_sample_metadata"
    image_folder = rf"{base_path1}\{term}.cyz.json_images"

    # Open the first two files
    sample_processing_data, sample_metadata = open_files(base_path1, search_term1, search_term2)

    # Open the additional file directly
    additional_file = rf"flowcytometer_utils\to_ecotaxa\Aneris_key.xlsx" 

    # Add sample_metadata to every row in sample_processing_data
    sample_metadata_row = sample_metadata.iloc[0]  # Extract the first (and only) row of sample_metadata
    sample_processing_data_total = sample_processing_data.assign(**sample_metadata_row)

    # Rename columns based on the renaming_key
    renaming_dict = dict(zip(renaming_key["EXISTING TERM"], renaming_key["NEW TERM"]))
    sample_processing_data_total.rename(columns=renaming_dict, inplace=True)

    # Verify the result
    print(sample_processing_data_total.head())

    # Create a dictionary mapping 'NEW TERM' to 'TYPE'
    renaming_dict = pd.Series(renaming_key["TYPE"].values, index=renaming_key["NEW TERM"]).to_dict()

    # Add the 'TYPE' values as the first row in the renamed dataset
    type_values = [renaming_dict.get(col, None) for col in sample_processing_data_total.columns]
    type_row = pd.DataFrame([type_values], columns=sample_processing_data_total.columns)

    # Append the type row to the top of the DataFrame
    sample_processing_data_total_with_type = pd.concat([type_row, sample_processing_data_total], ignore_index=True)
    sample_processing_data_total_with_type['img_file_name'] = sample_processing_data_total_with_type['object_id']
    sample_processing_data_total_with_type = sample_processing_data_total_with_type.drop('object_protocol', axis=1)

    sample_processing_data_total_with_type['object_id'] = sample_processing_data_total_with_type[
        'object_id'].str.replace('.png', '.jpg')
    sample_processing_data_total_with_type['img_file_name'] = sample_processing_data_total_with_type[
        'img_file_name'].str.replace('.png', '.jpg')

    # Add image properties to the dataset
    sample_processing_data_total_with_type = add_image_properties_to_data(sample_processing_data_total_with_type,
                                                                                image_folder)

    # Assuming your DataFrame is named sample_processing_data_total_with_type
    sample_processing_data_total_with_type.iloc[0] = sample_processing_data_total_with_type.iloc[0].fillna('[f]')


    # Get all image files from the folder (assuming the images have a .jpg, .png, etc. extension)
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('jpg', 'jpeg', 'png', 'gif'))]
    sample_processing_data_total_with_type.to_csv(rf"output.csv", index=False)

    # Create a new directory to temporarily hold the files to be zipped
    temp_dir = rf"{base_path1}\TEMP_ZIP"
    # shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    tsv_file_path = rf"{temp_dir}\ecotaxa_{term}.tsv"  # Replace with the actual path

    # Copy the image files to the temporary directory
    for img_file in image_files:
        img_path = os.path.join(image_folder, img_file)
        shutil.copy(img_path, temp_dir)

    # Copy the TSV file to the temporary directory
    sample_processing_data_total_with_type.to_csv(tsv_file_path, sep='\t', index=False)

    print(f"Data has been saved as a TSV file at: {tsv_file_path}")

    # Define the output ZIP file path
    zip_file_path = rf"{base_path1}\output_to_ecotaxa\ecotaxa_{term}.zip"

    # Zip the contents of the temporary directory
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    # Clean up by removing the temporary directory
    shutil.rmtree(temp_dir)

    print(f"Files have been zipped into: {zip_file_path}")