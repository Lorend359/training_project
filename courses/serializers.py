from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор урока (материала).
    Используется для вложенного отображения в курсе и отдельного CRUD.
    """

    class Meta:
        model = Lesson
        fields = ["id", "title", "content", "order", "course"]


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор курса.
    Вложенный список уроков включается только для чтения.
    """

    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "owner", "created_at", "lessons"]
        read_only_fields = ["owner", "created_at"]

# CourseSerializer включает в себя вложенные уроки (lessons) для удобного отображения.
# Сами уроки редактируются отдельно, но могут быть отображены при получении курса.
# Поля owner и created_at защищены от изменений вручную — их заполняет система.