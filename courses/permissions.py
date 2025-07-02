from rest_framework import permissions
from core.constants import ADMINS_GROUP, TEACHERS_GROUP

class IsAdminOrTeacher(permissions.BasePermission):
    """
    Разрешает доступ только администраторам и преподавателям.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.is_staff or
            request.user.groups.filter(name__in=[ADMINS_GROUP, TEACHERS_GROUP]).exists()
        )
