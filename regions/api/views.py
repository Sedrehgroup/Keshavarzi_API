from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from regions.models import Region
from regions.api.serializers import UpdateRegionExpertSerializer, RetrieveUpdateRegionSerializer, UpdateRegionUserSerializer, \
    ListRegionExpertSerializer, ListRegionUserSerializer, \
    CreateRegionSerializer
from regions.permissions import IsRegionExpert, IsRegionUser
from users.permissions import IsExpertUser, IsRegularUser, IsAdmin


class UpdateRegionExpert(UpdateAPIView):
    permission_classes = [IsAdmin]
    queryset = Region.objects.filter(is_active=True)
    serializer_class = UpdateRegionExpertSerializer


class UpdateRegionUser(UpdateAPIView):
    permission_classes = [IsAdmin]
    queryset = Region.objects.filter(is_active=True)
    serializer_class = UpdateRegionUserSerializer


class ListRegionsExpert(ListAPIView):
    permission_classes = [IsExpertUser]
    serializer_class = ListRegionExpertSerializer

    def get_queryset(self):
        return Region.objects.filter(expert_id=self.request.user.id) \
            .defer("expert") \
            .select_related("user")


class ListRegionsUser(ListAPIView):
    permission_classes = [IsRegularUser]
    serializer_class = ListRegionUserSerializer

    def get_queryset(self):
        return Region.objects.filter(user_id=self.request.user.id) \
            .defer("user") \
            .select_related("expert")


class CreateRegion(CreateAPIView):
    permission_classes = [IsRegularUser]
    serializer_class = CreateRegionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RetrieveUpdateRegion(RetrieveUpdateAPIView):
    queryset = Region.objects.all()
    serializer_class = RetrieveUpdateRegionSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            # Retrieve
            self.permission_classes = [IsAuthenticated, IsRegionUser | IsRegionExpert | IsAdmin]
        else:
            # Update
            self.permission_classes = [IsAuthenticated, IsRegularUser | IsAdmin, IsRegionUser | IsAdmin]
        return super(RetrieveUpdateRegion, self).get_permissions()
