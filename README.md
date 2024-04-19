# ReceiptHub

This app was commissioned by RealCeipt™️ 

It is an app where users can upload their receipts so they can be reimbursed at a later date

The receipt data is automatically extracted and displayed

Users can upload receipts and view and delete the receipts they own

In order to run the app locally, please refer to the documentation below

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

NOTES: 
- ```bash``` means that the command below it must be put in a terminal
- please run all commands separately
- in order to open a terminal, navigate to the folder where you want to download the project -> right click -> open in terminal


1. Clone the repository:

    ```bash
    git clone https://github.com/SamVermeulenCiphix/RealCeiptApp.git
    ```

2. Navigate to the project directory:

    ```bash
    cd RealCeiptApp
    ```

3. Create and activate a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate      # For Unix/Linux
    .\venv\Scripts\activate      # For Windows
    ```

4. Install dependencies using `pip`:

    ```bash
    pip install -r requirements.txt
    python -m pip install django-debug-toolbar
    ```

5. Prepare the database:
    
    ```bash
    python manage.py migrate ReceiptHub zero
    python manage.py makemigrations ReceiptHub
    python manage.py migrate ReceiptHub
    ```

## Usage

1. Run the Django development server:

    ```bash
    python manage.py runserver
    ```

2. Open your web browser and navigate to `http://127.0.0.1:8000/ReceiptHub/login/` to view the application.