from django.db.models.signals import post_save
from django.dispatch import receiver

from regions.models import Region
from users.models import User
from notes.models import Note


@receiver(post_save, sender=Region)
def create_note_after_attach_expert(sender, instance: Region, update_fields, **kwargs):
    if update_fields is not None:
        if ("expert_id" or "expert") in update_fields:  # Expert of region is updated
            if instance.expert_id is not None:  # Expert is not deleted
                note_text = f"کارشناس با شماره شناسایی {instance.expert_id} به ناحیه ای با شماره شناسایی {instance.id} متصل گردید."
                Note.objects.create(region=instance, expert_id=instance.expert_id, text=note_text)
