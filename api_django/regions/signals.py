import logging
import os

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from shutil import rmtree

from regions.models import Region
from notes.models import Note
from regions.tasks import call_download_images_celery_task

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Region)
def create_note_after_attach_expert(sender, instance: Region, update_fields, **kwargs):
    logger.info("Signal: Create note after attach expert")
    if update_fields is not None:
        if ("expert_id" or "expert") in update_fields:  # Expert of region is updated
            if instance.expert_id is not None:  # Expert is attached
                note_text = f"کارشناس با شماره شناسایی {instance.expert_id} به ناحیه ای با شماره شناسایی {instance.id} متصل گردید."
                Note.objects.create(region=instance, user_id=instance.expert_id,
                                    text=note_text, user_role="E")


@receiver(post_save, sender=Region)
def download_images_after_region(sender, instance: Region, **kwargs):
    if kwargs["created"]:
        logger.info(f"Signal: Download image of {instance.__str__()}")
        task = call_download_images_celery_task(instance)

        instance.task_id = task.id
        instance.save(update_fields=["task_id"])


@receiver(post_delete, sender=Region)
def delete_images_after_deleting_the_region(sender, instance: Region, **kwargs):
    logger.info(f"Signal: Remove images of {instance.__str__()}")
    rmtree(instance.folder_path)
