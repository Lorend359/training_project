from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from assessments.models import AnswerOption, Assessment, Question, UserAnswer
from core.constants import ADMINS_GROUP, STUDENTS_GROUP, TEACHERS_GROUP
from courses.models import Course, Lesson


class Command(BaseCommand):
    help = "Создаёт группы пользователей и назначает базовые права."

    def handle(self, *args, **kwargs):
        # --- Группы ---
        admin_group, _ = Group.objects.get_or_create(name=ADMINS_GROUP)
        teacher_group, _ = Group.objects.get_or_create(name=TEACHERS_GROUP)
        student_group, _ = Group.objects.get_or_create(name=STUDENTS_GROUP)

        self.stdout.write(self.style.SUCCESS("✅ Группы созданы или обновлены."))

        # --- Права преподавателя ---
        teacher_permissions = []

        for model in [Course, Lesson, Assessment, Question, AnswerOption]:
            content_type = ContentType.objects.get_for_model(model)
            for codename in ["add", "change", "delete", "view"]:
                perm = Permission.objects.get(
                    codename=f"{codename}_{model._meta.model_name}",
                    content_type=content_type,
                )
                teacher_permissions.append(perm)

        teacher_group.permissions.set(teacher_permissions)
        self.stdout.write(self.style.SUCCESS("✅ Права преподавателя назначены."))

        # --- Права студента (только просмотр и добавление ответов) ---
        student_permissions = []

        for model in [Course, Lesson, Assessment, Question, AnswerOption]:
            content_type = ContentType.objects.get_for_model(model)
            view_perm = Permission.objects.get(
                codename=f"view_{model._meta.model_name}",
                content_type=content_type,
            )
            student_permissions.append(view_perm)

        ua_ct = ContentType.objects.get_for_model(UserAnswer)
        student_permissions.append(Permission.objects.get(codename="add_useranswer", content_type=ua_ct))
        student_permissions.append(Permission.objects.get(codename="view_useranswer", content_type=ua_ct))

        student_group.permissions.set(student_permissions)
        self.stdout.write(self.style.SUCCESS("✅ Права студента назначены."))

        self.stdout.write(self.style.SUCCESS("🎉 Все группы и права успешно настроены."))
