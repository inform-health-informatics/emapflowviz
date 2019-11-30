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

# Initial data load
SQL = sql.SQL(cfg.SQL_STRING.format(cfg.TIME_ZERO, cfg.TIME_NOW))
df_pts_initial = pd.read_sql(SQL, conn)
# df_pts_initial = pd.DataFrame({"foo": [0,1], "bar":[2,3]})
df_pts_initial = utils.visits_lengthen_and_label(df_pts_initial, cfg.STAR_OR_OMOP)
df_pts_initial = utils.filter_visit_detail_long(df_pts_initial, column='ward', inclusions=['ED'])
df_pts_initial['group'] = df_pts_initial['slug_room']
df_pts_initial.to_csv('static/data/pts_initial.csv')

async def homepage(request):
    print(">>> homepage route called")
    # TODO assemble and send initial data set to the page

    return templates.TemplateResponse(
        "index.html", {
        "request": request,
        "WEBSOCKET_SERVER": cfg.WEBSOCKET_SERVER} 
        # "DF_PTS_INITIAL": df_pts_initial.to_json(orient="records")}
        # "DF_PTS_INITIAL": df_pts_initial.to_csv()}
    )


async def websocket_endpoint(websocket: WebSocket):
    """
    Handles the websocket connection
    """
    # pause to allow initil data load
    await asyncio.sleep(15)

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
    # TODO place logic here for initial load before opening the loop
    # e.g.
    # await websocket.send_json(INITIAL_PATIENT_POSITION_ARRAY)
    # then allow some time to lapse for the initial load before moving on in real time
    # send a flag to the page that you're about to switch the realtime load
    # await websocket.send_json({"REALTIME_LOOP_OPEN": true})

    try:
        while TIME_NOW < TIME_ENDS:

            # now update times for next iteration of the loop
            # TODO adjust the time multiplier by a multiplier so that it asymptotes to realtime
            TIME_THEN = TIME_NOW
            TIME_NOW += TIME_MULT * TIME_DELTA

            # Run query
            
            SQL = sql.SQL(SQL_STRING.format(TIME_THEN, TIME_NOW))
            df = pd.read_sql(SQL, conn)

            # TODO need some logic to handle empty or unhelpful queries
            try:
                df = utils.visits_lengthen_and_label(df, STAR_OR_OMOP)
            except KeyError as e:
                # KeyError raised when LOCATION not in index 
                print(f"!!!: Error on database query: {e}")
                print("!!!: Skipping forward one TIME_DELTA")
                continue

            df = utils.filter_visit_detail_long(df, column='ward', inclusions=['ED'])
            if df.shape[0] == 0:
                print(">>>: No ward movements: skipping forward one TIME_DELTA")
                continue

            # create a group indicator (from room slug)
            df['group'] = df['slug_room']

            await websocket.send_json({
                "n_events": df.shape[0],
                "time_then": str(TIME_THEN),
                "time_now": str(TIME_NOW)
            } )
            for index, row in df.iterrows():
                event = row.to_json()
                await websocket.send_json(event)
                await asyncio.sleep(SIM_SPEED_SECS/5)
            await asyncio.sleep(SIM_SPEED_SECS)

    except AttributeError as err:
        # try to capture error and end gracefully when there is no more data
        print("!!! No more data?", err)
    finally:
        # print("Closing connection to PostgreSQL")
        # curs.close()
        # conn.close()
        # await websocket.close()
        pass


routes = [
    Route("/", endpoint=homepage),
    Mount("/static", StaticFiles(directory="/app/static"), name="static"),
    Mount("/js", StaticFiles(directory="/app/js"), name="js"),
    WebSocketRoute("/ws", endpoint=websocket_endpoint),
]

app = Starlette(routes=routes)
