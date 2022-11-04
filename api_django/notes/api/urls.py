from django.urls import path

from notes.api.views import CreateNote, UpdateNote

app_name = "notes"

urlpatterns = [
    path("", CreateNote.as_view(), name="create"),
    path("<int:pk>/", UpdateNote.as_view(), name="update"),
]
