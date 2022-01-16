from rest_framework import (response, status, views, exceptions,
                            viewsets, filters, generics)
from django.utils import timezone
import django_filters
from .models import User
from rest_framework.pagination import LimitOffsetPagination
from .serializers import UserListSerializer, UserUpdateSerializer,\
    UserCreateSerializer, PasswordResetSerializer, RegisterSerializer,\
    LoginSerializer


class UserView(viewsets.ModelViewSet):
    model = User
    queryset = User.objects.all()

    pagination_class = LimitOffsetPagination

    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter
    ]

    filterset_fields = ['first_name', 'last_name']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    ordering_fields = ['created_on', ]
    ordering = ['-created_on']

    def get_serializer_class(self):
        if self.request.method in ['POST', ]:
            return UserCreateSerializer
        elif self.request.method in ['PATCH', ]:
            return UserUpdateSerializer
        else:
            return UserListSerializer

    def list(self, request, *args, **kwargs):
        if request.query_params.get('remove_pagination'):
            self.pagination_class = None
        return super(UserView, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.create_user(**serializer.validated_data)
            response_dict = user.basic_user_info()
            return response.Response(response_dict, status=status.HTTP_201_CREATED)


class PasswordResetView(generics.CreateAPIView):

    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            user_id = self.request.user_id
            user = User.objects.get(id=user_id)
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return response.Response("Successfully changed password.", status=status.HTTP_201_CREATED)


class UserRegistrationView(generics.CreateAPIView):

    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.create_user(**serializer.validated_data)
            auth_token = user.get_jwt_token_for_user()
            response_dict = user.basic_user_info()
            response_dict["auth_token"] = auth_token

            return response.Response(response_dict, status=status.HTTP_201_CREATED)


class LoginView(generics.CreateAPIView):

    serializer_class = LoginSerializer

    def post(self, request, *args, **kargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.get(username=serializer.validated_data.get("username"))
            auth_token = user.get_jwt_token_for_user()
            user.last_login = timezone.now()
            user.save()
            response_dict = user.basic_user_info()
            response_dict["auth_token"] = auth_token

            return response.Response(response_dict, status=status.HTTP_200_OK)
