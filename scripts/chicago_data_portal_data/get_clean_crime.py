### Author: Ashlynn Wimer
### Date: 5/4/2024
### About: Script used to grab and clean 2023 CPD data.

from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import geopandas as gpd
import pygris

URL = 'https://data.cityofchicago.org/resource/ijzp-q8t2.csv?$query=SELECT%0A%20%20%60id%60%2C%0A%20%20%60case_number%60%2C%0A%20%20%60date%60%2C%0A%20%20%60iucr%60%2C%0A%20%20%60primary_type%60%2C%0A%20%20%60description%60%2C%0A%20%20%60location_description%60%2C%0A%20%20%60arrest%60%2C%0A%20%20%60domestic%60%2C%0A%20%20%60beat%60%2C%0A%20%20%60district%60%2C%0A%20%20%60ward%60%2C%0A%20%20%60community_area%60%2C%0A%20%20%60fbi_code%60%2C%0A%20%20%60year%60%2C%0A%20%20%60latitude%60%2C%0A%20%20%60longitude%60%0AWHERE%20%60year%60%20IN%20(%222023%22)%0AORDER%20BY%20%60date%60%20DESC%20NULL%20FIRST'

VIOLENT_CRIMES = [
    'BATTERY', 'HOMICIDE', 'ASSAULT', 'ROBBERY', 
    'CRIMINAL SEXUAL ASSAULT', 'SEX OFFENSE', 'KIDNAPPING', 
    'HUMAN TRAFFICKING'
]

NARCOTICS = ['NARCOTICS', 'OTHER NARCOTIC VIOLATION']

def grab_thousand_crimes(lst, offset=0, URL=URL):
    '''
    Grab 1000 rows of crimes requests from the Chicago
    '''
    lst.append(pd.read_csv(URL+f'%20OFFSET%20{offset*1000}'))

if __name__ == "__main__":

    print('Grabbing crime data...')

    pds = []
    
    # we expect ~260,000 entries, so we offset higher for safety
    with ThreadPoolExecutor(max_workers=7) as executor:
        for i in range(270):
            executor.submit(grab_thousand_crimes, pds, i)
    
    df = pd.concat(pds, ignore_index=True).drop_duplicates()

    print('Grabbed! Attaching to tracts..')
    tracts = pygris.tracts(state='IL', county='Cook', cb=True, year=2023)
    gdf = gpd.GeoDataFrame(df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs='EPSG:4326')
    
    tracts.to_crs('EPSG:26916', inplace=True)
    gdf.to_crs('EPSG:26916', inplace=True)

    gdf = gdf.sjoin(
        tracts[['GEOID', 'geometry']],
        predicate='intersects'
    ).drop(['index_right', 'geometry'], axis=1)

    print('Attached! Splitting into violent and narcotic dataset..')

    violent_df = gdf[gdf['primary_type'].isin(VIOLENT_CRIMES)]
    narcotic_df = gdf[gdf['primary_type'].isin(NARCOTICS)]

    print('Saving...')
    violent_df.to_csv('../../data/violent_crime2023.csv')
    narcotic_df.to_csv('../../data/narcotic_crime2023.csv')