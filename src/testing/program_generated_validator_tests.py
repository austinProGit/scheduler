# Author: Austin Lee
# 9/21/22
# CPSC 4175 Group Project

import sys
import os
 

current = os.path.dirname(os.path.realpath(__file__)) # Gets the name of the directory where this file is present.
parent = os.path.dirname(current) # Gets the parent directory name where the current directory is present.
sys.path.append(parent) # Adds the parent directory to the sys.path.

from program_generated_evaluator import evaluate_container, NonDAGCourseInfoError, InvalidCourseError

# ================================ Unit Tests =======================================================

def program_generated_validator_tests() :

    tests_passed = True # Boolean to track if all tests pass

   
    class dummy_course_info_dataframe_container:
        """ This class simulates the course info container. It has access to the same relevant methods as does 
        the real container."""

        def __init__(self, course_path):
            self.course_path = course_path

        # Accesses the dataframe's course IDs and returns them as a list of strings.
        def get_courseIDs(self):
            courseids = list(self.course_path.keys()) 
            return courseids

        # Accesses the dataframe's prerequisites for a given course and returns the prereqs as a list of strings.
        def get_prereqs(self, courseid):
            prereqs = []
            try:
                for prereq in self.course_path[courseid]:
                    prereqs.append(prereq)
            except:
                raise ValueError(courseid)
            return prereqs

        # Gets all excused prereqs that are not listed as course id's
        def get_excused_prereqs(self):
            prereq_list = ['MISM 3145', 'MISM 3115', 'MISM 3109', 'MATH 1111', 'MATH 1131', 'MATH 1132']
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

    # Small path to graduation to test descendants with only one parent.
    desc_test_one_parent = {
        'CPSC 1000': [],
        'CPSC 2001': ['CPSC 1000'],
        'CPSC 3003': ['CPSC 2001'],
        'CPSC 2000': ['CPSC 1000'],
        'CPSC 3000': ['CPSC 2000'],
        'CPSC 4000': ['CPSC 3000'],
        'CPSC 3001': ['CPSC 2000'],
        'CPSC 3002': ['CPSC 2000']
    }

    # Descendants dictionary
    desc_test_one_parent_dict = {
    'CPSC 1000': 7,
    'CPSC 2000': 4,
    'CPSC 2001': 1,
    'CPSC 3000': 1,
    'CPSC 3001': 0,
    'CPSC 3002': 0,
    'CPSC 3003': 0,
    'CPSC 4000': 0
    }

    # Small path to graduation to test descendants with multiple parents.
    desc_test_multiple_parents = {
        'CPSC 1000': [],
        'CPSC 2001': ['CPSC 1000'],
        'CPSC 3003': ['CPSC 2001'],
        'CPSC 2000': ['CPSC 1000'],
        'CPSC 3000': ['CPSC 1000', 'CPSC 2000'],
        'CPSC 4000': ['CPSC 3000'],
        'CPSC 3001': ['CPSC 2000'],
        'CPSC 3002': ['CPSC 2000']
    }

    # Descendants dictionary
    desc_test_multiple_parents_dict = {
    'CPSC 1000': 7,
    'CPSC 2000': 4,
    'CPSC 2001': 1,
    'CPSC 3000': 1,
    'CPSC 3001': 0,
    'CPSC 3002': 0,
    'CPSC 3003': 0,
    'CPSC 4000': 0
    }

    print('=============================== Start Program Generated Validator Tests ===============================\n')

    test_case_list = []
    
    def add_test(test_name, test_data, should_validate, test_descendants=None):
        """For each test, a dictionary is added with the following information:"""
        test_case_list.append({"test_name": test_name, "test_data": test_data, "should_validate": should_validate, "test_descendants": test_descendants})

    add_test("current_path", current_path, True)
    add_test("short_cycle", short_cycle, False)
    add_test("long_cycle", long_cycle, False)
    add_test("multiple_cycles", multiple_cycles, False)
    add_test("single_invalid_course_prereq", single_invalid_course_prereq, False)
    add_test("multiple_invalid_courses_prereqs", multiple_invalid_courses_prereqs, False)
    add_test("single_excused_prereq", single_excused_prereq, True)
    add_test("multiple_excused_prereqs", multiple_excused_prereqs, True)
    add_test("desc_test_one_parent", desc_test_one_parent, True, test_descendants=desc_test_one_parent_dict)
    add_test("desc_test_multiple_parents", desc_test_multiple_parents, True, test_descendants=desc_test_multiple_parents_dict)

    for test in test_case_list:
        
        test_passed = False

        try:
            container = dummy_course_info_dataframe_container(test["test_data"])
            report = evaluate_container(container)
            test_passed = test["should_validate"]

            if expected_descendants := test["test_descendants"]:
                if report.course_descendants == expected_descendants:
                    test_passed = True
                else:
                    test_passed = False

        # Handling for any errors found during processing of Course Info in program_generated_evaluator
        except (NonDAGCourseInfoError) as config_error: 
            test_passed = not test["should_validate"]
        except (InvalidCourseError) as config_error:
            test_passed = not test["should_validate"]

        if test_passed:
            print(f'The {test["test_name"]} test PASSED.')
        else:
            tests_passed = False
            print(f'The {test["test_name"]} test FAILED.')

    print('\n=============================== End Program Generated Validator Tests ===============================\n')

    return tests_passed
