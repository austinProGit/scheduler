"""
TODO: fix one of the dataframes from tabula gets included as column title data, needs to be data
TODO: find solution for electives, Ex: 6 Credits in CPSC 3@ or 4@ or 5@
"""
import pandas as pd
import tabula
import re


def get_courses_needed(file_name):
    """Inputs file name as string, reads pdf tables into list of dataframes per table,
       merges list of dataframes into single dataframe, parses dataframe for course id's,
       adds course id's to list (can change to set or other), and returns list
       A lot of this code is over commented, but I want to make sure all of you understand it."""
    # create blank dataframe
    courses_needed_df = pd.DataFrame()
    # read and import tables from pdf, returns as list of dataframes
    courses_needed_df_list = tabula.read_pdf('src/input_files/' + file_name, pages='all')
    # regex shenanigans
    # [A-Z]{4} looks for 4 capital letters, \s{1} looks for 1 space, \d{4} looks for 4 digits/numbers
    # pattern is used to find course id, Ex: CPSC 1301, MATH 2125, etc.
    course_pattern = r'[A-Z]{4}\s{1}\d{4}'
    courses_needed_list = list()

    # merge list of dataframes into one dataframe
    for i in range(len(courses_needed_df_list)):
        courses_needed_df = pd.concat([courses_needed_df, courses_needed_df_list[i]], axis=0, ignore_index=True)

    # re.findall(pattern, string), searches and returns ALL patterns as list of string or tuple
    # re.search(pattern, string), searches for FIRST match of pattern and returns as match object

    # search dataframe for course id pattern, adds to list
    for element in courses_needed_df['Unnamed: 0']:
        match = re.search(course_pattern, str(element))
        if match:
            courses_needed_list.append(match.group())

    return courses_needed_list
