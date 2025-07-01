from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsAdminOrTeacher


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с курсами.
    Только авторизованные пользователи могут просматривать.
    Создавать, изменять и удалять — только админ или преподаватель.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrTeacher()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с уроками.
    Только авторизованные пользователи могут просматривать.
    Создавать, изменять и удалять — только админ или преподаватель.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrTeacher()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



# Используем ModelViewSet для быстрого создания CRUD-интерфейсов.
# Курс создаётся от имени текущего пользователя через perform_create.
# Все действия защищены: доступ только для авторизованных.