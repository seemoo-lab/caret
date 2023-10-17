from caret import app
from constants import APPS, CITIES
import argparse

def init():
    parser = argparse.ArgumentParser(description="Crisis and Resilience Evaluation Tool (CARET)")
    parser.add_argument("--city", "-c", type=str, help="City")
    parser.add_argument("--base-stations", "-b", type=int, help="Fraction of availabe base stations (percentage)")
    parser.add_argument("--edge-servers", "-e", type=int, help="Fraction of edge-capable base stations (percentage)")
    parser.add_argument("--link-radius", "-l", type=int, help="Maximum distance until all wireless links will be established (m)")
    parser.add_argument("--min-neighbours", "-n", type=int, help="Minimum amount of links to establish per base station")
    parser.add_argument("--routing", "-r", type=str, help="Routing strategy ('DISTANCE' or 'CAPACITY')")
    parser.add_argument("--service-deployment", "-s", type=str, help="Service deployment strategy ('CENTRAL' or 'DECENTRAL')")
    parser.add_argument("--apps", "-a", type=str, help="List of apps to consider for the evaluation")

    return parser

def validate_null(arg, desc):
    if not arg:
        print(f'The following argument is required: {desc}')
        exit(1)
        
def validate_null_int(arg, desc):
    if (not arg) and (not arg == 0):
        print(f'The following argument is required: {desc}')
        exit(1)

def validate_in_list(arg, list, desc):
    if not arg in list:
        print(f'Invalid {desc}. Available cities are {", ".join(list)}')
        exit(1)

def validate_non_negative(arg, desc):
    if arg < 0:
        print(f'Invalid {desc}]. {desc} must be non-negative.')
        exit(1)
        
def validate_percentage(arg, desc):
    if arg > 100:
        print(f'Invalid {desc}]. {desc} must be in [0, 100].')
        exit(1)

def validate_city(args):
    validate_null(args.city, '--city/-c')
    validate_in_list(args.city, CITIES, 'city')
    return args.city

def validate_bs(args):
    validate_null(args.base_stations, '--base-stations/-b'), 
    validate_non_negative(args.base_stations, 'BS fraction')
    validate_percentage(args.base_stations, 'BS fraction')
    return args.base_stations

def validate_radius(args):
    validate_null_int(args.link_radius, '--link_radius/-l')
    validate_non_negative(args.link_radius, 'link radius')
    return args.link_radius

def validate_min_neighbours(args):
    validate_null_int(args.min_neighbours, '--min_neighbours/-n')
    validate_non_negative(args.min_neighbours, 'min neighbours')
    return args.min_neighbours

def validate_edge(args):
    validate_null(args.edge_servers, '--edge-servers/-e'), 
    validate_non_negative(args.base_stations, 'fraction of edge-capable BSs')
    return args.edge_servers

def validate_apps(args):
    validate_null(args.apps, '--apps/-a')
    validate_in_list(args.apps, ['CRITICAL', 'ALL'], 'app strategy')
    return args.apps

def validate_deployment(args):
    validate_null(args.service_deployment, '--service-deployment/-s')
    validate_in_list(args.service_deployment, ['CENTRAL', 'DECENTRAL'], 'deployment strategy')
    return args.service_deployment

def validate_routing(args):
    validate_null(args.routing, '--routing/-r')
    validate_in_list(args.routing, ['DISTANCE', 'CAPACITY'], 'routing strategy')
    return args.routing