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
from starlette.config import Config

# Imports: local

# import settings
config = Config(".env")

DB_HOST = config("DB_HOST", cast=str, default="host.docker.internal")
DB_NAME = config("DB_NAME", cast=str)
DB_PORT = config("DB_PORT", cast=int)
# TODO use startlettes secret class: https://www.starlette.io/config/
DB_PASSWORD = config("DB_PASSWORD", cast=str)
DB_USER = config("DB_USER", cast=str)
WEBSOCKET_SERVER = config("WEBSOCKET_SERVER", cast=str)


# Define global variables

templates = Jinja2Templates(directory="/app/templates")

# POSTGRES CONNECTION
# TODO factor this out into a separate module
# setting up postgres stuff
# TODO move connection string details to ENV file
print(">>> Opening connection to PostgreSQL")
conn = psycopg2.connect(
    host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
)
print(">>> Connection open, making cursor")
curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


async def homepage(request):
    print(">>> homepage route called")
    return templates.TemplateResponse(
        "index.html", {"request": request, "WEBSOCKET_SERVER": WEBSOCKET_SERVER}
    )


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # NOTE these variables are not seen if they are declared outside of the function
    SIM_SPEED_SECS = 2
    TIME_START = datetime.datetime(2019, 11, 23, 17)
    TIME_ENDS = datetime.datetime(2019, 11, 25, 17)
    TIME_NOW = TIME_START
    TIME_DELTA = datetime.timedelta(hours=1)
    TIME_MULT = 1

    # await websocket.send_text()
    await websocket.send_json({"foo": DB_HOST})

    try:
        while TIME_NOW < TIME_ENDS:

            # now update times for next iteration of the loop
            # TODO adjust the time multiplier by a multiplier so that it asymptotes to realtime
            TIME_THEN = TIME_NOW
            TIME_NOW += TIME_MULT * TIME_DELTA

            # Run query
            # SQL = "SELECT visit_detail_id, visit_start_datetime, visit_end_datetime, care_site_id, person_id, visit_occurrence_id from omop_live.visit_detail where NOW() - visit_start_datetime < INTERVAL '{} HOURS'  order by visit_start_datetime desc; ".format(TIME_NOW)
            SQL = sql.SQL("""
                SELECT measurement_id, measurement_datetime, measurement_concept_id, value_as_number
                FROM measurement
                WHERE 
                    measurement_datetime > '{}'
                    AND
                    measurement_datetime <= '{}'
                ORDER BY measurement_datetime;
                """.format( TIME_THEN, TIME_NOW))
            curs.execute(SQL)
            rows = curs.fetchall()

            # convert to json
            events = [{i[0]: i[1] for i in row.items()} for row in rows]
            # TODO: print etc. does not work inside an async function
            # print(events[0])

            await websocket.send_json(len(events))
            for event in events:
                await websocket.send_json(json.dumps(event, default=str))
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
