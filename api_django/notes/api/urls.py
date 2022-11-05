from django.urls import path

from notes.api.views import ListCreateNote, RetrieveUpdateDestroyNote

app_name = "notes"

urlpatterns = [
    path("", ListCreateNote.as_view(), name="list_create"),
    path("<int:pk>/", RetrieveUpdateDestroyNote.as_view(), name="retrieve_update_destroy"),
]
