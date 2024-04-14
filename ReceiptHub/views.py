from typing import Any
from django.db.models import F
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.core.files.storage import FileSystemStorage

import uuid

from .document_processing_functions.handle_uploaded_files import handle_uploaded_file
from .forms import UploadFileForm
from .models import Question, Choice

class IndexView(generic.ListView):
    template_name = "ReceiptHub/index.html"
    context_object_name = "latest_question_list"
    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


def upload_file(request):
    context = {}
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        print("File uploaded with name: " + request.FILES['file'].name)
        for field in form:
            print("Field Error:", field.name,  field.errors)
        
        if form.is_valid():
            print("Upload success")
            uploaded_file = request.FILES["file"]
            fs = FileSystemStorage()
            file_uuid = str(uuid.uuid4()) + "_" + uploaded_file.name
            saved_name = fs.save(file_uuid, uploaded_file)
            url = "/ReceiptHub" + fs.url(saved_name)
            print(url)
            context['url'] = url
            context['shown_filename'] = uploaded_file.name
            strStatusCode, strStatusMessage, dfExtractedData = handle_uploaded_file(saved_name)
            if strStatusCode == "SUCCESS":
                htmlDataFrame = dfExtractedData.to_html()
                context['dataframe'] = htmlDataFrame
            elif strStatusCode == "ERROR":
                context['error'] = strStatusMessage
            else:
                print("Unexpected status code returned: " + strStatusCode)
                context['error'] = "An unexpected error occurred when reading the data from the file!"
            form.save()
            context['form'] = form
            return render(request, "ReceiptHub/upload_view.html", context=context)
    else:
        form = UploadFileForm()
    return render(request, "ReceiptHub/upload_view.html", {"form": form})




class DetailView(generic.DetailView):
    model = Question
    template_name = "ReceiptHub/details.html"
    def get_queryset(self) -> QuerySet[Any]:
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "ReceiptHub/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "ReceiptHub/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("ReceiptHub:results", args=(question.id,)))


# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "ReceiptHub/results.html", {"question": question})
