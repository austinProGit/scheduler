# Author: Vincent Miller
# Date: 12 November 2022
import pandas as pd


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
