from config.settings.local import *

DATABASES["default"]["TEST"] = {"NAME": DATABASES["default"]["NAME"]}
