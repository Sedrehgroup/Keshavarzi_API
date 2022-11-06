from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError

from notes.models import Note
from regions.api.serializers import RegionSerializer
from regions.models import Region
from users.api.serializers import UserSerializer


class RetrieveNoteSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = self.context['request'].user
        if user.is_admin:
            user = obj.user
        return UserSerializer(user).data

    class Meta:
        model = Note
        fields = '__all__'


class CreateNoteSerializer(serializers.ModelSerializer):
    region_id = serializers.IntegerField(min_value=1, write_only=True)

    def get_region_by_id(self, attrs):
        user = self.context['request'].user
        qs = Region.objects.filter(id=attrs['region_id'])
        if not user.is_admin:
            qs = qs.filter(Q(expert_id=user.id) | Q(user_id=user.id)).only("id")
        region = qs.order_by().first()  # Order-by empty value = dont order the qs

        if region is None:
            if Region.objects.filter(id=attrs['region_id']).order_by().exists():  # Order-by empty value = dont order the qs
                raise ValidationError({"Region validation": "You are not user of expert of given region."})
            raise NotFound({"Region not found": "Region with given ID is not exists."})
        return region

    def validate(self, attrs):
        attrs['region'] = self.get_region_by_id(attrs)
        return attrs

    def get_user_role(self):
        user = self.context["request"].user
        if user.is_expert:
            return "E"  # 'E' as Expert
        elif user.is_staff and user.is_superuser:
            return "A"  # 'A' as Admin
        else:
            return "U"  # 'U' as User

    def create(self, validated_data):
        # Get user_role by using the request
        validated_data["user_role"] = self.get_user_role()
        return Note.objects.create(**validated_data)

    class Meta:
        model = Note
        fields = ("text", "region_id")


class UpdateNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ("text",)


class ListUserNotesSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = Note
        exclude = ("user",)


class ListNotesByRegionSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Note
        exclude = ("region",)
