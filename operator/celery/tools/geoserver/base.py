from os import environ
from geoserver.catalog import Catalog

cat = Catalog(f'http://{environ["GEOSERVER_HOST"]}:{environ["GEOSERVER_PORT"]}/geoserver/rest/',
              username=environ["GEOSERVER_USER"],
              password=environ["GEOSERVER_PASS"])
