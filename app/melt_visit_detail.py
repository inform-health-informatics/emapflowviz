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

conn = utils.make_postgres_conn(cfg)
curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

TIME_THEN = datetime.datetime(2019, 10, 23, 17)
TIME_NOW = datetime.datetime(2019, 11, 23, 17)
SQL_STRING = "SELECT * FROM VISIT_DETAIL"

ID_VARS = ["person_id", "visit_occurrence_id", "visit_detail_id", "care_site_id"]
VALUE_VARS = ["visit_start_datetime", "visit_end_datetime"]
ALL_VARS = ID_VARS + VALUE_VARS

SQL = sql.SQL(SQL_STRING.format(TIME_THEN, TIME_NOW))

# Load data
df = pd.read_sql(SQL, conn)
df = df[ALL_VARS]
df = df.astype({"care_site_id": int, "person_id": int, "visit_occurrence_id": int, "visit_detail_id": int})
df = df.melt(
    id_vars=ID_VARS,
    value_vars=VALUE_VARS,
    var_name="event",
    value_name="timestamp"
)
# 
# df.shape
df = df.sort_values(by=["person_id", "visit_occurrence_id", "timestamp"])
# TODO better error checking here: am assuming that every end = preceding start hence all trnasitions are perfect
# Need a 'step' indicator by visit_occurence then delete all end times except for the last
df['detail_i'] = df.groupby(["person_id", "visit_occurrence_id"]).cumcount()+1
# df.head()

# now create a max indicator
df['detail_i_max'] = df.groupby(["person_id", "visit_occurrence_id"])['detail_i'].transform(max)
# df.head()

# now drop where visit_end_datetime unless detail_i = detail_i_max
df = df[ (df.event == 'visit_start_datetime') |
    ((df.event == 'visit_end_datetime') & (df.detail_i == df.detail_i_max))]

df = df[ID_VARS + ['event', 'timestamp', 'detail_i']]
# df.set_index('care_site_id', inplace=True)
df.head()

# Now join with care site info

care_site_clean = pd.read_csv('../data/care_site_clean.csv')
# care_site_clean.set_index('care_site_id')
care_site_clean.head()

df.merge(care_site_clean, how="left", left_on="care_site_id", right_on="care_site_id")







