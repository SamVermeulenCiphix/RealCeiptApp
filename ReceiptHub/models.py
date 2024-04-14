import datetime
from django.contrib import admin
from django.db import models
from django.utils import timezone



class Receipt(models.Model):
    def __str__(self):
        return "self.filename"
    
    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )

    def was_published_recently(self):
        return (self.pub_date >= timezone.now() - datetime.timedelta(days=1) and self.pub_date <= timezone.now())
    # FileField for the file, CharField for the HTML table, CharField for the filename, DateTimeField for the upload date
    # fields = ['uploaded_file',]
    # filename = models.CharField(max_length=200)
    # pub_date = models.DateTimeField("date published")
    


# TODO: REMOVE THESE TEST CLASSES
class Question(models.Model):
    def __str__(self):
        return self.question_text
    
    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )

    def was_published_recently(self):
        return (self.pub_date >= timezone.now() - datetime.timedelta(days=1) and self.pub_date <= timezone.now())

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")


class Choice(models.Model):
    def __str__(self):
        return self.choice_text
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
