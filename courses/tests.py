from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import CustomUser
from courses.models import Course, Lesson


class CoursesTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email="test@example.com", password="12345", full_name="Test User")
        self.teacher = CustomUser.objects.create_user(email="teacher@example.com", password="12345", full_name="Teacher")
        self.teacher.groups.create(name="Преподаватели")

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(title="Test Course", description="Test Desc", owner=self.teacher)
        self.lesson = Lesson.objects.create(course=self.course, title="Lesson 1", content="Content", order=1, owner=self.teacher)

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
        self.user = CustomUser.objects.create_user(email="student@example.com", password="12345", full_name="Student")
        self.teacher = CustomUser.objects.create_user(email="teacher@example.com", password="12345", full_name="Teacher")
        self.teacher.groups.create(name="Преподаватели")

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(title="Test Course", description="Test Desc", owner=self.teacher)
        self.lesson = Lesson.objects.create(course=self.course, title="Lesson 1", content="Content", order=1, owner=self.teacher)

    def test_list_lessons(self):
        response = self.client.get("/api/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_lesson(self):
        response = self.client.get(f"/api/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_lesson_forbidden(self):
        data = {
            "title": "New Lesson",
            "content": "Lesson content",
            "order": 2,
            "course": self.course.id
        }
        response = self.client.post("/api/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
