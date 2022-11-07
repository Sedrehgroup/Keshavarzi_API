from rest_framework.permissions import BasePermission


class IsRegionUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class IsRegionExpert(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.expert_id == request.user.id
