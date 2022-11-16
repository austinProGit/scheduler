# Author: Vincent Miller
# Date: 12 November 2022
import pandas as pd

# TODO: one of these approaches

class Alias:
    """create alias instance using path to Aliases.xlsx
       allows for updating of known bad course id with good course id"""
    def __init__(self, alias_file):
        self.alias_df = pd.read_excel(alias_file, sheet_name='Sheet1')

    def update_alias(self, course_id):
        try:
            return self.alias_df.loc[self.alias_df['old_id'] == course_id]['new_id'].tolist()[0]
        except IndexError:
            return course_id



ALIAS_FILE = 'Aliases.xlsx'

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
   
    
