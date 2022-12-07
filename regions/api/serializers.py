import os

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from regions.models import Region
from regions.utils import call_download_images_celery_task
from regions.utils import get_geojson_by_polygon, get_polygon_by_geojson
from users.api.serializers import UserSerializer
from users.models import User


class GeometrySerializer(serializers.Serializer):
    type = serializers.CharField()
    coordinates = serializers.ListField(
        child=serializers.ListField(
            child=serializers.ListField(
                child=serializers.FloatField())))


class FeatureSerializer(serializers.Serializer):
    type = serializers.CharField()
    property = serializers.DictField(allow_null=True, allow_empty=True, required=False)
    geometry = GeometrySerializer()


class PolygonSerializer(serializers.Serializer):
    type = serializers.CharField()
    features = FeatureSerializer(many=True)

    # def validate(self, attrs):
    #     print(attrs)
    #     return get_polygon_by_geojson(attrs)

    def to_representation(self, instance):
        return get_geojson_by_polygon(instance)


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


class UpdateRegionUserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(min_value=1, allow_null=False)

    def validate_user_id(self, val):
        if val and not User.objects.filter(id=val, is_expert=False,
                                           is_superuser=False, is_staff=False).exists():
            raise ValidationError({"Expert": "Expert user with given ID not found"})
        return val

    class Meta:
        model = Region
        fields = ("user_id",)


class CreateRegionSerializer(serializers.ModelSerializer):
    polygon = PolygonSerializer()

    def validate_polygon(self, value):
        return get_polygon_by_geojson(value)

    class Meta:
        model = Region
        fields = ("id", "name", "polygon")
        read_only_fields = ("id",)


class RetrieveUpdateRegionSerializer(serializers.ModelSerializer):
    dates = serializers.SerializerMethodField(read_only=True, allow_null=True)
    polygon = PolygonSerializer()

    def get_dates(self, obj: Region):
        if obj.dates is not None:
            return obj.dates_as_list
        return None

    def update(self, instance, validated_data):
        old_polygon = validated_data.get("polygon")
        if old_polygon and instance.polygon != old_polygon:
            # Polygon of region is updated
            for path in instance.images_path:
                os.remove(path)

            task = call_download_images_celery_task(instance)
            instance.task_id = task.id
            instance.dates = None

        return super(RetrieveUpdateRegionSerializer, self).update(instance, validated_data)

    def validate_polygon(self, value):
        return get_polygon_by_geojson(value)

    #
    # def to_representation(self, instance):
    #     ret = super(RetrieveUpdateRegionSerializer, self).to_representation(instance)
    #     ret["polygon"] = get_geojson_by_polygon(instance.polygon)
    #     return ret

    class Meta:
        model = Region
        fields = ("name", "polygon", "dates", "is_active")
