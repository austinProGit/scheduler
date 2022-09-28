# Author: Vincent Miller
# Date: 7 September 2022
import pandas as pd

# MERINO: are we even using this?
# V: You specifically demanded this file. We modeled to have this file.


def get_course_info(file_name):
    """ inputs file_name, reads Excel file_name (specifically Sheet1),
        returns pandas dataframe """
    df = pd.read_excel(file_name, sheet_name='Sheet1')
    return df
