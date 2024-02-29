# Dockerfile for projeckt
FROM python:3.9.13

WORKDIR /app

COPY . /app/

RUN pip install -r requirments.txt

RUN flask db init

RUN flask db migrate -m "First"

RUN flask db upgarde

CMD flask run --host=0.0.0.0 --port=80
