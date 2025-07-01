from rest_framework import permissions

class IsAdminOrTeacher(permissions.BasePermission):
    """
    Разрешает доступ только администраторам и преподавателям.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (
                request.user.is_staff or
                request.user.groups.filter(name__in=["Teachers"]).exists()
            )
        )
