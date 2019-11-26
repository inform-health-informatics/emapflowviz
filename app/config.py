import datetime
from starlette.config import Config

# Environment variables
config = Config(".env")
DB_HOST = config("DB_HOST", cast=str, default="host.docker.internal")
DB_NAME = config("DB_NAME", cast=str)
DB_PORT = config("DB_PORT", cast=int)
# TODO use startlettes secret class: https://www.starlette.io/config/
DB_PASSWORD = config("DB_PASSWORD", cast=str)
DB_USER = config("DB_USER", cast=str)
WEBSOCKET_SERVER = config("WEBSOCKET_SERVER", cast=str)

# Locally declared variables
SIM_SPEED_SECS = 2
TIME_START = datetime.datetime(2019, 11, 23, 17)
TIME_ENDS = datetime.datetime(2019, 11, 25, 17)
TIME_NOW = TIME_START
TIME_DELTA = datetime.timedelta(hours=1)
TIME_MULT = 1

SQL_STRING  = """
    SELECT measurement_id, measurement_datetime, measurement_concept_id, value_as_number
    FROM measurement
    WHERE
        measurement_datetime > '{}'
        AND
        measurement_datetime <= '{}'
    ORDER BY measurement_datetime;
"""
