from rest_framework import serializers

from .models import AnswerOption, Assessment, Question, UserAnswer


class AnswerOptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор варианта ответа.
    Используется для отображения и создания вариантов ответов.
    """

    class Meta:
        model = AnswerOption
        fields = ["id", "text", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    """
    Сериализатор вопроса с вложенным созданием вариантов ответов.

    Позволяет создать вопрос и сразу несколько вариантов ответов
    в рамках одного POST-запроса.
    """

    answer_options = AnswerOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "assessment", "text", "answer_options"]

    def create(self, validated_data):
        """
        Создаёт вопрос и связанные с ним варианты ответов.
        """
        answer_options_data = validated_data.pop("answer_options")
        question = Question.objects.create(**validated_data)
        for option_data in answer_options_data:
            AnswerOption.objects.create(question=question, **option_data)
        return question


class AssessmentSerializer(serializers.ModelSerializer):
    """
    Сериализатор оценки знаний (теста).
    Включает вложенные вопросы (только для чтения).
    """

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = ["id", "lesson", "title", "questions"]


class UserAnswerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отправки ответа пользователя на вопрос.
    Автоматически определяет правильность и номер попытки.
    """

    class Meta:
        model = UserAnswer
        fields = ["id", "user", "question", "selected_option", "is_correct", "answered_at", "attempt_number"]
        read_only_fields = ["user", "is_correct", "answered_at", "attempt_number"]

    def validate(self, attrs):
        user = self.context["request"].user
        question = attrs["question"]

        # Получаем все попытки пользователя
        previous_attempts = UserAnswer.objects.filter(user=user, question=question).order_by("answered_at")

        if previous_attempts.exists():
            # Проверяем, был ли уже правильный ответ
            if previous_attempts.filter(is_correct=True).exists():
                raise serializers.ValidationError("Вы уже правильно ответили на этот вопрос.")
            if previous_attempts.count() >= 3:
                raise serializers.ValidationError("Превышено количество попыток для этого вопроса.")

        return attrs

    def create(self, validated_data):
        selected_option = validated_data["selected_option"]
        validated_data["is_correct"] = selected_option.is_correct
        validated_data["user"] = self.context["request"].user

        # Номер попытки = кол-во предыдущих + 1
        validated_data["attempt_number"] = (
            UserAnswer.objects.filter(user=validated_data["user"], question=validated_data["question"]).count() + 1
        )

        return super().create(validated_data)


# AssessmentSerializer включает все Question, а те в свою очередь — AnswerOption.
#
# Все вложенные поля только на чтение (пока) —
# мы не делаем массовое создание внутри, CRUD будет отдельно через ViewSet'ы.
