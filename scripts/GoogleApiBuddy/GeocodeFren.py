### Author: Ashlynn Wimer
### Date: 3/18/2024
### About: Helper class for interacting with Geocoder parts of the Google Maps
###        API. 
import pandas as pd
import requests

class GeocodeFren:
    '''
    Helper class for interacting with Google Maps geocoding API.
    '''

    def __init__(self, API_KEY):
        '''
        Args: API_KEY (str): Your Google API_KEY. (Be sure to store it
          somewhere safe!)
        '''
        self.API_KEY = API_KEY

    def geocode_point(self, address='', city='', state=''):
        '''
        Given the address, city, and state of a hospital,
        attempt to geocode it.

        Inputs:
          address (str): the street address of the location; opt, default ''
          city (str): the city of the location; opt, default ''
          state (str): the state of the location; opt, default ''
        
        Returns (int tuple): a latitude, longitude pair on WGS84
          pointing to the location described in the address. Defaults
          to city location if full address does not work.
        '''
        url = 'https://maps.googleapis.com/maps/api/geocode/json'

        params = {'sensor':'false',
                  'address':f'{address} {city} {state}',
                  'key':self.API_KEY}
        req = requests.get(url, params=params)
        try:
            location = req.json()['results'][0]['geometry']['location']
            lat, long = location['lat'], location['lng']
        except IndexError:
            if address == '':
                print(f"Failed to geocode {city} {state}, returning (-999), (-999)")
                return (-999, -999)

            print(f"Initial req didn't take for {address} {city} {state}, trying {city} {state} only")
            return self.geocode_point(city=city, state=state)
        
        return (lat, long)
    
    def geocode_addresses(self, addresses, ids=None):
        '''
        Given a list of (address, city, state) tuples,
        return a list of of (lat, long) tuples.

        Inputs:
          addresses (list of str tuples, or dataframe): If list of str tuples,
            then a list of (address, city, state) tuples address, city, or state 
            can be be excluded by passing ''. 
            If a DataFrame, then a DataFrame with an "address", "city", and "state"
            column.
          ids (optional): Either list of id variables that will be returned as 
            part of the tuples, or string name of the ID variable column
            If list, must be same length as the addresses list.
            If no id is supplied, uses concat'd addresses as id
        
        Returns: Pandas DataFrame containing ID, Lat, Long
        '''

        # Assertions to prevent misuse -- no one wants to waste their API funds!
        assert (not ids) or (type(ids) == str) or (len(ids) == len(addresses)), 'ids list must be same length as addresses'
#        assert type(addresses) == list or type(addresses) == pd.DataFrame, 'Addresses must be a list of string tuples or a DataFrame'
        if type(addresses) == pd.DataFrame:
            assert 'Address' in addresses.columns, "DataFrame must have 'address' column"
            assert 'State' in addresses.columns, "DataFrame must have 'state' column"
            assert 'City' in addresses.columns, "DataFrame must have 'city' column"
        
        if type(ids) == str:
            ids = addresses[ids]

        if type(addresses) == pd.DataFrame:
            addresses = [(address[1], address[2], address[3]) for address in addresses[['Address', 'City', 'State']].itertuples()]

        if ids is None:
            ids = [' '.join(address) for address in addresses]

        coordinates = {'id':[], 'lat':[], 'long':[]}
        for id_, (address, city, state) in zip(ids, addresses):
            lat, long = self.geocode_point(address, city, state)
            coordinates['lat'].append(lat)
            coordinates['long'].append(long)
            coordinates['id'].append(id_)

        return pd.DataFrame(coordinates)
    