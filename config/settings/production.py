from config.settings.base import *

DEBUG = os.getenv("DEBUG", False)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', " ").split()
SECRET_KEY = os.environ.get("SECRET_KEY")
