from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from Users.models import UserAccount


class RegisterUserTestCase(APITestCase):
    """
    Different tests to make sure registration system works as intended
    """
    signup_url = reverse('sign_up')

    def test_create_account(self):
        """
        Create a new user
        """
        # Create JSON data for sign up
        data = {'username': 'tests',
                'password': 'abc123',
                'email': 'tests@tests.com',
                'first_name': 'tests',
                'last_name': 'tests'}
        # Submit response.
        response = self.client.post(self.signup_url, data, format='json')
        # Check if 201 status was returned
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check if user 'tests' was created as intended
        self.assertEqual(UserAccount.objects.get().username, 'tests')
        self.assertEqual(UserAccount.objects.get().is_active, True)
        self.assertEqual(UserAccount.objects.get().is_staff, False)
        self.assertEqual(UserAccount.objects.get().is_superuser, False)
        self.assertEqual(UserAccount.objects.get().email, 'tests@tests.com')
        self.assertEqual(UserAccount.objects.get().first_name, 'tests')
        self.assertEqual(UserAccount.objects.get().last_name, 'tests')

    def test_create_account_without_username(self):
        """
        Create an account with missing username field
        """
        # Create JSON data for sign up
        data = {'password': 'abc123',
                'email': 'tests@tests.com'}
        # Submit response.
        response = self.client.post(self.signup_url, data, format='json')
        # Check if 400 status was returned
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_account_without_email(self):
        """
        Create an account with missing email field
        """
        # Create JSON data for sign up
        data = {'password': 'abc123',
                'username': 'abc'}
        # Submit response.
        response = self.client.post(self.signup_url, data, format='json')
        # Check if 400 status was returned
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_account_without_password(self):
        """
        Create an account with missing password field
        """
        # Create JSON data for sign up
        data = {'email': 'adfad@asdg.com',
                'username': 'abc'}
        # Submit response.
        response = self.client.post(self.signup_url, data, format='json')
        # Check if 400 status was returned
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_account_without_first_name(self):
        """
        Create an account with missing first_name field
        """
        # Create JSON data for sign up
        data = {'password': 'abc123',
                'username': 'abc',
                'email': 'tests@tests.com'}
        # Submit response.
        response = self.client.post(self.signup_url, data, format='json')
        # Check if 400 status was returned
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_account_without_last_name(self):
        """
        Create an account with missing last_name field
        """
        # Create JSON data for sign up
        data = {'password': 'abc123',
                'username': 'abc',
                'email': 'tests@tests.com',
                'first_name': 'tests'}
        # Submit response.
        response = self.client.post(self.signup_url, data, format='json')
        # Check if 400 status was returned
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_username(self):
        """
        Create an account with duplicate username field
        """
        # Create JSON data for sign up
        data = {'password': 'abc123',
                'username': 'abc',
                'email': 'tests@tests.com',
                'first_name': 'tests',
                'last_name': 'tests'}
        # Submit response.
        response = self.client.post(self.signup_url, data, format='json')
        # Successfully create the account
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {'password': 'abc123',
                'username': 'abc',
                'email': 'tessadgts@tesadts.com',
                'first_name': 'tests',
                'last_name': 'tests'}
        response = self.client.post(self.signup_url, data, format='json')
        # Request is failed due to duplicate email address
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_duplicate_email(self):
        """
        Create an account with duplicate email field
        """
        # Create JSON data for sign up
        data = {'password': 'abc123',
                'username': 'abc',
                'email': 'tests@tests.com',
                'first_name': 'tests',
                'last_name': 'tests'}
        # Submit response.
        response = self.client.post(self.signup_url, data, format='json')
        # Successfully create the account
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {'password': 'abc123',
                'username': 'abc1',
                'email': 'tests@tests.com',
                'first_name': 'saf',
                'last_name': 'asa'}
        response = self.client.post(self.signup_url, data, format='json')
        # Request is failed due to duplicate email address
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
