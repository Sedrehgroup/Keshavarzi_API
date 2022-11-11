"""FirstPrj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi
# schema_view = get_schema_view(
#     openapi.Info(
#         title="Keshavarzi",
#         default_version='1.0.0',
#         description="Created by Sedreh group",
#         contact=openapi.Contact(email="sedreh@gmail.com"),  # ToDo
#     ),
#     public=True,
#     permission_classes=[permissions.AllowAny],
# )
urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('admin/', admin.site.urls),
    path("users/", include("users.api.urls", namespace="users")),
    path("regions/", include("regions.api.urls", namespace="regions")),
    path("notes/", include("notes.api.urls", namespace="notes")),
]
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
