from rest_framework import permissions
from core.constants import ADMINS_GROUP, TEACHERS_GROUP

class IsAdminOrTeacher(permissions.BasePermission):
    """
    Доступ только для админов и преподавателей.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.is_staff or
            request.user.groups.filter(name__in=[ADMINS_GROUP, TEACHERS_GROUP]).exists()
        )

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Изменять/удалять может только владелец объекта или админ.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            user == getattr(obj, "owner", None)
            or user.is_staff
            or user.groups.filter(name=ADMINS_GROUP).exists()
        )
