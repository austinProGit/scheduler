# Author: Vincent Miller
# Date: 7 September 2022
import pandas as pd


def get_course_info(file_name):
    """ inputs file_name, reads Excel file_name (specifically Sheet1),
        returns pandas dataframe """
    df = pd.read_excel('src/input_files/' + file_name, sheet_name='Sheet1') # TODO: file_name path is lame, pick the one that works for you
    # df = pd.read_excel('input_files/' + file_name, sheet_name='Sheet1')
    return df
