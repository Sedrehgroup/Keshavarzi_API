from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import DestroyAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from notes.api.serializers import CreateNoteSerializer, ListNotesByRegionSerializer, ListUserNotesSerializer, RetrieveNoteSerializer, UpdateNoteSerializer
from notes.models import Note
from notes.paginations import NotePagination
from notes.permissions import IsCreator
from users.permissions import IsAdmin


class ListCreateNote(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(description="Get list of created notes of logged in user")
    def list(self, request, *args, **kwargs):
        return super(ListCreateNote, self).list(request, *args, **kwargs)

    @extend_schema(description="Create a note object for logged in user")
    def create(self, request, *args, **kwargs):
        return super(ListCreateNote, self).create(request, *args, **kwargs)

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
    permission_classes = [IsAuthenticated, IsRegionUser | IsRegionExpert | IsAdmin]
    serializer_class = ListNotesByRegionSerializer
    pagination_class = NotePagination

    @extend_schema(description="List created notes that are related to a specific region.")
    def list(self, request, *args, **kwargs):
        return super(ListNotesByRegion, self).list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs = Note.objects.filter(region_id=self.kwargs['pk']).select_related("user")
        if not user.is_admin:
            return qs.filter(Q(region__user_id=user.id) | Q(region__expert_id=user.id))
        return qs


@extend_schema_view(get=extend_schema(summary="Get note by id", description="Only creator or admin can get the note."),
                    delete=extend_schema(summary="Delete note by id", description="Only creator or admin can delete the note."),
                    put=extend_schema(summary="Update note by id", description="Only creator or admin can update the note."),
                    patch=extend_schema(summary="Update note by id", description="Only creator or admin can update the note."),
                    )
class RetrieveUpdateDestroyNote(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsCreator | IsAdmin]
    default_description = "Only creator or admin can {} the note."

    @extend_schema(summary="Get note by id", description=default_description.format("get"))
    def retrieve(self, request, *args, **kwargs):
        return super(RetrieveUpdateDestroyNote, self).retrieve(request, *args, **kwargs)

    @extend_schema(summary="Delete note by id", description=default_description.format("delete"))
    def destroy(self, request, *args, **kwargs):
        return super(RetrieveUpdateDestroyNote, self).destroy(request, *args, **kwargs)

    @extend_schema(summary="Update note by id", description=default_description.format("update"))
    def update(self, request, *args, **kwargs):
        return super(RetrieveUpdateDestroyNote, self).update(request, *args, **kwargs)

    def get_queryset(self):
        qs = Note.objects.all()
        if self.request.method == "GET" and self.request.user.is_admin:
            return qs.select_related("user")
        return qs

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UpdateNoteSerializer
        return RetrieveNoteSerializer

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
