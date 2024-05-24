### Author: Ashlynn Wimer
### Date: 5/19/2024
### About: This script extracts the relevant attribute data from the 
###        place-pulse-2.0 zipfile.

import zipfile
import shutil

FILES = ['qscores.tsv', 'locations.tsv', 'places.tsv', 'votes.tsv', 'studies.tsv']

with zipfile.ZipFile('../../../data/place-pulse-2.0.zip') as place_pulse:
    for f in FILES:
        with place_pulse.open(f) as original_file, open(f"../../../data/raw/{f}", 'wb') as output_file:
            shutil.copyfileobj(original_file, output_file)