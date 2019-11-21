from starlette.applications import Starlette
# from starlette.responses import HTMLResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket

templates = Jinja2Templates(directory='/app/templates')


async def homepage(request):
    return templates.TemplateResponse('index.html', {'request': request})


async def websocket_endpoint(websocket):
    await websocket.accept()
    # process incoming messages
    while True:
        mesg = await websocket.receive_text()
        await websocket.send_text(mesg.replace("Client", "Server"))
    await websocket.close()


routes = [
    Route('/', endpoint=homepage),
    Mount('/static', StaticFiles(directory='/app/static'), name='static'),
    Route('/ws', endpoint=websocket_endpoint)
]

app = Starlette(routes=routes)
