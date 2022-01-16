from calendar import timegm
import jwt
from django.utils.deprecation import MiddlewareMixin
from django.conf import LazySettings
import datetime
from django.http import JsonResponse
from documents.models import Document, DocumentVersion

settings = LazySettings()


class RestTokenDecoderMiddleware(MiddlewareMixin):

    def process_request(self, request):

        if "/media/document_version_files/" in request.path or "/media/document/" in request.path:
            return JsonResponse({"error": "Use '/api/v1/fetch_document/' api to fetch or view a media document."},
                                status=401)
        elif "/media/document_diff_files/" in request.path:
            return

        if request.path not in ['/docs',
                                '/api/v1/login/',
                                '/api/v1/register/',
                                '/api/v1/reset-password/']:
            request.user_val = self.get_jwt_user(request)
            if not request.user_val:
                return JsonResponse({'error': 'Invalid token in header.'}, status=401)
        else:
            return

    def get_jwt_user(self, request):

        try:
            assert request.META.get('HTTP_AUTHORIZATION', None)
            token_name, token_key = request.META.get('HTTP_AUTHORIZATION', None).split()
        except AssertionError:
            return None

        user_jwt = False
        if token_key is not None:
            try:
                user_jwt_data = jwt.decode(
                    token_key,
                    settings.JWT_SECRET_KEY,
                )
                time_current = timegm(datetime.datetime.utcnow().utctimetuple())
                if time_current < user_jwt_data['exp']:
                    return user_jwt_data
            except Exception as e:
                return False
        return user_jwt
