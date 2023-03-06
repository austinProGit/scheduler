# Author: Thomas Merino
# Date: 27 February 2023

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Union
    from pathlib import Path

import pandas as pd


# This is the default file for constructing
COURSE_ALIAS_FILE: str = 'input_files/Aliases.xlsx'

alias_translations: dict[str, str] = {}
OLD_LABEL: str = 'old_id'
NEW_LABEL: str = 'new_id'

def setup_aliases(alias_file: Union[str, Path] = COURSE_ALIAS_FILE) -> None:
    '''Setup the alias system for course number updating from the contents of the passed filepath.'''

    courses_needed_df = pd.read_excel(alias_file, sheet_name='Sheet1')
    row: pd.Series
    for _, row in courses_needed_df.iterrows():
        alias_translations[row[OLD_LABEL]] = row[NEW_LABEL]

def get_latest_id(id: str) -> str:
    '''Update the passed course id if it is outdated.'''
    return id if id not in alias_translations else alias_translations[id]
   
if __name__ == '__main__':
    setup_aliases()
