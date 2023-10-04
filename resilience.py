from constants import *
from caret import spatial, station, tilestation, topology
from plot import geoplot as gp
from rw import log, parse
import networkx as nx

logger = log.init(f'{BASE_DIR}/out/logs/connectivity.log')
parser = parse.init()

# (0) parse arguments
args = parser.parse_args()

if not args.city:
    print('The following argument is required: --city/-c')
    exit(1)
if not args.city in CITIES:
    print(f'Invalid city. Available cities are {", ".join(CITIES)}')
    exit(1)
city = args.city

if not args.base_stations:
    print('The following argument is required: --base-stations/-b')
    exit(1)
if args.base_stations < 0:
    print('Invalid BS fraction. BS fraction must be non-negative.')
    exit(1)
bs_fraction = args.base_stations
if (not args.link_radius) and (not args.link_radius == 0):
    print('The following argument is required: --link_radius/-l')
    exit(1)    
if args.link_radius < 0:
    print('Invalid link radius. Link radius must be non-negative.')
    exit(1)
radius = args.link_radius
    
if (not args.min_neighbours) and (not args.min_neighbours == 0):
    print('the following argument is required: --min_neighbours/-n')
    exit(1)
if args.min_neighbours < 0:
    print('Invalid min neighbours. Min neighbours must be non-negative.')
    exit(1)
min_neighbours = args.min_neighbours

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