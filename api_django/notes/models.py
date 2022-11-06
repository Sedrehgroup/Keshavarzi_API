from django.db import models
from django.utils.timezone import now

from regions.models import Region

from users.models import User

USER_ROLE_CHOICES = (
    ("U", "User"),
    ("E", "Expert"),
    ("A", "Admin")
)


class Note(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_role = models.CharField(max_length=1, choices=USER_ROLE_CHOICES)
    text = models.TextField()
    created_date = models.DateTimeField(default=now)
    updated_date = models.DateTimeField(auto_now=True)  # Note: Not working with note.update()

    def save(self, *args, **kwargs):
        if self.user_role is None:
            if self.user.is_expert:
                self.user_role = "E"
            elif self.user.is_admin:
                self.user_role = "A"
            else:
                self.user_role = "U"
        super(Note, self).save(*args, **kwargs)
