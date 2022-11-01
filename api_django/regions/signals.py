import datetime
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from regions.models import Region
from notes.models import Note
from regions.tasks import download_images
from regions.utils import get_geojson_by_polygon

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
        logger.info("Signal: Download image after region")
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=30)
        geom = get_geojson_by_polygon(instance.polygon)
        task = download_images.delay(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'),
                                     geom, instance.user_id, instance.id, instance.dates)
        instance.task_id = task.id
        instance.save(update_fields=["task_id"])
