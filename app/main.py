from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket
from starlette.templating import Jinja2Templates
from jinja2 import Template

from starlette.staticfiles import StaticFiles

templates = Jinja2Templates(directory='app/templates')

app = Starlette()


@app.route("/")
async def homepage(request):
    return templates.TemplateResponse('index.html', {'request': request})

# routes = [
#     Route('/', endpoint=homepage),
#     Mount('/static', StaticFiles(directory='static'), name='static')
# ]

# @app.route("/")
# async def homepage(request):
#     return HTMLResponse(Template(template).render())


app.mount("/app/static", StaticFiles(directory="app/static"), name="static")


@app.websocket_route("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    # process incoming messages
    while True:
        mesg = await websocket.receive_text()
        await websocket.send_text(mesg.replace("Client", "Server"))
    await websocket.close()
