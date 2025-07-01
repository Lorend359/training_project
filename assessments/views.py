from rest_framework import generics, permissions
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Assessment, Question, AnswerOption
from .serializers import AssessmentSerializer, QuestionSerializer, AnswerOptionSerializer, UserAnswerSerializer


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с оценками (Assessment).
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsAuthenticated]


class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с вопросами (Question).
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]


class AnswerOptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с вариантами ответов (AnswerOption).
    """
    queryset = AnswerOption.objects.all()
    serializer_class = AnswerOptionSerializer
    permission_classes = [IsAuthenticated]


class SubmitAnswerAPIView(generics.CreateAPIView):
    """
    Эндпоинт для отправки ответа пользователя на вопрос.
    """
    serializer_class = UserAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]