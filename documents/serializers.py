import uuid
from rest_framework import serializers
from .models import Document, DocumentVersion
from users.models import User
from users.serializers import UserMinimalListSerializer
import pathlib


class DocumentCreateSerializer(serializers.ModelSerializer):
    """
    Document serializer used for the POST action 
    """
    owner = serializers.SerializerMethodField(required=False)

    def get_owner(self, obj):
        return UserMinimalListSerializer(obj.owner).data

    def validate(self, attrs):
        document_name = attrs.get("document_name")
        user = self.context.get("request").user
        if Document.objects.filter(owner=user, document_name=document_name).exists():
            attrs["document_name"] = f"{document_name}_{uuid.uuid4().__str__()[:8]}"
        return super(DocumentCreateSerializer, self).validate(attrs)
    class Meta:
        model = Document
        """
        excluding the only fields that are updated through API. Not allowing these fields to be initialized by
        the user.
        """
        exclude = ("shared_with", "currently_edited_by")


class DocumentUpdateSerializer(serializers.ModelSerializer):
    """
    Document serializer used for the PATCH action 
    """
    class Meta:
        model = Document
        """
        excluding the only fields that are either getting auto-updated or updated through API.
        'document' field is mentioned here because we have a seprated API to updated the document. 
        """
        exclude = ("currently_edited_by", "document", "created_on", "shared_with")


class DocumentListSerializer(serializers.ModelSerializer):
    """
    Document serializer used for the GET action 
    """

    owner = UserMinimalListSerializer()
    currently_edited_by = UserMinimalListSerializer()
    shared_with = serializers.SerializerMethodField()

    def get_shared_with(self, obj):
        """
        Instead of returning a list with ids (eg. [1,2,3]). It returns a list with user object dict.
        Check the APIdocumentation PDF mentioned in the README.md
        """
        user_qs = User.objects.filter(id__in=obj.shared_with)
        return UserMinimalListSerializer(user_qs, many=True).data

    class Meta:
        model = Document
        fields = "__all__"


class DocumentMinimalListSerializer(serializers.ModelSerializer):
    """
    Document serializer with minimal document object info that is used in as a nested serializer in other
    serializers.
    """
    owner = UserMinimalListSerializer()

    class Meta:
        model = Document
        fields = ("id", "document_name", "owner")


class AddCollaboratorSerializer(serializers.Serializer):
    """
    AddCollaborator serializer used for the POST action
    """
    document_id = serializers.IntegerField(required=True)
    collaborator = serializers.IntegerField(required=True)

    def validate_document_id(self, document_id):
        """
        Check whether the document id reviced in the request exists in the DB or not.
        """
        try:
            document_obj = Document.objects.filter(id=document_id)
            assert document_obj
            document_obj = document_obj.first()
        except AssertionError:
            raise serializers.ValidationError("Invalid Document ID")
        return document_obj

    def validate_collaborator(self, collaborator_user_id):
        """
        Check whether the user id reviced in the request exists in the DB or not.
        """
        try:
            user_obj = User.objects.filter(id=collaborator_user_id)
            assert user_obj
            user_obj = user_obj.first()
        except AssertionError:
            raise serializers.ValidationError("Invalid User ID")
        return user_obj


class RemoveCollaboratorSerializer(serializers.Serializer):
    document_id = serializers.IntegerField(required=True)
    collaborator = serializers.IntegerField(required=True)

    def validate_document_id(self, document_id):
        """
        Check whether the document id reviced in the request exists in the DB or not.
        """
        try:
            document_obj = Document.objects.filter(id=document_id)
            assert document_obj
            document_obj = document_obj.first()
        except AssertionError:
            raise serializers.ValidationError("Invalid Document ID")
        return document_obj

    def validate_collaborator(self, collaborator_user_id):
        """
        Check whether the user id reviced in the request exists in the DB or not.
        """
        try:
            user_obj = User.objects.filter(id=collaborator_user_id)
            assert user_obj
            user_obj = user_obj.first()
        except AssertionError:
            raise serializers.ValidationError("Invalid User ID")
        return user_obj


class DocumentVersionListSerializer(serializers.ModelSerializer):
    """
    Document version serializer used for the GET action
    """

    updated_by = UserMinimalListSerializer()
    parent_document = DocumentMinimalListSerializer()

    class Meta:
        model = DocumentVersion
        fields = "__all__"


class UploadEditedDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer used for POST action of the API responsible for the uploading edited documents.
    """

    def validate(self, attrs):
        """
        manually making the document field required field to avoid declaring the document as fileField above.
        """
        if not attrs.get("document"):
            raise serializers.ValidationError({"document": ["This field is required.", ]})
        try:
            """
            Checking whether the file extension of the new file and the original are same or not.
            """
            document_obj = self.context.get('document_obj')
            current_file_extension = pathlib.Path(document_obj.document.path).suffix
            new_file_extension = pathlib.Path(attrs.get("document").name).suffix
            assert current_file_extension == new_file_extension
            return attrs
        except AssertionError:
            raise serializers.ValidationError(f"File extension doesn't path with the original file."
                                              f" New file should be {current_file_extension}")
        except Exception as e:
            raise serializers.ValidationError(e.__str__())

    class Meta:
        model = Document
        fields = ("document", )
