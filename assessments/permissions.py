from rest_framework.permissions import SAFE_METHODS, BasePermission

from core.constants import ADMINS_GROUP


class IsCourseOwnerOrPrivileged(BasePermission):
    """
    Разрешает доступ владельцу курса или администратору.
    Читать могут все аутентифицированные пользователи.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Разрешить чтение всем аутентифицированным
        if request.method in SAFE_METHODS:
            return True

        # Универсальный способ добраться до owner курса
        owner = None

        if hasattr(obj, "lesson") and hasattr(obj.lesson, "course"):
            owner = obj.lesson.course.owner
        elif (
            hasattr(obj, "assessment")
            and hasattr(obj.assessment, "lesson")
            and hasattr(obj.assessment.lesson, "course")
        ):
            owner = obj.assessment.lesson.course.owner
        elif (
            hasattr(obj, "question")
            and hasattr(obj.question, "assessment")
            and hasattr(obj.question.assessment, "lesson")
            and hasattr(obj.question.assessment.lesson, "course")
        ):
            owner = obj.question.assessment.lesson.course.owner
        elif hasattr(obj, "course") and hasattr(obj.course, "owner"):
            owner = obj.course.owner
        elif hasattr(obj, "owner"):
            owner = obj.owner
        else:
            return False

        is_admin = user.is_staff or user.groups.filter(name=ADMINS_GROUP).exists()
        return user == owner or is_admin
