from django.urls import path

from notes.api.views import CreateNote, ListUserNotes, RetrieveUpdateDestroyNote

app_name = "notes"

urlpatterns = [
    path("", CreateNote.as_view(), name="create"),
    path("", ListUserNotes.as_view(), name="list"),
    path("<int:pk>/", RetrieveUpdateDestroyNote.as_view(), name="retrieve_update_destroy"),
]
