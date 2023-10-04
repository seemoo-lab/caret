from constants import *
from enum import Enum
from rw import csv, geojson
from caret import spatial
from util import transformator

import geojson as gj
import geopandas as gpd
import pandas as pd

class StationStrategy(Enum):
    HIGH_TRAFFIC_10 = 10
    HIGH_TRAFFIC_20 = 20
    HIGH_TRAFFIC_30 = 30
    HIGH_TRAFFIC_40 = 40
    HIGH_TRAFFIC_50 = 50
    HIGH_TRAFFIC_60 = 60
    HIGH_TRAFFIC_70 = 70
    HIGH_TRAFFIC_80 = 80
    HIGH_TRAFFIC_90 = 90
    ALL = 100

def get(city, logger):
    """Read or create the stations (geo) data frame for a city.

    Args:
        city (_str_): the city to get the stations data frame for

    Returns:
        _geopandas.GeoDataFrame_: the city's stations (geo) data frame
    """
    
    def generate_df():
        """Reads station coords + info from cartoradio, convert to geojson, remove stations outside the city.

        Returns:
            geopandas.GeoDataFrame: station dataframe with primary key `station_id`, foreign key 'tile_id', geometry + additional station info
        """
        
        # (1) read cartoradio anntena + site csv's, join them on `support_number` and extract station info
        antennas = get_antennas(city, logger)
        support_numbers = antennas.index.to_numpy()
        sites = get_sites(city, support_numbers, logger)
        station_info = sites.join(antennas, on='support_number', how='left').reset_index()

        # (2) create a geojson feature list from the stations' coords
        features = [
            gj.Feature(
                geometry=gj.Point((station_info.loc[sn]['longitude'], station_info.loc[sn]['latitude'])),
                properties=station_info.loc[sn].to_dict())
            for sn in station_info.index
        ]

        # (3) create the (geo) dataframe
        stations = gpd.GeoDataFrame.from_features(features)
        
        # (4) get the city bounds and remove stations outside of the city
        city_bounds = spatial.get_bounds(city, logger).at[0, 'geometry']
        stations = stations[stations['geometry'].within(city_bounds)].reset_index(drop=True)
        
        # (5) add station_id column
        stations['station_id'] = pd.Series(stations.index)
        
        return stations

    return geojson.read_or_create(f'{BASE_DIR}/out/station/{city}.geojson', generate_df, logger)

def apply_strategy(stations, bs_strategy, all_traffic, traffic_timeslotwise):
    if bs_strategy == StationStrategy.ALL:
        return stations
    
    percentage = bs_strategy.value
    
    num_stations = int(percentage / 100 * len(stations.index))
    
    stations_by_traffic = transformator.Transformator(all_traffic[['station_id', 'traffic']]).groupby_sum('station_id').sort('traffic', ascending=False).reset_index().get()
    stations = stations[stations['station_id'].isin(stations_by_traffic.iloc[:num_stations]['station_id'])].reset_index(drop=True)
    
    return stations # (stations, all_traffic, [t[t['station_id'].isin(stations['station_id'])] for t in traffic_timeslotwise])

def get_antennas(city, logger):
    """Reads antenna csv exported from cartoradio.

    Returns:
        pandas.DataFrame: antennas dataframe with primary key `support_number`
    """
    
    # (1) read cartoradio antenna csv
    antennas = csv.read_cartoradio(
        f'{BASE_DIR}/data/station/cartoradio/{city}/Antennes_Emetteurs_Bandes_Cartoradio.csv',
        ["support_number", "cartoradio_number", "station_number", "commissioning_date", "operator", "antenna_type", "antenna_number", "antenna_size", "directivity", "azimuth", "height_ground", "servive_type", "system", "start", "end", "unit"],
        logger
    )
    
    # (2) remove non-LTE antennas and antennas not operated by Orange
    antennas = antennas[(antennas['operator'] == 'ORANGE') & antennas['system'].apply(lambda x: 'LTE' in x)]
    
    # (3) remove irrelevant columns
    antennas = antennas[['station_number', 'antenna_number', 'support_number']].set_index(['station_number', 'antenna_number']).drop_duplicates().reset_index().set_index('support_number')
    
    return antennas
    
def get_sites(city, support_numbers, logger):
    """Reads site csv exported from cartoradio.

    Args:
        city (_str_): the city to read the sites for
        support_numbers (_numpy.array(_): _description_

    Returns:
        pandas.DataFrame: sites dataframe with primary key `support_number`
    """
    # (1) read cartoradio site csv
    sites = csv.read_cartoradio(
        f'{BASE_DIR}/data/station/cartoradio/{city}/Sites_Cartoradio.csv',
        ["support_number", "longitude", "latitude", "position", "insee", "locality", "address", "postcode", "town", "support_type", "height", "owner"],
        logger
    )
    
    # (2) remove non-LTE antennas and antennas not operated by Orange (based on the pre-filtered support numbers from the antennas dataframe)
    sites = sites[sites['support_number'].apply(lambda x: x in support_numbers)].set_index('support_number')
    
    return sites