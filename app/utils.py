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


def make_postgres_conn(cfg, debug=False):
    """
    Connect to Postgres as per settings in config
    Setting debug=True uses DB_HOST_LOCAL
    """
    if debug:
        _host = cfg.DB_HOST_LOCAL
    else:
        _host = cfg.DB_HOST

    return psycopg2.connect(
        host=_host,
        database=cfg.DB_NAME,
        user=cfg.DB_USER,
        password=cfg.DB_PASSWORD
    )

def visits_lengthen_and_label(df, STAR_OR_OMOP):
    """
    convert df produced from raw SQL to long form
    then label by merging with care_site_clean to get ward/bed/room
    """
    if STAR_OR_OMOP == 'OMOP':
        df = omop_visit_detail_to_long(df, fake_value=True)
        df = join_visit_detail_to_care_site_clean(df)
    elif STAR_OR_OMOP == 'STAR':
        df = star_visits_to_long(df, fake_value=True)
        df = join_visit_detail_to_care_site_clean(df, join_on="care_site_name")
    else:
        print("!!!: INVALID CONFIGURATION for STAR_OR_OMOP: only START or OMOP are valid choices")
        sys.exit(1)
    return df

def join_visit_detail_to_care_site_clean(
        df: pd.DataFrame,
        join_on: str = "care_site_id",
        csc: pd.DataFrame = DF_CSC):
    """
    Join care_site_clean on care_site_id
    with option to modify join column (e.g. when using star, then use care_site_name)
    """
    df = df.merge(csc, how="left", left_on=join_on, right_on=join_on)
    return df

def filter_visit_detail_long(
    df: pd.DataFrame,
    column: str,
    inclusions: list)  -> pd.DataFrame:
    """
    Filters out long form visit_detail by column using list of inclusions
    """
    # TODO convert so iterates over list of columns
    df = df[df[column].isin(inclusions)]
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

def star_visits_to_long(df: pd.DataFrame, fake_value: bool = False) -> pd.DataFrame:
    """
    Transforms the the star visit query to match as best as possible the OMOP visit_detail table conversion
    Drops all end times except the last
    Assumes therefore that all visit_details are contiguous
    fake_value: creates fake value_as_number for demoing

    2019-11-28
    SQL query on star for reference
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
    -- include 5 for hospital visit
    pf.fact_type IN (5,6,7,8,9)
    AND
        pf.valid_until IS NULL
    AND 
        pp.valid_until IS NULL
    AND 
        pf.stored_from > CURRENT_TIMESTAMP - INTERVAL '6 HOUR' 
    order by pp.stored_from desc;
    """
    # Convert all ids to integers
    # df = df.astype({"encounter": int, "pp_parent_fact_id": int, "pf_parent_fact_id": int, "property_id": int})
    # Convert to datetime64 else get errors on subtracting non tz aware
    if pd.api.types.is_object_dtype(df['value_as_datetime']):
        df['value_as_datetime'] = pd.to_datetime(df['value_as_datetime'], utc=True)

    # Sort out hospital visits first
    # ==============================
    dfh = df[df['short_name_pf'] == 'HOSP_VISIT']
    # now cast wide and see what open visits you have
    dfh = dfh.pivot(
        index='encounter',
        columns='short_name_pp',
        values='value_as_datetime'
    )
    dfh = dfh.rename({
        'ARRIVAL_TIME': 'hosp_visit_start',
        'DISCH_TIME': 'hosp_visit_end',
        'encounter': 'visit_occurrence_id'
    }, axis=1)
    # calculate hospital los
    dfh = dfh.assign(hosp_los=lambda dfh: (dfh.hosp_visit_end-dfh.hosp_visit_start).dt.total_seconds())

    # Now sort out bed visits
    # =======================
    # df becomes just bed visits
    df = df[df['short_name_pf'] == 'BED_VISIT']

    # prepare bed LOS and start stop
    df_blos=df[['encounter', 'pp_parent_fact_id', 'short_name_pp', 'value_as_datetime']]
    df_blos = df_blos[df_blos.short_name_pp !='LOCATION']
    df_blos = df_blos.pivot(
            index='pp_parent_fact_id',
            columns='short_name_pp',
            values='value_as_datetime'
        )
    df_blos = df_blos.rename({
            'ARRIVAL_TIME': 'bed_visit_start',
            'DISCH_TIME': 'bed_visit_end'
        }, axis=1)
    df_blos = df_blos.assign(bed_los=lambda df_blos: (df_blos.bed_visit_end-df_blos.bed_visit_start).dt.total_seconds())

    # Prepare as long form ; one row per event and an end event
    # Drop unnecssary columns
    df = df[['encounter', 'pp_parent_fact_id', 'property_id', 'short_name_pp', 'value_as_datetime', 'value_as_string']]
    # Melt -> now becomes pivot because data is already long
    df1 = df.set_index(['encounter', 'pp_parent_fact_id'])
    # this seems v slow but it's the only way I can get this to work
    df2 = df.pivot_table(
        index=['encounter', 'pp_parent_fact_id'],
        columns='short_name_pp',
        values='value_as_string',
        aggfunc='first'
    )
    df = df2.merge(df1, left_index=True, right_index=True)
    df = df.reset_index()
    df = df[['encounter', 'pp_parent_fact_id', 'short_name_pp', 'LOCATION', 'value_as_datetime']]
    df = df.rename({
        'encounter': 'visit_occurrence_id',
        'short_name_pp': 'event',
        'value_as_datetime': 'timestamp',
        'LOCATION': 'care_site_name'
    }, axis=1)

    # drop LOCATION rows
    df = df[df['event'] != 'LOCATION']

    # rename values in event column
    mask = (df['event'] == "ARRIVAL_TIME")
    df.loc[mask,'event']
    df.loc[mask,'event'] = 'visit_start_datetime'

    mask = (df['event'] == "DISCH_TIME")
    df.loc[mask,'event']
    df.loc[mask,'event'] = 'visit_end_datetime'

    # TODO better way to track patients across bed moves
    # create a person_id so that we can update the correct dots
    # the following is nice but won't work b/c it is per query so just reproduce visit_occurrence_id
    # df['person_id'] = df.groupby('visit_occurrence_id').ngroup()
    df['person_id'] = df['visit_occurrence_id']

    # Identify the last visit_end_datetime in each visit_occurrence
    # TODO better error checking here: am assuming that every end = preceding start hence all trnasitions are perfect
    # Need a 'step' indicator by visit_occurence then delete all end times except for the last
    df = df.sort_values(by=["person_id", "visit_occurrence_id", "timestamp"])
    df['detail_i'] = df.groupby(["person_id", "visit_occurrence_id"]).cumcount()+1
    # now create a max indicator
    df['detail_i_max'] = df.groupby(["person_id", "visit_occurrence_id"])['detail_i'].transform(max)

    
    # now drop where visit_end_datetime 
    df = df[ (df.event == 'visit_start_datetime') ]

    # Drop unnecessary columns
    df = df[['person_id', 'visit_occurrence_id', 'pp_parent_fact_id', 'care_site_name', 'event', 'timestamp', 'detail_i']]

    df['timestamp_str'] = df['timestamp'].apply(lambda x: str(x))

    # Now join on bed los info
    df = df.merge(df_blos, left_on='pp_parent_fact_id', right_index=True)
    # Now join back on hospital visits
    df = df.merge(dfh, left_on='visit_occurrence_id', right_on='encounter')

    if fake_value:
        df['value_as_number'] = np.random.random(df.shape[0])*200   

    return df
