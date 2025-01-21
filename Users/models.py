from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.core.mail import EmailMultiAlternatives
from django.db.models import signals
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from drf_boilerplate.settings import common


class UserManager(BaseUserManager):
    """
    This is a custom users model registration class that creates user objects
    with extra fields that Django's default user model class does not allow.
    It implements basic registration with username, password and email, and
    allows for future expandability if required.
    """
    use_in_migrations = True

    def create_user(self, username, email, password, **other_fields):
        """
        Create and save a user with the given username, email and password.
        :param username: User's username.
        :param email: User's email address.
        :param password: User's password.
        :param other_fields: Other user fields such as first_name and last_name etc.
        :return: User object with JWT token.
        """
        # If username/email/password fields are empty, throw an error.
        if not username:
            raise ValueError('Users must have username')
        if not email:
            raise ValueError('Users must have email')
        if not password:
            raise ValueError('Users must have a password')
        # Populate the user model
        user = self.model(email=self.normalize_email(email),
                          username=username,
                          **other_fields)
        # Set the password
        user.set_password(password)
        # Save the user in our database
        user.save(using=self._db)

        # Returns the user object which in our API is going to be the JWT token
        return user

    def create_superuser(self, username, email, password, **other_fields):
        """
        This is a custom model registration class that creates a super_user
        with appropriate privileges.

        :param username: User's username
        :param email: User's email
        :param password: User's password
        :param other_fields: Not required when creating super_user from django admin terminal
        :return: User object
        """
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('is_staff flag cannot be False')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser flag cannot be False')

        # Return to create_user function above for normal processing of user creation
        return self.create_user(username, email, password, **other_fields)


class UserAccount(AbstractUser):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=60, unique=True)
    # We leave these two fields to be blank so we don't have issues creating super_user.
    # We can handle them not being blank in the frontend for normal users.
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Telling the model to use our custom registration manager we created above
    objects = UserManager()
    # Set default field logged in with as username. Can be changed to email.
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens. When a token is created, an e-mail needs to be sent to the user

    @param  sender: View Class that sent the signal
    @param  instance: View Instance that sent the signal
    @param  reset_password_token: Token Model Object
    """
    url = 'http://awesome-website.com'  # Todo change this in production to valid url
    if common.DEBUG:
        url = 'http://localhost:8000'

    # send an e-mail to the user
    context = {
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            url + '/account/password_reset/validate_token',
            reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string('Users/email/user_reset_password.html', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset Request for {title}".format(title="Couples Tools"),
        # message:
        '',
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


@receiver(signals.pre_save, sender=UserAccount)
def revoke_tokens(sender, instance, update_fields, **kwargs):
    """
    Deletes the given user's refresh token on password change.

    @param sender: django.db.models
    @param instance: UserAccount
    """
    # instance._state.adding gives true if object is being created for the first time
    if not instance._state.adding:
        existing_user = UserAccount.objects.get(pk=instance.pk)
        # If instance.password is not the same as user's current password
        if instance.password != existing_user.password:
            # Get all the user tokens
            outstanding_tokens = OutstandingToken.objects.filter(user__pk=instance.pk)

            for out_token in outstanding_tokens:
                if hasattr(out_token, 'blacklistedtoken'):
                    # Token already blacklisted. Skip
                    continue

                BlacklistedToken.objects.create(token=out_token)
