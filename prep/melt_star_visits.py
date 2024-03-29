# Steve Haris
# 2019-11-28
# working directly with a query that pulls data from star
# EMAP STAR visit query pasted here for reference
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
# linear script to tezt the logic

# Standard library
import datetime

# Additional modules
import numpy as np
import pandas as pd
import psycopg2
import psycopg2.extras
from psycopg2 import sql

# Local modules
import config as cfg
import utils

conn = utils.make_postgres_conn(cfg, debug=True)

curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

from utils import star_visits_to_long


TIME_THEN = datetime.datetime(2019, 10, 27, 17)
TIME_NOW = datetime.datetime(2019, 11, 23, 23)
SQL_STRING = "SELECT * FROM star_visits"

ID_VARS=["encounter","pp_parent_fact_id"]
# VALUE_VARS = ["visit_start_datetime", "visit_end_datetime"]
# ALL_VARS = ID_VARS + VALUE_VARS

SQL = sql.SQL(SQL_STRING.format(TIME_THEN, TIME_NOW))

# Load data
df = pd.read_sql(SQL, conn)
star_visits_to_long(df)

df = df.astype({"encounter": int, "pp_parent_fact_id": int, "attr_id_pf": int, "pf_parent_fact_id": int, "property_id": int})
df.columns

df = df[['encounter', 'pp_parent_fact_id', 'property_id', 'short_name_pp', 'value_as_datetime', 'value_as_string']]
# df.set_index(['encounter', 'pp_parent_fact_id']).unstack('short_name_pp')
df1 = df.set_index(['encounter', 'pp_parent_fact_id'])
# this seems v slow but it's the only way I can get this to work
df2 = df.pivot_table(
    index=['encounter', 'pp_parent_fact_id'],
    columns='short_name_pp',
    values='value_as_string',
    aggfunc='first'
)
df = df2.merge(df1, left_index=True, right_index=True)
df
df = df.reset_index()
df = df[['encounter', 'pp_parent_fact_id', 'short_name_pp', 'LOCATION', 'value_as_datetime']]
df = df.rename({
    'encounter': 'visit_occurrence_id',
    'short_name_pp': 'event',
    'value_as_datetime': 'timestamp',
    'LOCATION': 'care_site_name'
}, axis=1)

df = df[df['event'] != 'LOCATION']
df
df = df.sort_values(by=["timestamp"])
df
df = df.sort_values(by=["visit_occurrence_id", "timestamp"])
df

# TODO better way to track patients across bed moves
# create a person_id so that we can update the correct dots
# the following is nice but won't work b/c it is per query so just reproduce visit_occurrence_id
# df['person_id'] = df.groupby('visit_occurrence_id').ngroup()
df['person_id'] = df['visit_occurrence_id']
df


# TODO better error checking here: am assuming that every end = preceding start hence all trnasitions are perfect
# Need a 'step' indicator by visit_occurence then delete all end times except for the last
df = df.sort_values(by=["person_id", "timestamp"])
df['detail_i'] = df.groupby(["person_id", "visit_occurrence_id"]).cumcount()+1
df

# now create a max indicator
df = df.sort_values(by=["person_id", "timestamp"])
df['detail_i_max'] = df.groupby(["person_id", "visit_occurrence_id"])['detail_i'].transform(max)
df.head(10)

tdf = df.copy()

mask = (tdf['event'] == "ARRIVAL_TIME")
tdf.loc[mask,'event']
tdf.loc[mask,'event'] = 'visit_start_datetime'

mask = (tdf['event'] == "DISCH_TIME")
tdf.loc[mask,'event']
tdf.loc[mask,'event'] = 'visit_end_datetime'

df = tdf



# now drop where visit_end_datetime unless detail_i = detail_i_max
df = df[ (df.event == 'visit_start_datetime') |
    ((df.event == 'visit_end_datetime') & (df.detail_i == df.detail_i_max))]

df

df = df[['person_id', 'visit_occurrence_id', 'care_site_name', 'event', 'timestamp', 'detail_i']]
# df.set_index('care_site_id', inplace=True)
df.head(30)

# Now join with care site info

care_site_clean = pd.read_csv('../data/care_site_clean.csv')
# care_site_clean.set_index('care_site_id')
care_site_clean.head()

df.merge(care_site_clean, how="left", left_on="care_site_name", right_on="care_site_name")







