from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.api.views import CustomTokenObtainPairView, CreateUser

app_name = "users"

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', CreateUser.as_view(), name='create'),
]
