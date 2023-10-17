from constants import *
from rw import csv, geojson

import geopandas as gpd
import geojson as gj
import math
import pandas as pd

def map(city, tiles, stations, logger):
    """Map each tile to the closest base station and write the mapping to file.
    
    Adds a column 'station_id' for the closest station to the tiles dataframe.
    Adds a column 'coverage_area' to stations representing the coveraed area.
    
    Args:
        city (_str_): the city
        tiles (_geopandas.GeoDataFrame_): tiles geo data frame
        stations (_geopandas.GeoDataFrame_): base stations geo data frame
    
    Returns:
        _(List(geopandas.GeoDataFrame, geopandas.GeoDataFramem, geopandas.GeoDataFrame))_: a set (tiles, stations, coverage) with added columns for the mappings
    """
    
    def generate_df():
        """Maps each tile (provided by netmob) to the closest base station (provided by cartoradio).

        Returns:
            _pandas.DataFrame_: a data frame with two columns mapping each tile to the closest base station
        """
        
        # (1) get the GeoSeries of all base stations and align the crs
        # s = stations['geometry'].to_crs(tiles['geometry'].crs)
        
        if stations.crs == None:
            stations.crs = 4326
        
        stations_metric = stations.to_crs(32643) 
        tiles_metric = tiles.to_crs(32643)
        
        # (2) prepare the map with one colum for all tile ids
        ts = pd.DataFrame(tiles_metric.index, columns=['tile_id'])
        
        # (3) for each tile, find the closest station in terms of geopandas.GeoSeries.distance
        ts['station_id'] = ts['tile_id'].apply(lambda t: stations_metric['geometry'].distance(tiles_metric.at[t, 'geometry']).idxmin())
        
        return ts
    
    ts = csv.read_or_create(f'{BASE_DIR}/out/station/{city}-tilestation.csv', generate_df, logger)
    
    tiles['station_id'] = ts['station_id']
    stations['coverage'] = stations['station_id'].apply(lambda s: tiles[tiles['station_id'] == s]['geometry'].unary_union)
    
    def gen_df():
        features = [
            gj.Feature(
                geometry=stations.at[station, 'coverage'],
                properties={
                    'station': station
                    }
                )
            for station in stations.index
        ]
                
        # (x) create link geo data frame with geometry column
        coverage = gpd.GeoDataFrame.from_features(features)
        
        return coverage

    coverage = geojson.read_or_create(f'{BASE_DIR}/out/station/{city}-coverage.geojson', gen_df, logger)
    
    return (tiles, stations, coverage)
