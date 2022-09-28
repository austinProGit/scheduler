import pandas as pd
import re

# def parse_path_to_grad(file_name)
df = pd.read_excel("input_files/Path to Graduation1.xlsx", sheet_name='Sheet1')

with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print(df)

schedule = list()
course_pattern = r'[A-Z]{4}\s{1}\d{4}'
# TODO: CPSC elective pattern


def parse_semester(_start, _stop, _column):
    _semester = []
    for i in range(_start, _stop):
        _course = df[_column][i]
        _course = re.search(course_pattern, str(_course))
        if _course is not None:
            semester.append(_course.group())
    return _semester


# first semester, all FALL is in this column

semester = parse_semester(2, 9, 'Unnamed: 0')
print(semester)
schedule.append(semester)
print(schedule)
semester = parse_semester(2, 9, 'Unnamed: 2')
schedule.append(semester)
print(schedule)
semester = parse_semester(2, 4, 'Unnamed: 4')
schedule.append(semester)

# all fall ranges
# 2, 9
# 11, 18
# 20, 27
# 29, 36
# 38, 45

# all spring ranges
# 2, 9
# 11, 18
# 20, 27
# 29, 36
# 38, 45

# all summer ranges
# 2, 4
# 11, 13
# 20, 22
# 29, 31
# 38, 40

print(schedule)
