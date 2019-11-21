FROM tiangolo/uvicorn-gunicorn:python3.7

COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY ./app /app
