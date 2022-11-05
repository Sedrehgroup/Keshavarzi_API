from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from notes.api.serializers import CreateNoteSerializer, ListUserNotesSerializer, RetrieveNoteSerializer, UpdateNoteSerializer
from notes.models import Note
from notes.permissions import IsCreator
from users.permissions import IsAdmin


class ListUserNotes(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListUserNotesSerializer

    def get_queryset(self):
        return Note.objects \
            .filter(user_id=self.request.user.id) \
            .defer("user") \
            .select_related("region")


class CreateNote(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateNoteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RetrieveUpdateDestroyNote(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsCreator | IsAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = Note.objects.all()
        if user.is_admin:
            return qs.select_related("user")
        return qs

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UpdateNoteSerializer
        return RetrieveNoteSerializer


class UpdateNote(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsCreator]
    serializer_class = UpdateNoteSerializer
    queryset = Note.objects.all()

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class DeleteNote(DestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdmin | IsCreator]
    queryset = Note.objects.all()
