from rest_framework import generics, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Assessment, Question, AnswerOption
from .permissions import IsCourseOwnerOrModerator
from .serializers import (
    AssessmentSerializer,
    QuestionSerializer,
    AnswerOptionSerializer,
    UserAnswerSerializer,
)


@extend_schema(
    tags=["Оценки знаний"],
    summary="Управление тестами",
    description="CRUD операции над тестами. Доступно только владельцу курса или модератору.",
    responses={
        200: AssessmentSerializer,
        403: OpenApiResponse(description="Недостаточно прав"),
    }
)
class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated, IsCourseOwnerOrModerator]

    def perform_create(self, serializer):
        lesson = serializer.validated_data["lesson"]
        course_owner = lesson.course.owner
        user = self.request.user

        if user != course_owner and not user.groups.filter(name="Модераторы").exists():
            raise PermissionDenied("У вас нет прав на создание теста для этого урока.")

        serializer.save()


@extend_schema(
    tags=["Вопросы"],
    summary="Управление вопросами",
    description="CRUD операции над вопросами. Доступно только владельцу курса или модератору.",
    responses={
        200: QuestionSerializer,
        403: OpenApiResponse(description="Недостаточно прав"),
    }
)
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsCourseOwnerOrModerator]

    def perform_create(self, serializer):
        assessment = serializer.validated_data["assessment"]
        course_owner = assessment.lesson.course.owner
        user = self.request.user

        if user != course_owner and not user.groups.filter(name="Модераторы").exists():
            raise PermissionDenied("У вас нет прав на добавление вопроса к этому тесту.")

        serializer.save()


@extend_schema(
    tags=["Ответы"],
    summary="Управление вариантами ответов",
    description="CRUD операции над вариантами ответов. Доступно только владельцу курса или модератору.",
    responses={
        200: AnswerOptionSerializer,
        403: OpenApiResponse(description="Недостаточно прав"),
    }
)
class AnswerOptionViewSet(viewsets.ModelViewSet):
    queryset = AnswerOption.objects.all()
    serializer_class = AnswerOptionSerializer
    permission_classes = [IsAuthenticated, IsCourseOwnerOrModerator]

    def perform_create(self, serializer):
        question = serializer.validated_data["question"]
        course_owner = question.assessment.lesson.course.owner
        user = self.request.user

        if user != course_owner and not user.groups.filter(name="Модераторы").exists():
            raise PermissionDenied("У вас нет прав на добавление ответа к этому вопросу.")

        serializer.save()


@extend_schema(
    tags=["Ответы студентов"],
    summary="Отправка ответа на вопрос",
    description="Позволяет студенту отправить ответ на вопрос теста. "
                "Проверяется правильность и количество попыток.",
    request=UserAnswerSerializer,
    responses={
        201: UserAnswerSerializer,
        400: OpenApiResponse(description="Ошибка валидации — превышено количество попыток или уже есть правильный ответ."),
        403: OpenApiResponse(description="Неавторизованный пользователь."),
    }
)
class SubmitAnswerAPIView(generics.CreateAPIView):
    serializer_class = UserAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
