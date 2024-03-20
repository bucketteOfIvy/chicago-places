### Author: Ashlynn Wimer
### Date: 3/18/2024
### About: Helper class for interacting with Geocoder parts of the Google Maps
###        API. 
import pandas as pd
import requests

class StreetviewFren:
    '''
    Helper class for interacting with Google Maps Streetview API.
    '''

    def __init__(self, API_KEY):
        self.API_KEY = API_KEY


    def get_metadata(lat, long):
        