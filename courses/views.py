from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsAdminOrTeacher


@extend_schema(
    tags=["Курсы"],
    summary="Управление курсами",
    description="Позволяет создавать, просматривать, изменять и удалять курсы. "
                "Просмотр — для всех авторизованных, управление — только для преподавателей и администраторов.",
    responses={
        200: CourseSerializer,
        403: OpenApiResponse(description="Недостаточно прав"),
    }
)
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrTeacher()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema(
    tags=["Уроки"],
    summary="Управление уроками",
    description="Позволяет создавать, просматривать, изменять и удалять уроки. "
                "Просмотр — для всех авторизованных, управление — только для преподавателей и администраторов.",
    responses={
        200: LessonSerializer,
        403: OpenApiResponse(description="Недостаточно прав"),
    }
)
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrTeacher()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
