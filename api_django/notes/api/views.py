from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from notes.api.serializers import CreateNoteSerializer, UpdateNoteSerializer
from notes.permissions import IsCreator


class CreateNote(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateNoteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UpdateNote(UpdateAPIView):
    permission_classes = [IsAuthenticated, IsCreator]
    serializer_class = UpdateNoteSerializer

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
