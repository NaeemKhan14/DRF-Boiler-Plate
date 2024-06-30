from functools import partial

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from Users.models import UserAccount


class LoginTestCase(APITestCase):
    """
    Different tests to make sure login system works as intended
    """


    def setUp(self):
        # Set up a user account in the DB
        UserAccount.objects.create_user(username='test',
                                        password='abc123',
                                        email='test@test.com',
                                        first_name='test',
                                        last_name='test')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

    def _login(self, extra_data=None):
        """
        Helper function for login so we can test the content of JWT token and HTTP status
        :return:
        """
        data = {'username': 'test', 'password': 'abc123'} if not extra_data else extra_data
        response = self.client.post(self.login_url, data)
        body = response.json()
        return response, body

    def test_login(self):
        """
        Login with correct username and password
        """
        response, _ = self._login()
        # Make sure it returns 200 HTTP code, and the response contains 'access' and 'refresh' keys.
        # These two keys are our JWT tokens
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'access')
        self.assertContains(response, 'refresh')

    def test_invalid_login(self):
        """
        Login with a wrong password
        """
        response, _ = self._login({'username': 'test', 'password': 'abc1234'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout(self):
        """
        Login user successfully then logout
        """
        _, body = self._login()

        # Get refresh token from the login response and use it to logout
        response = self.client.post(self.logout_url, {'refresh': body['refresh']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_refresh_token_in_blacklist(self):
        """
        Validate that refresh token is blacklisted after logging out
        """
        _, body = self._login()
        r = self.client.post(self.logout_url, body)
        token = partial(RefreshToken, body['refresh'])
        self.assertRaises(TokenError, token)
