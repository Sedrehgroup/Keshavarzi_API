# Generated by Django 4.0.8 on 2022-10-22 09:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('regions', '0002_remove_region_images_date_region_dates'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='expert',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_expert': True, 'is_superuser': False}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expert', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='region',
            name='date_created',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='region',
            name='user',
            field=models.ForeignKey(limit_choices_to={'is_expert': False, 'is_superuser': False}, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
    ]
