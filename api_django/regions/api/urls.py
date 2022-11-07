from django.urls import path

from regions.api.views import (UpdateRegionExpert, UpdateRegionUser,
                               CreateRegion, RetrieveUpdateRegion,
                               ListRegionsUser, ListRegionsExpert)

app_name = "regions"

urlpatterns = [
    path('<int:pk>/expert/', UpdateRegionExpert.as_view(), name='update_region_expert'),
    path('<int:pk>/user/', UpdateRegionUser.as_view(), name='update_region_user'),
    path('<int:pk>/', RetrieveUpdateRegion.as_view(), name='retrieve_update_region'),
    path('expert/', ListRegionsExpert.as_view(), name='list_expert_regions'),
    path('user/', ListRegionsUser.as_view(), name='list_user_regions'),
    path('', CreateRegion.as_view(), name='create'),
]
