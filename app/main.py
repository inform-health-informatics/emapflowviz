# Steve Harris
# 2019-11-22 : app to serve d3 viz in realtime for EMAP

# Imports: standard library
import asyncio  # e.g. asyncio.sleep preferred else the event loop blocks
import datetime
import json

# Imports: 3rd party
import psycopg2
import psycopg2.extras  #  for dictionary cursor
from psycopg2 import sql
from starlette.applications import Starlette
from starlette.websockets import WebSocket
from starlette.templating import Jinja2Templates
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

import pandas as pd
import numpy as np

# Imports: local
import utils
# TODO work out why outputs don't appear until after the programme restarts
# assume it is because it is an application being run by a server
utils.utils_hello('bar1')

# Define global variables from config and directly
# import configuration
import config as cfg


templates = Jinja2Templates(directory="/app/templates")

conn = utils.make_postgres_conn(cfg)
curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


async def homepage(request):
    print(">>> homepage route called")
    return templates.TemplateResponse(
        "index.html", {"request": request, "WEBSOCKET_SERVER": cfg.WEBSOCKET_SERVER}
    )


async def websocket_endpoint(websocket: WebSocket):
    """
    Handles the websocket connection
    """

    TIME_START = cfg.TIME_START
    TIME_ENDS = cfg.TIME_ENDS
    TIME_NOW = cfg.TIME_NOW
    TIME_DELTA = cfg.TIME_DELTA
    TIME_MULT = cfg.TIME_MULT
    SIM_SPEED_SECS = cfg.SIM_SPEED_SECS
    STAR_OR_OMOP = cfg.STAR_OR_OMOP
    SQL_STRING = cfg.SQL_STRING


    await websocket.accept()

    # await websocket.send_text()
    await websocket.send_json({"foo": cfg.DB_HOST})

    try:
        # NOTE these variables are not seen if they are declared outside of the function
        while TIME_NOW < TIME_ENDS:

            # now update times for next iteration of the loop
            # TODO adjust the time multiplier by a multiplier so that it asymptotes to realtime
            TIME_THEN = TIME_NOW
            TIME_NOW += TIME_MULT * TIME_DELTA

            # Run query
            
            SQL = sql.SQL(SQL_STRING.format(TIME_THEN, TIME_NOW))
            df = pd.read_sql(SQL, conn)

            if STAR_OR_OMOP == 'OMOP':
                df = utils.omop_visit_detail_to_long(df, fake_value=True)
                df = utils.join_visit_detail_to_care_site_clean(df)
            elif STAR_OR_OMOP == 'STAR':
                df = utils.star_visits_to_long(df, fake_value=True)
                df = utils.join_visit_detail_to_care_site_clean(df, join_on="care_site_name")
            else:
                print("!!!: INVALID CONFIGURATION for STAR_OR_OMOP: only START or OMOP are valid choices")
                sys.exit(1)

            df = utils.filter_visit_detail_long(df, column='ward', inclusions=['ED'])

            await websocket.send_json({
                "n_events": df.shape[0],
                "time_then": str(TIME_THEN),
                "time_now": str(TIME_NOW)
            } )
            for index, row in df.iterrows():
                event = row.to_json()
                await websocket.send_json(event)
                await asyncio.sleep(SIM_SPEED_SECS/10)
            await asyncio.sleep(SIM_SPEED_SECS)

    except AttributeError as err:
        # try to capture error and end gracefully when there is no more data
        print("!!! No more data?", err)
        # print("Closing connection to PostgreSQL")
        # curs.close()
        # conn.close()
    # finally:
    # await websocket.close()


routes = [
    Route("/", endpoint=homepage),
    Mount("/static", StaticFiles(directory="/app/static"), name="static"),
    Mount("/js", StaticFiles(directory="/app/js"), name="js"),
    WebSocketRoute("/ws", endpoint=websocket_endpoint),
]

app = Starlette(routes=routes)
