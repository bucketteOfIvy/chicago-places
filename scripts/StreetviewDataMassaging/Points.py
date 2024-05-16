### Author: Ashlynn Wimer
### Last Modified: 3/27/2024
### About: This script was made out of spite. In short, I need to select
###        25,000 points randomly on Chicago's street network. That seemed easy,
###        but I've discovered that doing it with GeoPandas is.. very slow.
###        Thus, this script, which should be able to accomplish that job with
###        MUCH less suffering.

from numba import jit
import numpy as np
import geopandas as gpd
import pandas as pd # maybe unneeded?

from shapely.geometry import MultiPoint
from geopandas.array import from_shapely, points_from_xy

def uniform(geom, size, rng=None):
    generator = np.random.default_rng(seed=rng)

    # only accepting linestrings
    fracs = generator.uniform(size=size)
    