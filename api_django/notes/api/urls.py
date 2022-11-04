from django.urls import path

from notes.api.views import CreateNote, UpdateNote, DeleteNote

app_name = "notes"

urlpatterns = [
    path("", CreateNote.as_view(), name="create"),
    path("<int:pk>/", UpdateNote.as_view(), name="update"),
    path("<int:pk>/", DeleteNote.as_view(), name="delete"),
]
