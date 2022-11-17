# Author: Vincent Miller, Thomas Merino
# Date: 11 November 2022

from alias_module import get_latest_id
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
                _semester.append(get_latest_id(course.group()))
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
    
    # Remove the empty YEARS at the end of the schedule (do not make empty, though)
    # This should ensure the end is always consistent (Summer in this case)
    while len(schedule) > 3 and not schedule[-1] and \
                                not schedule[-2] and \
                                not schedule[-3]:
        # Pop an entire year of courses
        schedule.pop()
        schedule.pop()
        schedule.pop()
    
    return schedule

if __name__ == "__main__":
    result = parse_path_to_grad('input_files/Path to Graduation3.xlsx')
    
    for sem in result:
        print(sem)
    


