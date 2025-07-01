from django.contrib import admin
from .models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at")
    search_fields = ("title", "owner__email")
    list_filter = ("created_at",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    search_fields = ("title", "course__title")
    list_filter = ("course",)
