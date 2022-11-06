from rest_framework.permissions import BasePermission


class IsRegionUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and not (user.is_expert or user.is_admin))


class IsRegionExpert(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.expert_id == request.user.id

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_expert)
