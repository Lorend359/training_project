from rest_framework.test import APITestCase
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.core.management import call_command
from django.contrib.auth.models import Group
from users.models import CustomUser
from courses.models import Course, Lesson
from assessments.models import Assessment, Question, AnswerOption, UserAnswer
from assessments.permissions import IsCourseOwnerOrPrivileged
from assessments import services
from core.constants import ADMINS_GROUP, TEACHERS_GROUP, STUDENTS_GROUP

# --- 1. UNIT-ТЕСТЫ PERMISSIONS ---

class IsCourseOwnerOrPrivilegedTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner = CustomUser.objects.create_user(email='owner@test.com', full_name='Owner', password='pass')
        self.admin = CustomUser.objects.create_user(email='admin@test.com', full_name='Admin', password='pass', is_staff=True)
        self.teacher = CustomUser.objects.create_user(email='teacher@test.com', full_name='Teacher', password='pass')
        Group.objects.create(name=TEACHERS_GROUP)
        Group.objects.create(name=ADMINS_GROUP)
        self.teacher.groups.add(Group.objects.get(name=TEACHERS_GROUP))
        self.admin.groups.add(Group.objects.get(name=ADMINS_GROUP))
        self.other = CustomUser.objects.create_user(email='other@test.com', full_name='Other', password='pass')

        self.course = Course.objects.create(title="Course", owner=self.owner, description="...")
        self.lesson = Lesson.objects.create(course=self.course, title="Lesson", content="...", order=1, owner=self.owner)
        self.assessment = Assessment.objects.create(lesson=self.lesson, title="Assessment")
        self.question = Question.objects.create(assessment=self.assessment, text="Q1")
        self.permission = IsCourseOwnerOrPrivileged()

    def _make_request(self, user, method="GET"):
        req = self.factory.get("/")
        req.user = user
        req.method = method
        return req

    def test_permission_for_lesson_owner(self):
        obj = type("Fake", (), {"lesson": self.lesson})()
        self.assertTrue(self.permission.has_object_permission(self._make_request(self.owner), None, obj))

    def test_permission_for_admin(self):
        obj = type("Fake", (), {"lesson": self.lesson})()
        self.assertTrue(self.permission.has_object_permission(self._make_request(self.admin), None, obj))

    def test_permission_for_foreign_teacher(self):
        obj = type("Fake", (), {"lesson": self.lesson})()
        req = self._make_request(self.teacher, method="PATCH")
        self.assertFalse(self.permission.has_object_permission(req, None, obj))

    def test_permission_for_question_attr(self):
        obj = type("Fake", (), {"question": self.question})()
        self.assertTrue(self.permission.has_object_permission(self._make_request(self.owner), None, obj))

    def test_permission_for_assessment_attr(self):
        obj = type("Fake", (), {"assessment": self.assessment})()
        self.assertTrue(self.permission.has_object_permission(self._make_request(self.owner), None, obj))

    def test_permission_for_course_attr(self):
        obj = type("Fake", (), {"course": self.course})()
        self.assertTrue(self.permission.has_object_permission(self._make_request(self.owner), None, obj))

    def test_permission_safe_method_allows_anyone(self):
        obj = type("Fake", (), {"lesson": self.lesson})()
        req = self._make_request(self.other, method="GET")
        self.assertTrue(self.permission.has_object_permission(req, None, obj))

    def test_permission_not_authenticated(self):
        obj = type("Fake", (), {"lesson": self.lesson})()
        # Мокаем анонимного пользователя с нужным атрибутом
        anon = type("Anon", (), {"is_authenticated": False})()
        req = self.factory.get("/")
        req.user = anon
        self.assertFalse(self.permission.has_object_permission(req, None, obj))


# --- 2. UNIT-ТЕСТЫ SERVICES ---

class ServicesTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email="u@x.com", password="p", full_name="U")
        self.course = Course.objects.create(title="C", description="...", owner=self.user)
        self.lesson = Lesson.objects.create(course=self.course, title="L", content="...", order=1, owner=self.user)
        self.assessment = Assessment.objects.create(lesson=self.lesson, title="A")
        self.question = Question.objects.create(assessment=self.assessment, text="Q")
        self.opt1 = AnswerOption.objects.create(question=self.question, text="Yes", is_correct=True)
        self.opt2 = AnswerOption.objects.create(question=self.question, text="No", is_correct=False)

    def test_submit_user_answer_success(self):
        answer = services.submit_user_answer(self.user, self.question, self.opt2)
        self.assertFalse(answer.is_correct)
        self.assertEqual(answer.attempt_number, 1)

    def test_submit_user_answer_correct(self):
        services.submit_user_answer(self.user, self.question, self.opt2)
        answer = services.submit_user_answer(self.user, self.question, self.opt1)
        self.assertTrue(answer.is_correct)
        self.assertEqual(answer.attempt_number, 2)

    def test_submit_user_answer_too_many_attempts(self):
        for _ in range(3):
            services.submit_user_answer(self.user, self.question, self.opt2)
        with self.assertRaises(ValueError):
            services.submit_user_answer(self.user, self.question, self.opt2)

    def test_submit_user_answer_already_correct(self):
        services.submit_user_answer(self.user, self.question, self.opt1)
        with self.assertRaises(ValueError):
            services.submit_user_answer(self.user, self.question, self.opt2)


# --- 3. UNIT-ТЕСТЫ SERIALIZERS ---

from assessments.serializers import (
    AssessmentSerializer, QuestionSerializer, AnswerOptionSerializer, UserAnswerSerializer
)

class AssessmentSerializerTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email="test@x.com", full_name="User", password="pass")
        self.course = Course.objects.create(title="C", description="D", owner=self.user)
        self.lesson = Lesson.objects.create(course=self.course, title="L", content="...", order=1, owner=self.user)
        self.assessment = Assessment.objects.create(lesson=self.lesson, title="A")
        self.question = Question.objects.create(assessment=self.assessment, text="Q")
        self.option = AnswerOption.objects.create(question=self.question, text="1", is_correct=True)

    def test_assessment_serializer_fields(self):
        ser = AssessmentSerializer(instance=self.assessment)
        self.assertEqual(ser.data["title"], "A")
        self.assertEqual(ser.data["lesson"], self.lesson.id)

    def test_question_serializer_fields(self):
        ser = QuestionSerializer(instance=self.question)
        self.assertEqual(ser.data["text"], "Q")
        self.assertEqual(ser.data["assessment"], self.assessment.id)

    def test_answer_option_serializer_fields(self):
        ser = AnswerOptionSerializer(instance=self.option)
        # Чекаем только существующие поля!
        self.assertEqual(ser.data["text"], "1")
        # Только если question есть в fields
        if "question" in ser.data:
            self.assertEqual(ser.data["question"], self.question.id)

    def test_user_answer_serializer_validation(self):
        data = {"question": self.question.id, "selected_option": self.option.id}
        fake_request = type("Req", (), {"user": self.user})()
        ser = UserAnswerSerializer(data=data, context={"request": fake_request})
        self.assertTrue(ser.is_valid(), ser.errors)


# --- 4. API-ТЕСТЫ ---

class AssessmentTests(APITestCase):
    def setUp(self):
        call_command("init_groups", verbosity=0)
        self.teacher = CustomUser.objects.create_user(
            email="teacher@example.com",
            password="pass1234",
            full_name="Teacher User"
        )
        self.teacher.groups.add(Group.objects.get(name="Преподаватели"))
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
        self.assertIn("уже правильно ответили", str(response.data).lower())

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
        self.assertIn("превышено количество попыток", str(response.data).lower())

    def test_fourth_attempt_raises_value_error(self):
        # Прямой вызов сервиса — проверяем логику ограничения попыток
        for _ in range(3):
            services.submit_user_answer(self.teacher, self.question, self.option_wrong)
        with self.assertRaises(ValueError) as exc:
            services.submit_user_answer(self.teacher, self.question, self.option_wrong)
        self.assertIn("превышено количество попыток", str(exc.exception).lower())


class AssessmentNegativeTests(APITestCase):
    def setUp(self):
        call_command("init_groups", verbosity=0)
        self.teacher = CustomUser.objects.create_user(email="owner@ex.com", password="pass", full_name="T1")
        self.teacher.groups.add(Group.objects.get(name="Преподаватели"))
        self.other_teacher = CustomUser.objects.create_user(email="other@ex.com", password="pass", full_name="T2")
        self.other_teacher.groups.add(Group.objects.get(name="Преподаватели"))
        self.student = CustomUser.objects.create_user(email="stud@ex.com", password="pass", full_name="Stud")
        self.student.groups.add(Group.objects.get(name="Студенты"))

        self.course = Course.objects.create(title="C1", description="...", owner=self.teacher)
        self.lesson = Lesson.objects.create(title="L1", content="...", course=self.course, order=1, owner=self.teacher)
        self.assessment = Assessment.objects.create(lesson=self.lesson, title="A1")
        self.question = Question.objects.create(assessment=self.assessment, text="Q1")
        self.option_correct = AnswerOption.objects.create(question=self.question, text="Yes", is_correct=True)
        self.option_wrong = AnswerOption.objects.create(question=self.question, text="No", is_correct=False)

    def test_student_patch_assessment_forbidden(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("assessment-detail", args=[self.assessment.id])
        response = self.client.patch(url, {"title": "Hack"})
        self.assertEqual(response.status_code, 403)

    def test_teacher_not_owner_delete_question_forbidden(self):
        self.client.force_authenticate(user=self.other_teacher)
        url = reverse("question-detail", args=[self.question.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

