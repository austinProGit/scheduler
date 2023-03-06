# Thomas Merino
# 3/5/23
# CPSC 4176 Group Project

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING, Iterator
if TYPE_CHECKING:
    from typing import Any, Union, Optional
    from pathlib import Path

import pandas as pd

def dataframe_xlsx_writes(filename: Path, dataframe_mapping: dict[Union[int, str], pd.DataFrame]) -> None:
    '''Write to an xlsx file at the passed filename. This will write the to sheets (keys of dataframe mapping
    parameter) the contents in the dataframes (values of dataframe mapping parameter). That is, the dataframe
    mapping is a dictionary. This will override all of the contents of the sheets for the sheets specified.
    Other sheets will remain uneffected. This will also create a file if it does not exist.'''
    writer: pd.ExcelWriter
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        
        # Iterate over every sheet-dataframe pairing for writing
        sheet: Union[int, str]
        dataframe: pd.DataFrame
        for sheet, dataframe in dataframe_mapping.items():
            dataframe.to_excel(writer, sheet_name=sheet, index=False)

def dataframe_xlsx_write(filename: Path, sheet: Union[int, str], dataframe: pd.DataFrame) -> None:
    '''Save the passed dataframe to the sheet in the xlsx file at the passed filename. This will override all
    of the contents of the specified sheet. Other sheets will remain uneffected. This will also create a file
    if it does not exist.'''
    dataframe_xlsx_writes(filename, {sheet: dataframe})
    
def dataframe_xlsx_read(filename: Path, sheet: Union[int, str] = 0) -> Optional[pd.DataFrame]:
    '''Read the contents of the xlsx file at the passed filename and return it. Sheet may be not specified
    (gives the first sheet), a string (give the single dataframe), or a list of string (gives a dictionary of
    the dataframes).'''
    result: Optional[pd.DataFrame] = None
    try:
        result = pd.read_excel(filename, sheet_name=sheet)
    except (FileNotFoundError, ValueError):
        # NOTE: FileNotFoundError occurs when the file is not found, and ValueError occurs when the sheet is not found
        pass
    return result
    
