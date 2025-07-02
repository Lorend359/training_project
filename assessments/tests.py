from rest_framework.test import APITestCase
from django.test import TestCase
from django.urls import reverse
from users.models import CustomUser
from courses.models import Course, Lesson
from assessments.models import Assessment, Question, AnswerOption
from assessments.permissions import IsCourseOwnerOrModerator


class AssessmentTests(APITestCase):
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            email="teacher@example.com",
            password="pass1234",
            full_name="Teacher User"
        )
        self.client.force_authenticate(user=self.teacher)

        self.course = Course.objects.create(
            title="Course 1",
            description="Test course",
            owner=self.teacher
        )
        self.lesson = Lesson.objects.create(
            title="Lesson 1",
            content="Lesson content",
            course=self.course,
            order=1,
            owner=self.teacher
        )
        self.assessment = Assessment.objects.create(
            lesson=self.lesson,
            title="Test 1"
        )
        self.question = Question.objects.create(
            assessment=self.assessment,
            text="What is 2 + 2?"
        )
        self.option_correct = AnswerOption.objects.create(
            question=self.question,
            text="4",
            is_correct=True
        )
        self.option_wrong = AnswerOption.objects.create(
            question=self.question,
            text="3",
            is_correct=False
        )

    def test_assessment_detail_view(self):
        url = reverse("assessment-detail", args=[self.assessment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Test 1")

    def test_submit_correct_answer(self):
        url = reverse("submit-answer")
        data = {
            "question": self.question.id,
            "selected_option": self.option_correct.id
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["is_correct"])
        self.assertEqual(response.data["attempt_number"], 1)

    def test_submit_wrong_answer_then_correct(self):
        url = reverse("submit-answer")
        self.client.post(url, {
            "question": self.question.id,
            "selected_option": self.option_wrong.id
        })
        response = self.client.post(url, {
            "question": self.question.id,
            "selected_option": self.option_correct.id
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["is_correct"])
        self.assertEqual(response.data["attempt_number"], 2)

    def test_submit_after_successful_answer_denied(self):
        url = reverse("submit-answer")
        self.client.post(url, {
            "question": self.question.id,
            "selected_option": self.option_correct.id
        })
        response = self.client.post(url, {
            "question": self.question.id,
            "selected_option": self.option_wrong.id
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Вы уже правильно ответили", str(response.data))

    def test_submit_more_than_three_attempts_denied(self):
        url = reverse("submit-answer")
        for _ in range(3):
            self.client.post(url, {
                "question": self.question.id,
                "selected_option": self.option_wrong.id
            })
        response = self.client.post(url, {
            "question": self.question.id,
            "selected_option": self.option_wrong.id
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Превышено количество попыток", str(response.data))


class PermissionTests(TestCase):
    def setUp(self):
        self.owner_user = CustomUser.objects.create_user(
            email="owner@example.com", password="pass1234", full_name="Owner User"
        )
        self.other_user = CustomUser.objects.create_user(
            email="other@example.com", password="pass1234", full_name="Other User"
        )

    def test_owner_has_permission(self):
        permission = IsCourseOwnerOrModerator()
        request = type("Request", (), {"method": "GET", "user": self.owner_user})()
        obj = type("Obj", (), {
            "lesson": type("Lesson", (), {
                "course": type("Course", (), {"owner": self.owner_user})()
            })()
        })()
        self.assertTrue(permission.has_object_permission(request, None, obj))

    def test_non_owner_has_no_permission(self):
        permission = IsCourseOwnerOrModerator()
        request = type("Request", (), {"method": "PUT", "user": self.other_user})()
        obj = type("Obj", (), {
            "lesson": type("Lesson", (), {
                "course": type("Course", (), {"owner": self.owner_user})()
            })()
        })()
        self.assertFalse(permission.has_object_permission(request, None, obj))