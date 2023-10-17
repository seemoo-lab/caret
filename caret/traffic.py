from constants import *
# from mappers.tilestation import TileStationMapper
import multiprocessing
from rw import csv
import logging
import pandas as pd


def get(city, dates, logger):
    """Get the city's traffic data for all the dates.

    Args:
        city (str): the city
        dates (list(str)): the dates

    Returns:
        list(pandas.DataFrame): A traffic data frame for all times of all dates in a list
    """
    # (1) read all traffic data for all the timeslots of all dates into a list
    traffic = [csv.read(f'{BASE_DIR}/out/{city}/traffic/{date}/{time.replace(":", "")}.csv', logger) for time in TIMES for date in dates]
    
    return traffic

def prepare_day(city, date, apps, tiles, logger):
    # helper method to prepare one date
    def generate_df():
        return prepare_entire_day(city, date, apps, tiles, logger)
    
    csv.read_or_create(f'{BASE_DIR}/out/{city}/traffic/{date}/all.csv', generate_df, logger)

def prepare(city, dates, apps, tiles, logger):
    """Ensures that the city's traffic data for all the dates has been prepared.

    Args:
        city (str): the city
        dates (list(str)): the dates
        tiles (geopandas.GeoDataFrame): the tiles data frame

    Returns:
        _type_: _description_
    """
    
    # (1) for each date check if the traffic data has been prepared for evaluation
    for date in dates:
        
        # helper method to prepare one date
        def generate_df():
            return prepare_entire_day(city, date, apps, tiles, logger)
        
        # (1.1) only prepare the days that have not been prepared yet
        csv.read_or_create(f'{BASE_DIR}/out/{city}/traffic/{date}/all.csv', generate_df)

def prepare_entire_day(city, date, apps, tiles, logger):
    """Reads the city's traffic data for the date, brings it into long format, and stores it to file.

    Args:
        city (_str_): the city
        date (_str_): the date
        tiles (_geopandas.GeoDataFrame_): the tiles data frame

    Returns:
        pandas.DataFrame: the data frame containing all the traffic data of the entire day
    """
    
    # (1) prepare columns for all dfs
    columns=['app_id', 'link', 'station_id', 'traffic']
    
    # (2) set tile index for easier access in (4.1.2)
    tiles = tiles.set_index('tile_id')
    
    # (3) prepare a data frame for each timeslot
    dfs = [pd.DataFrame(columns=columns) for _ in TIMES]
    
    # (4) fill traffic data frames with the traffic off all apps 
    apps = apps['app_id'].to_list()
    for i in range(len(apps)):
        app = apps[i]
        logging.debug(f'({i+1}/{len(APPS)}) reading {app} traffic from {date}')
        
        # (4.1) consider uplink + downlink
        for link in LINKS:
            
            # (4.1.1) read csv provided by netmob
            traffic_by_tile = csv.read_netmob(city, app, date, link, logger)

            # (4.1.2) look up each tile's station_id
            traffic_by_tile['station_id'] = traffic_by_tile['tile_id'].map(lambda tile_id: tiles.at[tile_id, 'station_id'])
            
            # (4.1.3) group traffic by station
            traffic_by_station = traffic_by_tile.drop('tile_id', axis=1).groupby(by='station_id').sum().reset_index()
            
            # (4.1.4) store station ids in pandas.Series for easier access in (2.1.4.3)
            station_ids = traffic_by_station['station_id']
            
            # (4.1.5) extract each timeslot's traffic from the current file
            for i in range(len(TIMES)):
                
                # (4.1.5.1) get current timeslot
                time = TIMES[i]
                
                # (4.1.5.2) extract that timeslot's traffic
                traffic = traffic_by_station[time]
                
                # (4.1.5.3) fill remaining columns
                df = pd.DataFrame(columns=columns)
                df['traffic'] = traffic
                df['station_id'] = station_ids
                df['link'] = link
                df['app_id'] = app
                df['date'] = date
                df['time'] = time
                
                # (4.1.5.4) concat traffic to the timeslot's data frame
                dfs[i] = pd.concat([dfs[i], df], ignore_index=True)

    # (5) prepare data frame for the entire date
    entire_day = pd.DataFrame(columns=columns)
    
    # (6) fill data frame with each timeslots traffic
    for i in range(len(TIMES)):
        logging.debug(f'({i+1}/{len(TIMES)}) writing {date} {TIMES[i]}')
        # (6.1) get current timeslot
        time = TIMES[i]
        
        # (6.2) get corresponding traffic data frame
        df = dfs[i]
        
        # (6.3) store that timeslot's traffic to file
        path = f'{BASE_DIR}/out/{city}/traffic/{date}/{time.replace(":", "")}.csv'
        csv.write(df, path, logger)
        
        # (6.4) concat that timeslots' traffic to data frame of the entire day
        entire_day = pd.concat([entire_day, df], ignore_index=True)
    
    return entire_day