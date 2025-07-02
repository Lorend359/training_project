from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsAdminOrTeacher, IsOwnerOrAdmin


@extend_schema(
    tags=["Курсы"],
    summary="Управление курсами",
    description=(
        "Позволяет создавать, просматривать, изменять и удалять курсы. "
        "Просмотр — для всех авторизованных, управление — только для преподавателей и администраторов."
    ),
    responses={
        200: CourseSerializer,
        403: OpenApiResponse(description="Недостаточно прав"),
    }
)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    ordering_fields = ["created_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Course.objects.none()
        return Course.objects.all().select_related("owner").prefetch_related("lessons")

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        # На любые действия кроме чтения — требуется и роль (админ/преподаватель), и владение объектом/админство
        return [IsAuthenticated(), IsAdminOrTeacher(), IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema(
    tags=["Уроки"],
    summary="Управление уроками",
    description=(
        "Позволяет создавать, просматривать, изменять и удалять уроки. "
        "Просмотр — для всех авторизованных, управление — только для преподавателей и администраторов."
    ),
    responses={
        200: LessonSerializer,
        403: OpenApiResponse(description="Недостаточно прав"),
    }
)
class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Lesson.objects.none()
        return Lesson.objects.all().select_related("course__owner")

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrTeacher(), IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
