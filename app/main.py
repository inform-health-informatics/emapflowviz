# Steve Harris
# 2019-11-22 : app to serve d3 viz in realtime for EMAP

# Imports: standard library
import asyncio  # e.g. asyncio.sleep preferred else the event loop blocks
import time
import json

# Imports: 3rd party
import psycopg2
import psycopg2.extras  #  for dictionary cursor
from starlette.applications import Starlette
from starlette.websockets import WebSocket
from starlette.templating import Jinja2Templates
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.config import Config

# Imports: local

# import settings
config = Config(".env")

DB_HOST=config('DB_HOST', cast=str, default="host.docker.internal")
DB_NAME=config('DB_NAME', cast=str)
DB_PORT=config('DB_PORT', cast=int)
# TODO use startlettes secret class: https://www.starlette.io/config/
DB_PASSWORD=config('DB_PASSWORD', cast=str)
DB_USER=config('DB_USER', cast=str)


# Define global variables

templates = Jinja2Templates(directory="/app/templates")

# POSTGRES CONNECTION
# TODO factor this out into a separate module
# setting up postgres stuff
# TODO move connection string details to ENV file
print(">>> Opening connection to PostgreSQL")
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
print(">>> Connection open, making cursor")
curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)



async def homepage(request):
    print(">>> homepage route called")
    return templates.TemplateResponse("index.html", {"request": request})

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # NOTE these variables are not seen if they are declared outside of the function
    TIME_THEN = 0
    TIME_NOW = 1  # uses the elapsed time column in the data
    TIME_MULT = 1/60  # multiplier to speed up time passing else marches in 60s steps
    TIME_ENDS = 24

    # await websocket.send_text()
    await websocket.send_json({"foo": DB_HOST})

    try:
        while TIME_NOW < TIME_ENDS:

            # Run query
            SQL = "SELECT visit_detail_id, visit_start_datetime, visit_end_datetime, care_site_id, person_id, visit_occurrence_id from omop_live.visit_detail where NOW() - visit_start_datetime < INTERVAL '{} HOURS'  order by visit_start_datetime desc; ".format(TIME_NOW)
            # need this while debugging to undo bad SQL queries
            # curs.execute('ROLLBACK')
            curs.execute(SQL)
            rows = curs.fetchall()

            # now update times for next iteration of the loop
            TIME_THEN = TIME_NOW
            TIME_NOW += 60 * TIME_MULT

            # convert to json
            events = [ 
                {i[0]: i[1] for i in row.items()}
                for row in rows
            ]
            # TODO: print etc. does not work inside an async function
            # print(events[0])

            await websocket.send_json( len(events))
            await websocket.send_json( 
                json.dumps(events, default=str)
            )
            # NOTE every second is equivalent to TIME_MULT seconds
            await asyncio.sleep(1)


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
    WebSocketRoute('/ws', endpoint=websocket_endpoint)
]

app = Starlette(routes=routes)
