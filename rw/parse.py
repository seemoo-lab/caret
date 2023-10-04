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
