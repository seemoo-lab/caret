from caret import transformator
from constants import *
from enum import Enum
import ast
import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from rw import geojson
from rw import csv


def get(city, stations, links, graph, flows, radius, server_location_strategy, thread_id, logger):
    """Computes the network load from a data frame of flows.

    Args:
        city (str): the city
        stations (geopandas.GeoDataFrame): the stations
        links (geopandas.GeoDataFrame): the links
        graph (networkx.Graph): the topology graph
        flows (pandas.DataFrame): the flows
        wireless_link_strategy (topology.WirelessLinkStrategy): the wireless link strategy
        server_location_strategy (server.ServerLocationStrategy): the server location strategy
        server_amount_strategy (server.ServerAmountStrategy): the server amount strategy
        thread_id (int): the thread id
        
    Returns:
            geopandas.GeoDataFrame: the network load per link in a geo data frame
    """
    
    # helper method to generate the data frame
    def generate_df():
        
        # (1) prepare data frame
        loads = pd.DataFrame(columns=['link_id', 'app_id', 'traffic'])
        
        # (2) for each flow, copy 'app_id' and 'traffic', then compute the link_ids of all links required to route from 'start' to 'end'
        loads['app_id'] = flows['app_id']
        loads['traffic'] = flows['traffic']
        loads['link_id'] = flows.apply(lambda f: flows_to_routes(f, stations, graph), axis=1)
        
        
        # (3) explode link lists into separate rows
        loads = loads.explode('link_id')
        
        # (4) group loads by link_id and sum up traffic
        loads = transformator.Transformator(loads).filter_columns(['link_id', 'traffic']).groupby_sum('link_id').get()
        
        links['link_id'] = links['link_id'].astype('str')
        loads['link_id'] = loads['link_id'].astype('str')
        
        # (5) join with the link data frame to add columns 'geometry', 'start', 'end', 'weight', and 'type
        loads = links.set_index('link_id').join(loads.set_index('link_id'), how='outer').reset_index()
        
        # (6) set traffic of unused links to zero
        loads['traffic'] = loads['traffic'].fillna(0)
        
        return loads
        
    return geojson.read_or_create(f'{BASE_DIR}/out/{city}/loads/{radius}/{server_location_strategy}/{thread_id}.geojson', generate_df, logger)

def flows_to_routes(f, stations, graph):
    (start, end) = recover_stations(f['start_station'], f['end_station'], stations)
    
    if start == end:
        return 'local'
    
    try:
        hops = nx.shortest_path(graph, source=start, target=end)
    except:
        return 'none'
    
    link_ids = [graph[hops[i]][hops[i+1]]['id'] if graph.has_edge(hops[i], hops[i+1]) else graph[hops[i+1]][hops[i]]['id'] for i in range(len(hops)-1)]
    return np.asarray(link_ids)

def recover_stations(start, end, stations):
    if 'station_id' in stations.columns:
        stations.set_index('station_id', inplace=True)
    
    try:
        start = int(start)
    except:
        candidates = pd.Series(np.fromstring(start[1:-1], dtype=int, sep=' '))
        distances = candidates.apply(lambda s: stations.at[int(s), 'geometry'].distance(stations.at[int(end), 'geometry']))
        start = int(candidates.loc[distances.idxmin()])
    
    try:
        end = int(end)
    except:
        candidates = pd.Series(np.fromstring(end[1:-1], dtype=int, sep=' '))
        distances = candidates.apply(lambda e: stations.at[int(e), 'geometry'].distance(stations.at[int(start), 'geometry']))
        end = int(candidates.loc[distances.idxmin()])
        
    return (start, end)