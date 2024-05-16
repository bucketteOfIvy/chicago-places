### Author: Ashlynn Wimer
### Last Modified: 3/26/2024
### About: Helper class for interacting with Google Maps Streetview API.

from PIL import Image
from io import BytesIO
import numpy as np
import pandas as pd
import requests

class StreetviewFren:
    '''
    Helper class for interacting with Google Maps Streetview API.
    '''

    def __init__(self, API_KEY, locs=None, 
                 fov=90, pitch=0, 
                 radius=50, size = (600, 400), 
                 source='outdoor'):
        '''
        Define self and set initial parameters

        Arguments:
          API_KEY (str): Google Maps API_Key for this object 
          locs (list of strings or float tuples): from where to grab 
            streetview images; if None, set separately. Defaults to None.
          fov (int): field of view parameter. Minimum 0, 
            maximum 120. Defaults to 90.
          pitch (int): up-down angle of the camera relative the vehicle.
            Must be between -90 and 90 (straight down and straight up).
            Defaults to 0.
          radius (int): The radius around the requested location to search 
            for a viable panorama. Must be non-negative. Defaults to 50.
          size (int tuple): The resolution of the retrieved image in 
            width x height format. Maximum is 640x640. Defaults to (600, 400). 
          source (str): "default" if allowing indoor panoramas, "outdoor" for
            only outdoor panoramas. Defaults to "outdoor".        
        '''
        # Constants
        self.METADATA_URL = 'https://maps.googleapis.com/maps/api/streetview/metadata?'
        self.IMAGE_URL = 'https://maps.googleapis.com/maps/api/streetview?'
        self.API_KEY = API_KEY
        
        # Image info for requests
        self.locs = locs
        self.fov = fov
        self.pitch = pitch
        self.radius = radius
        self.size = size
        self.source = source

        
        self.rdf = None

    def get(self, minimize_spending=False):
        '''
        Use the pull parameters to acquire images and metadata, returning them
        as a dataframe.

        Inputs:
          minimize_spending (bool): If true, requests metadata first, and requests
            the actual images only for locations with extant metadata. Defaults False.
        
        Returns: pandas dataframe with images and metadata.
        '''

        metadata = self.__get_metadata()
        print(metadata)

        # attach new URLs to request from
        metadata['imageUrl'] = self.__generate_requests()

        # drop NAs, if requested
        if minimize_spending: metadata = metadata.dropna()

        images = self.__get_images(metadata['imageUrl'])
        print(images)

        rdf = metadata.merge(images, on='imageUrl')
        rdf = rdf.drop(['imageUrl', 'metadataUrl'], axis=1)
        self.rdf = rdf

        return rdf

    def save(self, file_loc, metadata_name='metadata', image_file_type='jpg'):
        '''
        Save the pulled images and metadata. Must be called after a get.

        Inputs:
          file_loc (str): the folder to store the metadata and images in.
          metadata_name (str): the name of the metadata file, not including file type.
          image_file_type (str): defaults to jpg, is not inferred.

        Returns: None
        '''
        assert not (self.rdf is None), 'There is nothing to save -- call get() first.'
        
        # Generate an ID
        self.rdf['id'] = np.arange(len(self.rdf)).astype(str)
        self.rdf['id'] = 'I' + self.rdf['id']

        # Save everything
        self.__save_images(file_loc, self.rdf['id'].values, self.rdf['image'].values)
        self.__save_metadata(file_loc, self.rdf.drop(['image'], axis=1), metadata_name)
            
    def __save_images(self, file_loc, ids, images, image_file_type='jpg'):
        '''
        Save image data
        '''
        for id, image in zip(ids, images):
            image.save(f'{file_loc}/{id}.{image_file_type}')

    def __save_metadata(self, file_loc, metadata, metadata_name):
        '''
        Save metadata
        '''
        metadata.to_csv(f'{file_loc}/{metadata_name}.csv')


    def __get_metadata(self):
        '''
        Use the parameters provided to the object to get metadata
        for all of the locations. 

        Inputs: None. 

        Returns: pandas DataFrame of containg location, date, panorama id, copyright, and status. 
        '''

        urls = self.__generate_requests(use_metadata_url=True)

        resp_df = pd.DataFrame({'metadataUrl':[], 'lat':[], 'long':[], 
                           'copyright':[], 'date':[], 'pano_id':[], 
                           'status':[]})
        for url in urls:
            resp = requests.get(url).json()

            # Add a new row -- if we get errors, there is no image there, so
            # just add NAs for later handling
            try:
                new_row = pd.DataFrame(
                            {'metadataUrl':[url],
                             'lat':[resp['location']['lat']], 'long':[resp['location']['lng']],
                             'copyright':[resp['copyright']], 'date':[resp['date']],
                             'pano_id':[resp['pano_id']], 'status':[resp['status']]}
                        )
            except KeyError:
                new_row = pd.DataFrame(
                    {'metadataUrl':[url], 'lat':[pd.NA], 'long':[pd.NA],
                     'copyright':[pd.NA], 'date':[pd.NA], 'pano_id':[pd.NA],
                     'status':[pd.NA]}
                )
            
            # Update our DataFrame
            resp_df = pd.concat([resp_df, new_row], ignore_index=True)

        return resp_df
    
    def __get_images(self, urls=None):
        '''
        Use the parameters provided to the object to get streetview images
        for all of the locations.

        Inputs: 
          urls (list of str): API Request URLs. If None, generates own URLs from
            info fed to object. Defaults to None.

        Returns: DataFrame associating images with URLs
        '''
        if urls is None:
            urls = self.__generate_requests(use_metadata_url=False)

        imgs = []
        for url in urls:
            resp = requests.get(url)
            print(resp.content)
            img = Image.open(BytesIO(resp.content))
            imgs.append(img)

        return pd.DataFrame({'imageUrl':urls, 'image':imgs})

    def __generate_requests(self, use_metadata_url=False):
        '''
        Generate list of requests

        Inputs:
          metadata (bool): True if this is a metadata pull, False otherwise

        Returns: List of URLS to request
        '''
        size_rq = f'size={self.size[0]}x{self.size[1]}'
        fov_rq = f'fov={self.fov}'
        pitch_rq = f'pitch={self.pitch}'
        radius_rq = f'radius={self.radius}'
        source_rq = f'source={self.source}'
        key_rq = f'key={self.API_KEY}'
        return_error_code_rq = f'return_error_code=true'        
        
        parameters = f'{size_rq}&{fov_rq}&{pitch_rq}&{radius_rq}&{source_rq}&{return_error_code_rq}&{key_rq}'
        if use_metadata_url:
            base_rq = f'{self.METADATA_URL}{parameters}'
        else:
            base_rq = f'{self.IMAGE_URL}{parameters}'
        
        rqs = []
        for loc in self.locs:
            # Generate the URL for our request
            rq = f'{base_rq}&location={loc}' if type(loc) == str else f'{base_rq}&location={loc[0]}, {loc[1]}'        
            rqs.append(rq)

        return rqs