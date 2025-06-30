from rest_framework import serializers
from .models import Assessment, Question, AnswerOption


class AnswerOptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор варианта ответа.
    Используется для создания и отображения вариантов ответа к вопросу.
    """

    class Meta:
        model = AnswerOption
        fields = ["id", "question", "text", "is_correct"]



class QuestionSerializer(serializers.ModelSerializer):
    """
    Сериализатор вопроса.
    Включает вложенные варианты ответов только для чтения.
    """
    answer_options = AnswerOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "assessment", "text", "answer_options"]


class AssessmentSerializer(serializers.ModelSerializer):
    """
    Сериализатор оценки знаний.
    Включает вложенные вопросы только для чтения.
    """
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = ["id", "lesson", "title", "questions"]



# AssessmentSerializer включает все Question, а те в свою очередь — AnswerOption.
#
# Все вложенные поля только на чтение (пока) — мы не делаем массовое создание внутри, CRUD будет отдельно через ViewSet'ы.