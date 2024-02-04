# Dockerfile for projeckt
FROM python:3.9.13

WORKDIR /app

COPY . /app/

RUN pip install -r requirments.txt

CMD flask run --host 0.0.0.0