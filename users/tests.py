from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationTestCase(APITestCase):

    def test_user_registration(self):
        url = reverse('rest_register')  # 또는 직접 '/api/auth/registration/'
        data = {
            "email": "test@example.com",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_passwords_do_not_match(self):
        url = reverse('rest_register')
        data = {
            "email": "wrong@example.com",
            "password1": "Str0ngP@ssw0rd123!",
            "password2": "MismatchPassword!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)