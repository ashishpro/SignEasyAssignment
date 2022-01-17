from rest_framework import (response, status, views, exceptions,
                            viewsets, filters, generics)
from .models import Document, DocumentVersion
import django_filters
from rest_framework.pagination import LimitOffsetPagination
from .serializers import DocumentCreateSerializer, DocumentListSerializer,\
    DocumentUpdateSerializer, AddCollaboratorSerializer,\
    DocumentVersionListSerializer, RemoveCollaboratorSerializer, UploadEditedDocumentSerializer
from django.http import HttpResponse
import mimetypes
import pathlib
import uuid
import difflib
import filecmp
from django.core.files import File


class DocumentView(viewsets.ModelViewSet):
    """
    Basic Document CRUD API
    """
    model = Document
    queryset = Document.objects.all()

    pagination_class = LimitOffsetPagination

    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter
    ]

    filterset_fields = ['owner', ]
    search_fields = ['document_name', ]

    ordering_fields = ['created_on', ]
    ordering = ['-created_on']

    def get_serializer_class(self):
        if self.request.method in ['POST', ]:
            return DocumentCreateSerializer
        elif self.request.method in ['PATCH', ]:
            return DocumentUpdateSerializer
        else:
            return DocumentListSerializer

    def list(self, request, *args, **kwargs):
        """
        overriding the list(get) method to give the functionality to remove pagination if needed.
        """
        if request.query_params.get('remove_pagination'):
            self.pagination_class = None
        return super(DocumentView, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Create the document object and also create the document version object.
        """
        serializer = self.get_serializer(data=request.data, context={"request": self.request})
        if serializer.is_valid(raise_exception=True):
            self.perform_create(serializer)
            instance = serializer.instance
            """
            fetching current user from the request that is currently logged in.
            """
            instance.owner = self.request.user
            instance.save()

            try:
                document_version_obj = DocumentVersion(parent_document=instance,
                                                       updated_by=self.request.user)
                document_version_obj.document = instance.document
                document_version_obj.save()

            except Exception as e:
                raise exceptions.ValidationError(f"Unknown error occurred while creating document"
                                                 f" version object. {e.__str__()}")

            return response.Response(serializer.data, status=status.HTTP_201_CREATED)


class DocumentVersionView(generics.ListAPIView, generics.RetrieveAPIView):
    """
    Document Version supports only GET
    """
    model = DocumentVersion
    queryset = DocumentVersion.objects.all()

    serializer_class = DocumentVersionListSerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter
    ]

    filterset_fields = ['updated_by', ]
    search_fields = ['document__document_name', ]

    ordering_fields = ['created_on', ]
    ordering = ['-created_on']

    def list(self, request, *args, **kwargs):
        """
        overriding the list(get) method to give the functionality to remove pagination if needed.
        """
        if request.query_params.get('remove_pagination'):
            self.pagination_class = None
        return super(DocumentVersionView, self).list(request, *args, **kwargs)


class AddCollaboratorView(generics.CreateAPIView, generics.DestroyAPIView):
    """
    API responsible for adding new collaborator to the document.
    Note: go through the validation errors below to understand the validation conditions.
    """
    model = Document
    serializer_class = AddCollaboratorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            document_obj = serializer.validated_data.get("document_id")
            collaborator_obj = serializer.validated_data.get("collaborator")

            if document_obj.owner != self.request.user:
                raise exceptions.ValidationError("Only document owner is allowed to add collaborator.")

            elif document_obj.owner == collaborator_obj:
                raise exceptions.ValidationError("Cannot add owner as a collaborator.")

            elif collaborator_obj.id in document_obj.shared_with:
                raise exceptions.ValidationError("This user is already added as a collaborator.")

            document_obj.add_collaborator(collaborator_obj.id)
            document_obj.save()

            return response.Response(DocumentListSerializer(document_obj).data, status=status.HTTP_201_CREATED)


class RemoveCollaboratorView(generics.CreateAPIView, generics.DestroyAPIView):
    """
    API responsible for removing a collaborator to the document.
    Note: go through the validation errors below to understand the validation conditions.
    """
    model = Document
    serializer_class = RemoveCollaboratorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            document_obj = serializer.validated_data.get("document_id")
            collaborator_obj = serializer.validated_data.get("collaborator")

            if document_obj.owner != self.request.user:
                raise exceptions.ValidationError("Only document owner is allowed to remove collaborator.")

            elif document_obj.owner == collaborator_obj:
                raise exceptions.ValidationError("Cannot remove owner as a collaborator.")

            elif collaborator_obj.id not in document_obj.shared_with:
                raise exceptions.ValidationError("This user already doesn't exist as a collaborator for this document.")

            elif document_obj.currently_edited_by and collaborator_obj == document_obj.currently_edited_by:
                raise exceptions.ValidationError("Cannot remove a collaborator who's currently editing the document.")

            document_obj.remove_collaborator(collaborator_obj.id)
            document_obj.save()

            return response.Response(DocumentListSerializer(document_obj).data, status=status.HTTP_201_CREATED)


class FetchDocumentView(views.APIView):
    """
    API responsible for downloading the document and locking the document object.
    So no other collaborators or owner are allowed to download it.
    (downloading the document through the django media URL has been disabled)
    Note: go through the validation errors below to understand the validation conditions.
    """
    model = Document
    queryset = Document.objects.all()

    def get_object(self, **kwargs):
        if self.model.objects.filter(id=kwargs.get('pk')).exists():
            return self.model.objects.get(id=kwargs.get('pk'))
        raise exceptions.ValidationError("Invalid document ID in the URL.")

    def is_valid(self, current_user, document_obj):
        if current_user.id not in document_obj.shared_with and current_user.id != document_obj.owner.id:
            raise exceptions.ValidationError("Only collaborator and owners are authorized to download this document.")
        elif document_obj.currently_edited_by:
            if document_obj.currently_edited_by != current_user:
                raise exceptions.ValidationError("Cannot download a document which is currently being edited by a "
                                                 "collaborator or owner")
        return True

    def get(self, request, *args, **kwargs):

        current_user = self.request.user
        document_obj = self.get_object(**kwargs)

        if self.is_valid(current_user, document_obj):
            try:
                """
                dynamically determing the content-type of the document for the HttpResponse below.
                """
                mime_type = mimetypes.guess_type(document_obj.document.path)
                mime_type = mime_type[0]
            except Exception:
                raise exceptions.ValidationError("Unable to guess mime-type of the file. Try downloading later.")

            file_name = document_obj.document_name
            file_extension = pathlib.Path(document_obj.document.path).suffix
            file_content = open(document_obj.document.path, "rb")

            if document_obj.currently_edited_by is None:
                document_obj.currently_edited_by = current_user
                document_obj.save()

            file_response = HttpResponse(file_content, content_type=mime_type)
            file_response['Content-Disposition'] = f'attachment; filename={file_name}{file_extension}'
            return file_response


class UploadEditedDocumentView(generics.UpdateAPIView):
    """
    API responsible for uploading the edited document and un-locking the document object.
    So other collaborators or owner are allowed to download it again.
    Note: go through the validation errors below to understand the validation conditions.
    """
    model = Document
    queryset = Document.objects.all()
    serializer_class = UploadEditedDocumentSerializer

    def get_object(self, **kwargs):
        """
        Checking whether the pk mentioned in the URL is valid or not.
        """
        if self.model.objects.filter(id=kwargs.get('pk')).exists():
            return self.model.objects.get(id=kwargs.get('pk'))
        raise exceptions.ValidationError("Invalid document ID in the URL.")

    def patch(self, request, *args, **kwargs):
        document_obj = self.get_object(**kwargs)
        serializer = self.serializer_class(
            data=request.data, context={"request": request, 'document_obj': document_obj}, partial=True)
        if serializer.is_valid(raise_exception=True):
            new_document = serializer.validated_data.get("document")
            file_ext = pathlib.Path(document_obj.document.path).suffix

            try:
                """
                creating the file of the new document that is in the request body.
                """
                temp_file_dir = '/tmp'
                temp_file_path = f"{temp_file_dir}/document_{uuid.uuid4().__str__()[:8]}{file_ext}"
                with open(temp_file_path, "wb+") as outfile:
                    outfile.write(new_document.file.getbuffer())

            except Exception as e:
                raise exceptions.ValidationError("Unable to create temporary document file.")

            """
            Checking whether the file new document file in the request and the document file whos PK is mentioned
            in the URL are same are not.
            If the file are same then create a document version and return response.
            """
            if filecmp.cmp(document_obj.document.path, temp_file_path, shallow=False):
                try:
                    document_version_obj = DocumentVersion(parent_document=document_obj, updated_by=self.request.user)
                    document_version_obj.document = new_document
                    document_version_obj.save()

                except Exception as e:
                    raise exceptions.ValidationError("Unknown error occurred while creating document version object.")

                return response.Response(DocumentListSerializer(document_obj).data, status=status.HTTP_200_OK)

            else:
                temp_file_diff_name = f"document_diff_{uuid.uuid4().__str__()[:8]}{file_ext}"
                temp_file_diff_path = f"{temp_file_dir}/{temp_file_diff_name}"

                differ = difflib.Differ()
                """
                check line by line and write the file difference in a new file. That will be saved against the
                'diff_file' filed of the documentVersion model.
                """
                with open(document_obj.document.path, "r") as current_file, open(temp_file_path, "r") as new_file,\
                        open(temp_file_diff_path, "w+") as diff_file:
                    for line in differ.compare(current_file.readlines(), new_file.readlines()):
                        diff_file.write(line)

                try:
                    document_obj.document = new_document
                    document_obj.remove_file_lock()
                    document_obj.save()
                except Exception as e:
                    raise exceptions.ValidationError("Unknown error occurred while creating document object.")

                try:
                    diff_file = open(temp_file_diff_path, "rb")
                    document_version_obj = DocumentVersion(parent_document=document_obj, updated_by=self.request.user)
                    document_version_obj.diff_file.save(temp_file_diff_name, File(diff_file))
                    document_version_obj.document = new_document
                    document_version_obj.save()

                except Exception as e:
                    raise exceptions.ValidationError("Unknown error occurred while creating document version object.")

                return response.Response(DocumentListSerializer(document_obj).data, status=status.HTTP_200_OK)







