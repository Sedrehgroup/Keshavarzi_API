from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from users.api.views import CustomTokenObtainPairView, CreateUser, RetrieveUser

app_name = "users"

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('', CreateUser.as_view(), name='create'),
    path('<int:pk>/', RetrieveUser.as_view(), name='retrieve'),
]
