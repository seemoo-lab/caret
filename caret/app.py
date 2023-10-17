from constants import *
from enum import Enum
from rw import csv

class AppStrategy(Enum):
    CRITICAL = 0
    ALL = 100

def get(app_strategy, logger):
    apps = csv.read(f'{BASE_DIR}/data/apps/categories.csv', logger)
    
    if app_strategy == 'CRITICAL':
        apps = apps[apps['app_id'].isin(CRITICAL_APPS)]
        return apps
    
    return apps