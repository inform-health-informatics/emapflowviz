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

# Imports: local
# None yet

# Define global variables
templates = Jinja2Templates(directory="/app/templates")

# TODO factor this out into a separate module
# setting up postgres stuff
print(">>> Opening connection to PostgreSQL")
conn = psycopg2.connect(
    host="host.docker.internal",
    database="mart_flow",
    user="steve",
    password=""
)
print(">>> Connection open, making cursor")
curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# TODO wrap this up in a while loop that pulls the latest patients every
# minute then updates the python data structure as needed and pushes them
# out every few seconds
SQL = "SELECT * FROM events LIMIT 5;"
print(">>> Running SQL query")
curs.execute(SQL)


async def homepage(request):
    print(">>> homepage route called")
    return templates.TemplateResponse("index.html", {"request": request})

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            point_data = curs.fetchone()
            point_data = {i[0]: i[1] for i in point_data.items()}
            point_data = json.dumps(point_data, default=str)
            # TODO: print etc. does not work inside an async function
            print(point_data)

            await websocket.send_json(point_data)
            mesg = "foo bar"
            await websocket.send_json(json.dumps(mesg))
            await asyncio.sleep(0.5)

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
