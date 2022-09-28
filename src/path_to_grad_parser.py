import pandas as pd
import re

ROW_RANGES = [
    (2, 9),
    (11, 18),
    (20, 27),
    (29, 36),
    (38, 45)
]

def parse_path_to_grad(file_name):
    df = pd.read_excel(file_name, sheet_name='Sheet1')

#    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#        print(df)

    schedule = list()
    course_pattern = r'[A-Z]{4}\s{1}\d{4}'
    # TODO: CPSC elective patternn (is this even necessary given the application?)

    def parse_semester(_start, _stop, _column):
        _semester = []
        for i in range(_start, _stop):
            _course = df[_column][i]
            _course = re.search(course_pattern, str(_course))
            if _course is not None:
                _semester.append(_course.group())
        return _semester
    
    for (start, end) in ROW_RANGES:
        for column in ['Unnamed: 0', 'Unnamed: 2', 'Unnamed: 4']:
            schedule.append(parse_semester(start, end, column))
            
    return schedule

# first semester, all FALL is in this column



if __name__ == '__main__':
    schedule = parse_path_to_grad("input_files/Path to Graduation3.xlsx")
    for semester in schedule:
        print(semester)
