# Author: Vincent Miller, Thomas Merino
# Date: 11 November 2022

import pandas as pd
import re

FIRST_ROW_PLACE = 2
LAST_ROW_PLACE = 100
FALL_CURSOR_INDEX = 0
SPRING_CURSOR_INDEX = 1
SUMMER_CURSOR_INDEX = 2
COLUMN_NAMES = ['Unnamed: 0', 'Unnamed: 2', 'Unnamed: 4']
ROW_ITERATION_LIMIT = 30
    
COURSE_PATTERN = r'[A-Z]{4}\s{1}\d{4}'
DELIMITING_PATTERN = r'(?i)total' # regex pattern to look for 'total' (ignoring case)

def parse_path_to_grad(file_name):
    """reads file name/path, parses courses out by semester, 
       returns schedule as list of lists, inner list is one semester"""
    
    # Create the cursors that manage the parsing of the catalog columns (Fall, Spring, and Summer)
    cursor_indices = [FIRST_ROW_PLACE for _ in range(3)]
    
    def get_entry(column):
        row_number = cursor_indices[column]
        column_name = COLUMN_NAMES[column]
        table_entry = df[column_name][row_number]
        if table_entry is None or type(table_entry) == float:
            table_entry = ''
        return table_entry
    
    def parse_semester_from_column(column, max_row):
        """helper function, parses courses from one semester"""
        _semester = []
        
        # Iterate until a delimiter is encountered or the maximum iterations is reached (consume courses)
        course_consume_counter = 0
        while course_consume_counter < ROW_ITERATION_LIMIT and cursor_indices[column] < max_row:
            table_entry = get_entry(column)
            course = re.search(COURSE_PATTERN, table_entry)
            delimiter = re.search(DELIMITING_PATTERN, table_entry)
                            
            cursor_indices[column] += 1
            course_consume_counter += 1
            
            if course is not None:
                _semester.append(course.group())
            elif delimiter is not None:
                break
        
        return _semester
    
    def should_loop():
        stop = min(LAST_ROW_PLACE, row_count)
        return cursor_indices[0] < stop or \
               cursor_indices[1] < stop or \
               cursor_indices[2] < stop
    
    
    df = pd.read_excel(file_name, sheet_name='Sheet1')
    row_count = len(df.index)
    schedule = []
    
    # loops through to extract schedule
    
    while should_loop():
        for index in [FALL_CURSOR_INDEX, SPRING_CURSOR_INDEX, SUMMER_CURSOR_INDEX]:
            schedule.append(parse_semester_from_column(index, row_count))
            
    return schedule

if __name__ == "__main__":
    result = parse_path_to_grad('input_files/Path to Graduation3.xlsx')
    
    for sem in result:
        print(sem)
    



#
#
#def parse_path_to_grad(file_name):
#    """reads file name/path, parses courses out by semester,
#       returns schedule as list of lists, inner list is one semester"""
#
#    # Create the cursors that manage the parsing of the catalog columns (Fall, Spring, and Summer)
#    fall_cursor = 2
#    spring_cursor = 2
#    summer_cursor = 2
#
#    def parse_semester(_start, _stop, _column):
#        """helper function, parses courses from one semester"""
#        _semester = []
#        for i in range(_start, _stop):
#            _course = df[_column][i]
#            _course = re.search(course_pattern, str(_course))
#            if _course is not None:
#                _semester.append(_course.group())
#        return _semester
#
#    # courses are in these ranges in dataframe
#    ROW_RANGES = [(2, 9),
#                  (11, 18),
#                  (20, 27),
#                  (29, 36),
#                  (38, 45)]
#
#    df = pd.read_excel(file_name, sheet_name='Sheet1')
#    schedule = list()
#    course_pattern = r'[A-Z]{4}\s{1}\d{4}'
#
#    # loops through to extract schedle, Unnamed: 0 = Fa, Unnamed: 2 = Sp, Unnamed: 4 = Su
#    for (start, end) in ROW_RANGES:
#        for column in ['Unnamed: 0', 'Unnamed: 2', 'Unnamed: 4']:
#            schedule.append(parse_semester(start, end, column))
#
#    return schedule
