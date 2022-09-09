<<<<<<< HEAD
import pandas as pd


def get_course_info(file_name):
    """ inputs file_name, reads excel file (specifically Sheet1),
        returns pandas dataframe """
    df = pd.read_excel('src/input_files/' + file_name, sheet_name='Sheet1')
    return df
=======
import pandas as pd


def get_course_info(file_name):
    """ inputs file_name, reads excel file (specifically Sheet1),
        returns pandas dataframe """
    df = pd.read_excel('src/input_files/' + file_name, sheet_name='Sheet1')
    return df
>>>>>>> 4d843d10a2a378353d9295a6c0fde3c7968a14a5
