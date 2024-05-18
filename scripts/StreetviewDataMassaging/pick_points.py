### Author: Ashlynn Wimer
### Last Modified: 5/16/2024
### About: Multithreaded approach which grabs the initial points for my Streetview 
###        data pulls.

from shapely import (
    MultiLineString, 
    get_coordinates
)

from concurrent.futures import ThreadPoolExecutor
import geopandas as gpd
import pandas as pd
import numpy as np

STREETS = gpd.read_file('../../data/shapes/center_line/trans.shp')\
    .geometry\
    .make_valid()\
    .to_crs('EPSG:4326')
STREETS = STREETS[~(STREETS.is_empty | STREETS.isna())]

N_POINTS = 25000

def grab_thousand_points(lst: list, streets: gpd.GeoDataFrame=STREETS) -> None:
    '''
    Grab 1000 random points on the Chicago street network and append them to a list
    of points in-place.
    '''
    rdm = np.random.default_rng()
    loc_vals = [rdm.random() for _ in range(1000)]
    streets = MultiLineString(streets.values)

    pnts = streets.line_interpolate_point(loc_vals, normalized=True)
    
    # Append our points to the list
    lst.append(pnts)

if __name__ == '__main__':

    print(f'Grabbing {(N_POINTS // 1000) * 1000} points...')

    pnts = []

    with ThreadPoolExecutor(max_workers=7) as executor:
        for i in range(N_POINTS // 1000):
            executor.submit(grab_thousand_points, pnts)

    print('Points grabbed! Cleaning and assembling..')

    coords = pd.DataFrame(get_coordinates(pnts), columns=['longitude', 'latitude'])
    coords['ID'] = 'I' + coords.index.astype(str)

    print(f'Saving {len(coords)} points to csv..')

    coords.to_csv('../../data/shapes/streetview_locations_initial.csv', index=False)