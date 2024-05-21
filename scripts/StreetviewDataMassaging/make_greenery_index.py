### Author: Ashlynn Wimer
### Date: 5/21/2024
### About: This script creates a greenery index for Chicago streets, and saves
###        based on the segmented streetview imagery.

import pandas as pd
import numpy as np

REL_SEGMENTS = ['tree', 'grass', 'field', 'flower', 'hill']

if __name__ == "__main__":
    segments = pd.read_parquet('../../data/raw/streetview_segments.parquet')\
                [REL_SEGMENTS]\
                .reset_index()

    # Strip '.png' from images
    segments['image_id'] = segments['index'].apply(lambda x: x[:-4])

    # generate absolute and relative greenery
    segments['absolute_greenery'] = np.sum(segments[REL_SEGMENTS], axis=1)
    segments['relative_greenery'] = ((segments['absolute_greenery'] - segments['absolute_greenery'].min())/(segments['absolute_greenery'].max() - segments['absolute_greenery'].min()))

    segments['relative_tree'] = (segments['tree'] - segments['tree'].min()) / (segments['tree'].max() - segments['tree'].min())

    # keep just relevant columns
    segments = segments[['image_id', 'absolute_greenery', 'relative_greenery', 'relative_tree']]

    # attach metadata
    metadata = pd.read_csv('../../data/shapes/streetview_metadata_and_locs.csv')

    merged = metadata\
        .merge(segments, how='inner', left_on='ID', right_on='image_id')\
        .drop('image_id', axis=1)

    # To ensure merge was clean enough
    print(f'Merged has shape {merged.shape}, segments has shape {segments.shape}, metadata has shape {metadata.shape}.')

    merged.to_csv('../../data/streetview_greenery.csv', index=False)

