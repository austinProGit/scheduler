# Author: Austin Lee
# 9/21/22
# CPSC 4175 Group Project

from dataclasses import dataclass
import sys
import os
 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)

from program_generated_validator import NonDAGCourseInfoError, InvalidCourseError, validate_course_path

# ================================ Unit Tests =======================================================

def program_generated_validator_tests() :

    # Boolean to track if all tests pass
    tests_passed = True

    #This class simulates the course info container. It has access to the same methdos as does the real container.
    #The container needs to be updated to include the same return types for the methods used below.
    class dummy_course_info_dataframe_container:

        # constructor
        def __init__(self, course_path):
            self.course_path = course_path

    # Accesses the dataframe's course IDs and returns them as a list of strings.
        def get_courseIDs(self):
            courseids = []
            courseids = ['MATH 1113','MATH 2125','MATH 5125','CPSC 2108','CPSC 1301','CPSC 1302','CPSC 2105','CYBR 2159','CYBR 2106','CPSC 3175','CPSC 3125','CPSC 3131','CPSC 5135','CPSC 3165','CPSC 3121','CPSC 5155','CPSC 5157','CPSC 4175','CPSC 5115','CPSC 5128','CPSC 4176','CPSC 4000']
            # courseids = list(current_path.keys())
            return courseids

    # Accesses the dataframe's prerequisites for a given course and returns the prereqs as a list of strings.
        def get_prereqs(self, courseid):
            prereqs = []
            try:
                for prereq in self.course_path.get(courseid):
                    prereqs.append(prereq)
            except:
                prereqs = 'courseID not found'
            return prereqs

    # Gets all excused prereqs that are not listed as course id's
        def get_excused_prereqs(self):
            prereq_list = ['MISM 3145', 'MISM 3115', 'MISM 3109', 'MATH 1111']
            return prereq_list
    
    # Our current required path, which is known to be valid.
    current_path = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': [],
        'CPSC 1302': ['CPSC 1301'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # shortest cycle: CPSC 1302 requires itself as a prerequisite.
    shortest_cycle = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113', 'MATH 5125'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': [],
        'CPSC 1302': ['CPSC 1301', 'CPSC 1302'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # short cycle: MATH 2125 and MATH 5125 require each other as prerequisites
    short_cycle = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113', 'MATH 5125'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': [],
        'CPSC 1302': ['CPSC 1301'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # MATH 2125 requires CPSC 5128 as a prerequisite, creating a long cycle.
    long_cycle = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113', 'CPSC 5128'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': [],
        'CPSC 1302': ['CPSC 1301'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # cycle 1: CPSC 2105 requires CPSC 5155 as a prerequisite. 
    # cycle 2: CPSC 2108 requires CPSC 4175 as a prerequisite.
    # cycle 3: CPSC 1301 requires CPSC 4176 as a prerequisite.
    # cycle 4: CPSC 1302 requires CPSC 5115 as a prerequisite.
    # cycle 5: CPSC 3175 requires CPSC 4175 as a prerequisite.
    multiple_cycles = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302', 'CPSC 4175'],
        'CPSC 1301': ['CPSC 4176'],
        'CPSC 1302': ['CPSC 1301', 'CPSC 5115'],
        'CPSC 2105': ['CPSC 1301', 'CPSC 5155'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108', 'CPSC 4175'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # invalid course: CPSC 1300 as a prerequisite for CPSC 1301
    single_invalid_course_prereq = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': ['CPSC 1300'],
        'CPSC 1302': ['CPSC 1301'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # invalid course 1: BLAH 3000 as prerequisite for CPSC 3165
    # invalid course 2: MATH 2158 as prerequisite for CPSC 4000
    multiple_invalid_courses_prereqs = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': [],
        'CPSC 1302': ['CPSC 1301'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': ['BLAH 3000'],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': ['MATH 2158']
    }

    # excused prereq: MISM 3145 required for MATH 1113
    single_excused_prereq = {
        'MATH 1113': ['MISM 3145'],
        'MATH 2125': ['MATH 1113'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': [],
        'CPSC 1302': ['CPSC 1301'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # excused prereqs: MISM 3145 required for MATH 1113 and MATH 1111 required for CPSC 4176
    multiple_excused_prereqs = {
        'MATH 1113': ['MISM 3145'],
        'MATH 2125': ['MATH 1113'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': [],
        'CPSC 1302': ['CPSC 1301'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175', 'MATH 1111'],
        'CPSC 4000': []
    }

    print('=============================== Start Program Generated Validator Tests ===============================\n')

    test_case_list = []
    
    def add_test(test_name, test_data, should_validate):
        test_case_list.append({"test_name": test_name, "test_data": test_data, "should_validate": should_validate})

    # add_test("current_path", current_path, True)
    # add_test("short_cycle", short_cycle, False)
    # add_test("long_cycle", long_cycle, False)
    # add_test("multiple_cycles", multiple_cycles, False)
    # TODO: make a function that auto-formats the cycle lists found. Belongs in program_generated_validator.
    # TODO: add to tests: check that the expected cycles are present and that they have been formatted with the auto-formatter.
    add_test("single_invalid_course_prereq", single_invalid_course_prereq, False)
    add_test("multiple_invalid_courses_prereqs", multiple_invalid_courses_prereqs, False)
    add_test("single_excused_prereq", single_excused_prereq, True)
    add_test("multiple_excused_prereqs", multiple_excused_prereqs, True)
    
    for test in test_case_list:
        test_passed = False
        try:
            validate_course_path(dummy_course_info_dataframe_container(test["test_data"]))
            test_passed = test["should_validate"]
        except (NonDAGCourseInfoError) as config_error:
            test_passed = not test["should_validate"]
            print(config_error)
        except (InvalidCourseError) as config_error:
            test_passed = not test["should_validate"]
            print(config_error)
        if test_passed:
            print(f'The {test["test_name"]} test PASSED.')
        else:
            tests_passed = False
            print(f'The {test["test_name"]} test FAILED.')

    print('\n=============================== End Program Generated Validator Tests ===============================\n')

    return tests_passed
