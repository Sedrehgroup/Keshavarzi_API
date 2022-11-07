from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from regions.models import Region
from regions.utils import get_geojson_by_polygon, get_polygon_by_geojson
from users.api.serializers import UserSerializer
from users.models import User


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
    def validate_polygon(self, value):
        return get_polygon_by_geojson(value)

    class Meta:
        model = Region
        fields = ("polygon", "name")


class RetrieveUpdateRegionSerializer(serializers.ModelSerializer):
    dates = serializers.SerializerMethodField(read_only=True)

    def get_dates(self, obj: Region):
        return obj.dates_as_list

    def validate_polygon(self, value):
        return get_polygon_by_geojson(value)

    class Meta:
        model = Region
        fields = ("name", "polygon", "is_active")
