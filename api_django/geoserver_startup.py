from os import environ
from geoserver.catalog import Catalog

cat = Catalog(f'http://{environ["GEOSERVER_HOST"]}:{environ["GEOSERVER_PORT"]}/geoserver/rest/',
              username=environ["GEOSERVER_USER"],
              password=environ["GEOSERVER_PASS"])

default_workspace_name = "DefaultWorkspace"
if not cat.get_workspace(default_workspace_name):
    cat.create_workspace(default_workspace_name)
cat.set_default_workspace(default_workspace_name)
