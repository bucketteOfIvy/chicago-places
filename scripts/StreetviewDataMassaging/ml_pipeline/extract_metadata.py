### Author: Ashlynn Wimer
### Date: 5/19/2024
### About: This script extracts the relevant attribute data from the 
###        place-pulse-2.0 zipfile.

import pandas as pd
import zipfile
import shutil
import re

FILES = ['qscores.tsv', 'locations.tsv', 'places.tsv', 'votes.tsv', 'studies.tsv']

# Extract files
with zipfile.ZipFile('../../../data/place-pulse-2.0.zip') as place_pulse:
    for f in FILES:
        with place_pulse.open(f) as original_file, open(f"../../../data/raw/{f}", 'wb') as output_file:
            shutil.copyfileobj(original_file, output_file)

# Do a spot of cleaning
for file in FILES:
    data = pd.read_csv(f'../../../data/raw/{file}', sep='\t')
    rename_dict = {
        column_name:re.sub(r'\.', '_', column_name) for column_name in data.columns
    }
    print(rename_dict)
    data.rename(rename_dict, axis=1).to_csv(f'../../../data/raw/{file}', sep='\t')