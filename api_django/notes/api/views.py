from django.db.models import Q
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, extend_schema_view, inline_serializer
from rest_framework.exceptions import NotFound
from rest_framework.generics import DestroyAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from notes.api.serializers import CreateNoteSerializer, ListNotesByRegionSerializer, ListUserNotesSerializer, RetrieveNoteSerializer, UpdateNoteSerializer
from notes.models import Note
from notes.paginations import NotePagination
from notes.permissions import IsCreator
from regions.models import Region
from regions.permissions import IsRegionExpert, IsRegionUser
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


@extend_schema_view(get=extend_schema(summary="List notes by region ID",
                                      description="List created notes that are related to a specific region.",
                                      responses={200: OpenApiResponse(ListNotesByRegionSerializer),
                                                 403: OpenApiResponse(description="User is not authenticated.\nUser doesn't have permission to access this region."),
                                                 404: OpenApiResponse(description="Region or any note, not found",
                                                                      examples=[OpenApiExample("Region not found", value=[{"Region": "Region with given ID is not exists."}]),
                                                                                OpenApiExample("Note not found", value=[{"Notes": "We didn't find any matching note."}])])
                                                 }))
class ListNotesByRegion(ListAPIView):
    permission_classes = [IsAuthenticated, IsRegionUser | IsRegionExpert | IsAdmin]
    serializer_class = ListNotesByRegionSerializer
    pagination_class = NotePagination

    def get_object(self):
        region = Region.objects.filter(id=self.kwargs['pk']).order_by().first()
        if not region:
            raise NotFound({"Region": "Region with given ID is not exists."})
        self.check_object_permissions(self.request, region)
        return region

    def get_queryset(self):
        region = self.get_object()
        return Note.objects.filter(region_id=region.id).select_related("user")


@extend_schema_view(get=extend_schema(summary="Get note by id", description="Only creator or admin can get the note."),
                    delete=extend_schema(summary="Delete note by id", description="Only creator or admin can delete the note."),
                    put=extend_schema(summary="Update note by id", description="Only creator or admin can update the note."),
                    patch=extend_schema(summary="Update note by id", description="Only creator or admin can update the note."),
                    )
class RetrieveUpdateDestroyNote(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsCreator | IsAdmin]
    default_description = "Only creator or admin can {} the note."

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
