from django.urls import path

from notes.api.views import CreateNote

app_name = "notes"

urlpatterns = [
    path("", CreateNote.as_view(), name="create"),
]
