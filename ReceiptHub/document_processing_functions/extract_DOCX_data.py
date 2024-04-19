import docx
import pandas as pd
import os
import re


'''
    parses the given text to a pandas dataframe
    @input:
        arrExtractedPages->[str]:   array containing all lines read from the document
    @output:
        strStatusCode->str:     ERROR or SUCCESS depending on extraction status
        strStatusMessage->str:  contains a message explaining the status code
        dfExtractedData->pd.DF: the extracted data in a pd.DataFrame, empty if extraction unsuccessful
'''
def parse_data_to_df(arrExtractedPages):
    # will be set to true when parsable data is found
    isDataFound = False
    arrParsedNames = []
    arrParsedPrices = []
    arrExtractedLines = []
    # the extracted text is in paragraphs, we split it by \n and append it to arrExtractedLines if the line isn't empty
    for page in arrExtractedPages:
        [arrExtractedLines.append(line) for line in str.split(page, '\n') if line]
    # print(f"Lines found: {str(len(arrExtractedLines))}")
    # for every line found in the document
    for idx, line in enumerate(arrExtractedLines):
        # replace any random amount of spaces/tabs etc. with single spaces
        line = re.sub("\s+", " ", line)
        # split on spaces to find all separate words in a file
        arrSplitLine = [value.strip() for value in str.split(line, " ") if value.strip()]
        if isDataFound:
            if len(arrSplitLine) != 2:
                return "ERROR", f"Not exactly two values on line {str(idx)} starting below item and price headers", pd.DataFrame([])
            else:
                try:
                    strItemName = arrSplitLine[0].strip()
                    arrParsedNames.append(strItemName)
                    intItemPrice = int(arrSplitLine[1])
                    arrParsedPrices.append(intItemPrice)
                except Exception as e:
                    strErrorMessage = f"Couldn't process values on line {str(idx)} starting below item and price headers. Message: {e}"
                    return "ERROR", strErrorMessage, pd.DataFrame([])
        else:
            # if we find item and price in a line, data is below it, so start parsing data
            if len(arrSplitLine) == 2 and arrSplitLine[0].lower() == "item" and arrSplitLine[1].lower() == "price":
                # print(f"Line {idx} is start of data! Line text: {line}")
                isDataFound = True
            else:
                pass
                # print(f"Start of data NOT found on line {str(idx)}! Line text: {line}")
    dictExtractedData = {'ItemName': arrParsedNames, 'ItemPrice': arrParsedPrices}
    dfExtractedData = pd.DataFrame(dictExtractedData)
    dfExtractedData.columns.name = "Nr"
    return "SUCCESS", "Data parsing successful!", dfExtractedData




'''
    extracts the contents of the given docx receipt
    @input:
        strFilePath->str:       the full filepath to the receipt
        isWriteOutput->bool:    if True, writes extracted csv to TEST_receipt_files/generated_output
    @output:
        strStatusCode->str:     ERROR or SUCCESS depending on extraction status
        strStatusMessage->str:  contains a message explaining the status code
        dfExtractedData->pd.DF: the extracted data in a pd.DataFrame, empty if extraction unsuccessful
'''
def extract_docx_data(strFilePath, isWriteOutput=False):
    arrLines = []
    # reads the text in the document
    docxDocument = docx.Document(strFilePath)
    for paragraph in docxDocument.paragraphs:
        arrLines.append(paragraph.text)
        # print(paragraph.text)
    # tries to convert the found text to a DF
    strStatusCode, strStatusMessage, dfExtractedData = parse_data_to_df(arrLines)
    # write the DF to disk as a CSV
    if isWriteOutput:
        try:
            # dir of current file
            strDirname = os.path.dirname(__file__)
            strOutputDirname = os.path.join(strDirname, "TEST_receipt_files\generated_output")
            # gets full name of file
            _, strFileName = os.path.split(strFilePath)
            strOutputCSVPath = os.path.join(strOutputDirname, strFileName) + ".csv"
            dfExtractedData.to_csv(strOutputCSVPath)
            # print(f"DF CSV written to: {strOutputCSVPath}")
        except Exception as e:
            # not essential, so don't return exception message
            print(f"ERROR: Couldn't write DF CSV to {strOutputCSVPath} with message: {e}")
    return strStatusCode, strStatusMessage, dfExtractedData




if __name__ == "__main__":
    strRelTestFilePath = "TEST_receipt_files\input_files\DOCX\Receipt10.docx"
    strDirname = os.path.dirname(__file__)
    strAbsTestFilePath = os.path.join(strDirname, strRelTestFilePath)
    strStatusCode, strStatusMessage, dfExtractedData = extract_docx_data(strAbsTestFilePath, True)
    print(f"Status: {strStatusCode}, Message: {strStatusMessage}")
    
