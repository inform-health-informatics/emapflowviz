# import time
# import datetime
# import random
# from random import randint
# from datetime import timedelta

import json

import psycopg2
import psycopg2.extras  #  for dictionary cursor

from starlette.applications import Starlette
# from starlette.responses import HTMLResponse
# from starlette.websockets import WebSocket
from starlette.templating import Jinja2Templates
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

templates = Jinja2Templates(directory="/app/templates")

# TODO factor this out into a separate module
# setting up postgres stuff
print("Opening connection to PostgreSQL")
conn = psycopg2.connect(
    host="host.docker.internal",
    database="mart_flow",
    user="steve",
    password=""
)
curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# TODO wrap this up in a while loop that pulls the latest patients every
# minute then updates the python data structure as needed and pushes them
# out every few seconds
SQL = "SELECT * FROM pts;"
curs.execute(SQL)


async def homepage(request):
    return templates.TemplateResponse("index.html", {"request": request})

async def websocket_endpoint(websocket):
    await websocket.accept()
    # Process incoming messages
    while True:
        mesg = await websocket.receive_text()
        # await websocket.send_text(mesg.replace("Client", "Server"))

        # bar = random.randrange(10, 100)
        # point_data = {"foo": bar}
        # point_data = json.dumps(point_data,  default=str)

        point_data = curs.fetchone()
        point_data = {i[0]: i[1] for i in point_data.items()}
        point_data = json.dumps(point_data, default=str)
        print(point_data)

        await websocket.send_json(point_data)
    await websocket.close()

    print("Closing connection to PostgreSQL")
    curs.close()
    conn.close()

routes = [
    Route("/", endpoint=homepage),
    Mount("/static", StaticFiles(directory="/app/static"), name="static"),
    Mount("/js", StaticFiles(directory="/app/js"), name="js"),
    WebSocketRoute('/ws', endpoint=websocket_endpoint)
]

app = Starlette(routes=routes)

