FROM python:3.8
LABEL MAINTAINER="Sedreh"

ENV PYTHONUNBUFFERD=TRUE

RUN apt-get -y update
RUN apt-get -y upgrade

RUN apt-get -y install binutils libproj-dev gdal-bin
RUN apt-get -y install postgresql
RUN apt-get -y install cron

WORKDIR /api_django

COPY ../requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python manage.py shell < utils/geoserver/startup.py
COPY .. .

