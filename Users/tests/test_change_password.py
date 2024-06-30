from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from Users.models import UserAccount
from Users.serializers import ChangePasswordSerializer


class ChangePasswordTestCase(APITestCase):
    login_url = reverse('login')
    change_pass_url = reverse('change_password')

    def setUp(self):
        # Set up a user account in the DB
        self.user = UserAccount.objects.create_user(username='test',
                                                    password='abc123',
                                                    email='test@test.com',
                                                    first_name='test',
                                                    last_name='test')

    def _login(self):
        """
        Helper function for login so we can test the content of JWT token and HTTP status
        :return:
        """
        data = {'username': 'test', 'password': 'abc123'}
        response = self.client.post(self.login_url, data)
        body = response.json()
        return response, body

    def _change_password(self, data):
        # Login and get access token
        _, body = self._login()

        # Add access token to request's header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + body['access'])
        # Return PUT request's response
        return self.client.put(self.change_pass_url, data)

    def test_change_password(self):
        """
        Successfully change password
        """
        data = {'old_password': 'abc123',
                'password': 'abc12343245',
                'password2': 'abc12343245'}
        response = self._change_password(data)
        # HTTP 200 indicates that password has been changed
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_password(self):
        """
        Test where password is invalid
        """
        data = {'old_password': 'abc123ss',
                'password': 'abc12343245',
                'password2': 'abc12343245'}
        response = self._change_password(data)
        # HTTP 400 indicates that password change has failed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('old_password')['old_password'], 'Old password is not correct')

    def test_passwords_not_matching(self):
        """
        Test where new passwords do not match
        """
        data = {'old_password': 'abc123',
                'password': 'abc12343245',
                'password2': 'abc1235'}
        response = self._change_password(data)
        # HTTP 400 indicates that password change has failed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('password')[0], "Password fields didn't match.")

    def test_password_too_common(self):
        """
        Test where new password is too common
        """
        data = {'old_password': 'abc123',
                'password': 'abc12345',
                'password2': 'abc12345'}
        response = self._change_password(data)
        # HTTP 400 indicates that password change has failed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('password')[0], "This password is too common.")

    def test_password_too_short(self):
        """
        Test where new password is too common
        """
        data = {'old_password': 'abc123',
                'password': '1@4^e3',
                'password2': '1@4^e3'}
        response = self._change_password(data)
        # HTTP 400 indicates that password change has failed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('password')[0],
                         "This password is too short. It must contain at least 8 characters.")
