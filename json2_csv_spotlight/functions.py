import os
import pandas as pd
import zipfile
import shutil
from skimage.io import imread
from skimage import measure, morphology
from skimage.color import rgb2gray
import numpy as np

import os
import pandas as pd
from tqdm import tqdm  # tqdm for progress bar



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

    # All possible keys from getMaxAreaDict
    all_keys = [
        'object_additional_centroid_row', 'object_additional_centroid_col', 'object_additional_diameter_equivalent',
        'object_additional_length_minor_axis', 'object_additional_length_major_axis', 'object_additional_area_convex',
        'object_additional_area_filled', 'object_additional_box_min_row', 'object_additional_box_max_row',
        'object_additional_box_min_col', 'object_additional_box_max_col', 'object_additional_ratio_extent',
        'object_additional_ratio_solidity', 'object_additional_inertia_tensor_eigenvalue1',
        'object_additional_inertia_tensor_eigenvalue2', 'object_additional_moments_hu1', 'object_additional_moments_hu2',
        'object_additional_moments_hu3', 'object_additional_moments_hu4', 'object_additional_moments_hu5',
        'object_additional_moments_hu6', 'object_additional_moments_hu7', 'object_additional_euler_number',
        'object_additional_eccentricity', 'object_additional_perimeter', 'object_additional_orientation', 
        'object_additional_area', 'object_additional_countcoords'
    ]

    # Use tqdm for progress bar
    for _, row in tqdm(data.iterrows(), total=len(data), desc="Processing images"):
        img_file = os.path.join(image_folder, str(row['object_id']))
        if os.path.exists(img_file):
            props = getMaxAreaDict(img_file)
        else:
            props = {key: None for key in all_keys}  # Assign None if file missing

        image_properties.append(props)

    # Convert to DataFrame and merge
    properties_df = pd.DataFrame(image_properties)
    data = pd.concat([data, properties_df], axis=1)

    return data

