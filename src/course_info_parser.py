import pandas as pd


def get_course_info(file_name):
    # df = pd.read_excel('input_files/ClassInfo.xlsx', sheet_name='Sheet1')
    df = pd.read_excel('src/input_files/' + file_name, sheet_name='Sheet1')
    return df
