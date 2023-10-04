from constants import *
from rw import geojson
import geojson as gj
import geopandas as gpd
import logging
import pandas as pd
import shapely

def get_bounds(city, logger):
    """Read or create the bounds of a city.

    Args:
        city (_str_): the city to get the bounds for
        
    Returns:
        _geojson.GeoDataFrame_: city bounds
    """
    
    def generate_df():
        """Get the tiles provided by netmob, compute city bounds, and convert to geo data frame.

        Returns:
            _geojson.GeoDataFrame_: city bounds
        """
        
        # (1) get all tiles from the netmob geojson
        tiles = get_tiles(city, logger)
        
        # (2) compute city bounds
        city_bounds = tiles['geometry'].unary_union
        
        # (3) create geojson feature list
        city_feature = gj.Feature(geometry=city_bounds, properties={'city': city})
        
        # (4) convert to geo data frame
        city_gdf = gpd.GeoDataFrame.from_features([city_feature], crs=tiles.crs)
        
        return city_gdf
    
    return geojson.read_or_create(f'{BASE_DIR}/data/spatial/{city}-bounds.geojson', generate_df, logger)
    
def get_tiles(city, logger):
    """Read the city's tiles provided by netmob.

    Args:
        city (_str_): the city

    Returns:
        _geopandas.GeoDataFrame_: the city's tiles in a geo data frame.
    """
    
    def generate_df():
        return geojson.read(f'{BASE_DIR}/data/spatial/{city}.geojson', logger)
    
    return geojson.read_or_create(f'{BASE_DIR}/out/spatial/{city}.geojson', generate_df, logger)