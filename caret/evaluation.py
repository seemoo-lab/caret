from constants import *
from caret import flow, load, transformator
import logging
import pandas as pd

def evaluate_multi_cpu(city, dates, stations, links, graph, servers, radius, server_location_strategy, traffic_timeslotwise, thread_id, logger):
    timeslot_count = len(traffic_timeslotwise)
    date = dates[int((thread_id) / len(TIMES))]
    time = TIMES[(thread_id) % len(TIMES)]
    
    logger.debug(f'({thread_id}/{timeslot_count}) evaluating {date} {time}')
    flows = flow.get(city, traffic_timeslotwise[thread_id], servers, radius, server_location_strategy, thread_id, logger)
    logger.debug(f'flows from {date} {time}')
    logger.debug(flows)
    
    loads = load.get(city, stations, links, graph, flows, radius, server_location_strategy, thread_id, logger)
    logger.debug(f'loads from {date} {time}')
    logger.debug(loads)
    
    link_load = pd.DataFrame(columns=['date', 'time', 'wireless_link', 'server_location', 'server_amount', 'link_type', 'traffic'])
    
    l = loads
    l['link_type'] = l['link_id'].apply(lambda link_id: 'wireless' if str(link_id).isdigit() else link_id)
    l = transformator.Transformator(l).filter_columns(['link_type', 'traffic']).groupby_sum('link_type').get()
    
    link_load['link_type'] = l['link_type']
    link_load['traffic'] = l['traffic']
    link_load['date'] = date
    link_load['time'] = time
    link_load['wireless_link'] = radius
    link_load['server_location'] = server_location_strategy
    
    logger.debug(f'load per link from {date} {time}')
    logger.debug(link_load)
    
    return link_load