from django.db.models import Model
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Receipt
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
import uuid

from .models import Receipt

# Check if user belongs to "Employees" group
def is_employee(user):
    return user.groups.filter(name='Employees').exists()
from django.utils.decorators import method_decorator


# Require login and "Employees" group membership
# @login_required
# @user_passes_test(is_employee)
def receipt_view(request, file_uuid):
    receipt = get_object_or_404(Receipt, file_uuid=file_uuid)
    print(request.user.id)
    print(receipt.creator_id)
    if not request.user or str(request.user.id) != str(receipt.creator_id):
        return render(request, "ReceiptHub/receipt.html", {'denied': "You do not have permission to view this receipt."})
    
    return render(request, "ReceiptHub/receipt.html", {'receipt': receipt})

# Require login and "Employees" group membership
# @method_decorator(login_required, name='dispatch')
# @method_decorator(user_passes_test(is_employee), name='dispatch')
# class ReceiptView(generic.DetailView):
#     model = Receipt
#     template_name = "ReceiptHub/receipt.html"
#     def get_object(self) -> Model:
#         slug = self.kwargs.get('file_uuid')
#         receipt = Receipt.objects.get(file_uuid=slug)
#         return receipt

def receipt_index_view(request):
    if request.user.id:
        receipt_list = Receipt.objects.filter(creator_id=str(request.user.id)).order_by("file_displayname")[:50]
    else:
        receipt_list = []
    context = {
        'receipt_list': receipt_list
    }
    return render(request, "ReceiptHub/receipt_index.html", context)

# # Require login and "Employees" group membership
# @method_decorator(login_required, name='dispatch')
# @method_decorator(user_passes_test(is_employee), name='dispatch')
class ReceiptIndexView(generic.ListView):
    template_name = "ReceiptHub/receipt_index.html"
    context_object_name = "receipt_list"
    def get_queryset(self):
        return Receipt.objects.all().order_by("file_displayname")[:50]


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('ReceiptHub:receipt_index')
        else:
            # Return an 'invalid login' error message.
            messages.add_message(request, messages.ERROR, 'Invalid username or password.')
            return redirect('ReceiptHub:login')
    else:
        return render(request, 'ReceiptHub/login.html')



# @login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('ReceiptHub:login')


def create_account(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check if any fields are empty
        if not (username and email and first_name and last_name and password and confirm_password):
            return render(request, 'ReceiptHub/create_account.html', {'error': 'All fields are required'})
        
        # Check if passwords match
        if password != confirm_password:
            return render(request, 'ReceiptHub/create_account.html', {'error': 'Passwords do not match'})
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'ReceiptHub/create_account.html', {'error': 'Username already exists'})
        
        # Check if email address already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'ReceiptHub/create_account.html', {'error': 'Email address already exists'})
        

        # Create user
        user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
        # Create or get the "Employees" group
        employees_group, _ = Group.objects.get_or_create(name='Employees')
        user.groups.add(employees_group)
        user.save()
        # user = authenticate(request, username=username, password=password)
        login(request, user)
        # Redirect to a success page.
        return redirect('ReceiptHub:receipt_index')
        
    
    return render(request, 'ReceiptHub/create_account.html')



# Require login and "Employees" group membership
# @login_required
# @user_passes_test(is_employee)
def delete_receipt(request, file_uuid):
    receipt = get_object_or_404(Receipt, file_uuid=file_uuid)
    receipt.delete()
    return redirect('ReceiptHub:receipt_index')

# Require login and "Employees" group membership
# @login_required
# @user_passes_test(is_employee)
def upload_file(request):
    context = {}
    print(request.user)
    print(request.user.pk)
    if not request.user or not is_employee(request.user):
        # Return an 'invalid login' error message.
        messages.add_message(request, messages.ERROR, 'Please log in to upload files.')
        return redirect('ReceiptHub:login')
    if request.method == "POST":
        # form = UploadFileForm(request.POST, request.FILES)
        print("File uploaded with name: " + request.FILES['file'].name)
        
        # if form.is_valid():
        print("Upload success")
        uploaded_file = request.FILES["file"]
        
        receipt = Receipt()
        
        receipt.save_file(uploaded_file, request.user.id)
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
    # else:
        # form = Receipt()
    return render(request, "ReceiptHub/upload_view.html", context)


# class DetailView(generic.DetailView):
#     model = Question
#     template_name = "ReceiptHub/details.html"
#     def get_queryset(self) -> QuerySet[Any]:
#         return Question.objects.filter(pub_date__lte=timezone.now())


# class ResultsView(generic.DetailView):
#     model = Question
#     template_name = "ReceiptHub/results.html"


# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST["choice"])
#     except (KeyError, Choice.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(
#             request,
#             "ReceiptHub/detail.html",
#             {
#                 "question": question,
#                 "error_message": "You didn't select a choice.",
#             },
#         )
#     else:
#         selected_choice.votes = F("votes") + 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse("ReceiptHub:results", args=(question.id,)))


# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "ReceiptHub/results.html", {"question": question})
