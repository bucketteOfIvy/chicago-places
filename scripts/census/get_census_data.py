### Author: Ashlynn Wimer
### Date: 5/5/2024
### About: This script pulls Census data for Cook County,
###        used in the opioid risk environment project.
import CensusFriendo
import geopandas as gpd
import pandas as pd
import numpy as np
import pygris
import os


tables = {
"B06009_001E":"TotalEducation",
"B06009_002E":"LessThanHighSchoolGrad",
"B06009_003E":"HighSchoolGrad",
"B02001_001E":"TotalRace",
"B02001_002E":"White",
"B02001_003E":"Black",
"B02001_005E":"Asian",
"B03002_012E":"Hispanic",
"B01001_007E":"M18and19",
"B01001_008E":"M20",
"B01001_009E":"M21",
"B01001_010E":"M22to24",
"B01001_031E":"F18and19",
"B01001_032E":"F20",
"B01001_033E":"F21",
"B01001_034E":"F22to24",
"B01001_020E":"M65and66",
"B01001_021E":"M67to69",
"B01001_022E":"M70to74",
"B01001_023E":"M75to79",
"B01001_024E":"M80to84",
"B01001_025E":"M85plus",
"B01001_044E":"F65and66",
"B01001_045E":"F67to69",
"B01001_046E":"F70to74",
"B01001_047E":"F75to79",
"B01001_048E":"F80to84",
"B01001_049E":"F85plus",
"B01001_001E":"TotalPopulation",
"B21004_001E":"MedInc",
"B17010_001E":"PovUni",
"B17010_002E":"PovCount",
"B23025_002E":"LaborForce",
"B23025_005E":"Unemployed",
"B08126_001E":"HighRiskUniverse",
"B08126_002E":"AgrForFishMining",
"B08126_003E":"Construction",
"B08126_004E":"Manufacturing",
"B08126_007E":"TransWareUtilities",
"B28002_001E":"InternetUniverse",
"B28002_013E":"NoInternetAccess"
}

cf = CensusFriendo.CensusFriendo(API_KEY=os.environ['CENSUS_API_KEY'])

df = cf.get_acs(tables, survey='acs5', year=2022, geography='tract', state='17')

df = df.astype(np.float64)

# What percent of the population has *at most* a high school degree?
df['MHSdP']  = 100 * (df['HighSchoolGrad'] + df['LessThanHighSchoolGrad']) / df['TotalEducation']

# Race breakdowns
df['WhiteP'] = 100 * df['White'] / df['TotalRace']
df['BlackP'] = 100 * df['Black'] / df['TotalRace']
df['AsianP'] = 100 * df['Asian'] / df['TotalRace']
df['HispP']  = 100 * df['Hispanic'] / df['TotalRace']

# Age breakdowns
df['18to24P'] = 100 * (df['M18and19'] + df['M20'] + df['M21'] + df['M22to24'] + df['F18and19'] + df['F20'] + df['F21'] + df['F22to24']) / df['TotalPopulation']

df['Ovr65P'] = 100 * (df['M65and66'] + df['M67to69'] + df['M70to74'] + df['M75to79'] + df['M80to84'] + df['M85plus'] + df['F65and66'] + df['F67to69'] + df['F70to74'] + df['F75to79'] + df['F80to84'] + df['F85plus']) / df['TotalPopulation']

# High risk jobs
df['HighRiskJobP'] = 100 * (df['AgrForFishMining'] + df['Construction'] + df['Manufacturing'] + df['TransWareUtilities']) / df['HighRiskUniverse']

# Unemployment
df['Unemployment'] = 100 * df['Unemployed'] / df['LaborForce']

# Poverty
df['PovP']= 100 * df['PovCount'] / df['PovUni']

# No internet
df['NoIntP'] = 100 * df['NoInternetAccess'] / df['InternetUniverse']

df = df[['GEOID', 'TotalPopulation', 'WhiteP', 'BlackP', 'AsianP', 'HispP', '18to24P', 'Ovr65P', 'MHSdP', 'MedInc', 'HighRiskJobP', 'Unemployment', 'PovP', 'NoIntP']]

# Subset spatially
tracts = pygris.tracts(cb=True, county='cook', state='il')[['GEOID', 'geometry']].to_crs("EPSG:26916")
chicago_boundaries = gpd.read_file('../../data/shapes/chicago_boundaries.geojson').to_crs('EPSG:26916')
relevant_geoids = gpd\
    .sjoin( 
        chicago_boundaries.to_crs('EPSG:26916'),
        gpd.GeoDataFrame(
            tracts.drop('geometry', axis=1), 
            geometry=tracts.centroid, 
            crs='EPSG:26916'
        ),
        predicate='contains'
        )['GEOID']

df['GEOID'] = df.GEOID.astype(str).apply(lambda x: x.split('.')[0])

df = df[df['GEOID'].isin(relevant_geoids)]

print(df.shape)

df.to_csv('../../data/censusdata.csv', index=False)
