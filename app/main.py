from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket

# TODO do you need this as awell as the starlette template lib?
from jinja2 import Template

templates = Jinja2Templates(directory='app/templates')

# @app.route("/")
async def homepage(request):
    return templates.TemplateResponse('index.html', {'request': request})


# @app.websocket_route("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    # process incoming messages
    while True:
        mesg = await websocket.receive_text()
        await websocket.send_text(mesg.replace("Client", "Server"))
    await websocket.close()


routes = [
    Route('/', endpoint=homepage),
    Mount('/static', StaticFiles(directory='/app/static'), name='static')
]

app = Starlette(routes=routes)