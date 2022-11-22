FROM python:3.8
LABEL MAINTAINER="Sedreh"

ENV PYTHONUNBUFFERD=TRUE

RUN apt-get -y update
RUN apt-get -y upgrade

COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .
