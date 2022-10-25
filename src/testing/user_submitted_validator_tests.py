# Author: Austin Lee and Max Lewis
# 9/21/22
# CPSC 4175 Group Project

from dataclasses import dataclass
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from user_submitted_validator import validate_user_submitted_path
from course_info_container import *
import pandas as pd
import collections

def user_submitted_validator_tests():
    
    tests_passed = True
    
    #==============================================Test Cases==============================================

    # Test Case 1: Correct 
    correct_input_1 = [['CPSC 3121', 'CPSC 3165', 'CPSC 3XXX'], ['CPSC 3XXX', 'CPSC 4157'], 
    ['CPSC 4175', 'CPSC 4115', 'CPSC 4155'], ['CPSC 4176', 'CPSC 4135', 'CPSC 4148', 'CPSC 4000']]

    # Test Case 2: Correct 
    correct_input_2 = [['CPSC 1302', 'CPSC 2105', 'CPSC 3165', 'CPSC 3XXX'], ['CPSC 3XXX', 'MATH 5125'], 
    ['CPSC 2108', 'CPSC 3131'], ['CPSC 3175', 'CPSC 3121', 'CPSC 3125'], 
    ['CPSC 4157'], ['CPSC 4175', 'CPSC 4115', 'CPSC 4155'], 
    ['CPSC 4176', 'CPSC 4135', 'CPSC 4148', 'CPSC 4000']]

    # Test Case 3: Correct, note: includes CYBR 2160 scheduled in same semester as corequisite CYBR 2159
    correct_input_3 = [['CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'CYBR 2160', 'MATH 5125'], ['CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3125', 'CPSC 3175', 'CPSC 4115'], ['CPSC 4135', 'CPSC 4148'], [], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4176', 'CPSC 4000']]

    # Test Case 4: Correct 
    correct_input_4 = [['CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'CYBR 2160', 'MATH 5125'], ['CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3125', 'CPSC 3175', 'CPSC 4115'], ['CPSC 4135', 'CPSC 4148'], [], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4176', 'CPSC 4000']]

    # Test Case 5: Single prereq problem, course scheduled same semester as prereq: From correct input 1, 
    # CPSC 4176 is taken in the same semester as its prereq CPSC 4175
    single_prereq_problem_same_sem = [['CPSC 3121', 'CPSC 3165', 'CPSC 3XXX'], ['CPSC 3XXX', 'CPSC 4157'], 
    ['CPSC 4175', 'CPSC 4115', 'CPSC 4155', 'CPSC 4176'], ['CPSC 4135', 'CPSC 4148', 'CPSC 4000']]

    # Test Case 6: Single prereq problem, course scheduled far prior to prereq: From correct input 3,
    # CPSC 4176 was moved to the first semester, before its prereq CPSC 4175.
    single_prereq_problem_dif_sem = [['CPSC 4176', 'CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'CYBR 2160', 'MATH 5125'], ['CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3125', 'CPSC 3175', 'CPSC 4115'], ['CPSC 4135', 'CPSC 4148'], [], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4000']]

    # Test Case 7: Multiple prereq problems, course scheduled same semester as one of its prereqs. From correct 
    # input 3, CPSC 4115 was moved to the fourth semester, so that prereq MATH 5125 is already satisfied, but 
    # CPSC 2108 is in the same semester. 
    multiple_prereq_problem_mixed_sem = [['CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'CYBR 2160', 'MATH 5125'], ['CPSC 4115', 'CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3125', 'CPSC 3175'], ['CPSC 4135', 'CPSC 4148'], [], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4176', 'CPSC 4000']]

    # Test Case 8: Multiple prereq problems, course scheduled prior to both of its prereqs. From correct 
    # input 3, CPSC 4115 was moved to the first semester, prior to its prereqs MATH 5125 and CPSC 2108.
    multiple_prereq_problem_dif_sem = [['CPSC 4115', 'CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'CYBR 2160', 'MATH 5125'], ['CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3125', 'CPSC 3175'], ['CPSC 4135', 'CPSC 4148'], [], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4176', 'CPSC 4000']]

    # Test Case 9: Single corequisite problem, course scheduled prior to its corequisite. From correct input 3,
    # CYBR 2160 is moved to be scheduled prior to its corequisite CYBR 2159.
    single_coreq_problem = [['CYBR 2160', 'CPSC 1302', 'CPSC 2105', 'CPSC 3165'], ['CPSC 3XXX', 'CPSC 3XXX'], 
    ['CYBR 2159', 'MATH 5125'], ['CPSC 2108', 'CPSC 3121', 'CPSC 3131'], 
    ['CPSC 4157'], ['CPSC 3125', 'CPSC 3175', 'CPSC 4115'], ['CPSC 4135', 'CPSC 4148'], [], 
    ['CPSC 4155', 'CPSC 4175'], ['CPSC 4176', 'CPSC 4000']]

    excused_prereqs = ['MISM 3145', 'MISM 3115', 'MISM 3109', 'MATH 1111']

    container = CourseInfoContainer(load_course_info('src/input_files/Course Info.xlsx'), excused_prereqs)

    test_case_list = []

    def add_test(test_name, test_data, ex_out):
        test_case_list.append({"test_name": test_name, "test_data": test_data, "ex_out": ex_out})

    add_test("correct_input_1", correct_input_1, [])
    add_test("correct_input_2", correct_input_2, [])
    add_test("correct_input_3", correct_input_3, [])
    add_test("correct_input_4", correct_input_4, [])
    add_test("single_prereq_problem_same_sem", single_prereq_problem_same_sem, ['CPSC 4176 taken before/during CPSC 4175.'])
    add_test("single_prereq_problem_dif_sem", single_prereq_problem_dif_sem, ['CPSC 4176 taken before/during CPSC 4175.'])
    add_test("multiple_prereq_problem_mixed_sem", multiple_prereq_problem_mixed_sem, ['CPSC 4115 taken before/during CPSC 2108.'])
    add_test("multiple_prereq_problem_dif_sem", multiple_prereq_problem_dif_sem, ['CPSC 4115 taken before/during CPSC 2108.', 'CPSC 4115 taken before/during MATH 5125.'])
    add_test("single_coreq_problem", single_coreq_problem, ['CYBR 2160 taken before CYBR 2159.'])

    print('=============================== Start User Submitted Validator Tests ===============================\n')


    for test in test_case_list:
        test_passed = False
        if collections.Counter(validate_user_submitted_path(container, test["test_data"])) == collections.Counter(test["ex_out"]):
            test_passed = True
            print(f'The {test["test_name"]} test PASSED.')
        else:
            tests_passed = False
            print(f'The {test["test_name"]} test FAILED.')

    print('\n=============================== End User Submitted Validator Tests ===============================\n')

    return tests_passed