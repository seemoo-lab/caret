from constants import *
from caret import spatial, station, tilestation, topology
from plot import geoplot as gp
from rw import log, parse
import networkx as nx

logger = log.init(f'{BASE_DIR}/out/logs/connectivity.log')
parser = parse.init()

# (0) parse arguments
args = parser.parse_args()

city = parse.validate_city(args)
bs_fraction = parse.validate_bs(args)
radius = parse.validate_radius(args)
min_neighbours = parse.validate_min_neighbours(args)

print('################\n# CARET CONFIG #\n################\n')
print(f'city:\t\t{city}')
print(f'available BSs:\t{bs_fraction}%')
print(f'link radius:\t{radius}m')
print(f'min neighbours:\t{min_neighbours}\n')
    
# (1) get tiles provided by netmob
tiles = spatial.get_tiles(city, logger)

# (2) get stations provided by cartoradio
stations = station.get(city, logger)

# (3) map each tile to the closest station
(tiles, stations, coverage) = tilestation.map(city, tiles, stations, logger)

# (4) establish links
stations['radius'] = -1
(links, graph) = topology.get(city, stations, radius, min_neighbours, logger)

# (5) identify main subgraph
main_subgraph = max(nx.connected_components(graph), key=len)
stations.loc[stations.index.isin(main_subgraph), 'radius'] = 1

# (6) plot figure
gp.plot_connectivity(stations, f'{BASE_DIR}/figures/connectivity-{city}-{radius}.pdf')
print(f'-> saved figure to {BASE_DIR}/figures/connectivity-{city}-{radius}.pdf')