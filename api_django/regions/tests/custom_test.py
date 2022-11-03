# ToDo
import os
from time import sleep

# Problem: Celery doesnt have access to django directory
from celery.result import AsyncResult

from regions.models import Region
from regions.tests.factories import fake_polygon
from users.tests.factories import UserFactory


def test_create_method_is_calling_download_image_signal():
    region = Region.objects.create(user_id=UserFactory.create().id, polygon=fake_polygon, name="test polygon")

    assert region.task_id is not None


def test_create_is_update_dates_field():
    region = Region.objects.create(user_id=UserFactory.create().id, polygon=fake_polygon, name="test update dates")
    task_id = region.task_id
    res = AsyncResult(task_id)

    while res.state == "PENDING":
        sleep(5)

    assert res.state != "FAILURE", res.result
    assert res.state == "SUCCESS"

    region.refresh_from_db()
    assert region.dates is not None
    assert len(region.dates.split("\n")) > 1


def test_create_is_save_images_in_directory():
    region = Region.objects.create(user_id=UserFactory.create().id, polygon=fake_polygon, name="test update dates")
    task_id = region.task_id
    res = AsyncResult(task_id)

    while res.state == "PENDING":
        sleep(5)

    assert res.state != "FAILURE", res.result
    assert res.state == "SUCCESS"

    region.refresh_from_db()
    assert region.dates is not None
    for date in region.dates_as_list:
        file_path = os.path.join("media", "images", f"user-{region.user_id}", f"region-{region.id}", f"{date}.tif")
        assert os.path.isfile(file_path)


def test_delete_images_after_delete_region():
    """ Test that images of the region will be deleted after the region is deleted. """
    user = UserFactory.create()
    region = Region.objects.create(user_id=user.id, polygon=fake_polygon, name="test polygon")

    res = AsyncResult(region.task_id)

    while res.state == "PENDING":
        sleep(5)
    assert res.state != "FAILURE", res.result
    assert res.state == "SUCCESS"
    region.refresh_from_db()

    region.delete()

    for image_path in region.images_path:
        assert image_path


test_create_is_save_images_in_directory()
print("test_create_is_save_images_in_directory")

test_create_method_is_calling_download_image_signal()
print("test_create_method_is_calling_download_image_signal")

test_create_is_update_dates_field()
print("test_create_is_update_dates_field")

test_delete_images_after_delete_region()
print("test_delete_images_after_delete_region")
