FROM python:3.11.1
LABEL MAINTAINER="Sedreh"

ENV PYTHONUNBUFFERD=TRUE

RUN apt-get -y update &&\
    apt-get -y upgrade &&\
    apt-get -y install binutils libproj-dev gdal-bin figlet cron

WORKDIR /api_django

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip &&\
    pip install -r requirements.txt

COPY ./.bashrc /root/.bashrc
COPY . .

CMD ["sh", "entrypoint.sh"]
