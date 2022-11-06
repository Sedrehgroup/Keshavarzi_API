from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from regions.models import Region
from regions.tests.factories import fake_polygon_geojson
from regions.utils import get_geojson_by_polygon, get_polygon_by_geojson
from users.api.serializers import UserSerializer
from users.models import User


@extend_schema_serializer(examples=[
    OpenApiExample('polygon', summary='geojson polygon', value={
        {
            "id": 0,
            "polygon": fake_polygon_geojson,
            "name": "lorem",
            "date_created": "2022-11-06",
            "date_last_download": "2022-11-06",
            "is_active": True,
            "user": 0,
            "expert": 0
        }
    })])
class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        exclude = ("dates", "task_id")


class BaseListRegionSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super(BaseListRegionSerializer, self).to_representation(instance)
        data["polygon"] = get_geojson_by_polygon(instance.polygon)
        return data


class ListRegionExpertSerializer(BaseListRegionSerializer):
    user = UserSerializer()

    class Meta:
        model = Region
        exclude = ("dates", "expert")


class ListRegionUserSerializer(BaseListRegionSerializer):
    expert = UserSerializer()

    class Meta:
        model = Region
        exclude = ("dates", "user")


class UpdateRegionExpertSerializer(serializers.ModelSerializer):
    expert_id = serializers.IntegerField(min_value=1, allow_null=True)

    class Meta:
        model = Region
        fields = ("expert_id",)

    def validate_expert_id(self, val):
        if val and not User.objects.filter(id=val, is_expert=True).exists():
            raise ValidationError({"Expert": "Expert user with given ID not found"})
        return val

    def update(self, instance, validated_data):
        expert_id = validated_data["expert_id"]
        if expert_id != 0:
            instance.expert_id = expert_id
            instance.save(update_fields=["expert_id"])
        else:
            instance.expert = None
            instance.save(update_fields=["expert"])
        return instance


class CreateRegionSerializer(serializers.ModelSerializer):
    def validate_polygon(self, value):
        return get_polygon_by_geojson(value)

    class Meta:
        model = Region
        exclude = ("date_created", "dates", "is_active", "expert", "user")
