from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf.urls.static import static

from django.conf import LazySettings
settings = LazySettings()


schema_view = get_schema_view(
    openapi.Info(
        title="Document Management Service Endpoint(s)",
        default_version='v1',
        description="Document Management Service Description(s)"
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

apis = [
    path('admin/', admin.site.urls),
    url(r'^api/v1/', include("users.urls")),
    url(r'^api/v1/', include("documents.urls")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = apis + [
    url(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger')
]
