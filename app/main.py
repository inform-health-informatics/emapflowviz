from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

app = FastAPI()


@app.get("/")
async def root():
    return {"message: hello world"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


app.mount("/static", StaticFiles(directory="static"), name="static")
