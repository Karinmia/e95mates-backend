import logging
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils.translation import gettext as _
from django.utils import timezone

from .utils import send_sms_code
from .serializers import *

logger = logging.getLogger(__name__)


class SignInRequestView(APIView):
    """
    Sign In first step - phone verification
    """
    permission_classes = (AllowAny,)
    serializer_class = SignInRequestSerializer
    parser_classes = [JSONParser, MultiPartParser]

    def post(self, request):
        request_time = timezone.now()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']
            except KeyError:
                user = serializer.save()

            if user.passcode_timer:
                if request_time < user.passcode_timer:
                    wait_for = (user.passcode_timer - request_time).seconds
                    raise ValidationError({'detail': f"Wait {wait_for} seconds and try again"})

            # Apple
            if str(user.phone).replace(" ", "") == "+380000000000":
                user.passcode = "0000"
                user.passcode_timer = timezone.now() + timezone.timedelta(minutes=1)
                user.save()
                user_serializer = UserPhoneSerializer(user)
                return Response({"user": user_serializer.data}, status=status.HTTP_200_OK)

            # if user is new or passcode time has passed
            code = send_sms_code(user.phone)
            if code:
                user.passcode = code
                user.passcode_timer = timezone.now() + timezone.timedelta(minutes=1)
                user.save()
                user_serializer = UserPhoneSerializer(user)
                return Response({"user": user_serializer.data}, status=status.HTTP_200_OK)
            else:
                raise ValidationError({'detail': "Message was not delivered to user"})
        else:
            raise ValidationError(serializer.errors)


class SignInVerifyView(APIView):
    """
    Sign In second step - code verification
    """
    permission_classes = (AllowAny,)
    serializer_class = SignInVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user_serializer = UserPhoneSerializer(user)

            # check if its new user
            is_new_user = False if user.full_name != "" else True

            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {'token': token.key, 'is_new_user': is_new_user, 'user': user_serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            raise ValidationError(serializer.errors)


class UserProfileView(APIView):
    """
    An endpoint for retrieving or updating User
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserFullSerializer

    def get(self, request):
        data = self.serializer_class(request.user).data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            data = UserFullSerializer(user).data
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ListSavedLocations(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SavedLocationSerializer

    def get_queryset(self):
        return SavedLocation.objects.filter(user=self.request.user)


class SavedLocationView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SavedLocationSerializer

    def get_queryset(self):
        return SavedLocation.objects.filter(user=self.request.user)
