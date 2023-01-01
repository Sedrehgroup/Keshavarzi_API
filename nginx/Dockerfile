FROM nginx:latest

RUN apt-get -y update &&\
    apt-get -y upgrade &&\
    apt-get -y install geoip-database ligeoip1

COPY ./nginx.conf /etc/nginx/conf.d/default.conf:ro
