from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

app = FastAPI()


@app.get("/")
async def root():
    return {"message: hello world"}

app.mount("/static", StaticFiles(directory="static"), name="static")
