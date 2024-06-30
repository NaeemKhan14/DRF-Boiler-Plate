from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import UserAccount


###############
# Create User #
###############

class UserAccountSerializer(serializers.ModelSerializer):
    """
    This serializer creates a new user account. Data is brought in through
    the API
    """

    class Meta:
        model = UserAccount
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        """
        Creates a new user account. Data is brought in through the API.

        :param validated_data: Fields from form
        :return: Newly created user account
        """
        # We handle these exceptions here because doing this in UserManager will prevent
        # the creation of superuser through Django CLI.
        if 'first_name' not in validated_data:
            raise serializers.ValidationError("First Name is required")
        if 'last_name' not in validated_data:
            raise serializers.ValidationError("Last Name is required")

        user = UserAccount.objects.create(username=validated_data['username'],
                                          email=validated_data['email'],
                                          first_name=validated_data['first_name'],
                                          last_name=validated_data['last_name'])
        user.set_password(validated_data['password'])
        # Save the user object
        user.save()
        # Return the newly created user
        return user


###################
# Change Password #
###################


class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    This serializer is used to change user's own password
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserAccount
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        # If passwords do not match
        if attrs['password'] != attrs['password2']:
            raise ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        # If password check fails
        if not user.check_password(value):
            raise ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user
        # If the given user is not the same one as logged in user, it will raise a validation error.
        # This is to prevent users from changing each others' passwords. Only the logged in user
        # can change their own password.
        if user.pk != instance.pk:
            raise ValidationError(
                {"authorize": "You don't have permission to change password for this user."})

        instance.set_password(validated_data['password'])
        instance.save()

        return instance
