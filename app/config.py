import datetime
from starlette.config import Config

# Environment variables
config = Config(".env")
DB_HOST = config("DB_HOST", cast=str, default="host.docker.internal")
DB_HOST_LOCAL = "localhost"
DB_NAME = config("DB_NAME", cast=str)
DB_PORT = config("DB_PORT", cast=int)
# TODO use startlettes secret class: https://www.starlette.io/config/
DB_PASSWORD = config("DB_PASSWORD", cast=str)
DB_USER = config("DB_USER", cast=str)
WEBSOCKET_SERVER = config("WEBSOCKET_SERVER", cast=str)

# Locally declared variables
DEBUG=True
STAR_OR_OMOP="STAR"  # config to define which DB to use

# STAR_OR_OMOP="OMOP"
# SIM_ SPEED_SECS is the delay between SQL queries and updates
# Each message then gets loaded 10x faster
SIM_SPEED_SECS = 5
TIME_ZERO = datetime.datetime(2019, 5, 25, 19)
TIME_START = datetime.datetime(2019, 5, 27, 19)
TIME_ENDS = datetime.datetime(2019, 11, 29, 19)
TIME_NOW = TIME_START
TIME_DELTA = datetime.timedelta(hours=1)
TIME_MULT = 1

if DEBUG:
    SQL_STRING = "SELECT * FROM star_visits"
else:
    if STAR_OR_OMOP == "STAR":
        # EMAP STAR version
        SQL_STRING = """
        -- converting to using live from omop_live for visit info
        SELECT
            pf.encounter,     
            
            pp.parent_fact pp_parent_fact_id,
            pf.fact_type attr_id_pf,
            att_pf.short_name short_name_pf,
            pf.parent_fact pf_parent_fact_id,
            pf.stored_from pf_stored_from,
            pf.valid_from pf_valid_from,
            
            pp.property_id,
            pp.attribute attr_pp,
            att_pp.short_name short_name_pp,
            pp.stored_from pp_stored_from,
            pp.valid_from pp_valid_from,
        
            pp.value_as_string,
            pp.value_as_datetime,
            pp.value_as_integer,
            pp.value_as_boolean,
            pp.value_as_attribute
            
        -- start from property and join out else v slow 

        FROM live.patient_property pp 
        LEFT JOIN live.patient_fact pf
            ON pp.parent_fact = pf.fact_id
        LEFT JOIN live.attribute att_pf
            ON pf.fact_type = att_pf.attribute_id
        LEFT JOIN live.attribute att_pp
            ON pp.attribute = att_pp.attribute_id 

        WHERE
            pf.fact_type IN (6,7,8,9)
        AND
            pf.valid_until IS NULL
        AND 
            pp.valid_until IS NULL
        AND 
        --   pf.stored_from > CURRENT_TIMESTAMP - INTERVAL '6 HOUR' 
            pf.stored_from > '{}'
        AND
            pf.stored_from <= '{}'
        ORDER BY pp.stored_from desc;
        """
    elif STAR_OR_OMOP=="OMOP":
        # Visit detail version
        SQL_STRING = """
            SELECT * FROM VISIT_DETAIL
            WHERE
                visit_start_datetime > '{}'
                AND
                visit_start_datetime <= '{}'
            ORDER BY visit_start_datetime;
        """
    else:
        print("!!!: INVALID CONFIGURATION for STAR_OR_OMOP: only START or OMOP are valid choices")
        sys.exit(1)

# Measurement version
# SQL_STRING  = """
#     SELECT measurement_id, measurement_datetime, measurement_concept_id, value_as_number
#     FROM measurement
#     WHERE
#         measurement_datetime > '{}'
#         AND
#         measurement_datetime <= '{}'
#     ORDER BY measurement_datetime;
# """
