from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from rest_framework_jwt.settings import api_settings
from users.managers import UserManager


class User(AbstractBaseUser):
    """
    User model responsible to store the basic user information.
    
    first_name[string]:
    last_name[string]:
    username[string]:
    email[email]:
    created_on[datetime]: datetime when this object is created
    """
    first_name = models.CharField(max_length=56)
    last_name = models.CharField(max_length=56)
    username = models.CharField(max_length=56, unique=True)
    email = models.EmailField(max_length=128)
    created_on = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    def __str__(self):
        return f"{self.username}"

    def basic_user_info(self):
        """
        method to return the basic user information used for the login and registration response.
        """
        user_info = dict()
        user_info['id'] = self.id
        user_info["last_login"] = self.last_login
        user_info["email"] = self.email
        user_info["username"] = self.username
        user_info["full_name"] = self.fullname
        return user_info

    @property
    def fullname(self):
        """
        dynamic full name property from the user model
        """
        return f"{self.first_name} {self.last_name}"

    def get_jwt_token_for_user(self):
        """
        get jwt token for the user
        """
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(self)
        payload.update({
            "user_id": self.id,
            "user_email": self.email,
        })

        token = jwt_encode_handler(payload)
        return token

