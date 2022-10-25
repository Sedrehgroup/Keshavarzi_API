# Generated by Django 4.0.8 on 2022-10-25 14:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('regions', '0005_remove_region_user_region_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='region',
            name='users',
        ),
        migrations.AddField(
            model_name='region',
            name='expert',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_expert': True, 'is_superuser': False}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expert', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='region',
            name='user',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_expert': False, 'is_superuser': False}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
    ]
