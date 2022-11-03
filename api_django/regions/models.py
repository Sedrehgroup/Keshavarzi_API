from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now

User = get_user_model()


class Region(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user",
                             limit_choices_to={"is_expert": False, "is_superuser": False})
    expert = models.ForeignKey(User, on_delete=models.CASCADE,
                               null=True, blank=True, related_name="expert",
                               limit_choices_to={"is_expert": True, "is_superuser": False})
    polygon = models.PolygonField()
    name = models.CharField(max_length=20, help_text="Maximum length for this field is 20 character")
    date_created = models.DateField(default=now)
    date_last_download = models.DateField(default=now)
    is_active = models.BooleanField(default=True)  # ToDo: Is necessary or not?
    dates = models.TextField(null=True, blank=True)
    task_id = models.CharField(null=True, blank=True, max_length=44)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.expert_id is not None and self.expert_id < 1:
            raise ValidationError({"Invalid expert id": "Expert id should be None or greater that 1"})
        super(Region, self).save(*args, **kwargs)

    @property
    def dates_as_list(self):
        dates_list = self.dates.split("\n")  # ['2021-01-02', '']
        dates_list.pop()  # Pop the last and empty value
        return dates_list

    @property
    def folder_path(self):
        return f"{settings.BASE_DIR}/{'/'.join(['media', 'images', f'user-{str(self.user_id)}', f'region-{str(self.id)}'])}"

    @property
    def images_path(self):
        folder_path = self.folder_path
        dates = self.dates_as_list
        result = []
        for date in dates:
            result.append(f"{folder_path}/{date}.tif")
        return result

    def get_file_path_by_date_and_folder_path(self, date, folder_path):
        return f"{folder_path}/{date}.tif"
