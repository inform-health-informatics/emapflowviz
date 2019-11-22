from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket
from starlette.templating import Jinja2Templates
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
# from jinja2 import Template
# import uvicorn

templates = Jinja2Templates(directory="/app/templates")


# @app.route('/')
async def homepage(request):
    # return HTMLResponse(Template(template).render())
    return templates.TemplateResponse("index.html", {"request": request})

routes = [
    Route("/", endpoint=homepage),
    Mount("/static", StaticFiles(directory="/app/static"), name="static")
    # Route('/ws', endpoint=websocket_endpoint)
]

app = Starlette(routes=routes)


@app.websocket_route('/ws')
async def websocket_endpoint(websocket):
    await websocket.accept()
    # Process incoming messages
    while True:
        mesg = await websocket.receive_text()
        await websocket.send_text(mesg.replace("Client", "Server"))
    await websocket.close()


# if __name__ == '__main__':
#     uvicorn.run(app, host='0.0.0.0', port=8000)