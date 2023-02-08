# Author: Vincent Miller
# Date: 31 August 2022
# Updated: 28 September 2022, Added exceptions for MATH 1113, 2125, 5125, and electives

from alias_module import get_latest_id
from courses_needed_container import CoursesNeededContainer

import pandas as pd
import tabula
import re

def get_courses_needed(file_name):
    """Inputs file_name name as string, reads pdf tables into list of dataframes per table,
       merges list of dataframes into single dataframe, parses dataframe for CPSC and CYBR course id's,
       adds course id's to list, and returns list"""

    # read and import tables from pdf, returns as list of dataframes
    courses_needed_df_list = tabula.read_pdf(file_name, guess=False, pages='all', silent=False)
    
    # merge list of dataframes into one dataframe
    courses_needed_df = pd.DataFrame()
    for i in range(len(courses_needed_df_list)):
        courses_needed_df = pd.concat([courses_needed_df, courses_needed_df_list[i]], axis=0, ignore_index=True)

    # regex pattern is used to find course id, Ex: CPSC 1301, MATH 2125, etc.
    # course_pattern = r'[A-Z]{4}\s{1}\d{4}'  # pattern for all courses
    cpsc_pattern = r'CPSC\s{1}\d{4}'
    cybr_pattern = r'CYBR\s{1}\d{4}'
    pre_cal_pattern = r'MATH 1113'
    intro_discrete_pattern = r'MATH 2125'
    discrete_pattern = r'MATH 5125'
    elective_pattern1 = r'6 Credits in CPSC 3@'
    elective_pattern2 = r'3 Credits in CPSC 3@'
    
    
    # search dataframe for course id pattern, adds to list
    courses_needed_list = list()
    for col_name, _ in courses_needed_df.iteritems():
        # check column names for pattern
        cspc_col_match = re.search(cpsc_pattern, str(col_name))
        cybr_col_match = re.search(cybr_pattern, str(col_name))
        pre_cal_col_match = re.search(pre_cal_pattern, str(col_name))
        intro_discrete_col_match = re.search(intro_discrete_pattern, str(col_name))
        discrete_col_match = re.search(discrete_pattern, str(col_name))
        elective_col_match1 = re.search(elective_pattern1, str(col_name))
        elective_col_match2 = re.search(elective_pattern2, str(col_name))

        # add to list if found
        if cspc_col_match:
            courses_needed_list.append(get_latest_id(cspc_col_match.group()))
        elif cybr_col_match:
            courses_needed_list.append(get_latest_id(cybr_col_match.group()))
        elif pre_cal_col_match:
            courses_needed_list.append(get_latest_id(pre_cal_col_match.group()))
        elif intro_discrete_col_match:
            courses_needed_list.append(get_latest_id(intro_discrete_col_match.group()))
        elif discrete_col_match:
            courses_needed_list.append(get_latest_id(discrete_col_match.group()))
        elif elective_col_match1:
            courses_needed_list.append('CPSC 3XXX')
            courses_needed_list.append('CPSC 3XXX')
        elif elective_col_match2:
            courses_needed_list.append('CPSC 3XXX')
    
        for element in courses_needed_df[col_name]:
            # check data in column for pattern
            cspc_match = re.search(cpsc_pattern, str(element))
            cybr_match = re.search(cybr_pattern, str(element))
            pre_cal_match = re.search(pre_cal_pattern, str(element))
            intro_discrete_match = re.search(intro_discrete_pattern, str(element))
            discrete_match = re.search(discrete_pattern, str(element))
            elective_match1 = re.search(elective_pattern1, str(element))
            elective_match2 = re.search(elective_pattern2, str(element))

            # add to list if found
            if cspc_match:
                courses_needed_list.append(get_latest_id(cspc_match.group()))
            elif cybr_match:
                courses_needed_list.append(get_latest_id(cybr_match.group()))
            elif pre_cal_match:
                courses_needed_list.append(get_latest_id(pre_cal_match.group()))
            elif intro_discrete_match:
                courses_needed_list.append(get_latest_id(intro_discrete_match.group()))
            elif discrete_match:
                courses_needed_list.append(get_latest_id(discrete_match.group()))
            elif elective_match1:
                courses_needed_list.append('CPSC 3XXX')
                courses_needed_list.append('CPSC 3XXX')
            elif elective_match2:
                courses_needed_list.append('CPSC 3XXX')

    # sample inputs have CPSC 4115 mislabeled as CPSC 5115
    if 'CPSC 5115' in courses_needed_list:
        courses_needed_list.remove('CPSC 5115')
        if 'CPSC 4115' not in courses_needed_list:
            courses_needed_list.append('CPSC 4115')

    courses_needed_list.sort()

    # return courses_needed_list

    # TODO: this is just a stub
    result = CoursesNeededContainer("Degree Plan", courses_needed_list)
    result.stub_all_unresolved_nodes()
    return result

    
