# syntax=docker/dockerfile:1

FROM python:3.9.15-slim-bullseye

WORKDIR /dps_svc_app

COPY ./requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY ./rest_api_server/*.py ./

EXPOSE 5003

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5003"]