from rest_framework.permissions import BasePermission, SAFE_METHODS
from core.constants import ADMINS_GROUP

class IsCourseOwnerOrPrivileged(BasePermission):
    """
    Разрешает доступ владельцу курса, администратору.
    Читать могут все аутентифицированные пользователи.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Разрешить чтение (GET, HEAD, OPTIONS) всем аутентифицированным
        if request.method in SAFE_METHODS:
            return True

        # Определяем владельца курса
        if hasattr(obj, "lesson"):
            course_owner = obj.lesson.course.owner
        elif hasattr(obj, "assessment"):
            course_owner = obj.assessment.lesson.course.owner
        elif hasattr(obj, "question"):
            course_owner = obj.question.assessment.lesson.course.owner
        elif hasattr(obj, "course"):
            course_owner = obj.course.owner
        else:
            return False

        # Доступ к изменению — только владельцу или админу
        is_admin = user.is_staff or user.groups.filter(name=ADMINS_GROUP).exists()
        return user == course_owner or is_admin
