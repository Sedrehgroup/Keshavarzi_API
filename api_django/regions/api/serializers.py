from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from regions.models import Region
from users.api.serializers import UserSerializer
from users.models import User


class ListRegionExpertSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Region
        exclude = ("dates", "expert")


class ListRegionUserSerializer(serializers.ModelSerializer):
    expert = UserSerializer()

    class Meta:
        model = Region
        exclude = ("dates", "user")


class UpdateRegionExpertSerializer(serializers.ModelSerializer):
    expert_id = serializers.IntegerField(min_value=0)

    class Meta:
        model = Region
        fields = ("expert_id",)

    def validate_expert_id(self, val):
        if val != 0 and not User.objects.filter(id=val, is_expert=True).exists():
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
