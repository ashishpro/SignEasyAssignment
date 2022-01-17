from django.db import models
from users.models import User


class Document(models.Model):
    """
    Model responsible to store all the documents.
    
    document_name[string]: name of the document
    document[file]: document file that'll be uploaded in the MEDIA_ROOT
    owner[object]: User that has first created this document object
    shared_with[list]: list of user_id's with whom the document is shared. (id's of Collaborators)
    created_on[datetime]: datetime when this object is created
    currently_edited_by[object]: User object of an owner or a collaborator that is currently working on it.
                                 Also works as a lock to identify whether this document free to edit or not.
    """
    document_name = models.CharField(max_length=128)
    document = models.FileField(upload_to="document/")
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="document_owner", null=True, blank=True)
    shared_with = models.JSONField(default=list)
    created_on = models.DateTimeField(auto_now_add=True)
    currently_edited_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True,
                                            related_name="document_currently_edited_by")

    class Meta:
        """
        A single owner can't have multiple documents with the same document name.
        """
        unique_together = ('owner', 'document_name',)

    def __str__(self):
        return f"{self.document_name}->{self.owner}"

    def add_collaborator(self, user_id):
        """
        Updating the list that contains the list of user ids(collaborators)
        user_id[int]: user id of a collaborator
        """
        self.shared_with.append(user_id)

    def remove_collaborator(self, user_id):
        """
        Updating the list that contains the list of user ids(collaborators)
        user_id[int]: user id of a collaborator
        """
        self.shared_with = [collaborator_id for collaborator_id in self.shared_with if collaborator_id != user_id]

    def remove_file_lock(self):
        """
        setting 'currently_edited_by' to None. When this field is not None, it means its being editted by a
        collaborator/owner else its free to edit.
        """
        self.currently_edited_by = None


class DocumentVersion(models.Model):
    """
    Model responsible for keeping track of all the versions of a document. 
    
    parent_document[object]: Foregin key of the parent document object of this document_version
    document[file]: the updated document file
    update_by[object]: user object who uploaded the updated document file
    created_on[datetime]: datetime when this object is created
    diff_file[file]: A file that contains the info of both the old lines and the new lines that replaced them.
                     Check the APIdocumentation PDF mentioned in the README.md
    """
    parent_document = models.ForeignKey("Document", on_delete=models.DO_NOTHING, null=True, blank=True)
    document = models.FileField(upload_to="document_version_files/", null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_on = models.DateTimeField(auto_now_add=True)
    diff_file = models.FileField(upload_to="document_diff_files/", null=True, blank=True)

    def __str__(self):
        return f"{self.document}"


