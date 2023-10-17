from constants import *
from enum import Enum
from caret import transformator
from functools import reduce
from rw import csv
import pandas as pd

class ServerStrategy(Enum):
    CENTRAL = 1
    DECENTRAL = 2

def get(city, traffic, edge_servers, server_strategy, logger):
    """Locate app servers corresponding to the server location and server amount strategies

    Args:
        traffic (pandas.DataFrame): the traffic data set
        server_location_strategy (server.ServerLocationStrategy): the server location strategy
        server_amount_strategy (server.ServerAmountStrategy): the server amount strategy

    Returns:
        pandas.DataFrame: all servers in a data frame
    """
    
    # (1) get the amount of servers to deploy per app
    server_amount = 1
    
    # helper method to locate the servers
    def generate_df():
        """Locate n servers for each app corresponding to the server location strategy

        Args:
            traffic (pandas.DataFrame): the traffic data frame
            server_location_strategy (server.ServerLocationStrategy): the server location strategy
            server_amount (int): the amount of servers to deploy per app (n)

        Returns:
            pandas.DataFrame: all servers in a data frame
        """
        
        # (1) sum up columns date, time, and link (uplink/downlink)
        t = transformator.Transformator(traffic[traffic['station_id'].isin(edge_servers['station_id'])]).sum(['link', 'date', 'time'])
        
        # (2) prepare servers data frame
        servers = pd.DataFrame(columns=['app_id', 'station_id'])
        
        # (3a) decentral: group traffic by app and find the station with the most traffic
        if server_strategy == 'DECENTRAL':
            stations = t.sort('traffic').groupby_tail(['app_id'], server_amount).get()
            servers['app_id'] = stations['app_id']
            servers['station_id'] = stations['station_id']
        
        # (3b) central: find the station with the most traffic and locate all app servers there
        elif server_strategy == 'CENTRAL':
            stations = t.copy().sort('traffic').filter_columns('station_id').get().tail(server_amount).to_list()
            servers['app_id'] = t.filter_columns('app_id').get().drop_duplicates()
            servers['station_id'] = [stations for i in servers.index]
        
        # # (3c) random: for each app sample n random stations
        # else:
        #     stations = t.copy().filter_columns('station_id').get().drop_duplicates()
        #     servers['app_id'] = t.filter_columns('app_id').get().drop_duplicates()
        #     servers['station_id'] = servers['app_id'].apply(lambda s: stations.sample(server_amount).to_numpy())

        # (4) explode lists of stations
        servers = servers.explode('station_id')
        
        # (5) add server_id
        servers = servers.reset_index(names='server_id')
        
        return servers
    
    # (2) locate n servers per app corresponding to the server location strategy
    servers = csv.read_or_create(f'{BASE_DIR}/out/servers/{city}-{server_strategy}.csv', generate_df, logger)
    
    return servers