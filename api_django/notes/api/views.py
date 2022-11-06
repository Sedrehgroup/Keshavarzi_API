from django.db.models import Q
from django.shortcuts import get_list_or_404
from rest_framework.generics import DestroyAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from notes.api.serializers import CreateNoteSerializer, ListNotesByRegionSerializer, ListUserNotesSerializer, RetrieveNoteSerializer, UpdateNoteSerializer
from notes.models import Note
from notes.paginations import NotePagination
from notes.permissions import IsCreator
from users.permissions import IsAdmin


class ListCreateNote(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ListUserNotesSerializer
        return CreateNoteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Note.objects \
            .filter(user_id=self.request.user.id) \
            .defer("user") \
            .select_related("region")


class ListNotesByRegion(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListNotesByRegionSerializer
    pagination_class = NotePagination

    def get_queryset(self):
        user = self.request.user
        qs = Note.objects.filter(region_id=self.kwargs['pk']).select_related("user")
        if not user.is_admin:
            return qs.filter(Q(region__user_id=user.id) | Q(region__expert_id=user.id))
        return qs


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
