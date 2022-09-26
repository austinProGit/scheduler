# Author: Vincent Miller
# Date: 7 September 2022
import pandas as pd

# MERINO: are we even using this?
def get_course_info(file_name):
    """ inputs file_name, reads Excel file_name (specifically Sheet1),
        returns pandas dataframe """
    # MERINO: removed "input_files/" from file_name
    df = pd.read_excel(file_name, sheet_name='Sheet1') # TODO: file_name path is lame, pick the one that works for you
    # df = pd.read_excel('input_files/' + file_name, sheet_name='Sheet1')
    return df
