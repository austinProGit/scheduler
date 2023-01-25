# Thomas Merino
# 1/23/23
# CPSC 4176 Group Project

import pandas as pd

# TODO: None of this code is implemented

def dataframe_xlsx_writes(filename, dataframe_mapping):
    '''Write to an xlsx file at the passed filename. This will write the to sheets (keys of dataframe mapping parameter) the contents in the dataframes (values of dataframe mapping parameter). That is, the dataframe mapping is a dictionary. This will override all of the contents of the sheets for the sheets specified. Other sheets will remain uneffected. This will also create a file if it does not exist.'''
    
    with pd.ExcelWriter(filename, if_sheet_exists='replace', mode='a', engine='openpyxl') as writer:
        
        # Iterate over every sheet-dataframe pairing for writing
        for sheet, dataframe in dataframe_mapping.items():
            dataframe.to_excel(writer, sheet_name=sheet, index=False)

def dataframe_xlsx_write(filename, sheet, dataframe):
    '''Save the passed dataframe to the sheet in the xlsx file at the passed filename. This will override all of the contents of the specified sheet. Other sheets will remain uneffected. This will also create a file if it does not exist.'''
    dataframe_xlsx_writes(filename, {sheet: dataframe})
    
def dataframe_xlsx_read(filename, sheet=0):
    '''Read the contents of the xlsx file at the passed filename and return it. Sheet may be not specified (gives the first sheet), a string (give the single dataframe), or a list of string (gives a dictionary of the dataframes).'''
    result = None
    try:
        result = pd.read_excel(filename, sheet_name=sheet)
    except (FileNotFoundError, ValueError):
        # NOTE: FileNotFoundError occurs when the file is not found, and ValueError occurs when the sheet is not found
        pass
    return result
    
