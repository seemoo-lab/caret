from constants import *
import geopandas as gpd
import os.path

def read_or_create(path, generate_df, logger):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if(os.path.isfile(path)):
        logger.debug(f'reading existing {path} ...')
        return read(path, logger)
    
    logger.debug(f'creating {path}')
    gdf = generate_df()
    if not gdf is None:
        gdf.to_file(path, driver='GeoJSON')
    return gdf

def read(path, logger):
    logger.debug(f'reading {path}')
    return gpd.read_file(path)