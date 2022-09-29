# Author: Vincent Miller, Thomas Merino
# Date: 28 September 2022

import pandas as pd
import re


def parse_path_to_grad(file_name):
    """reads file name/path, parses courses out by semester, 
       returns schedule as list of lists, inner list is one semester"""
    
    def parse_semester(_start, _stop, _column):
        """helper function, parses courses from one semester"""
        _semester = []
        for i in range(_start, _stop):
            _course = df[_column][i]
            _course = re.search(course_pattern, str(_course))
            if _course is not None:
                _semester.append(_course.group())
        return _semester
    
    # courses are in these ranges in dataframe
    ROW_RANGES = [(2, 9),
                  (11, 18),
                  (20, 27),
                  (29, 36),
                  (38, 45)]
    
    df = pd.read_excel(file_name, sheet_name='Sheet1')
    schedule = list()
    course_pattern = r'[A-Z]{4}\s{1}\d{4}'

    # loops through to extract schedle, Unnamed: 0 = Fa, Unnamed: 2 = Sp, Unnamed: 4 = Su
    for (start, end) in ROW_RANGES:
        for column in ['Unnamed: 0', 'Unnamed: 2', 'Unnamed: 4']:
            schedule.append(parse_semester(start, end, column))
            
    return schedule
