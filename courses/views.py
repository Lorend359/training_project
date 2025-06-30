from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с курсами.
    Доступ только для авторизованных пользователей.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Устанавливаем текущего пользователя владельцем курса.
        """
        serializer.save(owner=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с уроками.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]


# Используем ModelViewSet для быстрого создания CRUD-интерфейсов.
# Курс создаётся от имени текущего пользователя через perform_create.
# Все действия защищены: доступ только для авторизованных.