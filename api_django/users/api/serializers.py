from django.contrib.auth.hashers import make_password
from rest_framework import exceptions, serializers, status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ("date_joined", "password", "groups", "user_permissions")
        model = User


def phone_number_validator(phone_number: str) -> (bool, str):
    if phone_number[:3] != "+98":
        return False, "Phone number should start with '+98'"
    elif len(phone_number) != 13:
        if len(phone_number) < 13:
            return False, "(short) Phone number is shorter than 13 character"
        else:
            return False, "(long) Phone number is longer than 13 character"
    else:
        return True, ""


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        is_valid, msg = phone_number_validator(attrs["phone_number"])
        if not is_valid:
            raise AuthenticationFailed({"phone_number": msg})

        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        request = self.context["request"]
        regions_qs = Region.objects \
            .filter(Q(user_id=request.user.id) | Q(expert_id=request.user.id))
        regions = RegionSerializer(regions_qs, many=True).data
        data.update({"regions": regions})
        return data


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("phone_number", "password")

    def validate(self, attrs):
        is_valid, msg = phone_number_validator(attrs["phone_number"])
        if not is_valid:
            raise ValidationError({"phone_number": msg}, status.HTTP_400_BAD_REQUEST)
        return attrs

    def create(self, validated_data):
        password = validated_data.get('password')
        if password is not None:
            validated_data['password'] = make_password(password)
        return super(CreateUserSerializer, self).create(validated_data)

    def to_representation(self, instance):
        token = RefreshToken.for_user(instance)
        data = {'refresh': str(token), "access": str(token.access_token)}
        return data
