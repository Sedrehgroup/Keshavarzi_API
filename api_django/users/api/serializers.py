from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User

examples = [
    OpenApiExample(
        name='Valid example', request_only=False, response_only=True,
        summary="Return access and refresh token", value={'refresh': "Token", 'access': "Token"},
    ), OpenApiExample(
        name="Valid example", request_only=True, response_only=False,
        summary="✅13 character phone number length with raw password.", value={"phone_number": "+989032567181", "password": "raw password"}
    ), OpenApiExample(
        name="Invalid example 1", request_only=True, response_only=False,
        summary="❌Start with 0", value={"phone_number": "09032567181", "password": "raw_password"}
    ), OpenApiExample(
        name="Invalid example 2", request_only=True, response_only=False,
        summary="❌Doesn't start with '+98'", value={"phone_number": "+979032567181", "password": "raw_password"}
    ), OpenApiExample(
        name="Invalid example 3", request_only=True, response_only=False,
        summary="❌The length of phone number is not 13 character", value={"phone_number": "+9890325671812", "password": "raw_password"}
    )]


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


@extend_schema_serializer(examples=examples)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        is_valid, msg = phone_number_validator(attrs["phone_number"])
        if not is_valid:
            raise AuthenticationFailed({"phone_number": msg})

        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        return data


@extend_schema_serializer(examples=examples)
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
