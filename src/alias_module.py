
# Thomas Merino
# 10/12/22
# CPSC 4175

import pandas as pd

ALIAS_FILE = 'TestFile.xlsx'

alias_translations = {}
OLD_LABEL = 'old_id'
NEW_LABEL = 'new_id'

def setup_aliases(alias_file=ALIAS_FILE):
    '''Setup the alias system from the contents of the passed filepath.'''
    courses_needed_df = pd.read_excel(alias_file, sheet_name='Sheet1')
    for _, row in courses_needed_df.iterrows():
        alias_translations[row[OLD_LABEL]] = row[NEW_LABEL]

def get_latest_id(id):
    '''Update the passed course id if it is outdated.'''
    return id if id not in alias_translations else alias_translations[id]
   
    
