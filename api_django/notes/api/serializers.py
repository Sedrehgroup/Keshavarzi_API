from rest_framework import serializers
from rest_framework.exceptions import NotFound

from notes.models import Note
from regions.models import Region


class CreateNoteSerializer(serializers.ModelSerializer):
    region_id = serializers.IntegerField(min_value=1, write_only=True)

    def get_user_role(self):
        user = self.context["request"].user
        if user.is_expert:
            return "E"  # 'E' as Expert
        elif user.is_staff and user.is_superuser:
            return "A"  # 'A' as Admin
        else:
            return "U"  # 'U' as User

    def create(self, validated_data):
        # Get region object by passed region_id
        region_id = validated_data["region_id"]
        region = Region.objects.filter(id=region_id).only("id").first()
        if region is None:
            raise NotFound({"region not found": f"Region with given id({region_id}) not found"})

        # Get user_role by using the request
        validated_data["user_role"] = self.get_user_role()
        return Note.objects.create(region=region, **validated_data)

    class Meta:
        model = Note
        fields = ("text", "region_id")


class UpdateNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ("text",)
