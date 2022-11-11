from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import PermissionDenied

from users.api.serializers import CreateUserSerializer, CustomTokenObtainPairSerializer, UserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CreateUser(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CreateUserSerializer


class RetrieveUser(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        if self.kwargs["pk"] == self.request.user.id or self.request.user.is_admin:
            return self.request.user
        raise PermissionDenied("You don't have access to see the details of other users")
