# Script inside this repository

| Script | python | 
| ------ | ------ |
| conversion_json | python script to convert .cyz files in bulk | 
| extraction_image | python script that extract the images from the json files | 
| automated_directories | python script that automatically update the config file with new directory in case of bulk process |

## conversion_json 

Python script calling for the .NET program to convert the .cyz file into json file

### extraction_image

Python script to extract images (cropped and not cropped) from the json files. The images will be extracted and put in a subdirectory having the same name as the file. 

### automated_directories

Script to use if several directories need to be processed.  

## Additional information

A config file is also present and is required to run the scripts above. In the settings file, you must provide the directory containing the cyz file and the path to the cyz2json program. 


