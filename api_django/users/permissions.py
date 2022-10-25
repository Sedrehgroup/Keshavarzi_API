from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    Allows access only to admin(superuser) users.
    """

    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))


class IsExpertUser(BasePermission):
    """
    Allows access only to expert users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_expert)


class IsRegularUser(BasePermission):
    """
    Allows access only to regular users.

    ** tip **
        Regular user => Is not super user and is not expert user
    """

    def has_permission(self, request, view):
        if not request.user:
            return False
        return not (request.user.is_superuser or request.user.is_staff or request.user.is_expert)
