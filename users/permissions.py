from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Allows access only to admin(superuser) users.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_admin)


class IsExpertUser(BasePermission):
    """
    Allows access only to expert users.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_expert)


class IsRegularUser(BasePermission):
    """
    Allows access only to regular users.

    ** tip **
        Regular user => Is not super user and is not expert user
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and not (user.is_admin or user.is_expert))
