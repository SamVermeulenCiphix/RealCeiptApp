# ReceiptHub

This app was commissioned by RealCeipt™️ 

It is an app where users can upload their receipts so they can be reimbursed at a later date

The receipt data is automatically extracted and displayed

Users can upload receipts and view and delete the receipts they own

In order to run the app locally, please refer to the documentation below

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

NOTE: "```bash```" below means that the command below it must be put in a terminal

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
    ```

## Usage

1. Run the Django development server:

    ```bash
    python manage.py runserver
    ```

2. Open your web browser and navigate to `http://127.0.0.1:8000/ReceiptHub/receipts/` to view the application.