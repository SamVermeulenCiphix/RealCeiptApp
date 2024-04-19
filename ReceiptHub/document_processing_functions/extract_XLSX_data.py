import openpyxl
import pandas as pd
import os
import re


'''
    finds the coordinates of the "item" and "price" cells
    @input:
        xlsxDocument->xlsx workbook:    an excel document containing the data
    @output:
        strStatusCode->str:             SUCCESS or ERROR depending on extraction status
        strStatusMessage->str:          the message explaining the current status code
        sheetActiveSheet->xlsx sheet:   the active sheet of the document to be processed
        dictItemCoords->dict[str&int]:  contains the coordinates of the item and price headers as two letter-number pairs
'''
def find_header_coords(xlsxDocument):
    try:
        # finding the coordinates of the cells containing "price" and "item" 
        sheetActiveSheet = xlsxDocument.active
        # loop over all rows and their cells to find the item and price cells
        for row in sheetActiveSheet.iter_rows():
            for entry in row:
                if entry:
                    try:
                        # saves the coordinates of the item and price cells
                        # can't yet catch if there are multiple instances of item or price in the file
                        if 'item' in entry.value.lower():
                            strItemCoordLtr = re.search("[a-zA-Z]+", entry.coordinate).group()
                            strItemCoordNr = int(entry.coordinate.strip(strItemCoordLtr))
                        if 'price' in entry.value.lower():
                            strPriceCoordLtr = re.search("[a-zA-Z]+", entry.coordinate).group()
                            strPriceCoordNr = int(entry.coordinate.strip(strPriceCoordLtr))

                    except (AttributeError, TypeError):
                        continue
        if not strItemCoordLtr or not strItemCoordNr or not strPriceCoordLtr or not strPriceCoordNr:
            return "ERROR", f"Couldn't find item or price coordinate! ItemLtr: {strItemCoordLtr}, ItemNr: {strItemCoordNr}, PriceLtr: {strPriceCoordLtr}, PriceNr: {strPriceCoordNr}", None, None
    except Exception as e:
        return "ERROR", f"Couldn't find item or price coordinates due to exception! Message: {e}", None, None
    dictItemCoords = {}
    dictItemCoords['strItemCoordLtr'] = strItemCoordLtr
    dictItemCoords['strItemCoordNr'] = strItemCoordNr
    dictItemCoords['strPriceCoordLtr'] = strPriceCoordLtr
    dictItemCoords['strPriceCoordNr'] = strPriceCoordNr
    return "SUCCESS", "Found coordinates successfully", sheetActiveSheet, dictItemCoords


'''
    reads all the cells below the found header cells
    @input:
        sheetActiveSheet->xlsx sheet:   the active sheet of the document to be processed
        dictItemCoords->dict[str&int]:  contains the coordinates of the item and price headers as two letter-number pairs
    @output:
        strStatusCode->str:             SUCCESS or ERROR depending on extraction status
        strStatusMessage->str:          the message explaining the current status code
        arrExtractedItems->[str]:       contains all item names found
        arrExtractedPrices->[int]:      contains all item prices found
'''
def collect_data(sheetActiveSheet, dictItemCoords):
    try:
        arrExtractedItems = []
        arrExtractedPrices = []
        # we read a max of 1000 lines until we force a stop, also stops if no data found on a line
        for idx in range(1,1000):
            # reads the cell "idx" cells below the found headers, appends letter and number with "+"
            strItemVal = sheetActiveSheet[dictItemCoords['strItemCoordLtr'] + str(dictItemCoords['strItemCoordNr'] + idx)].value
            strPriceVal = sheetActiveSheet[dictItemCoords['strPriceCoordLtr'] + str(dictItemCoords['strPriceCoordNr'] + idx)].value
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
                    return "ERROR", f"Couldn't convert cell {dictItemCoords['strPriceCoordLtr'] + str(dictItemCoords['strPriceCoordNr'] + idx)} to integer! Message: {e}", None, None
    except Exception as e:
        return "ERROR", f"Couldn't extract values from XLSX file due to exception! Message: {e}", None, None
    return "SUCCESS", "Data gathered successfully", arrExtractedItems, arrExtractedPrices


'''
    extracts the contents of the given xlsx receipt
    @input:
        strFilePath->str:       the full filepath to the receipt
        isWriteOutput->bool:    if True, writes extracted csv to TEST_receipt_files/generated_output
    @output:
        strStatusCode->str:     ERROR or SUCCESS depending on extraction status
        strStatusMessage->str:  contains a message explaining the status code
        dfExtractedData->pd.DF: the extracted data in a pd.DataFrame, empty if extraction unsuccessful
'''
def extract_xlsx_data(strFilePath, isWriteOutput=False):
    xlsxDocument = openpyxl.load_workbook(strFilePath)
    
    # finds the coordinates of the "item" and "price" cells
    strStatusCode, strStatusMessage, sheetActiveSheet, dictItemCoords = find_header_coords(xlsxDocument)
    if strStatusCode == "ERROR":
        return strStatusCode, strStatusMessage, pd.DataFrame([])

    # gathers the data found below these header cells and returns them as arrays
    strStatusCode, strStatusMessage, arrExtractedItems, arrExtractedPrices = collect_data(sheetActiveSheet, dictItemCoords)
    if strStatusCode == "ERROR":
        return strStatusCode, strStatusMessage, pd.DataFrame([])
    
    # convert the found arrays to a pandas DF
    dictExtractedData = {'ItemName': arrExtractedItems, 'ItemPrice': arrExtractedPrices}
    dfExtractedData = pd.DataFrame(dictExtractedData)
    dfExtractedData.columns.name = "Nr"
    strStatusCode, strStatusMessage, dfExtractedData = ("SUCCESS", "Data parsing successful!", dfExtractedData)
    
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
    strRelTestFilePath = "TEST_receipt_files\input_files\XLSX\Receipt1.xlsx"
    strDirname = os.path.dirname(__file__)
    strAbsTestFilePath = os.path.join(strDirname, strRelTestFilePath)
    strStatusCode, strStatusMessage, dfExtractedData = extract_xlsx_data(strAbsTestFilePath, True)
    print(f"Status: {strStatusCode}, Message: {strStatusMessage}")
    
