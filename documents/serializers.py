from rest_framework import serializers
from .models import Document, DocumentVersion
from users.models import User
from users.serializers import UserMinimalListSerializer
import pathlib


class DocumentCreateSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField(required=False)

    def get_owner(self, obj):
        return UserMinimalListSerializer(obj.owner).data

    class Meta:
        model = Document
        exclude = ("shared_with", "currently_edited_by")


class DocumentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        exclude = ("currently_edited_by", "document", "created_on", "shared_with")


class DocumentListSerializer(serializers.ModelSerializer):

    owner = UserMinimalListSerializer()
    currently_edited_by = UserMinimalListSerializer()
    shared_with = serializers.SerializerMethodField()

    def get_shared_with(self, obj):
        user_qs = User.objects.filter(id__in=obj.shared_with)
        return UserMinimalListSerializer(user_qs, many=True).data

    class Meta:
        model = Document
        fields = "__all__"


class DocumentMinimalListSerializer(serializers.ModelSerializer):

    owner = UserMinimalListSerializer()

    class Meta:
        model = Document
        fields = ("id", "document_name", "owner")


class AddCollaboratorSerializer(serializers.Serializer):
    document_id = serializers.IntegerField(required=True)
    collaborator = serializers.IntegerField(required=True)

    def validate_document_id(self, document_id):
        try:
            document_obj = Document.objects.filter(id=document_id)
            assert document_obj
            document_obj = document_obj.first()
        except AssertionError:
            raise serializers.ValidationError("Invalid Document ID")
        return document_obj

    def validate_collaborator(self, collaborator_user_id):
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
        try:
            document_obj = Document.objects.filter(id=document_id)
            assert document_obj
            document_obj = document_obj.first()
        except AssertionError:
            raise serializers.ValidationError("Invalid Document ID")
        return document_obj

    def validate_collaborator(self, collaborator_user_id):
        try:
            user_obj = User.objects.filter(id=collaborator_user_id)
            assert user_obj
            user_obj = user_obj.first()
        except AssertionError:
            raise serializers.ValidationError("Invalid User ID")
        return user_obj


class DocumentVersionListSerializer(serializers.ModelSerializer):

    updated_by = UserMinimalListSerializer()
    parent_document = DocumentMinimalListSerializer()

    class Meta:
        model = DocumentVersion
        fields = "__all__"


class UploadEditedDocumentSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        if not attrs.get("document"):
            raise serializers.ValidationError({"document": ["This field is required.", ]})
        try:
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
