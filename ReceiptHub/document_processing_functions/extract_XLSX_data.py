import openpyxl
import pandas as pd
import os
import re


# def parse_data_to_df(arrExtractedPages):
#     isDataFound = False
#     arrParsedNames = []
#     arrParsedPrices = []
#     arrExtractedLines = []
#     for page in arrExtractedPages:
#         [arrExtractedLines.append(line) for line in str.split(page, '\n') if line]
#     print(f"Lines found: {str(len(arrExtractedLines))}")
#     for idx, line in enumerate(arrExtractedLines):
#         line = re.sub("\s+", " ", line)
#         arrSplitLine = str.split(line, " ")
#         if isDataFound:
#             if len(arrSplitLine) != 2:
#                 return "ERROR", f"Not exactly two values on line {str(idx)} starting below item and price headers", pd.DataFrame([])
#             else:
#                 try:
#                     strItemName = arrSplitLine[0]
#                     arrParsedNames.append(strItemName)
#                     intItemPrice = int(arrSplitLine[1])
#                     arrParsedPrices.append(intItemPrice)
#                 except Exception as e:
#                     strErrorMessage = f"Couldn't process values on line {str(idx)} starting below item and price headers. Message: {e}"
#                     return "ERROR", strErrorMessage, pd.DataFrame([])
#         else:
#             if len(arrSplitLine) == 2 and arrSplitLine[0].lower() == "item" and arrSplitLine[1].lower() == "price":
#                 print(f"Line {idx} is start of data! Line text: {line}")
#                 isDataFound = True
#             else:
#                 print(f"Start of data NOT found on line {str(idx)}! Line text: {line}")
#     dictExtractedData = {'ItemName': arrParsedNames, 'ItemPrice': arrParsedPrices}
#     dfExtractedData = pd.DataFrame(dictExtractedData)
#     dfExtractedData.index.name = "Nr"
#     return "SUCCESS", "Data parsing successful!", dfExtractedData





def extract_data(strFilePath, isWriteOutput=False) -> tuple[str, str, pd.DataFrame]:
    xlsxDocument = openpyxl.load_workbook(strFilePath)
    
    try:
        # finding the coordinates of the cells containing "price" and "item" 
        sheetActiveSheet = xlsxDocument.active
        for row in sheetActiveSheet.iter_rows():
            for entry in row:
                if entry:
                    try:
                        if 'item' in entry.value.lower():
                            strItemCoordLtr = re.search("[a-zA-Z]+", entry.coordinate).group()
                            strItemCoordNr = int(entry.coordinate.strip(strItemCoordLtr))
                        if 'price' in entry.value.lower():
                            strPriceCoordLtr = re.search("[a-zA-Z]+", entry.coordinate).group()
                            strPriceCoordNr = int(entry.coordinate.strip(strPriceCoordLtr))

                    except (AttributeError, TypeError):
                        continue
        if not strItemCoordLtr or not strItemCoordNr or not strPriceCoordLtr or not strPriceCoordNr:
            return "ERROR", f"Couldn't find item or price coordinate! ItemLtr: {strItemCoordLtr}, ItemNr: {strItemCoordNr}, PriceLtr: {strPriceCoordLtr}, PriceNr: {strPriceCoordNr}", pd.DataFrame([])
    except Exception as e:
        return "ERROR", f"Couldn't find item or price coordinates due to exception! Message: {e}", pd.DataFrame([])


    try:
        arrExtractedItems = []
        arrExtractedPrices = []
        for idx in range(1,1000):
            strItemVal = sheetActiveSheet[strItemCoordLtr + str(strItemCoordNr + idx)].value
            strPriceVal = sheetActiveSheet[strPriceCoordLtr + str(strPriceCoordNr + idx)].value
            if not strItemVal:
                # print(F"End of data found in cell: {strItemVal}. Stopping data extraction!")
                break
            elif not strPriceVal:
                # print(F"End of data found in cell: {strItemVal}. Stopping data extraction!")
                break
            else:
                arrExtractedItems.append(strItemVal)
                try:
                    arrExtractedPrices.append(int(strPriceVal))
                except ValueError as e:
                    return "ERROR", f"Couldn't convert cell {strPriceCoordLtr + str(strPriceCoordNr + idx)} to integer! Message: {e}", pd.DataFrame([])
    except Exception as e:
        return "ERROR", f"Couldn't extract values from XLSX file due to exception! Message: {e}", pd.DataFrame([])

    

    # strStatusCode, strStatusMessage, dfExtractedData = parse_data_to_df(arrLines)
    dictExtractedData = {'ItemName': arrExtractedItems, 'ItemPrice': arrExtractedPrices}
    dfExtractedData = pd.DataFrame(dictExtractedData)
    dfExtractedData.index.name = "Nr"
    strStatusCode, strStatusMessage, dfExtractedData = ("SUCCESS", "Data parsing successful!", dfExtractedData)
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
    strRelTestFilePath = "TEST_receipt_files\input_files\XLSX\Receipt1.xlsx"
    strDirname = os.path.dirname(__file__)
    strAbsTestFilePath = os.path.join(strDirname, strRelTestFilePath)
    strStatusCode, strStatusMessage, dfExtractedData = extract_data(strAbsTestFilePath, True)
    print(f"Status: {strStatusCode}, Message: {strStatusMessage}")
    
