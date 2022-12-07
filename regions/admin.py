from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from regions.models import Region


@admin.register(Region)
class RegionAdmin(GISModelAdmin):
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 17,
            'default_lon': 51.395509,
            'default_lat': 35.707619,
        },
    }
