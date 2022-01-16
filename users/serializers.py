from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("created_on", "last_login",)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password", "last_login", "created_on")


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', )


class UserMinimalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class PasswordResetSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    retype_password = serializers.CharField(required=True)

    def validate_username(self, username):
        if User.objects.filter(username=username):
            raise serializers.ValidationError("Username already exists.")
        return username

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('retype_password'):
            raise serializers.ValidationError("retype password doesn't match")
        return attrs


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        try:
            user_obj = User.objects.filter(username=attrs.get('username'))
            assert user_obj
        except AssertionError:
            raise serializers.ValidationError("Invalid Username.")

        user_obj = authenticate(username=attrs.get('username'), password=attrs.get('password'))

        if not user_obj:
            raise serializers.ValidationError("Invalid username/password or user doesn't exist")

        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(required=True)
    username = serializers.CharField(min_length=6, max_length=56, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def validate_username(self, username):
        if User.objects.filter(username=username):
            raise serializers.ValidationError("Username already exists.")
        return username

    def validate_email(self, email):
        if User.objects.filter(email=email):
            raise serializers.ValidationError("Email already exists")
        return email

    class Meta:
        model = User
        fields = (
            'username', 'email', 'last_name', 'id', 'first_name', 'password'
        )
