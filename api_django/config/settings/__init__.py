setting_env = 'LOCAL'  # Choices are: LOCAL, PRODUCTION

# Colors
ENDC = '\033[0m'
WARNING = '\033[93m'
OKGREEN = '\033[92m'
OKCYAN = '\033[96m'
FAIL = '\033[91m'

if setting_env == 'PRODUCTION':
    from config.settings.production import *
    print(OKCYAN + "-- Production setting imported --" + ENDC)
elif setting_env == 'LOCAL':
    from config.settings.local import *
    print(WARNING + "-- Local setting imported --" + ENDC)

else:
    raise Exception(OKCYAN + '-- Invalid setting_env --' + ENDC)

if DEBUG is True:
    mode = FAIL + "ON" + ENDC
else:
    mode = OKCYAN + "OFF" + ENDC

print(OKCYAN + "-- Debug mode is: " + mode + OKCYAN + " --" + ENDC)

from config.celery import app as celery_app

__all__ = ("celery_app",)
