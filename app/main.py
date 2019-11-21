from starlette.applications import Starlette

# from starlette.responses import HTMLResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware


templates = Jinja2Templates(directory="/app/templates")


async def homepage(request):
    return templates.TemplateResponse("index.html", {"request": request})


async def websocket_endpoint(websocket):
    await websocket.accept()
    # process incoming messages
    while True:
        mesg = await websocket.receive_text()
        await websocket.send_text(mesg.replace("Client", "Server"))
    await websocket.close()


routes = [
    Route("/", endpoint=homepage),
    Mount("/static", StaticFiles(directory="/app/static"), name="static")
    # Route('/ws', endpoint=websocket_endpoint)
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"]),
    # Middleware(CORSMiddleware, allowed_hosts=["*"])
    # Middleware(CORSMiddleware, allowed_methods=["*"])
    # Middleware(CORSMiddleware, allowed_headers=["*"])
    Middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    # Middleware(HTTPSRedirectMiddleware)
]

# allow CORS
# app.add_middleware(CORSMiddleware, allow_origins=['*'])
app = Starlette(routes=routes, middleware=middleware)
