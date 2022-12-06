# syntax=docker/dockerfile:1

FROM python:3.9.15-slim-bullseye

WORKDIR /dps_shared

COPY ./requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY ./dps_shared ./dps_shared
COPY ./setup.py ./setup.py

RUN pip install .
RUN pip3 list