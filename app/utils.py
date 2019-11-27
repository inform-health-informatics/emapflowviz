# Standard library

# Additional modules
import numpy as np
import pandas as pd
import psycopg2

# Local modules
import config as cfg

def make_postgres_conn(cfg):
    """
    Connect to Postgres as per settings in config
    """
    return psycopg2.connect(
        host=cfg.DB_HOST,
        database=cfg.DB_NAME,
        user=cfg.DB_USER,
        password=cfg.DB_PASSWORD
    )


def utils_hello(foo: str) -> str:
    """
    Dummy function
    """
    print(foo)
