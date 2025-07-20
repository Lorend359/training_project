from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from core.constants import ADMINS_GROUP, STUDENTS_GROUP, TEACHERS_GROUP
from courses.models import Course, Lesson
from courses.permissions import IsAdminOrTeacher
from users.models import CustomUser


class IsAdminOrTeacherPermissionTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = CustomUser.objects.create_user(
            email="admin@test.com", full_name="Admin", password="pass", is_staff=True
        )
        self.teacher = CustomUser.objects.create_user(email="teacher@test.com", full_name="Teacher", password="pass")
        self.student = CustomUser.objects.create_user(email="student@test.com", full_name="Student", password="pass")

        Group.objects.create(name=ADMINS_GROUP)
        teacher_group = Group.objects.create(name=TEACHERS_GROUP)
        student_group = Group.objects.create(name=STUDENTS_GROUP)

        self.teacher.groups.add(teacher_group)
        self.student.groups.add(student_group)

        self.permission = IsAdminOrTeacher()

    def test_admin_has_permission(self):
        request = self.factory.get("/")
        request.user = self.admin
        self.assertTrue(self.permission.has_permission(request, None))

    def test_teacher_has_permission(self):
        request = self.factory.get("/")
        request.user = self.teacher
        self.assertTrue(self.permission.has_permission(request, None))

    def test_student_has_no_permission(self):
        request = self.factory.get("/")
        request.user = self.student
        self.assertFalse(self.permission.has_permission(request, None))

    def test_anonymous_has_no_permission(self):
        request = self.factory.get("/")
        request.user = type("Anon", (), {"is_authenticated": False})()
        self.assertFalse(self.permission.has_permission(request, None))


class CoursesTests(APITestCase):
    def setUp(self):
        call_command("init_groups", verbosity=0)
        self.user = CustomUser.objects.create_user(email="test@example.com", password="12345", full_name="Test User")
        self.teacher = CustomUser.objects.create_user(
            email="teacher@example.com", password="12345", full_name="Teacher"
        )
        self.teacher.groups.add(Group.objects.get(name=TEACHERS_GROUP))

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(title="Test Course", description="Test Desc", owner=self.teacher)
        self.lesson = Lesson.objects.create(
            course=self.course, title="Lesson 1", content="Content", order=1, owner=self.teacher
        )

    def test_list_courses(self):
        response = self.client.get("/api/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_course(self):
        response = self.client.get(f"/api/courses/{self.course.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_course_forbidden(self):
        data = {"title": "New Course", "description": "New Desc"}
        response = self.client.post("/api/courses/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LessonsTests(APITestCase):
    def setUp(self):
        call_command("init_groups", verbosity=0)
        self.user = CustomUser.objects.create_user(email="student@example.com", password="12345", full_name="Student")
        self.teacher = CustomUser.objects.create_user(
            email="teacher@example.com", password="12345", full_name="Teacher"
        )
        self.teacher.groups.add(Group.objects.get(name=TEACHERS_GROUP))

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(title="Test Course", description="Test Desc", owner=self.teacher)
        self.lesson = Lesson.objects.create(
            course=self.course, title="Lesson 1", content="Content", order=1, owner=self.teacher
        )

    def test_list_lessons(self):
        response = self.client.get("/api/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_lesson(self):
        response = self.client.get(f"/api/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_lesson_forbidden(self):
        data = {"title": "New Lesson", "content": "Lesson content", "order": 2, "course": self.course.id}
        response = self.client.post("/api/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CoursePermissionsTestCase(APITestCase):
    def setUp(self):
        call_command("init_groups", verbosity=0)
        self.teacher1 = CustomUser.objects.create_user(
            email="teach1@example.com", full_name="Teacher1", password="pass123"
        )
        self.teacher2 = CustomUser.objects.create_user(
            email="teach2@example.com", full_name="Teacher2", password="pass123"
        )
        self.student = CustomUser.objects.create_user(
            email="stud@example.com", full_name="Student", password="pass123"
        )
        self.teacher1.groups.add(Group.objects.get(name=TEACHERS_GROUP))
        self.teacher2.groups.add(Group.objects.get(name=TEACHERS_GROUP))
        self.student.groups.add(Group.objects.get(name=STUDENTS_GROUP))

        self.course = Course.objects.create(title="Test Course", owner=self.teacher1, description="desc")
        self.lesson = Lesson.objects.create(
            course=self.course, title="Test Lesson", content="...", order=1, owner=self.teacher1
        )

    def test_student_cannot_patch_course(self):
        self.client.force_authenticate(self.student)
        url = reverse("course-detail", args=[self.course.pk])
        resp = self.client.patch(url, {"title": "Hacked!"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_edit_foreign_course(self):
        self.client.force_authenticate(self.teacher2)
        url = reverse("course-detail", args=[self.course.pk])
        resp = self.client.patch(url, {"title": "Foreign"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_delete_foreign_lesson(self):
        self.client.force_authenticate(self.teacher2)
        url = reverse("lesson-detail", args=[self.lesson.pk])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_teacher_can_patch(self):
        self.client.force_authenticate(self.teacher1)
        url = reverse("course-detail", args=[self.course.pk])
        resp = self.client.patch(url, {"title": "New Title"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
