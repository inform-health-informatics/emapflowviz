from starlette.applications import Starlette

# from starlette.responses import HTMLResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket

# 2019-11-21t235549
# did not fix the 403 so let's drop for now
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
    Mount("/static", StaticFiles(directory="/app/static"), name="static"),
    Route('/ws', endpoint=websocket_endpoint)
]

origins = [
    # "http://localhost.tiangolo.com",
    # "https://localhost.tiangolo.com",
    "ws://localhost/ws",
    "ws://localhost",
    "ws://localhost:80",
    "ws://localhost:80/ws",
    "ws:localhost",
    "http:localhost"
]

middleware = [
    Middleware(CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"]),
    #  allow_origins=["ws://localhost:80"]),
    # Middleware(CORSMiddleware, allowed_hosts=["*"])
    # Middleware(CORSMiddleware, allowed_methods=["*"])
    # Middleware(CORSMiddleware, allowed_headers=["*"])
    # Middleware(TrustedHostMiddleware, allowed_hosts=["ws://localhost:80"])
    # Middleware(HTTPSRedirectMiddleware)
]

# allow CORS
# app.add_middleware(CORSMiddleware, allow_origins=['*'])
# app = Starlette(routes=routes, middleware=middleware)
app = Starlette(debug=True, routes=routes)
