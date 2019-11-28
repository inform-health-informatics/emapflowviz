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
TIME_START = datetime.datetime(2019, 4, 23, 17)
TIME_ENDS = datetime.datetime(2019, 11, 25, 17)
TIME_NOW = TIME_START
TIME_DELTA = datetime.timedelta(hours=1)
TIME_MULT = 7*24

# EMAP STAR version
SQL = """
-- converting to using live from omop_live for visit info
select
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
  from live.patient_property pp 
  left join live.patient_fact pf
    on pp.parent_fact = pf.fact_id
  left join live.attribute att_pf
    on pf.fact_type = att_pf.attribute_id
  left join live.attribute att_pp
    on pp.attribute = att_pp.attribute_id 
  WHERE
    pf.fact_type IN (6,7,8,9)
  AND
     pf.valid_until IS NULL
  AND 
     pp.valid_until IS NULL
  AND 
     pf.stored_from > CURRENT_TIMESTAMP - INTERVAL '6 HOUR' 
  order by pp.stored_from desc;
"""

# Visit detail version
SQL_STRING = """
    SELECT * FROM VISIT_DETAIL
    WHERE
        visit_start_datetime > '{}'
        AND
        visit_start_datetime <= '{}'
    ORDER BY visit_start_datetime;
"""

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
