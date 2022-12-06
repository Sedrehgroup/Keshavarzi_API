import logging

from django.core.management.base import BaseCommand, CommandError
from os import environ
from geoserver.catalog import Catalog

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run startup commands for Geoserver'

    def handle(self, *args, **options):
        logger.info("Start: Geoserver startup")
        cat = Catalog(f'http://{environ["GEOSERVER_HOST"]}:{environ["GEOSERVER_PORT"]}/geoserver/rest/',
                      username=environ["GEOSERVER_USER"],
                      password=environ["GEOSERVER_PASS"])

        default_workspace_name = "DefaultWorkspace"
        if not cat.get_workspace(default_workspace_name):
            cat.create_workspace(default_workspace_name)
        cat.set_default_workspace(default_workspace_name)
        logger.info("End: Geoserver startup")
