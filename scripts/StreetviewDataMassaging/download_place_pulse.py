### Author: Ashlynn Wimer
### Date: 5/19/2024
### About: This script retrieves the place-pulse-2.0.zip file currently stored
###        in a UChicago Box.

import requests
import sys

if __name__ == "__main__":
    with requests.get(sys.argv[1], stream=True) as r:
        r.raise_for_status()
        with open('../../data/place-pulse-2.0.zip', 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)