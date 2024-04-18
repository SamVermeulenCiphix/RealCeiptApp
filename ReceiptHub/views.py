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
from django.utils.datastructures import MultiValueDictKeyError

import re
from .models import Receipt

# Check if user belongs to "Employees" group
def is_employee(user):
    return user.groups.filter(name='Employees').exists()
from django.utils.decorators import method_decorator


# shows the details of a single receipt
# prevents non-staff users from viewing receipts they don't own
def receipt_view(request, file_uuid):
    receipt = get_object_or_404(Receipt, file_uuid=file_uuid)
    # print(request.user.id)
    # print(receipt.creator_id)
    if request.user and request.user.is_staff or str(request.user.id) == str(receipt.creator_id):
        return render(request, "ReceiptHub/receipt.html", {'receipt': receipt})
    else:
        return render(request, "ReceiptHub/receipt.html", {'denied': "You do not have permission to view this receipt."})

# shows an overview of all receipts
# for staff, also shows which user created the receipt
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


# redirects from the blank URL to the main overview page
def redirect_to_index(request):
    return redirect("ReceiptHub:receipt_index")


# allows the user to log in
# redirects to receipt overview if login is successful
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


# logs the user out 
# if user isn't logged in, shows error message after redirect to login
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('ReceiptHub:login')
    else:
        messages.error(request, 'You were already logged out.')
        return redirect('ReceiptHub:login')

# allows the user to input various fields needed to create an account
def create_account(request):
    # validates if the given input is correct and can safely be put in the system
    def validate_data(username, email, first_name, last_name, password, confirm_password):
        arrErrors = []
        # Check if any fields are empty
        if not (username):
            arrErrors.append('Username is required')
        if not (email):
            arrErrors.append('Email is required')
        if not (first_name):
            arrErrors.append('First name is required')
        if not (last_name):
            arrErrors.append('Last name is required')
        if not (password):
            arrErrors.append('Please enter a password')
        if not (confirm_password):
            arrErrors.append('Please enter the password confirmation')

        # Check if passwords match
        if password and confirm_password and password != confirm_password:
            arrErrors.append('Passwords do not match')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            arrErrors.append('Username already exists')
        
        # Check if email address already exists
        if User.objects.filter(email=email).exists():
            arrErrors.append('Email address already exists')
        
        # prevent SQL injections and similar attacks in usernames, first names and last names
        if username and re.match(r"[!@#$%^&*()~`;:\s]", username):
            arrErrors.append('The characters "!@#$%^&*()~`;:" and spaces are not allowed in usernames')
        if first_name and re.match(r"[!@#$%^&*()~`;:]", first_name):
            arrErrors.append('The characters "!@#$%^&*()~`;:" are not allowed in first names')
        if last_name and re.match(r"[!@#$%^&*()~`;:]", last_name):
            arrErrors.append('The characters "!@#$%^&*()~`;:" are not allowed in last names')

        # checks if email is valid through regex
        strMailRegEx = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if email and not re.match(strMailRegEx, email).group(0) == email:
            arrErrors.append('Please enter a valid email address')
        
        return arrErrors
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # check input data for errors
        arrErrors = validate_data(username, email, first_name, last_name, password, confirm_password)
        if arrErrors:
            return render(request, 'ReceiptHub/create_account.html', {'errors': arrErrors})

        # Create user
        user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
        # Create or get the "Employees" group
        employees_group, _ = Group.objects.get_or_create(name='Employees')
        user.groups.add(employees_group)
        user.save()
        # Automatically logs the user in
        login(request, user)
        # Redirect to receipt overview
        messages.success(request, 'You have successfully created an account!')
        return redirect('ReceiptHub:receipt_index')
    return render(request, 'ReceiptHub/create_account.html')


# deletes a given receipt from the system
def delete_receipt(request, file_uuid):
    receipt = get_object_or_404(Receipt, file_uuid=file_uuid)
    # only staff or the creator of a receipt can delete it
    if request.user and (request.user.is_staff or str(request.user.id) == receipt.creator_id):
        receipt.delete()
        return redirect('ReceiptHub:receipt_index')
    else:
        messages.error(request, 'You are not authenticated to delete that receipt!')
        return redirect('ReceiptHub:receipt_index')
    

# upload a file to the system
def upload_file(request):
    context = {}
    # user must be authenticated
    if not request.user or not is_employee(request.user) and not request.user.is_staff:
        messages.add_message(request, messages.ERROR, 'Please log in to upload files.')
        return redirect('ReceiptHub:login')
    if request.method == "POST":
        # if the user hasn't selected a file before clicking upload, display error
        try:
            uploaded_file = request.FILES["file"]
        except MultiValueDictKeyError:
            messages.error(request, "An error occurred reading the file. \nPlease check if a file was selected before clicking upload.")
            print("MultiValueDictKeyError occurred when trying to access uploaded file")
            return render(request, "ReceiptHub/upload_view.html", context=context)
        # creates a new receipt and attaches the new file to it
        receipt = Receipt()
        receipt.save_file(uploaded_file, request.user.id)
        
        context['url'] = receipt.url
        context['shown_filename'] = receipt.file_displayname

        # try to extract the data of the file
        # if unsuccessful for any reason, the receipt object and uploaded file are deleted
        strStatusCode, strStatusMessage = receipt.handle_file()
        if strStatusCode == "SUCCESS":
            context['dataframe'] = receipt.html_datatable
            context['total_amount'] = receipt.total_amount
            receipt.save()
        # expected error, so message was returned
        elif strStatusCode == "ERROR":
            context['error'] = strStatusMessage
            receipt.delete()
        # a code other than SUCCESS or ERROR was returned, so unexpected error
        # therefore, log more details for easier bugfixing
        else:
            print("Unexpected status code returned: " + strStatusCode)
            context['error'] = f"An unexpected error code '{strStatusCode}' occurred when reading the data from the file! Message: {strStatusMessage}"
            receipt.delete()

    return render(request, "ReceiptHub/upload_view.html", context=context)
























































































































# you didn't see NOTHIN'
def hidden_from_view(request):
    return render(request, 'ReceiptHub/hidden_view.html')