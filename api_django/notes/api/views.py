from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
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

    def get_object(self):
        region = Region.objects \
            .filter(id=self.kwargs['pk']) \
            .only("id", "user_id", "expert_id") \
            .order_by() \
            .first()
        if not region:
            raise NotFound({"Region": "Region with given ID is not exists."})
        self.check_object_permissions(self.request, region)
        return region

    def get_queryset(self):
        region = self.get_object()
        return Note.objects.filter(region_id=region.id).select_related("user")


class RetrieveUpdateDestroyNote(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsCreator | IsAdmin]

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
