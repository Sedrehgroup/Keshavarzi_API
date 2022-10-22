from django.urls import path

from regions.api.views import UpdateRegionExpert

app_name = "regions"

urlpatterns = [
    path('<int:pk>/', UpdateRegionExpert.as_view(), name='update_region_expert'),
]
