# create_tsv_file_metrics.py

## Overview
The [`create_tsv_file_metrics.py`](create_tsv_file_metrics.py) script automates the extraction, processing, and export of flow cytometry image data for integration into the Ecotaxa platform. The script works by first reading image files and extracting object properties, then processes associated metadata files to ensure consistency across datasets. Image properties are systematically added to the dataset, linking object IDs to extracted features.

## Functionality  
1. **Finding Created CSV Files**: The script first locates the CSV files that were generated based on the `cyz.json` file names.  
2. **Renaming Based on Aneris Key**: It then renames columns using the reference key ([`Aneris_key.xlsx`](Aneris_key.xlsx)) to ensure consistency across datasets.  
3. **Calculating Metrics**: Various metrics are calculated, including particle-based measurements.  
4. **Adding Metrics to Dataset**: The computed metrics are integrated into the dataset, linking object IDs to their extracted features.  
5. **Saving and Zipping Data**: The final dataset, now enriched with metadata and image analysis results, is saved as a TSV file. The images are then bundled together with the TSV file into a ZIP archive for streamlined export to the Ecotaxa platform.  


## Extra Metrics  
For the additional metrics, parameters are used with the term `_additional_` inside the name. These metrics are inspired by methodologies from the National Data Science Bowl (Aurelia, Jessica Luo, Josette BoozAllen, Josh Sullivan, Steve Mills, and Will Cukierski, 2014). The competition, hosted on Kaggle, focused on leveraging machine learning for plankton image classification. More details can be found at: https://kaggle.com/competitions/datasciencebowl.  

The table below describes these metrics:  


| Key Name | Description |
| --- | --- |
| `object_additional_centroid_row` | Row coordinate of the object centroid. |
| `object_additional_centroid_col` | Column coordinate of the object centroid. |
| `object_additional_diameter_equivalent` | Equivalent diameter of the object. |
| `object_additional_length_minor_axis` | Length of the object's minor axis. |
| `object_additional_length_major_axis` | Length of the object's major axis. |
| `object_additional_area_convex` | Area of the convex hull of the object. |
| `object_additional_area_filled` | Area of the filled object. |
| `object_additional_box_min_row` | Minimum row of the bounding box of the object. |
| `object_additional_box_max_row` | Maximum row of the bounding box of the object. |
| `object_additional_box_min_col` | Minimum column of the bounding box of the object. |
| `object_additional_box_max_col` | Maximum column of the bounding box of the object. |
| `object_additional_ratio_extent` | Ratio of the object's extent. |
| `object_additional_ratio_solidity` | Ratio of the object's solidity (filled area / convex area). |
| `object_additional_inertia_tensor_eigenvalue1` | First eigenvalue of the object's inertia tensor. |
| `object_additional_inertia_tensor_eigenvalue2` | Second eigenvalue of the object's inertia tensor. |
| `object_additional_moments_hu1` | First Hu moment of the object (shape descriptor). |
| `object_additional_moments_hu2` | Second Hu moment of the object (shape descriptor). |
| `object_additional_moments_hu3` | Third Hu moment of the object (shape descriptor). |
| `object_additional_moments_hu4` | Fourth Hu moment of the object (shape descriptor). |
| `object_additional_moments_hu5` | Fifth Hu moment of the object (shape descriptor). |
| `object_additional_moments_hu6` | Sixth Hu moment of the object (shape descriptor). |
| `object_additional_moments_hu7` | Seventh Hu moment of the object (shape descriptor). |
| `object_additional_euler_number` | Euler number, a topological feature of the object. |
| `object_additional_eccentricity` | Count of coordinates (or pixels) associated with the object. |

## Final Output
The final output consists of:
1. **TSV File**: A TSV file with the enriched metadata and image analysis results.
2. **ZIP Archive**: A ZIP file containing the TSV file and corresponding images for streamlined export to the Ecotaxa platform.

## Conclusion
This script simplifies the process of collecting, processing, and exporting image data for further analysis and integration into the Ecotaxa platform, with a clear structure to ensure compatibility and consistency of the data.
