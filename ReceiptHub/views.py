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

from .models import Receipt

# Check if user belongs to "Employees" group
def is_employee(user):
    return user.groups.filter(name='Employees').exists()
from django.utils.decorators import method_decorator


def receipt_view(request, file_uuid):
    receipt = get_object_or_404(Receipt, file_uuid=file_uuid)
    # print(request.user.id)
    # print(receipt.creator_id)
    if request.user and request.user.is_staff or str(request.user.id) == str(receipt.creator_id):
        return render(request, "ReceiptHub/receipt.html", {'receipt': receipt})
    else:
        return render(request, "ReceiptHub/receipt.html", {'denied': "You do not have permission to view this receipt."})
    
    


def receipt_index_view(request):
    # staff can view all receipts
    if request.user.is_staff:
        receipt_list = Receipt.objects.all().order_by("file_displayname")
    elif request.user.id:
        receipt_list = Receipt.objects.filter(creator_id=str(request.user.id)).order_by("file_displayname")
    else:
        receipt_list = []
    context = {
        'receipt_list': receipt_list,
        'user': request.user
    }
    return render(request, "ReceiptHub/receipt_index.html", context)


def login_view(request):
    if request.user.is_authenticated:
        messages.add_message(request, messages.SUCCESS, 'You are already logged in. Please log out to switch accounts!')
        return redirect('ReceiptHub:receipt_index')
    elif request.method == 'POST':
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


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('ReceiptHub:login')
    else:
        messages.error(request, 'You were already logged out.')
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
        messages.success(request, 'You have successfully created an account!')
        return redirect('ReceiptHub:receipt_index')
    return render(request, 'ReceiptHub/create_account.html')


def delete_receipt(request, file_uuid):
    receipt = get_object_or_404(Receipt, file_uuid=file_uuid)
    # only staff or the creator of a receipt can delete it
    # print(request.user.id)
    # print(receipt.creator_id)
    if request.user and (request.user.is_staff or str(request.user.id) == receipt.creator_id):
        receipt.delete()
        return redirect('ReceiptHub:receipt_index')
    else:
        messages.error(request, 'You are not authenticated to delete that receipt!')
        return redirect('ReceiptHub:receipt_index')
    


def upload_file(request):
    context = {}
    if not request.user or not is_employee(request.user) and not request.user.is_staff:
        # Return an 'invalid login' error message.
        messages.add_message(request, messages.ERROR, 'Please log in to upload files.')
        return redirect('ReceiptHub:login')
    if request.method == "POST":
        # print("File uploaded with name: " + request.FILES['file'].name)
        # print("Upload success")
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
    return render(request, "ReceiptHub/upload_view.html", context)