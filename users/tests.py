from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import CustomUser


class UserRegistrationTestCase(APITestCase):
    def setUp(self):
        call_command("init_groups", verbosity=0)
        self.register_url = reverse("register")
        self.token_url = reverse("token_obtain_pair")

    def test_register_user_success(self):
        data = {"email": "testuser@example.com", "full_name": "Test User", "password": "securepassword123"}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], data["email"])
        self.assertTrue(CustomUser.objects.filter(email=data["email"]).exists())

    def test_register_user_missing_field(self):
        data = {
            "email": "test2@example.com",
            # full_name is missing
            "password": "12345678",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_token_success(self):
        CustomUser.objects.create_user(
            email="tokenuser@example.com", full_name="Token User", password="tokenpass123"
        )
        response = self.client.post(self.token_url, {"email": "tokenuser@example.com", "password": "tokenpass123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_get_token_invalid_credentials(self):
        response = self.client.post(self.token_url, {"email": "nonexistent@example.com", "password": "wrongpass"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class InitGroupsCommandTests(TestCase):
    def test_init_groups_command_creates_groups_and_permissions(self):
        call_command("init_groups", verbosity=0)

        self.assertTrue(Group.objects.filter(name="Преподаватели").exists())
        self.assertTrue(Group.objects.filter(name="Студенты").exists())

        teachers = Group.objects.get(name="Преподаватели")
        students = Group.objects.get(name="Студенты")

        self.assertGreater(teachers.permissions.count(), 0)
        self.assertGreater(students.permissions.count(), 0)
