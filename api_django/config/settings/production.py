from config.settings.base import *

DEBUG = bool(int(os.getenv("DEBUG", 0)))
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', " ").split()
SECRET_KEY = os.environ.get("SECRET_KEY")
