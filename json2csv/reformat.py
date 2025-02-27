import flowcytometer
import flowcytometerOutput
import os
import pathlib
import json

#### CUSTOM ROUTINE #####
pathdir = pathlib.Path(r"\\qarchive\data_simonstevin\cyto\ANERIS\LW\04_2023") # be carefull if you have raw .cyz files in your directory you need to skip these!
plist = os.listdir(pathdir)
plist.remove('raw')

for basename in plist:
    if basename.endswith('.cyz') or basename.endswith('.json_images') or basename.endswith('.csv'):
        continue
    fcdir_path = os.path.join(pathdir, basename)
    fcout = flowcytometerOutput.FlowcytometerOutput(path=fcdir_path, csv_check=True) #step 1
    fcout.add_manual_metadata_VLIZ()#step 2
    fcout.add_data_MIDAS() #step 3
    #fcout.add_any_metadata() #step 4


flowcytometer.concat_csv(pathdir)