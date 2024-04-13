import os
import pandas as pd
import extract_DOCX_data, extract_PDF_data, extract_XLSX_data


def extract_receipt_content(strFilePath: str) -> tuple[str, str, pd.DataFrame]:
    _, strFileExtension = os.path.splitext(strFilePath)
    isWriteExtractedData = True
    
    if strFileExtension.lower() == ".pdf":
        # print("Given filetype is PDF for file: " + strFilePath)
        return extract_PDF_data.extract_data(strFilePath, isWriteExtractedData)
    
    elif strFileExtension.lower() == ".docx":
        # print("Given filetype is DOCX for file: " + strFilePath)
        return extract_DOCX_data.extract_data(strFilePath, isWriteExtractedData)
    
    elif strFileExtension.lower() == ".xlsx":
        # print("Given filetype is XLSX for file: " + strFilePath)
        return extract_XLSX_data.extract_data(strFilePath, isWriteExtractedData)
    
    else:
        strStatusMessage = f"Extracted filetype \"{strFileExtension}\" is not accepted for file: " + strFilePath
        print(strStatusMessage)
        return "ERROR", strStatusMessage, pd.DataFrame([]) 


'''
This function tests file extraction for PDF, XLSX and DOCX files
It searches the given folder and its subfolders for these filetypes,
then extracts their data and compares it to the expected result
@input
'''
def test_extraction_all_types(strTestReceiptFolder, strTestReceiptContentFolder) -> str:
    
    if not os.path.isdir(strTestReceiptFolder):
        return "ERROR", f"Given folder {strTestReceiptFolder} does not refer to an existing directory"
    
    if not os.path.isdir(strTestReceiptContentFolder):
        return "ERROR", f"Given folder {strTestReceiptContentFolder} does not refer to an existing directory"
    
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

    #TODO: match the given files with a result file
    #   Still a WIP, since I need to generate them first

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