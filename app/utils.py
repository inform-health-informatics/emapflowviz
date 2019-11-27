# Standard library

# Additional modules
import numpy as np
import pandas as pd
import psycopg2

# Local modules
import config as cfg

# DEFINE VARIABLES
PATH_TO_CARE_SITE_CLEAN="static/data/care_site_clean.csv"
DF_CSC = pd.read_csv(PATH_TO_CARE_SITE_CLEAN)

def utils_hello(foo: str) -> str:
    """
    Dummy function
    """
    print(foo)


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


def join_visit_detail_to_care_site_clean(df: pd.DataFrame, csc: pd.DataFrame):
    """
    Join care_site_clean on care_site_id
    """
    df.merge(csc, how="left", left_on="care_site_id", right_on="care_site_id")
    return df

def omop_visit_detail_to_long(df: pd.DataFrame, fake_value: bool = False) -> pd.DataFrame:
    """
    Transforms the OMOP visit_detail table from wide to long
    and drops all end times except the last
    Assumes therefore that all visit_details are contiguous
    fake_value: creates fake value_as_number for demoing
    """

    ID_VARS = ["person_id", "visit_occurrence_id", "visit_detail_id", "care_site_id"]
    VALUE_VARS = ["visit_start_datetime", "visit_end_datetime"]
    ALL_VARS = ID_VARS + VALUE_VARS

    # Drop unnecssary columns
    df = df[ALL_VARS]
    # Convert all ids to integers
    df = df.astype({"care_site_id": int, "person_id": int, "visit_occurrence_id": int, "visit_detail_id": int})
    # Melt
    df = df.melt(
        id_vars=ID_VARS,
        value_vars=VALUE_VARS,
        var_name="event",
        value_name="timestamp"
    )

    # Identify the last visit_end_datetime in each visit_occurrence
    # TODO better error checking here: am assuming that every end = preceding start hence all trnasitions are perfect
    # Need a 'step' indicator by visit_occurence then delete all end times except for the last
    df = df.sort_values(by=["person_id", "visit_occurrence_id", "timestamp"])
    df['detail_i'] = df.groupby(["person_id", "visit_occurrence_id"]).cumcount()+1
    # now create a max indicator
    df['detail_i_max'] = df.groupby(["person_id", "visit_occurrence_id"])['detail_i'].transform(max)

    # now drop where visit_end_datetime unless detail_i = detail_i_max
    df = df[ (df.event == 'visit_start_datetime') |
        ((df.event == 'visit_end_datetime') & (df.detail_i == df.detail_i_max))]

    # Drop unnecessary columns
    df = df[ID_VARS + ['event', 'timestamp', 'detail_i']]

    if fake_value:
        df['value_as_number'] = np.random.random(df.shape[0])*200   

    return df
