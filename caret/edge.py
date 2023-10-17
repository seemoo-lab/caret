from caret import transformator
from constants import *
from enum import Enum
import pandas as pd

class EdgeStrategy(Enum):
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

def get(city, stations, all_traffic, edge_strategy, logger):
    
    df = pd.DataFrame(columns=['station_id'])
    
    percentage = edge_strategy
    
    num_edge_servers = int(percentage / 100 * len(stations.index))
    
    edge_equipped_stations = transformator.Transformator(all_traffic[['station_id', 'traffic']]).groupby_sum('station_id').sort('traffic', ascending=False).reset_index().get().iloc[:num_edge_servers]['station_id']
    
    if not 'station_id' in stations.columns:
        stations = stations.reset_index('station_id')
    
    df['station_id'] = stations[stations['station_id'].isin(edge_equipped_stations)].reset_index(drop=True)['station_id']
        
    df = df.reset_index(names='server_id')
    
    return df