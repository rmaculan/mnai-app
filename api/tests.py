from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from blog.models import User

class UserAuthenticationTests(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {'email': 'test@example.com', 'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_login_user(self):
        # First register a user
        url = reverse('register')
        data = {'email': 'test@example.com', 'username': 'testuser', 'password': 'testpassword'}
        self.client.post(url, data, content_type='application/json')

        # Then try to log them in
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('access', response_data)
        self.assertIn('refresh', response_data)
