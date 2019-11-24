# Dockerfile adapted from https://github.com/tiangolo/uvicorn-gunicorn-starlette-docker
# but I use requirements.txt rather than only install starlette
FROM tiangolo/uvicorn-gunicorn:python3.7

# fix for problems with libssl in postgres/python 
# then adds acl for permissions issues below
RUN apt-get update && apt-get install libssl-dev libffi-dev acl

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY app/ /app/
RUN chown -R 1015:994 /app && chmod -R g+rws,o+rws /app && setfacl -d -m g::rwx /app
EXPOSE 80
EXPOSE 5901

