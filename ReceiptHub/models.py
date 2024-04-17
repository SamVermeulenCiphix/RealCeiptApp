import datetime
from django.contrib import admin
from django.db import models
from django.core.files.storage import FileSystemStorage
from .document_processing_functions.handle_uploaded_files import handle_uploaded_file
import uuid
import os


class Receipt(models.Model):
    def __str__(self):
        if self.file_displayname:
            return self.file_displayname
        else:
            return "No displayname given"

    def remove_file(self):
        fs = FileSystemStorage()
        fs.delete(self.file_fullpath)

    def delete(self):
        self.remove_file()
        return super().delete()

    def save_file(self, file, creator_id):
        fs = FileSystemStorage()
        self.file_displayname = file.name
        self.upload_date = datetime.datetime.now()
        file_fullname = str(self.file_uuid) + "_" + file.name
        ''' 
            to make the files less cluttered, we use a 2-layer folder structure based on the filename
            abcdsnowman.xlsx is saved in ab\\cd\\abcdsnowman.xlsx
        '''
        file_fullpath = file_fullname[:2] + "\\" + file_fullname[2:4]  + "\\" + file_fullname
        saved_name = fs.save(file_fullpath, file)
        # self.uploaded_file = open(os.path.join(settings.MEDIA_ROOT, saved_name), encoding='latin-1').read()
        if os.path.isfile(file.name):
            os.remove(file.name)
        self.file_fullpath = saved_name
        # TODO: SET UP THE URL PREFIX DYNAMICALLY
        self.url = "/ReceiptHub" + fs.url(saved_name)
        self.creator_id = creator_id
        
    def handle_file(self):
        strStatusCode, strStatusMessage, dfExtractedData = handle_uploaded_file(self.file_fullpath)
        if strStatusCode == "SUCCESS":
            self.html_datatable = dfExtractedData.to_html()
            self.total_amount = dfExtractedData['ItemPrice'].sum()
        return strStatusCode, strStatusMessage

    # uploaded_file = models.FileField(null=True, blank=True)
    file_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator_id = models.CharField(max_length=32, null=True, blank=True)
    file_displayname = models.CharField(max_length=200, null=True, blank=True)
    file_fullpath = models.CharField(max_length=200, null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    html_datatable = models.CharField(max_length=5000, null=True, blank=True)
    url = models.CharField(max_length=200, null=True, blank=True)
    total_amount = models.IntegerField(null=True, blank=True)