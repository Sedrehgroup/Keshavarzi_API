from django.urls import path

from notes.api.views import ListCreateNote, RetrieveUpdateDestroyNote, ListNotesByRegion

app_name = "notes"

urlpatterns = [
    path("", ListCreateNote.as_view(), name="list_create"),
    path("<int:pk>/", RetrieveUpdateDestroyNote.as_view(), name="retrieve_update_destroy"),
    path("regions/<int:pk>/", ListNotesByRegion.as_view(), name="list_notes_by_region"),
]
