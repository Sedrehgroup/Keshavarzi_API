from rest_framework.generics import UpdateAPIView

from regions.models import Region
from regions.api.serializers import UpdateRegionExpertSerializer
from users.permissions import IsSuperUser


class UpdateRegionExpert(UpdateAPIView):
    permission_classes = [IsSuperUser]
    queryset = Region.objects.filter(is_active=True)
    serializer_class = UpdateRegionExpertSerializer
