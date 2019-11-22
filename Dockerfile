# Dockerfile adapted from https://github.com/tiangolo/uvicorn-gunicorn-starlette-docker
# but I use requirements.txt rather than only install starlette
FROM tiangolo/uvicorn-gunicorn:python3.7

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ /app/
