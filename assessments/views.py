from rest_framework import generics, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Assessment, Question, AnswerOption
from .permissions import IsCourseOwnerOrModerator
from .serializers import (
    AssessmentSerializer,
    QuestionSerializer,
    AnswerOptionSerializer,
    UserAnswerSerializer,
)


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с оценками (Assessment).
    """
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


class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с вопросами (Question).
    """
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


class AnswerOptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с вариантами ответов (AnswerOption).
    """
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


class SubmitAnswerAPIView(generics.CreateAPIView):
    """
    Эндпоинт для отправки ответа пользователя на вопрос.
    """
    serializer_class = UserAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
