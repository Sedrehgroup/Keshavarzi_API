from django.core.management.base import BaseCommand
from os import environ
from geoserver.catalog import Catalog


class Command(BaseCommand):
    help = 'Run startup commands for Geoserver'

    def handle(self, *args, **options):
        self.stdout.write("START: geoserver startup")
        cat = Catalog(f'http://{environ["GEOSERVER_HOST"]}:{environ["GEOSERVER_PORT"]}/geoserver/rest/',
                      username=environ["GEOSERVER_USER"],
                      password=environ["GEOSERVER_PASS"])

        default_workspace_name = environ["GEOSERVER_DEFAULT_WORKSPACE_NAME"]
        if not cat.get_workspace(default_workspace_name):
            cat.create_workspace(default_workspace_name)
        cat.set_default_workspace(default_workspace_name)
        self.stdout.write("END: geoserver startup")
