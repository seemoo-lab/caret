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

# class TileStationMapper:
#     def __init__(self, city) -> None:
#         self.city = city
#         self.tile_id_to_row_id = TILE_ID_TO_ROW_ID(city)
#         self.tile_id_to_col_id = TILE_ID_TO_COL_ID(city)
#         self.OUTPUT_FILE = f'{BASE_DIR}/data/processed/station/{city}-map.csv'
#         # self.csv_handler = CSVHandler()
#         self.spatial_handler = Spatial(city)
    
#     def map_tiles_to_stations(self, spatial, stations):
#         raise NotImplementedError('OLD')
#         def gen_tile_station_df():
#             # winners_in_doubt = dict.fromkeys(stations['station_id'], 0)
#             df = pd.DataFrame(spatial['tile_id'])
#             df['station_id'] = spatial['tile_id'].apply(lambda t: self.get_closest_station(t, spatial, stations))
#             df.to_csv(self.OUTPUT_FILE, index=False)
#             return df
    
#         res = self.csv_handler.read_or_create_csv(self.OUTPUT_FILE, gen_tile_station_df)
#         return res
    
#     def get_closest_station(self, tile_id, spatial, stations):
#         raise NotImplementedError('OLD')
#         def get_closest_stations(station_ids, tile_station_distance):
#             distances = station_ids.apply(tile_station_distance)
#             return distances.index[distances == distances.min()].dropna()
        
#         # tile to coords mappers
#         tile_id_to_tile_coords = lambda tile_id: (self.tile_id_to_row_id(tile_id), self.tile_id_to_col_id(tile_id))
#         tile_id_to_wgs_coords = lambda tile_id: self.spatial_handler.tile_id_to_wgs(spatial, tile_id) #gpd.GeoSeries([spatial[spatial['tile_id'] == tile_id]['geometry']])

#         # station to coords mappers
#         station_id_to_tile_coords = lambda station_id: (stations.loc[station_id]['row_id'], stations.loc[station_id]['col_id'])
#         station_id_to_wgs_coords = lambda station_id: gpd.GeoSeries([stations.at[station_id, 'geometry']]) #shapely.wkt.loads(stations.at[station_id, 'geometry']) 

#         # distance mappers
#         tile_distance = lambda station_id: math.dist(tile_id_to_tile_coords(tile_id), station_id_to_tile_coords(station_id))
#         def wgs_distance(station_id):
#             station = station_id_to_wgs_coords(station_id)
#             tile = tile_id_to_wgs_coords(tile_id)
            
#             return math.dist((tile.x,tile.y), (station.x,station.y))

#         closest_stations_by_tile = get_closest_stations(stations['station_id'], tile_distance)
#         if(len(closest_stations_by_tile) == 1):
#             return closest_stations_by_tile[0]

#         closest_stations_by_wgs = get_closest_stations(stations.loc[closest_stations_by_tile]['station_id'], wgs_distance)
#         if(len(closest_stations_by_wgs) == 1):
#             return closest_stations_by_wgs[0]
        
#         print(f'MOVE APART STATIONS WITH COORDS {station_id_to_wgs_coords(list(closest_stations_by_wgs)[0])}')
#         return closest_stations_by_wgs[0]
    
#     def map_to_station(self, tile, tilestation):
#         raise NotImplementedError('OLD')
#         return tilestation[tilestation['tile_id'] == tile]['station_id'].to_numpy()[0]
    
#     def group_by_station(self, traffic, tilestation, city, app, date, link):
#         raise NotImplementedError('OLD')
#         def generate_df():
#             traffic['station_id'] = tilestation['station_id']
#             station_count = max(tilestation['station_id'])
#             df = traffic.drop('tile_id', axis=1).groupby('station_id', dropna=False).sum()
            
#             for i in [i for i in range(station_count) if i not in df.index]:
#                 df_fill = df.loc[0].apply(lambda x: 0).rename(i)
#                 df = pd.concat([df,df_fill.to_frame().T])
            
#             return df.sort_index()
        
#         return self.csv_handler.read_or_create_csv(f'{BASE_DIR}/data/processed/traffic/by_station/{city}-{app}-{date}-{link}.csv', generate_df)