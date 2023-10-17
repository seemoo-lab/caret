from constants import *
import numpy as np
import pandas as pd
from rw import csv

def get(city, traffic, servers, radius, server_location_strategy, thread_id, logger):
    """Computes traffic flows from plain traffic data by looking up an application's app_server location and routing uplink traffic from the station to the server and downlink traffic from the server to the station.

    Args:
        city (str): the city
        traffic (pandas.DataFrame): the traffic
        servers (geopandas.GeoDataFrame): the servers
        wireless_link_strategy (topology.WirelessLinkStrategy): the wireless link strategy
        server_location_strategy (server.ServerLocationStrategy): the server location strategy
        server_amount_strategy (server.ServerAmountStrategy): the server amount strategy
        thread_id (int): the thread id

    Returns:
        pandas.DataFrame: the traffic flows in a data frame
    """
    
    def generate_df():
        
        # (1) prepare lists for the app servers and stations for easier access in (3)
        app_servers = traffic['app_id'].apply(lambda a: servers[servers['app_id'] == a]['station_id'].to_numpy()[0])
        stations = traffic['station_id']#.apply(lambda s: np.array(s))
        
        # (2) prepare the flows data frame
        flows = pd.DataFrame(columns=['flow_id', 'start_station', 'end_station', 'date', 'time', 'app_id', 'traffic'])
        
        # (3) set start_station to the station for (uplink) or the server (downlink)
        flows['start_station'] = np.where(traffic['link'] == 'UL', stations, app_servers)
        flows['end_station'] = np.where(traffic['link'] == 'DL', stations, app_servers)
        
        # (4) copy remaining columns from traffic, add flow_id
        flows['date'] = traffic['date']
        flows['time'] = traffic['time']
        flows['app_id'] = traffic['app_id']
        flows['traffic'] = traffic['traffic']
        flows['flow_id'] = pd.Series(flows.index)
        
        return flows
        
    return csv.read_or_create(f'{BASE_DIR}/out/{city}/flows/{radius}/{server_location_strategy}/{thread_id}.csv', generate_df, logger)
