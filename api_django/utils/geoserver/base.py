from django.conf import settings
from geoserver.catalog import Catalog

cat = Catalog(f"http://{settings.GEOSERVER['HOST']}:{settings.GEOSERVER['PORT']}/geoserver/rest/",
              username=settings.GEOSERVER['USERNAME'],
              password=settings.GEOSERVER['PASSWORD'])


def get_or_create_workspace(name):
    return cat.get_workspace(name) or cat.create_workspace(name)


def is_layer_exists(name):
    return cat.get_layer(name) is not None
