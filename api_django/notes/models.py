from django.db import models
from django.utils.timezone import now

from regions.models import Region

from users.models import User


class Note(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    expert = models.ForeignKey(User, limit_choices_to={'is_expert': True}, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=now)
    updated_date = models.DateTimeField(null=True, blank=True)
