from util import transformator
from constants import *
from enum import Enum
from rw import geojson
import geojson as gj
import geopandas as gpd
import networkx as nx
import pandas as pd

class LinkStrategy(Enum):
    MINIMUM = 0
    QUARTER = 1
    HALF = 2
    ALMOST = 3
    FULL = 4

def get(city, stations, radius, min_neighbours, logger):
    """Get the topology based on the requested link strategy

    Args:
        stations (_geopandas.GeoDataFrame_): the stations
        link_strategy (_topology.LinkStrategy_): the link strategy

    Returns:
        _networkx.Graph_: _description_
    """
    
    # (1) get graph based on link strategy
    graph = get_graph(stations, radius, min_neighbours)
    
    # (4) create links geo data frame
    links = get_links(city, radius, min_neighbours, logger, stations, graph)

    return (links, graph)

def get_graph(stations, radius, min_neighbours):
    """Create a graph where all stations are connected with their neighbors in a `r` radius proximity.

    Args:
        stations (pandas.DataFrame): the stations
        r (int): the radius

    Returns:
        networkx.Graph: The corresponding graph
    """
    
    if 'station_id' in stations.columns:
        stations.set_index('station_id', inplace=True)
    
    # (3) initialize link_id which will be updated with each added graph edge
    link_id = 0
    
    # (4) create a networkx graph
    graph = nx.Graph()
    
    c = 0
    
    stations_metric = stations.to_crs(32643)
    
    # (5) add each station as a node, and add an edge from this station to its reachable neighbors
    for station_id in pd.Series(stations_metric.index):
            
        # (5.1) add the station as a node
        graph.add_node(station_id)
        
        # (5.2) store the station's geojson position            
        station_position = stations_metric.at[station_id, 'geometry']
        
        station_ids = pd.Series(stations_metric.index)
        
        # (5.3) store the station_ids of all other stations (in a new series to avoid updating the original data frame)
        neighbors = pd.DataFrame(station_ids[station_ids != station_id], columns=['station_id'])
        
        # helper method that maps a neighbor to the distance from the station
        distance_to_station = lambda neighbor: station_position.distance(stations_metric.at[neighbor, 'geometry'])

        # (5.4) compute distance to each neighbor
        neighbors['distance'] = neighbors['station_id'].apply(distance_to_station)
        
        # (5.5) filter neighbors within radius
        proximity = neighbors[neighbors['distance'] <= radius]
        
        # (5.6) add all neighbors in proximity
        if len(proximity.index) > 0:
            
            # (5.6.1) add an edge from the station to the neighbors in proximity
            for neighbor in proximity.index:
                
                if 'station_id' in proximity.columns:
                    proximity.set_index('station_id', inplace=True)
                
                # (5.6.1) get distance from station
                distance = proximity.at[neighbor, 'distance']
                
                # (5.6.2) add the edge with distance as weight
                graph.add_edge(station_id, neighbor, weight=2*distance, id=link_id)
                
                # (5.6.3) increment link_id for next edge
                link_id += 1
                
        # (5.6. (b)) establish link to the closest n neighbors
        else:
            
            # (5.6.1) find closest neighbours
            closest = neighbors.sort_values('distance', ascending=True, ignore_index=True)
            
            for i in range(min_neighbours):
                
                # (5.6.2) add the edge with distance as weight
                graph.add_edge(station_id, closest.at[0, 'station_id'], weight=2*closest.at[i, 'distance'], id=link_id)
            
                # (5.6.3) increment link_id for next edge
                link_id += 1
    
        c += 1
    
    return graph

def get_links(city, radius, min_neighbours, logger, stations=None, graph=None):
    """Read or create all links in a city for a link strategy.
    
    If `city` and `link_strategy` are provided, read links from file.
    If `city` and `link_strategy` are not provided, extract links from `graph` and store to file.

    Args:
        city (_str_): the city
        link_strategy (_topology.LinkStrategy_): the link strategy
        graph (_geopandas.GeoDataFrame_): (optional) the stations geo data frame
        graph (_networkx.Graph_): (optional) the graph containing all links as edges

    Returns:
        _geopandas.GeoDataFrame_: a geo data frame containing all links
    """
    
    def generate_df():
        # (1) store edges in a dict
        edges = dict(graph.edges)
        
        if len(edges.keys()) == 0:
            return gpd.GeoDataFrame(columns=['link_id', 'start', 'end', 'feature'], geometry='feature')
        
        def to_line_string(link):
            if 'station_id' in stations.columns:
                stations.set_index('station_id', inplace=True)
            start = stations.at[link[0], 'geometry']
            end = stations.at[link[1], 'geometry']
            
            line_string = gj.LineString([(start.x, start.y), (end.x, end.y)])
            
            return line_string
        
        # (2) create a geojson feature list from links' start and end points
        features = [
            gj.Feature(
                geometry=to_line_string(link),
                properties={
                    'start': link[0],
                    'end': link[1],
                    'weight': edges[link]['weight'],
                    'marker-color': 'ff6600'
                    }
                )
            for link in edges.keys()
        ]
        
        # (3) create link geo data frame with geometry column
        links = gpd.GeoDataFrame.from_features(features)
        links = links.reset_index(names='link_id')
        
        # (4) add `start`, `end` columns from edge data
        ls = list(zip(*edges.keys()))
        links['start'] = ls[0]
        links['end'] = ls[1]
        
        # (5) add link type column (only `wireless` is supported for now)
        links['type'] = 'wireless'
        
        return links
    
    return geojson.read_or_create(f'{BASE_DIR}/out/links/{city}-radius{radius}-min{min_neighbours}.geojson', generate_df, logger)

def get_adjacency_matrix(graph):
    """Converts a graph into an adjacency matrix.

    Args:
        graph (_networkx.Graph_): the graph

    Returns:
        _np.array_: the adjacency matrix
    """
    am = nx.adjacency_matrix(graph).todense()
    
    am[am > 0] = 1
    
    return am

def get_minimum_spanning_tree(stations):
    """Creates a networkx graph that connects all stations (minimum spanning tree)

    Args:
        stations (_geopandas.GeoDataFrame_): the geo data frame containing all stations

    Returns:
        _networkx.Graph_: the minimum spanning tree connecting all stations
    """
    
    # (1) create full mesh tree
    full_mesh_graph = get_full_mesh(stations)
    
    # (2) let networkx turn full mesh into a minimum spanning tree using the `boruvka` algorithm
    minimum_spanning_tree = nx.minimum_spanning_tree(full_mesh_graph, algorithm='boruvka')
    
    return minimum_spanning_tree

def get_full_mesh(stations):
    """Creates a full mesh graph with all stations as nodes.

    Args:
        stations (_geopandas.DataFrame_): the geo data frame containing all stations

    Returns:
        _networkx.Graph_: the full mesh graph connecting all stations
    """
    
    # (1) create a networkx graph
    graph = nx.Graph()
    
    # (2) add each station as a node, and add an edge from this station to all other stations
    for start in pd.Series(stations.index):
        
        # (2.1) add the station as a node
        graph.add_node(start)
        
        stations_metric = stations.to_crs(32643)
        
        # (2.2) add an edge from the station to all other stations
        for end in [end for end in stations_metric.index if end != start]:
            
            # (2.2.1) convert to geojson points
            start_position = stations_metric.at[start, 'geometry']
            end_position = stations_metric.at[end, 'geometry']
            
            # (2.2.2) get the distance between both geojson points
            distance = start_position.distance(end_position)
            
            # (2.2.3) add the edge with distance as weight
            graph.add_edge(start, end, weight=2*distance)
    
    return graph

def get_mininum_radius(stations, n):
    """Compute the minimum radius enabling all stations to find a neighbor

    Args:
        stations (geopandas.GeoDataFrame): the stations

    Returns:
        float: the minimum radius enabling all stations to find a neighbor
    """
        
    # (1) prepare data frame
    ds = pd.DataFrame(columns=['start', 'end', 'distance'])
    
    # (2) fill data frame with all pairs of stations
    ds['start'] = pd.Series(stations.index)
    ds['end'] = ds['start'].apply(lambda s: [o for o in stations.index if s != o])
    ds = ds.explode('end', ignore_index=True)
    
    stations_metric = stations.to_crs(32643)
    
    # (3) calculate the distance between all pairs of stations
    ds['distance'] = pd.Series(ds.index).apply(lambda i: stations_metric.at[ds.at[i, 'start'], 'geometry'].distance(stations_metric.at[ds.at[i, 'end'], 'geometry']))
    
    # (4) compute the minimum radius that enables all nodes to find a neighbor
    dists = transformator.Transformator(ds).sort('distance', ascending=False).groupby_tail(['start'], 1).sort('distance', ascending=False).get()
    
    return dists['distance'].quantile((6+n)/10)
