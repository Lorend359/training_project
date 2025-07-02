from rest_framework import generics, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Assessment, Question, AnswerOption
from .permissions import IsCourseOwnerOrPrivileged
from .serializers import (
    AssessmentSerializer,
    QuestionSerializer,
    AnswerOptionSerializer,
    UserAnswerSerializer,
)
from . import services


@extend_schema(
    tags=["Оценки знаний"],
    summary="Управление тестами",
    description="CRUD операции над тестами. Доступно только владельцу курса или сотруднику.",
    responses={
        200: AssessmentSerializer,
        403: OpenApiResponse(description="Недостаточно прав"),
    }
)
class AssessmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated, IsCourseOwnerOrPrivileged]

    def get_queryset(self):
        return (
            Assessment.objects
            .select_related("lesson__course__owner")
            .prefetch_related("questions__answer_options")
        )

    def perform_create(self, serializer):
        lesson = serializer.validated_data["lesson"]
        course_owner = lesson.course.owner
        user = self.request.user

        if user != course_owner and not user.is_staff:
            raise PermissionDenied("У вас нет прав на создание теста для этого урока.")

        serializer.save()


@extend_schema(
    tags=["Вопросы"],
    summary="Управление вопросами",
    description="CRUD операции над вопросами. Доступно только владельцу курса или сотруднику.",
    responses={
        200: QuestionSerializer,
        403: OpenApiResponse(description="Недостаточно прав"),
    }
)
class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsCourseOwnerOrPrivileged]

    def get_queryset(self):
        return (
            Question.objects
            .select_related("assessment__lesson__course__owner")
            .prefetch_related("answer_options")
        )

    def perform_create(self, serializer):
        assessment = serializer.validated_data["assessment"]
        course_owner = assessment.lesson.course.owner
        user = self.request.user

        if user != course_owner and not user.is_staff:
            raise PermissionDenied("У вас нет прав на добавление вопроса к этому тесту.")

        serializer.save()


@extend_schema(
    tags=["Ответы"],
    summary="Управление вариантами ответов",
    description="CRUD операции над вариантами ответов. Доступно только владельцу курса или сотруднику.",
    responses={
        200: AnswerOptionSerializer,
        403: OpenApiResponse(description="Недостаточно прав"),
    }
)
class AnswerOptionViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerOptionSerializer
    permission_classes = [IsAuthenticated, IsCourseOwnerOrPrivileged]

    def get_queryset(self):
        return (
            AnswerOption.objects
            .select_related("question__assessment__lesson__course__owner")
        )

    def perform_create(self, serializer):
        question = serializer.validated_data["question"]
        course_owner = question.assessment.lesson.course.owner
        user = self.request.user

        if user != course_owner and not user.is_staff:
            raise PermissionDenied("У вас нет прав на добавление варианта ответа к этому вопросу.")

        serializer.save()


@extend_schema(
    tags=["Ответы студентов"],
    summary="Отправка ответа на вопрос",
    description=(
        "Позволяет студенту отправить ответ на вопрос теста. "
        "Проверяется правильность и количество попыток."
    ),
    request=UserAnswerSerializer,
    responses={
        201: UserAnswerSerializer,
        400: OpenApiResponse(description="Ошибка валидации — превышено количество попыток или уже есть правильный ответ."),
        403: OpenApiResponse(description="Неавторизованный пользователь."),
    }
)
class SubmitAnswerAPIView(generics.GenericAPIView):
    serializer_class = UserAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            answer = services.submit_user_answer(
                user=request.user,
                question=serializer.validated_data["question"],
                selected_option=serializer.validated_data["selected_option"],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        return Response(UserAnswerSerializer(answer).data, status=201)
