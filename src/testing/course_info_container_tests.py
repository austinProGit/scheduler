# Max Lewis
# 3/5/23
# CPSC 4176

import sys
import os
import re
 
current = os.path.dirname(os.path.realpath(__file__)) # getting the name of the directory where the this file is present.
parent = os.path.dirname(current) # Getting the parent directory name where the current directory is present.
sys.path.append(parent) # adding the parent directory to the sys.path.

from course_info_container import *
from dataframe_io import *
from driver_fs_functions import *
from instance_identifiers import *
import random


# ================================ Unit Tests =======================================================

def course_info_container_tests():

    test_passed = True
    test_count = 0
    test_passed_count = 0
    test_failed_count = 0

    def passed():
        nonlocal test_count
        nonlocal test_passed_count
        test_count += 1
        test_passed_count += 1


    def failed():
        nonlocal test_count
        nonlocal test_failed_count
        test_count += 1
        test_failed_count += 1


    file0 = get_source_path()
    file0 = get_source_relative_path(file0, 'input_files/Course Info.xlsx')
    dfdict = load_course_info(file0)
    container = CourseInfoContainer(dfdict)
    course_dict = get_pickle("course_dictionary.pickle")
    dept_dict = get_pickle("department_dictionary.pickle") 

    print('=============================== Start course_info_container Tests ===============================\n')
    
# --------------------------------------------------------------------------------------------------------------------------------
    for i in range(300):
        course = random.choice(list(course_dict.keys()))
        course_identifier_obj = CourseIdentifier(course)
        course_report = container.get_course_record(course_identifier_obj)

        if course_report.name == container.get_name(course): passed()
        else: failed()

        if course_report.hours == container.get_hours(course): passed()
        else: failed()

        if course_report.avail == container.get_availability(course): passed()
        else: failed()

        if course_report.prereqs == container.get_prereqs(course): passed()
        else: failed()

        if course_report.coreqs == container.get_coreqs(course): passed()
        else: failed()

        if course_report.restrictions == container.get_restrictions(course): passed()
        else: failed()

    course_identifier_obj_stub = CourseIdentifier('CPSC XXXX', 'Elective', True)
    stub = container.get_course_record(course_identifier_obj_stub)

    if stub.ID == 'CPSC XXXX': passed()
    else: failed()

    if stub.name == 'Elective': passed()
    else: failed()

    if stub.hours == 3: passed()
    else: failed()

    if stub.avail == ['Fa', 'Sp', '--']: passed()
    else: failed()

    course_identifier_wrong = CourseIdentifier('bull', 'crap')
    wrong = container.get_course_record(course_identifier_wrong)

    if wrong == None: passed()
    else: failed()

    print(f"TOTAL TESTS: {test_count}")
    print(f"TOTAL PASSED: {test_passed_count}")
    print(f"TOTAL FAILED: {test_failed_count}")

    print('=============================== End course_info_container Tests ================================\n')
    return test_failed_count == 0