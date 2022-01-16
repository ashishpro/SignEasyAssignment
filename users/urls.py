from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views as apis

router = DefaultRouter()
router.register(r"user", apis.UserView, basename="user-api")

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^register/$', apis.UserRegistrationView.as_view(), name="user-registration"),
    url(r'^login/$', apis.LoginView.as_view(), name="user-login"),
    url(r'^reset-password/$', apis.PasswordResetView.as_view(), name="change-password"),
]