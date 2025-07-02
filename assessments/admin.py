from django.contrib import admin

from .models import AnswerOption, Assessment, Question, UserAnswer


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson")
    search_fields = ("title", "lesson__title")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "assessment")
    search_fields = ("text", "assessment__title")


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    list_filter = ("is_correct",)


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "selected_option", "is_correct", "attempt_number", "answered_at")
    list_filter = ("is_correct", "attempt_number")
    search_fields = ("user__email", "question__text")
