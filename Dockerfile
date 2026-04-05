FROM python:3.12.10-slim

RUN apt update -y

WORKDIR /app

RUN pip install uv

COPY . /app
RUN python3 -m uv pip install -e .