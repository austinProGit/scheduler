# Max Lewis
# 3/5/23
# CPSC 4176

import sys
import os
import re
 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)

from course_info_container import *
import pickle
from dataframe_io import *
from driver_fs_functions import *
from CSU_public_data_parser import get_pickle_file
import re

# ================================ Unit Tests =======================================================

def course_info_container_tests() :
    test_passed = True
    test_count = 0
    test_passed_count = 0
    test_failed_count = 0

    file0 = get_source_path()
    file0 = get_source_relative_path(file0, 'input_files/Course Info.xlsx')
    dfdict = load_course_info(file0)
    container = CourseInfoContainer(dfdict)
    course_dict = get_pickle_file("course_dictionary.pickle")
    dept_dict = get_pickle_file("department_dictionary.pickle") 

    test_file = get_source_path()
    test_file = get_source_relative_path(test_file, 'output_files/New Course Info.xlsx')
    test_df_dict = load_course_info(test_file)
    test_container = CourseInfoContainer(test_df_dict)

    print('=============================== Start course_info_container Tests ===============================\n')
    
# --------------------------------------------------------------------------------------------------------------------------------

    # We check our container against our master dictionary of known course IDs per the CSU website.
    print("Testing get_courseIDs function...")

    courseIDs = container.get_courseIDs()
    for course in courseIDs:
        test_count += 1
        if course in course_dict.keys():
            test_passed_count += 1
        else:
            test_failed_count += 1

    print("Testing of get_courseIDs complete.\n")

# --------------------------------------------------------------------------------------------------------------------------------

    # We created another container and compared the course names to each other.
    print("Testing get_name function...")

    for course in course_dict.keys():
        test_count += 1
        if container.get_name(course) == test_container.get_name(course):
            test_passed_count += 1
        else:
            test_failed_count += 1

    test_count += 2
    if container.get_name("bull") == None:
        test_passed_count += 1
    else: test_failed_count += 1
    if container.get_name(None) == None:
        test_passed_count += 1
    else: test_failed_count += 1

    print("Testing of get_name complete.\n")
    
# --------------------------------------------------------------------------------------------------------------------------------

    # Does availability contain Fa or Sp or Su or a combination of these semesters.  
    print("Testing get_availability function...")

    semesters = ["Fa", "Sp", "Su"]
    for course in course_dict.keys():
        test_count += 1
        avail = container.get_availability(course)
        if semesters[0] in avail or semesters[1] in avail or semesters[2] in avail:
            test_passed_count += 1
        else:
            test_failed_count += 1

    test_count += 2
    if container.get_availability("bull") == ["Fa", "Sp", "--"]: 
        test_passed_count += 1
    else: test_failed_count += 1

    if container.get_availability(None) == ["Fa", "Sp", "--"]: 
        test_passed_count += 1
    else: test_failed_count += 1

    print("Testing of get_availability complete.\n")

# --------------------------------------------------------------------------------------------------------------------------------

    # This test only checks for structural integrity, not correctness.  
    print("Testing get_prereqs function...")

    for course in course_dict.keys():
        if container.get_prereqs(course) != None:
            prereq = container.get_prereqs(course)
            left_bracket_count = 0
            right_bracket_count = 0
            test_count += 1
            for char in prereq:
                if char == "[": left_bracket_count += 1
                if char == "]": right_bracket_count += 1
            if left_bracket_count == right_bracket_count: test_passed_count += 1 
            else: test_failed_count += 1

    test_count += 2
    if container.get_prereqs("bull") == None:  
        test_passed_count += 1
    else: test_failed_count += 1

    if container.get_prereqs(None) == None:  
        test_passed_count += 1
    else: test_failed_count += 1

    print("Testing of get_prereqs complete.\n")

# --------------------------------------------------------------------------------------------------------------------------------

    print("Testing get_coreqs function...")

    for course in course_dict.keys():
        deliverable_pattern = r"\[d\s<n=[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?>\]"
        if container.get_coreqs(course) != None:
            test_count += 1
            coreq = container.get_coreqs(course)
            if re.search(deliverable_pattern, coreq): test_passed_count += 1
            else: test_failed_count += 1

    test_count += 2
    if container.get_coreqs("bull") == None:  
        test_passed_count += 1
    else: test_failed_count += 1

    if container.get_coreqs(None) == None:  
        test_passed_count += 1
    else: test_failed_count += 1

    print("Testing of get_coreqs complete.\n")

# --------------------------------------------------------------------------------------------------------------------------------

    print("Testing get_hours function...")

    hours_pattern = r"\d+"
    for course in course_dict.keys():
        test_count += 1
        hours = container.get_hours(course)
        if hours >= 0:
            test_passed_count += 1
        else: test_failed_count += 1

    test_count += 2
    if container.get_hours("bull") == 0:
        test_passed_count += 1
    else: test_failed_count += 1

    if container.get_hours(None) == 0:
        test_passed_count += 1
    else: test_failed_count += 1

    print("Testing of get_hours complete.\n")

# --------------------------------------------------------------------------------------------------------------------------------

    print(f"TOTAL TESTS: {test_count}")
    print(f"TOTAL PASSED: {test_passed_count}")
    print(f"TOTAL FAILED: {test_failed_count}")

    print('=============================== End course_info_container Tests ================================\n')
    return test_passed

#course_info_container_tests()