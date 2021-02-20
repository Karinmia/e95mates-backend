from phonenumbers import is_valid_number, parse as phonenumbers_parse
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import User


class UserPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone']


class UserFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'full_name']


class SignInRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate(self, attrs):
        phone = attrs.get('phone').replace(" ", "")
        if phone == "+380000000000" or is_valid_number(phonenumbers_parse(phone, None)):
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                attrs['phone'] = phone
            else:
                if user.is_active:
                    attrs['user'] = user
                else:
                    msg = 'User is deactivated.'
                    raise exceptions.ValidationError(msg)
        else:
            msg = 'Must provide phonenumber in international format.'
            raise exceptions.ValidationError(msg)
        return attrs


class SignInVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    passcode = serializers.CharField(required=True)

    def validate(self, attrs):
        phone = attrs.get('phone').replace(' ', '').replace('-', '')
        passcode = attrs.get('passcode')

        if len(passcode) == 4 and passcode.isdecimal():
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                msg = {'phone': "User with provided phone does not exist"}
                raise exceptions.ValidationError(msg)
            else:
                if passcode == user.passcode:
                    attrs['user'] = user
                    return attrs
                else:
                    msg = {'passcode': "Incorrect passcode"}
                    raise exceptions.ValidationError(msg)
        else:
            msg = {'passcode': "Passcode must be 4-digit number"}
            raise exceptions.ValidationError(msg)


class UserUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ('full_name',)

    # def validate(self, attrs):
    #
    #     if self.partial is False:  # then all fields is required
    #         if not email:
    #             raise exceptions.ValidationError("Email is required")
    #         if not attrs.get('full_name', None):
    #             raise exceptions.ValidationError("Full name is required")
    #
    #     return attrs

