from django.urls import path

from regions.api.views import UpdateRegionExpert, ListRegionsUser, ListRegionsExpert, CreateRegion

app_name = "regions"

urlpatterns = [
    path('<int:pk>/', UpdateRegionExpert.as_view(), name='update_region_expert'),
    path('expert/', ListRegionsExpert.as_view(), name='list_expert_regions'),
    path('user/', ListRegionsUser.as_view(), name='list_user_regions'),
    path('', CreateRegion.as_view(), name='create'),
]
