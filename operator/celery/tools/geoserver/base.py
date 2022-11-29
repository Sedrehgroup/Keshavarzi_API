from os import environ
from geoserver.catalog import Catalog

cat = Catalog(f'http://{environ["GEOSERVER_HOST"]}:{environ["GEOSERVER_PORT"]}/geoserver/rest/',
              username=environ["GEOSERVER_USER"],
              password=environ["GEOSERVER_PASS"])


def get_or_create_workspace(name):
    return cat.get_workspace(name) or cat.create_workspace(name)


def is_layer_exists(name):
    return cat.get_layer(name) is not None
