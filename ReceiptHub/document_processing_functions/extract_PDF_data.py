import pdfplumber
import pandas as pd
import os
import re


def parse_data_to_df(arrExtractedPages):
    isDataFound = False
    arrParsedNames = []
    arrParsedPrices = []
    arrExtractedLines = []
    for page in arrExtractedPages:
        [arrExtractedLines.append(line) for line in str.split(page, '\n') if line]
    # print(f"Lines found: {str(len(arrExtractedLines))}")
    for idx, line in enumerate(arrExtractedLines):
        line = re.sub(" +", " ", line)
        arrSplitLine = [value.strip() for value in str.split(line, " ") if value.strip()]
        if isDataFound:
            if len(arrSplitLine) != 2:
                return "ERROR", f"Not exactly two values on line {str(idx)} starting below item and price headers", pd.DataFrame([])
            else:
                try:
                    strItemName = arrSplitLine[0]
                    arrParsedNames.append(strItemName)
                    intItemPrice = int(arrSplitLine[1])
                    arrParsedPrices.append(intItemPrice)
                except Exception as e:
                    strErrorMessage = f"Couldn't process values on line {str(idx)} starting below item and price headers. Message: {e}"
                    return "ERROR", strErrorMessage, pd.DataFrame([])
        else:
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





def extract_pdf_data(strFilePath, isWriteOutput=False) -> tuple[str, str, pd.DataFrame]:
    arrLines = []
    with pdfplumber.open(strFilePath) as pdf:
        for page in pdf.pages:
            arrLines.append(page.extract_text())
            # print(page.extract_text())
    strStatusCode, strStatusMessage, dfExtractedData = parse_data_to_df(arrLines)
    if isWriteOutput:
        try:
            strDirname = os.path.dirname(__file__)
            strOutputDirname = os.path.join(strDirname, "TEST_receipt_files\generated_output")
            _, strFileName = os.path.split(strFilePath)
            strOutputCSVPath = os.path.join(strOutputDirname, strFileName) + ".csv"
            dfExtractedData.to_csv(strOutputCSVPath)
            # print(f"DF CSV written to: {strOutputCSVPath}")
        except Exception as e:
            # not essential, so don't return exception message
            # print(f"ERROR: Couldn't write DF CSV to {strOutputCSVPath} with message: {e}")
            pass
    return strStatusCode, strStatusMessage, dfExtractedData



if __name__ == "__main__":
    strRelTestPDFPath = "TEST_receipt_files\input_files\PDF\Receipt8.pdf"
    strDirname = os.path.dirname(__file__)
    strAbsTestPDFPath = os.path.join(strDirname, strRelTestPDFPath)
    strStatusCode, strStatusMessage, dfExtractedData = extract_pdf_data(strAbsTestPDFPath, True)
    print(dfExtractedData.to_string())
    print(f"Status: {strStatusCode}, Message: {strStatusMessage}")