import datetime
import logging
import os

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from shutil import rmtree

from regions.models import Region
from notes.models import Note
from regions.tasks import download_images
from regions.utils import get_geojson_by_polygon

logger = logging.getLogger(__name__)


def call_download_images_celery_task(instance: Region):
    logger.info(f"Signal: Download image of {instance.__str__()}")
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=30)
    geom = get_geojson_by_polygon(instance.polygon)
    task = download_images.delay(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'),
                                 geom, instance.user_id, instance.id, instance.dates)
    return task


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
        task = call_download_images_celery_task(instance)

        instance.task_id = task.id
        instance.save(update_fields=["task_id"])


@receiver(post_save, sender=Region)
def download_images_after_update_polygon(sender, instance: Region, update_fields, **kwargs):
    if not kwargs["created"] and update_fields is not None:
        if "polygon" in update_fields:  # Polygon of region is updated
            for path in instance.images_path:
                os.remove(path)

            task = call_download_images_celery_task(instance)
            instance.task_id = task.id
            instance.dates = None
            instance.save(update_fields=["dates", "task_id"])


@receiver(post_delete, sender=Region)
def delete_images_after_deleting_the_region(sender, instance: Region, **kwargs):
    logger.info(f"Signal: Remove images of {instance.__str__()}")
    rmtree(instance.main_folder_path)
