
from caret import app, edge, evaluation, routing, spatial, station, server, tilestation, traffic, topology, transformator
from constants import *
from plot import geoplot as gp
from rw import csv, log, parse
import multiprocessing
import pandas as pd

if __name__ == "__main__":
    
    parser = parse.init()
    args = parser.parse_args()
    
    city = parse.validate_city(args)
    bs_fraction = parse.validate_bs(args)
    edge_fraction = parse.validate_edge(args)
    radius = parse.validate_radius(args)
    min_neighbours = parse.validate_min_neighbours(args)
    app_strategy = parse.validate_apps(args)
    service_deployment = parse.validate_deployment(args)
    routing_strategy = parse.validate_routing(args)
    
    dates = DATES[-1:]
    
    print('################\n# CARET CONFIG #\n################\n')
    print(f'city:\t\t\t{city}')
    print(f'dates:\t\t\t{dates}')
    print(f'available BSs:\t\t{bs_fraction}%')
    print(f'edge-capable BSs:\t{edge_fraction}%')
    print(f'link radius:\t\t{radius}m')
    print(f'min neighbours:\t\t{min_neighbours}')
    print(f'app strategy:\t\t{app_strategy}')
    print(f'deployment strategy:\t{service_deployment}')
    print(f'routing strategy:\t{routing_strategy}\n')

    logger = log.init(f'{BASE_DIR}/out/logs/{city}.log')

    apps = app.get(app_strategy, logger)
    tiles = spatial.get_tiles(city, logger)
    stations = station.get(city, logger) # bs strategy will be applied later when traffic is available
    (tiles, stations, coverage) = tilestation.map(city, tiles, stations, logger)

    num_cpus = multiprocessing.cpu_count()

    # () bring traffic into parallelizable format
    with multiprocessing.Pool(processes=num_cpus) as pool:
        pool.starmap(
            traffic.prepare_day,
            [
                (city, date, apps, tiles, logger)
                for date in dates
            ]
        )

    pool.close()
    pool.join()

    # () get a traffic data frame for each timeslot
    traffic_timeslotwise = traffic.get(city, dates, logger)
    all_traffic = pd.concat(traffic_timeslotwise, ignore_index=True)
    stations = station.apply_strategy(stations, bs_fraction, all_traffic, traffic_timeslotwise)
    edge_servers = edge.get(city, stations, all_traffic, edge_fraction, logger)
    servers = server.get(city, all_traffic, edge_servers, service_deployment, logger)
    (links, graph) = topology.get(city, stations, radius, min_neighbours, logger)
    timeslot_count = len(traffic_timeslotwise)
    
    with multiprocessing.Pool(processes=num_cpus) as pool:
        load_per_link_type = pool.starmap(
            evaluation.evaluate_multi_cpu,
            [
                (city, dates, stations, links, graph, servers, radius, service_deployment, traffic_timeslotwise, i, logger)
                for i in range(timeslot_count)
            ]
        )

    pool.close()
    pool.join()
    
    loads = pd.concat(load_per_link_type, ignore_index=True)
    
    
    eval = transformator.Transformator(loads[['link_type', 'traffic']]).groupby_sum('link_type').add_column('city', city).add_column('app_server_strategy', service_deployment).set_index('link_type').get()
    
    service = eval.at['local', 'traffic'] + eval.at['wireless', 'traffic']
    no_service = eval.at['none', 'traffic']
    
    print(f'servicable traffic flows: {service}')
    print(f'non-servicable traffic flows: {no_service}')
    print(f'-> connectivity of {int(10000 * service/(service+no_service))/100}%')