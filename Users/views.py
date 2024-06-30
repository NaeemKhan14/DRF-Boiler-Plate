from rest_framework import status, generics
from rest_framework.views import APIView

from .serializers import UserAccountSerializer, ChangePasswordSerializer
from rest_framework.response import Response


class RegisterUser(APIView):
    http_method_names = ['post']

    def post(self, request):
        serializer = UserAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'data': 'User {} created successfully'.format(serializer.data['username'])},
                        status=status.HTTP_201_CREATED)


class ChangePasswordView(generics.UpdateAPIView):
    """
    Profile page view where user can change their own password.
    """
    serializer_class = ChangePasswordSerializer
    http_method_names = ['put']

    def get_object(self, queryset=None):
        """
        Get the current logged-in user's userobject to change the password for
        :param queryset: Currently logged in user's UserAccount object (queryset)
        :return: UserAccount object
        """
        user = self.request.user
        return user

    def update(self, request, *args, **kwargs):
        # If in case user is not authenticated, throw this error
        if not request.user.is_authenticated:
            return Response({'error': 'You are not logged in.'}, status=status.HTTP_400_BAD_REQUEST)
        # Pass the updating part to ChangePasswordSerializer
        return super().update(request, *args, **kwargs)
