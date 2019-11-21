# from starlette.applications import Starlette
# from starlette.responses import JSONResponse

# app = Starlette()


# @app.route("/")
# async def homepage(request):
#     return JSONResponse({"message": "Hello World!"})

# from fastapi import FastAPI

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket
from jinja2 import Template

from starlette.staticfiles import StaticFiles

# import uvicorn

template = """\
<!DOCTYPE HTML>
<html>
<head>
    <script type = "text/javascript">
        function runWebsockets() {
            if ("WebSocket" in window) {
                var ws = new WebSocket("ws://localhost:80/ws");
                ws.onopen = function() {
                    console.log("Sending websocket data");
                    ws.send("Hello From Client");
                };
                ws.onmessage = function(e) {
                    alert(e.data);
                };
                ws.onclose = function() {
                    console.log("Closing websocket connection");
                };
            } else {
                alert("WS not supported, sorry!");
            }
        }
    </script>
</head>
<body>
    <p>hello from starlette template</p>
    <body><a href="javascript:runWebsockets()">Say Hello From Client</a></body>
</body>
</html>
"""

# app = FastAPI()
app = Starlette()


@app.route("/")
async def homepage(request):
    return HTMLResponse(Template(template).render())


# @app.get("/hello")
# async def hello():
#     return {"message: hello world"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str = None):
#     return {"item_id": item_id, "q": q}

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.websocket_route("/ws")
async def websocket_endpoint(websocket):
    await websocket.accept()
    # process incoming messages
    while True:
        mesg = await websocket.receive_text()
        await websocket.send_text(mesg.replace("Client", "Server"))
    await websocket.close()


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8002)
