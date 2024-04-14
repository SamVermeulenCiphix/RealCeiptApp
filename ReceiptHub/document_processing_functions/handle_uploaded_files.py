import pandas as pd
from datetime import datetime
from .extract_receipt_data import extract_receipt_content
from django.conf import settings
import os


def generate_filepath_id(file):
    return f"{int(round(datetime.now().timestamp()))}"


def handle_uploaded_file(file):
    # strFileID = generate_filepath_id(file)
    # with open(f"uploaded_receipts/{strFileID}_{file.name}") as f:
    #     for chunk in file.chunks():
    #         f.write(chunk)
    strFilePath = os.path.join(settings.MEDIA_ROOT, file)
    strStatusCode, strStatusMessage, dfExtractedData = extract_receipt_content(strFilePath)
    print(f"{strStatusCode}! {strStatusMessage}")
    print(f"Extracted data: \n {dfExtractedData.to_string()}")
    return strStatusCode, strStatusMessage, dfExtractedData


if __name__ == "__main__":
    print(generate_filepath_id("test"))