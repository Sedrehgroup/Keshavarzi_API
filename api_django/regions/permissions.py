from rest_framework.permissions import BasePermission


class IsRegionUser(BasePermission):
    message = "This user is not related to region"

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class IsRegionExpert(BasePermission):
    message = "This expert user is not related to region"

    def has_object_permission(self, request, view, obj):
        return obj.expert_id == request.user.id
