from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views as apis

router = DefaultRouter()
router.register(r"document", apis.DocumentView, basename="document-api")

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^document_version/$', apis.DocumentVersionView.as_view(), name='document-version'),
    url(r'^add_document_collaborator/$', apis.AddCollaboratorView.as_view(), name='add-collaborator'),
    url(r'^remove_document_collaborator/$', apis.RemoveCollaboratorView.as_view(), name='remove-collaborator'),
    url(r'^fetch_document/(?P<pk>\d+)/$', apis.FetchDocumentView.as_view(), name='fetch-document'),
    url(r'^reupload_document/(?P<pk>\d+)/$', apis.UploadEditedDocumentView.as_view(), name='re-upload-document'),
]