from django.db import models
from django.conf import settings


class Course(models.Model):
    """
    Модель курса.
    Один курс может содержать несколько материалов (Lesson).
    Владелец — пользователь-преподаватель.
    """

    title = models.CharField(max_length=255, verbose_name="Название курса")
    description = models.TextField(blank=True, verbose_name="Описание курса")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Автор курса"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """
    Модель материала (урока).
    Привязан к курсу. Содержит текст или ссылку на видео.
    """

    title = models.CharField(max_length=255, verbose_name="Название урока")
    content = models.TextField(verbose_name="Содержимое")
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Автор урока",
        null=True
    )

    def __str__(self):
        return f"{self.title} ({self.course.title})"


# Модель Course содержит основную информацию о курсе: название, описание, и владельца-преподавателя.
# Модель Lesson реализует материалы для курса.
# Один курс может содержать множество уроков (ForeignKey), order задаёт порядок вывода.