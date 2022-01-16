from django.contrib.auth.base_user import BaseUserManager
from rest_framework import exceptions


class UserManager(BaseUserManager):

    def _create_user(self, **extra_fields):
        try:
            password = extra_fields.pop('password')
            if not extra_fields.get('email'):
                raise ValueError('The given email must be set')
            email = self.normalize_email(extra_fields.pop('email'))
            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            user.save()
        except Exception as e:
            print(e.__str__())
            raise exceptions.ValidationError("Unable to create user.")
        return user

    def create_user(self, **extra_fields):
        return self._create_user(**extra_fields)
