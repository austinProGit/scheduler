# Scheduler file
# WORK IN PROGRESS
from courses_needed_parser import get_courses_needed
from course_info_container import *
import pandas as pd


def check_availability(_course_id, _current_semester):
    # TODO: return list instead? @Max idk how much this matters as I just .split() here
    _availability = courses_info.get_availability(_course_id).split()
    if _current_semester in _availability:
        return True
    else:
        return False


def check_prerequisites(_course):
    # TODO: need .get_prereqs() to return a list to account for 2+ pre-reqs
    _prerequisites = courses_info.get_prereqs(_course)
    print("PreReq: " + _prerequisites)
    # if PreReq is in courses_needed or in current_semester, can't take course.
    if _prerequisites in courses_needed or _prerequisites in temporary_semester:
        return False
    else:
        return True


# file names
needed_file = 'Sample Input1.pdf'
info_file = "ClassInfo.xlsx"

# get data being worked with
courses_needed = get_courses_needed(needed_file)
courses_info = Course_info_dataframe_container(load_course_info('ClassInfo.xlsx'))

# create blank dataframe for final schedule
schedule_df = pd.DataFrame(columns=['Spring 2023', 'Summer 2023', 'Fall 2023',
                                    'Spring 2024', 'Summer 2024', 'Fall 2024',
                                    'Spring 2025', 'Summer 2025', 'Fall 2025',
                                    'Spring 2026', 'Summer 2026', 'Fall 2026'])

# only adding this course because it has two pre-reqs, Need one to test scheduler
courses_needed.append("CPSC 3125")

# we need a max courses, and not a hard n courses per semester
# I personally only had ONE class in a previous semester and could not take ANY other
max_courses = 6
# sorting should speed up the scheduler, as lower tier courses are more likely to be required sooner
courses_needed.sort()

# only adding this course, to get a fail on my pre-reqs
courses_needed.append("CPSC 2108")

# ************ single semester ********************
temporary_semester = []
current_courses = 1  # need to manually control this loop
while current_courses < max_courses:
    # TODO: Need to create something to check current semester and assign two letter semester
    this_semester = 'Sp'

    # get first course in list
    course = courses_needed.pop(0)
    print("Course: " + course)

    # check availability
    available = check_availability(course, this_semester)
    if not available:
        print("unavailable, skipped")
        courses_needed.append(course)
        continue

    # check prerequisites
    # TODO: create co-requisites check
    prerequisites = check_prerequisites(course)
    if not prerequisites:
        print("PreReq failed, skipped")
        courses_needed.append(course)
        continue

    # slot course in semester
    temporary_semester.append(course)
    current_courses += 1

print(temporary_semester)

# first attempt, constant errors trying to go too broad at the start
"""for semester in schedule_df:
    # get course from courses needed
    course = courses_needed.pop(0)

    # check availability"""
