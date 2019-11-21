# # FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
# FROM tiangolo/uvicorn-gunicorn-starlette:python3.7

# COPY ./app /app

# # - [ ] @NOTE: (2019-11-21) had to manually install aiofile pip module to make this work
# WORKDIR /app
# RUN pip install -r requirements.txt
FROM tiangolo/uvicorn-gunicorn:python3.7

COPY ./app /app
# WORKDIR /app
# RUN pip install starlette
RUN pip install -r requirements.txt
