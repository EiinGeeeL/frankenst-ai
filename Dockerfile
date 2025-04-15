FROM python:3.12.5-slim

RUN apt update -y
WORKDIR /app

COPY . /app
RUN python3 -m pip install -e .