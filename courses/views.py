from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsAdminOrTeacher
from core.constants import TEACHERS_GROUP


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
        qs = Course.objects.all().select_related("owner").prefetch_related("lessons")
        if user.groups.filter(name=TEACHERS_GROUP).exists() and not user.is_staff:
            qs = qs.filter(owner=user)
        return qs

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrTeacher()]

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
        qs = Lesson.objects.all().select_related("course__owner")
        if user.groups.filter(name=TEACHERS_GROUP).exists() and not user.is_staff:
            qs = qs.filter(course__owner=user)
        return qs

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrTeacher()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
