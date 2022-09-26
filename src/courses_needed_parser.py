# Author: Vincent Miller
# Date: 31 August 2022
"""
TODO: fix one of the dataframes from tabula gets included as column title data, needs to be data
TODO: find solution for electives, Ex: 6 Credits in CPSC 3@ or 4@ or 5@
TODO: decide on regex pattern
"""
import pandas as pd
import tabula
import re


def get_courses_needed(file_name):
    """Inputs file_name name as string, reads pdf tables into list of dataframes per table,
       merges list of dataframes into single dataframe, parses dataframe for CPSC and CYBR course id's,
       adds course id's to list, and returns list"""

    # read and import tables from pdf, returns as list of dataframes
    
    # MERINO: removed "input_files/" from file_name, turned off guess search area, and turned silent (no error output) on
    courses_needed_df_list = tabula.read_pdf(file_name, guess=False, pages='all', silent=False)
    
    # merge list of dataframes into one dataframe
    courses_needed_df = pd.DataFrame()
    for i in range(len(courses_needed_df_list)):
        courses_needed_df = pd.concat([courses_needed_df, courses_needed_df_list[i]], axis=0, ignore_index=True)

    # regex pattern is used to find course id, Ex: CPSC 1301, MATH 2125, etc.
    # course_pattern = r'[A-Z]{4}\s{1}\d{4}'  # pattern for all courses
    course_pattern2 = r'CPSC\s{1}\d{4}'  # pattern for CPSC courses
    course_pattern3 = r'CYBR\s{1}\d{4}'  # pattern for CYBR courses

    # MERINO: Commented out the origianl code in place of ugly code that handles dumbass inputs
    
    # search dataframe for course id pattern, adds to list
#    courses_needed_list = list()
#    for element in courses_needed_df['Unnamed: 0']:
#        cspc_match = re.search(course_pattern2, str(element))
#        cybr_match = re.search(course_pattern3, str(element))
#        if cspc_match:
#            courses_needed_list.append(cspc_match.group())
#        elif cybr_match:
#            courses_needed_list.append(cybr_match.group())
    
    courses_needed_list = list()
    for col_name, _ in courses_needed_df.iteritems():
    
        cspc_col_match = re.search(course_pattern2, str(col_name))
        cybr_col_match = re.search(course_pattern3, str(col_name))
        if cspc_col_match:
            courses_needed_list.append(cspc_col_match.group())
        elif cybr_col_match:
            courses_needed_list.append(cybr_col_match.group())
    
        for element in courses_needed_df[col_name]:
            cspc_match = re.search(course_pattern2, str(element))
            cybr_match = re.search(course_pattern3, str(element))
            if cspc_match:
                courses_needed_list.append(cspc_match.group())
            elif cybr_match:
                courses_needed_list.append(cybr_match.group())

    return courses_needed_list
