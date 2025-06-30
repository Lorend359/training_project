from django.db import models


class Assessment(models.Model):
    """
    Модель оценки знаний (тестирования), привязанная к конкретному уроку.
    Один Assessment может включать в себя несколько вопросов (Question).
    Каждый урок может иметь не более одного Assessment.
    """

    lesson = models.OneToOneField(
        "courses.Lesson",
        on_delete=models.CASCADE,
        related_name="assessment",
        verbose_name="Урок"
    )
    title = models.CharField(max_length=255, verbose_name="Название оценки")

    def __str__(self):
        return f"Assessment for: {self.lesson.title}"


class Question(models.Model):
    """
    Модель вопроса, входящего в Assessment.
    Вопрос содержит текст и связан с несколькими вариантами ответа (AnswerOption).
    """

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Оценка"
    )
    text = models.CharField(max_length=1024, verbose_name="Текст вопроса")

    def __str__(self):
        return self.text


class AnswerOption(models.Model):
    """
    Модель варианта ответа для вопроса.
    Каждый вариант принадлежит одному вопросу.
    Поле is_correct указывает, является ли этот ответ правильным.
    """

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answer_options",
        verbose_name="Вопрос"
    )
    text = models.CharField(max_length=512, verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный ответ")

    def __str__(self):
        return f"{self.text} ({'✔' if self.is_correct else '✘'})"

# --- Assessment ---
# Привязан к уроку через OneToOneField, т.е. один урок — один тест.
# Это гарантирует, что для каждого урока может быть не более одной связанной оценки.
# Поле title позволяет задать краткое имя для самого теста (например, "Итоговый тест").

# --- Question ---
# Каждый вопрос связан с одной оценкой (assessment).
# Один тест может включать в себя несколько вопросов.
# Используем CharField (а не TextField), так как вопрос обычно короткий.

# --- AnswerOption ---
# Привязан к вопросу: один вопрос — много вариантов ответов.
# Поле is_correct помогает реализовать автоматическую проверку теста:
# на его основе можно потом сравнивать ответы пользователя.
# Если нужно будет поддерживать несколько правильных ответов — логика готова.