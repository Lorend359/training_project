from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsCourseOwnerOrModerator(BasePermission):
    """
    Разрешение для владельцев курса или модераторов.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS:
            return True

        # Для объекта Assessment
        if hasattr(obj, "lesson"):
            course_owner = obj.lesson.course.owner

        # Для объекта Question
        elif hasattr(obj, "assessment"):
            course_owner = obj.assessment.lesson.course.owner

        # Для объекта AnswerOption
        elif hasattr(obj, "question"):
            course_owner = obj.question.assessment.lesson.course.owner

        else:
            return False

        return user == course_owner or user.groups.filter(name="Модераторы").exists()
