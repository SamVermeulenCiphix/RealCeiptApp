from django.db import models
from django.core.files.storage import FileSystemStorage

from .document_processing_functions.handle_uploaded_files import handle_uploaded_file

import os
import uuid
import datetime

''' 
    a class for storing all crucial data related to receipts
    properties:
        file_uuid = a generated, 32-length UUID to uniquely id files, even if they have the same name
        creator_id = the id of the user that uploaded the receipt
        file_displayname = the name shown on file overviews, same as the name of the original uploaded document
        file_fullpath = the full path to the file on the disk, includes subfolder structure
        upload_date = the date and time at which the file was uploaded
        html_datatable = an HTML representation of the extracted data, for easy display on pages
        url = the url that leads to the file. append this to the host url to download the file directly
        total_amount = the total calculated amount of euros on a receipt
'''
class Receipt(models.Model):
    def __str__(self):
        if self.file_displayname:
            return self.file_displayname
        else:
            return "No displayname given"

    # removes the attached/uploaded document from the disk
    def remove_file(self):
        fs = FileSystemStorage()
        fs.delete(self.file_fullpath)

    # activates file removal, then its own object instance
    def delete(self):
        self.remove_file()
        return super().delete()


    #saves the file to disk and saves crucial info as properties
    def save_file(self, file, creator_id):
        fs = FileSystemStorage()
        self.file_displayname = file.name
        self.upload_date = datetime.datetime.now()
        # to prevent duplicate filenames from interfering, we incorporate the uuid into the filename
        # this makes the exact name of a file on disk predictable from its UUID and original name
        file_fullname = str(self.file_uuid) + "_" + file.name
        ''' 
            to make the files less cluttered, we use a 2-layer folder structure based on the filename
            e.g. abcdsnowman.xlsx is saved in ab\\cd\\abcdsnowman.xlsx
        '''
        file_fullpath = file_fullname[:2] + "\\" + file_fullname[2:4]  + "\\" + file_fullname
        # if a duplicate file exist, this name is different from fullpath,
        #   because the FSS automatically appends a random string to the filename
        saved_name = fs.save(file_fullpath, file)
        # the original file is no longer needed, since we saved our own copy under a different name
        if os.path.isfile(file.name):
            os.remove(file.name)
        self.file_fullpath = saved_name
        self.url = "/ReceiptHub" + fs.url(saved_name)
        self.creator_id = creator_id
    
    # attempts to extract the data from the uploaded file
    # saves data only when this extraction is successful
    # does not take destructive action when it fails
    def handle_file(self):
        strStatusCode, strStatusMessage, dfExtractedData = handle_uploaded_file(self.file_fullpath)
        if strStatusCode == "SUCCESS":
            self.html_datatable = dfExtractedData.to_html()
            self.total_amount = dfExtractedData['ItemPrice'].sum()
        return strStatusCode, strStatusMessage

    # for explanations of these filetypes, refer to the class description above
    file_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator_id = models.CharField(max_length=32, null=True, blank=True)
    file_displayname = models.CharField(max_length=200, null=True, blank=True)
    file_fullpath = models.CharField(max_length=200, null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    html_datatable = models.CharField(max_length=5000, null=True, blank=True)
    url = models.CharField(max_length=200, null=True, blank=True)
    total_amount = models.IntegerField(null=True, blank=True)