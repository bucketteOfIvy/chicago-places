### Author: Ashlynn Wimer
### Date: 5/2/2024
### About: Script used to acquire and clean 2023 311 data.

from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import geopandas as gpd
import json
import pygris

URL = "https://data.cityofchicago.org/resource/v6vf-nfxy.csv?$query=SELECT%0A%20%20%60sr_number%60%2C%0A%20%20%60sr_type%60%2C%0A%20%20%60sr_short_code%60%2C%0A%20%20%60created_date%60%2C%0A%20%20%60duplicate%60%2C%0A%20%20%60community_area%60%2C%0A%20%20%60latitude%60%2C%0A%20%20%60longitude%60%0AWHERE%0A%20%20%60created_date%60%0A%20%20%20%20BETWEEN%20%222023-01-01T00%3A00%3A00%22%20%3A%3A%20floating_timestamp%0A%20%20%20%20AND%20%222023-12-31T23%3A59%3A59%22%20%3A%3A%20floating_timestamp%0AORDER%20BY%20%60sr_number%60%20DESC%20NULL%20FIRST"
pds = []

def grab_thousand_311s(offset=0, URL=URL):
    '''
    Grab 1000 rows of 311 requests from the Chicago API and attach
    it to a global (or inputted!) list.
    '''
    data = pd.read_csv(URL+f'%20OFFSET%20{offset*1000}')
    pds.append(data)

print('Grabbing the 311 data from Chicago Data Portal. This may take ~20 minutes')
with ThreadPoolExecutor(max_workers=7) as executor:
    executor.map(grab_thousand_311s, range(1, 1800))

print('311 acquired! Cleaning..')
df = pd.concat(pds, ignore_index=True).drop_duplicates('sr_number')
df = df[df['duplicate'] != True]
df = df[df['sr_short_code'] != '311IOC']

print('Basic cleaning done, attaching classifications.')

with open('../../data/raw/311classification.json') as f:
    request_classes = json.loads(f.read())

df['disorder_class'] = df['sr_short_code'].apply(lambda x: request_classes.get(x, 'MISSING'))
df = df[df['disorder_class'] != 'MISSING']

print('Classes attached and missing dropped!')
print('Reading in spatial data to work with..')

# Get tracts
tracts = pygris.tracts(state='IL', county='Cook', cb=True, year=2023)
gdf = gpd.GeoDataFrame(df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs='EPSG:4326')

print("Spatial data read in! Processing..")

tracts.to_crs('EPSG:26916', inplace=True)
gdf.to_crs('EPSG:26916', inplace=True)

gdf = gdf.sjoin(
    tracts[['GEOID', 'geometry']],
    predicate='intersects'
).drop(['index_right', 'duplicate', 'geometry'], axis=1)

print('Saving!')
gdf.to_csv('../../data/311reqs.csv')

