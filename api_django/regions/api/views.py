from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from regions.models import Region
from regions.api.serializers import UpdateRegionExpertSerializer, \
    ListRegionExpertSerializer, ListRegionUserSerializer
from users.permissions import IsExpertUser, IsRegularUser, IsSuperUser


class UpdateRegionExpert(UpdateAPIView):
    permission_classes = [IsSuperUser]
    queryset = Region.objects.filter(is_active=True)
    serializer_class = UpdateRegionExpertSerializer


class ListRegionsExpert(ListAPIView):
    permission_classes = [IsAuthenticated & IsExpertUser]
    serializer_class = ListRegionExpertSerializer

    def get_queryset(self):
        return Region.objects.filter(expert_id=self.request.user.id) \
            .defer("expert") \
            .select_related("user")


class ListRegionsUser(ListAPIView):
    permission_classes = [IsAuthenticated & IsRegularUser]
    serializer_class = ListRegionUserSerializer

    def get_queryset(self):
        return Region.objects.filter(user_id=self.request.user.id) \
            .defer("user") \
            .select_related("expert")
