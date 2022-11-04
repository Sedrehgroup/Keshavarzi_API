from rest_framework.permissions import BasePermission

from notes.models import Note


class IsCreator(BasePermission):
    def has_object_permission(self, request, view, obj: Note):
        return request.user.id == obj.user_id
