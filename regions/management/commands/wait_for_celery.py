from time import sleep
from django.core.management import BaseCommand

from config import celery_app


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Waiting for celery...')
        workers = None
        while not workers:
            workers = celery_app.control.inspect().stats()
            if not workers:
                self.stdout.write('Celery is unavailable, waiting 1 second...')
                sleep(1)
        self.stdout.write(self.style.SUCCESS('Celery is available!'))
