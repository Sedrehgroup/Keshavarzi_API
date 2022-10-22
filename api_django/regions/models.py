from django.contrib.auth import get_user_model
from django.contrib.gis.db import models

User = get_user_model()


class Region(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    polygon = models.PolygonField()
    name = models.CharField(max_length=20, help_text="Maximum length for this field is 20 character")
    date_created = models.DateField()
    is_active = models.BooleanField(default=True)  # ToDo: Is necessary or not?
    dates = models.TextField(null=True, blank=True)
