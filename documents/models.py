from django.db import models
from users.models import User


class Document(models.Model):
    document_name = models.CharField(max_length=128)
    document = models.FileField(upload_to="document/")
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="document_owner", null=True, blank=True)
    shared_with = models.JSONField(default=list)
    created_on = models.DateTimeField(auto_now_add=True)
    currently_edited_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True,
                                            related_name="document_currently_edited_by")

    class Meta:
        unique_together = ('owner', 'document_name',)

    def __str__(self):
        return f"{self.document_name}->{self.owner}"

    def is_file_identical(self, new_file_path):
        return True

    def add_collaborator(self, user_id):
        self.shared_with.append(user_id)

    def remove_collaborator(self, user_id):
        self.shared_with = [collaborator_id for collaborator_id in self.shared_with if collaborator_id != user_id]

    def remove_file_lock(self):
        self.currently_edited_by = None


class DocumentVersion(models.Model):
    parent_document = models.ForeignKey("Document", on_delete=models.DO_NOTHING, null=True, blank=True)
    document = models.FileField(upload_to="document_version_files/", null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_on = models.DateTimeField(auto_now_add=True)
    diff_file = models.FileField(upload_to="document_diff_files/", null=True, blank=True)

    def __str__(self):
        return f"{self.document}"


