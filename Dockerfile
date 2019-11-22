# Dockerfile adapted from https://github.com/tiangolo/uvicorn-gunicorn-starlette-docker
# but I use requirements.txt rather than only install starlette
FROM tiangolo/uvicorn-gunicorn:python3.7

# - [ ] @NOTE: (2019-11-22) fix for problems with libssl in postgres/python 
RUN apt-get update && apt-get install libssl-dev libffi-dev

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ /app/
