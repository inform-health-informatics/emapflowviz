# import time
# import datetime
# import random
# from random import randint
# from datetime import timedelta

import json

# import psycopg2
# import psycopg2.extras # for dictionary cursor

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket
from starlette.templating import Jinja2Templates
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

templates = Jinja2Templates(directory="/app/templates")


# @app.route('/')
async def homepage(request):
    return templates.TemplateResponse("index.html", {"request": request})


routes = [
    Route("/", endpoint=homepage),
    Mount("/static", StaticFiles(directory="/app/static"), name="static"),
    Mount("/js", StaticFiles(directory="/app/js"), name="js")
    # TODO see below: enabling this route means the app fails
    # Route('/ws', endpoint=websocket_endpoint)
]

app = Starlette(routes=routes)


# TODO decorating the route is OK; but including in the routes array produces a 403 error
@app.websocket_route("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    # Process incoming messages
    while True:
        mesg = await websocket.receive_text()
        # await websocket.send_text(mesg.replace("Client", "Server"))
        point_data = {"foo": "bar"}
        point_data = json.dumps(point_data,  default=str)
        await websocket.send_json(point_data)
    await websocket.close()
