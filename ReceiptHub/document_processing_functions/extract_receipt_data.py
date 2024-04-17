import os
import pandas as pd
# when running this file locally, remove the "." for relative imports
# when running it through the Django app, keep the "."
from .extract_DOCX_data import extract_docx_data
from .extract_PDF_data import extract_pdf_data
from .extract_XLSX_data import extract_xlsx_data

'''
    extracts the content of a receipt
    currently only works for PDF, DOCX and XLSX files
    @input: 
        strFilePath=str: absolute filepath to where the receipt is stored
    @returns: 
        str: status code
        str: status message
        pd_df: extracted contents
'''
def extract_receipt_content(strFilePath: str):
    _, strFileExtension = os.path.splitext(strFilePath)
    isWriteExtractedData = True
    
    if strFileExtension.lower() == ".pdf":
        # print("Given filetype is PDF for file: " + strFilePath)
        return extract_pdf_data(strFilePath, isWriteExtractedData)
    
    elif strFileExtension.lower() == ".docx":
        # print("Given filetype is DOCX for file: " + strFilePath)
        return extract_docx_data(strFilePath, isWriteExtractedData)
    
    elif strFileExtension.lower() == ".xlsx":
        # print("Given filetype is XLSX for file: " + strFilePath)
        return extract_xlsx_data(strFilePath, isWriteExtractedData)
    
    else:

        strStatusMessage = f"Extracted filetype \"{strFileExtension}\" is not accepted for file: " + os.path.basename(strFilePath)
        print(strStatusMessage)
        return "ERROR", strStatusMessage, pd.DataFrame([]) 


'''
This function tests file extraction for PDF, XLSX and DOCX files
It searches the given folder and its subfolders for these filetypes,
    then extracts their data and logs all errors and successful extractions

@input:
    strTestReceiptFolder=str: absolute path of folder that will be checked for receipt files
@returns:
    bool: True if all files were read and processed successfully, else False
'''
def test_extraction_all_types(strTestReceiptFolder) -> str:
    
    if not os.path.isdir(strTestReceiptFolder):
        return "ERROR", f"Given folder {strTestReceiptFolder} does not refer to an existing directory"
        
    arrFoundFiles = []
    arrNotAcceptedFiles = []
    for path, _, files in os.walk(strTestReceiptFolder):
        for name in files:
            _, strFileExtension = os.path.splitext(name)
            if strFileExtension.lower() in [".docx",".xlsx",".pdf"]:
                arrFoundFiles.append(os.path.join(path, name))
            else:
                arrNotAcceptedFiles.append(os.path.join(path, name))
    print("Found files usable for extraction: " + '\n'  + '\n'.join(arrFoundFiles) + '\n')
    print("Found files NOT usable for extraction: " + '\n'  + '\n'.join(arrNotAcceptedFiles) + '\n')


    arrResults = [extract_receipt_content(file) for file in arrFoundFiles]
    isAllSuccessful = True
    for idx, tpResult in enumerate(arrResults):
        print(f"Status: {tpResult[0]} with message: {tpResult[1]} for file: {arrFoundFiles[idx]}")
        if tpResult[0] == "ERROR":
            isAllSuccessful = False
    
    return isAllSuccessful

if __name__ == "__main__": 
    strInputFolderPath = "ReceiptHub/document_processing_functions/TEST_receipt_files/input_files"
    strExpectedOutputFPath = "ReceiptHub\document_processing_functions\TEST_receipt_files\generated_output"
    test_extraction_all_types(strInputFolderPath, strExpectedOutputFPath)