from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.messages import get_messages

class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = Client()  

    def test_get_method(self):
        response = self.client.get(reverse('campaign_management:login'))
        self.assertEqual(response.status_code, 200)

    def test_valid_post_method(self):
        response = self.client.post(reverse('campaign_management:login'), {'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)

    def test_invalid_post_method(self):
        response = self.client.post(reverse('campaign_management:login'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Invalid Credentials!")

    def test_logged_in_user_post_method(self):
        login_success = self.client.login(username='testuser', password='password123')
        self.assertTrue(login_success)

        response = self.client.post(reverse('campaign_management:login'), {'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
