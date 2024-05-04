import requests
import pandas as pd
import ast

BASE_URL = 'https://api.census.gov/data'
VALID_GEOGRAPHIES = ['us', 'state', 'county', 'tract']
STATE_FIPS = ['01', '02', '04', '05', '06', '08', '09', '10', '11', 
              '12', '13', '15', '16', '17', '18', '19', '20', '21', 
              '22', '23', '24', '25', '26', '27', '28', '29', '30', 
              '31', '32', '33', '34', '35', '36', '37', '38', '39', 
              '40', '41', '42', '44', '45', '46', '47', '48', '49', 
              '50', '51', '53', '54', '55', '56']
ACCEPTED_SURVEYS = ['acs5', 'acs1']


class CensusFriendo:
    '''
    Class that helps with Census data pulls.
    '''

    def __init__(self, API_KEY):
        '''
        make a census friendo +
        set your secret password (api key)
        '''
        self.API_KEY = API_KEY

    def __generate_geography(self, geography, state):
        '''
        Turn valid geographies into a portion of the link.
        
        Input: geography (str): one of tract, us, state, county, block
            or block group.

        Returns: list of strings for API request.
        '''
        assert geography.lower() in VALID_GEOGRAPHIES, 'Geography must be one of tract'
        assert (state != '' or geography.lower() != 'tract'), 'Must provide state if pulling tract level data.'
        assert (state == '' or state in STATE_FIPS), 'Must use one of 50 states.'

        rv = f'for={geography.lower()}:*'

        if state != '':
            rv = rv + f'&in=state:{state}'

        return rv

    def __api_return_to_df(self, api_return, name):
        '''
        Takes the returned value from an API call and turns it into a pandas
        dataframe.
        
        Inputs: 
            api_return (api return value)
            name (str): name of the table

        Returns: pandas dataframe
        '''
        lst = ast.literal_eval(api_return.text.strip())
        lst[0][0] = name

        df = pd.DataFrame(lst[1:], columns=lst[0])
        
        df['GEOID'] = df.get('us', '') + df.get('state', '')\
            + df.get('county', '') + df.get('tract', '')
        
        df = df.drop(['state'],  errors='ignore', axis=1)
        df = df.drop(['county'], errors='ignore', axis=1)
        df = df.drop(['tract'],  errors='ignore', axis=1)

        return df

    def __make_api_url(self, year, survey, table, geography, state):
        '''
        Given the year, survey, table, and geography,
        make a valid API request URL
        '''
        geography = self.__generate_geography(geography, state)

        return f'{BASE_URL}/{year}/acs/{survey}?get={table}&{geography}&key={self.API_KEY}'

    def __add_table_to_df(self, df, year, survey, table_tuple, geography, state):
        '''
        Given the request parameters, return an updated version of the DataFrame
        with the results of the given request.
        '''

        url = self.__make_api_url(year, survey, table_tuple[0], geography, state)
        response = requests.get(url)            
        
        if df is None: return self.__api_return_to_df(response, table_tuple[1])
        
        return pd.DataFrame.merge(df, self.__api_return_to_df(response, table_tuple[1]), on='GEOID', how='outer')
        
    def get_acs(self, tables, survey="acs5", year=2022, geography='county', state=''):
        '''
        Get ACS 5-Year estimates data using the Census API 
        
        Inputs:
          tables (str, list of str, or dict): Either a list of strings of table names to pull, 
            a string of a single table to pull, or a dictionary mapping table names to their 
            desired column name.
          year (int): year of estimate to pull (defaults to 2022)
          survey (str): Specific thing to pull. either "acs5" or "acs1", defaults
            to "acs-5"
          geography (str): geographic scale to grab values at (defaults to 'county')
          state (str): the state fips to pull sources from. defaults to '', only required
            if pulling tracts. 

        Returns: pandas DataFrame of the API
        '''

        # validate our inputs
        assert survey in ACCEPTED_SURVEYS, 'This function only supports 1- and 5-year estimates.'

        assert type(tables) in [list, str, dict]
        if type(tables) == list: tables = {table:table for table in tables}
        if type(tables) == str: tables = {tables:tables}

        # Pull all requested tables
        rdf = None
        for table_tuple in tables.items():
            rdf = self.__add_table_to_df(rdf, year, survey, table_tuple, geography, state)

        return rdf

    def get_accepted_surveys():
        '''
        Returns a list of accepted surveys.
        '''
        return ACCEPTED_SURVEYS
    
    def get_accepted_geographies():
        '''
        Returns a list of accepted geographies.
        '''
        return VALID_GEOGRAPHIES