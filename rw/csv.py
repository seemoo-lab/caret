from constants import *
import os.path
import logging
import pandas as pd

def read_or_create(path, generate_df, logger):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if(os.path.isfile(path)):
        logger.debug(f'reading existing {path} ...')
        return pd.read_csv(path, sep=',')

    logger.debug(f'creating {path} ...')
    df = generate_df()
    if not df is None:
        write(df, path, logger)
    return read(path, logger)

def write(df, path, logger):
    logger.debug(f'creating {path} ...')
    df.to_csv(path, index=False)
    
def append(df, path, logger):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if(os.path.isfile(path)):
        logger.debug(f'appending to {path} ...')
        df.to_csv(path, mode='a', index=False, header=False)
    else:
        write(df, path, logger)

def read(path, logger):
    logger.debug(f'reading {path} ...')
    return pd.read_csv(
        path,
        sep=','
    )

def read_cartoradio(path, columns, logger):
    logger.debug(f'reading {path} ...')
    return pd.read_csv(
        path,
        sep=';',
        encoding='latin1',
        header=0,
        names=columns
    )
    
def read_netmob(city, app, date, link, logger):
    logger.debug(f'reading {BASE_DIR}/data/traffic/{city}/{app}/{date}/{city}_{app}_{date}_{link}.txt')
    return pd.read_csv(
        f'{BASE_DIR}/data/traffic/{city}/{app}/{date}/{city}_{app}_{date}_{link}.txt',
        sep=' ',
        names=['tile_id'] + TIMES
    )