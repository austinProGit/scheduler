# Author: Austin Lee and Max Lewis
# 9/21/22
# CPSC 4175 Group Project

import sys
import os

current = os.path.dirname(os.path.realpath(__file__)) # Gets the name of the directory where this file is present.
parent = os.path.dirname(current) # Gets the parent directory name where the current directory is present.
sys.path.append(parent) # Adds the parent directory to the sys.path.

from user_submitted_validator import validate_user_submitted_path
from course_info_container import CourseInfoContainer, load_course_info
from collections import Counter

def user_submitted_validator_tests():
    
    tests_passed = True # Boolean to track if all tests pass
    
    #==============================================Test Cases==============================================

    # Test Case 1: Correct 
    correct_input_1 = [['CPSC 3121', 'CPSC 3165', 'CPSC 3XXX'], ['CPSC 3XXX', 'CPSC 4157'], 
    ['CPSC 4175', 'CPSC 4115', 'CPSC 4155'], ['CPSC 4176', 'CPSC 4135', 'CPSC 4148', 'CPSC 4000'],[]]

    # Test Case 2: Correct 
    correct_input_2 = [['CPSC 1302', 'CPSC 2105', 'CPSC 3165', 'CPSC 3XXX'], ['CPSC 3XXX', 'MATH 5125'], 
    ['CPSC 2108', 'CPSC 3131'], ['CPSC 3175', 'CPSC 3121', 'CPSC 3125'], 
    ['CPSC 4157'], ['CPSC 4175', 'CPSC 4115', 'CPSC 4155'], 
    ['CPSC 4176', 'CPSC 4135', 'CPSC 4148', 'CPSC 4000'],[]]

    # Test Case 3: Correct, note: includes CYBR 2160 scheduled in same semester as corequisite CYBR 2159
    correct_input_3 = [['CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'CYBR 2160', 'MATH 5125'], ['CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3125', 'CPSC 3175', 'CPSC 4115'], ['CPSC 4135', 'CPSC 4148'], [], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4176', 'CPSC 4000'],[]]

    # Test Case 4: Correct 
    correct_input_4 = [['CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'CYBR 2160', 'MATH 5125'], ['CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3125', 'CPSC 3175', 'CPSC 4115'], ['CPSC 4135', 'CPSC 4148'], [], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4176', 'CPSC 4000'],[]]

    # Test Case 5: Single prereq problem, course scheduled same semester as prereq: From correct input 2, 
    # CPSC 4135 is taken in the same semester as its prereq CPSC 3175
    single_prereq_problem_same_sem = [['CPSC 1302', 'CPSC 2105', 'CPSC 3165', 'CPSC 3XXX'], ['CPSC 3XXX', 'MATH 5125'], 
    ['CPSC 2108', 'CPSC 3131'], ['CPSC 3175', 'CPSC 4135', 'CPSC 3121', 'CPSC 3125'], 
    ['CPSC 4157'], ['CPSC 4175', 'CPSC 4115', 'CPSC 4155'], 
    ['CPSC 4176', 'CPSC 4148', 'CPSC 4000'],[]]

    # Test Case 6: Single prereq problem, course scheduled far prior to prereq: From correct input 3,
    # CPSC 4176 was moved to the first semester, before its prereq CPSC 4175.
    single_prereq_problem_dif_sem = [['CPSC 4176', 'CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'CYBR 2160', 'MATH 5125'], ['CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3125', 'CPSC 3175', 'CPSC 4115'], ['CPSC 4135', 'CPSC 4148'], [], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4000'],[]]

    # Test Case 7: Multiple prereq problems, course scheduled same semester as one of its prereqs. From correct 
    # input 3, CPSC 4115 was moved to the fourth semester, so that prereq MATH 5125 is already satisfied, but 
    # CPSC 2108 is in the same semester. Note: this will also fail the availability check.
    multiple_prereq_problem_mixed_sem = [['CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'CYBR 2160', 'MATH 5125'], ['CPSC 4115', 'CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3125', 'CPSC 3175'], ['CPSC 4135', 'CPSC 4148'], [], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4176', 'CPSC 4000'],[]]

    # Test Case 8: Multiple prereq problems, course scheduled prior to both of its prereqs. From correct 
    # input 3, CPSC 4115 was moved to the first semester, prior to its prereqs MATH 5125 and CPSC 2108. Note:
    # This will also fail the availability check.
    multiple_prereq_problem_dif_sem = [['CPSC 4115', 'CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'CYBR 2160', 'MATH 5125'], ['CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3125', 'CPSC 3175'], ['CPSC 4135', 'CPSC 4148'], [], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4176', 'CPSC 4000'],[]]

    # Test Case 9: Single corequisite problem, course scheduled prior to its corequisite. From correct input 3,
    # CYBR 2160 is moved to be scheduled prior to its corequisite CYBR 2159.
    single_coreq_problem = [['CYBR 2160', 'CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'MATH 5125'], ['CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3125', 'CPSC 3175', 'CPSC 4115'], ['CPSC 4135', 'CPSC 4148'], [], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4176', 'CPSC 4000'],[]]

    # Test Case 10: Single course scheduled when it is not offered. From correct input 3, CPSC 3125 was moved to 
    # a semester that it is not offered, without violating any prereq rules.
    single_availability_violation = [['CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'CYBR 2160', 'MATH 5125'], ['CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3175', 'CPSC 4115'], ['CPSC 4135', 'CPSC 4148'], ['CPSC 3125'], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4176', 'CPSC 4000'],[]]

    # Test Case 11: Two courses scheduled when they are not offered. From correct input 3, CPSC 3125 and CPSC 3131 were
    #  moved to a semester when they are not offered, without violating any prereq rules.
    multiple_availability_violations = [['CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'CYBR 2160', 'MATH 5125'], ['CPSC 2108', 'CPSC 3121'], 
    ['CPSC 4157'], ['CPSC 3175', 'CPSC 4115'], ['CPSC 4135', 'CPSC 4148'], ['CPSC 3125', 'CPSC 3131'], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4176', 'CPSC 4000'],[]]

    # Known prereqs that will appear as prereqs in Course Info but not as courses in column 1 of Course Info
    excused_prereqs = ['MISM 3145', 'MISM 3115', 'MISM 3109', 'MATH 1111']

    # Create a course info container from the real Course Info input
    container = CourseInfoContainer(load_course_info('src/input_files/Course Info.xlsx'), excused_prereqs)

    test_case_list = []

    def add_test(test_name, test_data, ex_out):
        """For each test, a dictionary is added with the following information:"""
        test_case_list.append({"test_name": test_name, "test_data": test_data, "ex_out": ex_out})

    add_test("correct_input_1", correct_input_1, [])
    add_test("correct_input_2", correct_input_2, [])
    add_test("correct_input_3", correct_input_3, [])
    add_test("correct_input_4", correct_input_4, [])
    add_test("single_prereq_problem_same_sem", single_prereq_problem_same_sem, ['CPSC 4135 taken before/during CPSC 3175.'])
    add_test("single_prereq_problem_dif_sem", single_prereq_problem_dif_sem, ['CPSC 4176 taken before/during CPSC 4175.'])
    add_test("multiple_prereq_problem_mixed_sem", multiple_prereq_problem_mixed_sem, ['CPSC 4115 taken during the Spring term (not available).', 'CPSC 4115 taken before/during CPSC 2108.'])
    add_test("multiple_prereq_problem_dif_sem", multiple_prereq_problem_dif_sem, ['CPSC 4115 taken during the Spring term (not available).', 'CPSC 4115 taken before/during CPSC 2108.', 'CPSC 4115 taken before/during MATH 5125.'])
    add_test("single_coreq_problem", single_coreq_problem, ['CYBR 2160 taken before CYBR 2159.'])
    add_test("single_availability_violation", single_availability_violation, ['CPSC 3125 taken during the Summer term (not available).'])
    add_test("multiple_availability_violations", multiple_availability_violations, ['CPSC 3125 taken during the Summer term (not available).', 'CPSC 3131 taken during the Summer term (not available).'])

    print('=============================== Start User Submitted Validator Tests ===============================\n')


    for test in test_case_list:
        test_passed = False
        # Controls for unpredictable list orders
        if Counter(validate_user_submitted_path(container, test["test_data"])) == Counter(test["ex_out"]):
            test_passed = True
            print(f'The {test["test_name"]} test PASSED.')
        else:
            tests_passed = False
            print(f'The {test["test_name"]} test FAILED.')

    print('\n=============================== End User Submitted Validator Tests ===============================\n')

    return tests_passed