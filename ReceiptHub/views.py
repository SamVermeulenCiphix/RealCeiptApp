from typing import Any
from django.db.models import F
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.core.files.storage import FileSystemStorage

import uuid

# from .forms import UploadFileForm
from .models import Question, Choice, Receipt

class IndexView(generic.ListView):
    template_name = "ReceiptHub/index.html"
    context_object_name = "latest_question_list"
    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]

class ReceiptView(generic.DetailView):
    model = Receipt
    template_name = "ReceiptHub/receipt.html"
    def get_object(self) -> Model:
        slug = self.kwargs.get('file_uuid')
        receipt = Receipt.objects.get(file_uuid=slug)
        return receipt

class ReceiptIndexView(generic.ListView):
    template_name = "ReceiptHub/receipt_index.html"
    context_object_name = "receipt_list"
    def get_queryset(self):
        return Receipt.objects.all().order_by("file_displayname")[:50]

def delete_receipt(request, file_uuid):
    receipt = get_object_or_404(Receipt, file_uuid=file_uuid)
    receipt.delete()
    return HttpResponseRedirect("/ReceiptHub/receipts/")


def upload_file(request):
    context = {}
    if request.method == "POST":
        # form = UploadFileForm(request.POST, request.FILES)
        print("File uploaded with name: " + request.FILES['file'].name)
        
        # if form.is_valid():
        print("Upload success")
        uploaded_file = request.FILES["file"]
        
        receipt = Receipt()
        
        receipt.save_file(uploaded_file)
        context['url'] = receipt.url
        context['shown_filename'] = receipt.file_displayname

        strStatusCode, strStatusMessage = receipt.handle_file()
        if strStatusCode == "SUCCESS":
            context['dataframe'] = receipt.html_datatable
            context['total_amount'] = receipt.total_amount
            receipt.save()
        elif strStatusCode == "ERROR":
            context['error'] = strStatusMessage
            receipt.delete()
        else:
            print("Unexpected status code returned: " + strStatusCode)
            context['error'] = f"An unexpected error code '{strStatusCode}' occurred when reading the data from the file! Message: {strStatusMessage}"
            receipt.delete()

        return render(request, "ReceiptHub/upload_view.html", context=context)
    else:
        form = Receipt()
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
