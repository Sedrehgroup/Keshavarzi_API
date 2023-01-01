FROM nginx:latest

RUN apt-get -y update &&\
    apt-get -y upgrade &&\
    apt-get -y install geoip-database libgeoip1

COPY ./error_pages /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/nginx.conf:ro
