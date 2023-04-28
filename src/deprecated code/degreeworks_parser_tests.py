# Author: Austin Lee
# 9/21/22
# CPSC 4175 Group Project

import sys
import os

current = os.path.dirname(os.path.realpath(__file__)) # Gets the name of the directory where this file is present.
parent = os.path.dirname(current) # Gets the parent directory name where the current directory is present.
sys.path.append(parent) # Adds the parent directory to the sys.path.

from degreeworks_parser import *
from degree_extraction_container import DegreeExtractionContainer

def degreeworks_parser_v2_tests():

    tests_passed = True # Boolean to track if all tests pass

    #==============================================Test Cases==============================================

    # Test Case 1
    degreeworks_input_1_ex_out = DegreeExtractionContainer(
        ['MATH 1111', 'CPSC 1***', 'MATH 2125', 'MATH 1113', 
        'CPSC 1301K', 'GEOG 1101I', 'ECON 2105', 'HIST 2111', 
        'MUSC 1100', 'PHIL 2010', 'PERS 1506', 'SPAN 1001I', 
        'ENGL 1102', 'ENGL 1101'],

        '''
        (POLS 1101,POLS 1101,STAT 1401,POLS 1101,CPSC 1302,
        CPSC 2105,CYBR 2159,CYBR 2160,CPSC 2108,CPSC 3125,
        CPSC 3131,CPSC 3165,CPSC 3175,CPSC 4000,MATH 5125,
        CPSC 2125,CPSC 3105,CPSC 4125,CPSC 4126,CPSC 4135,
        CPSC 4175,CPSC 4176,ITDS 1774,STAT 3127,DSCI 3111,
        ITDS 4779)
        
        [s <c=2, n=Choose from 2 of the following:>
            [c <c=2, n= Descriptive Astronomy: The Solar System >
                [d <n=ASTR 1105>]
                [d <n=ASTR 1305>]
            ]
            [r <c=4, n=Principles of Biology >
                [d <n=BIOL 1215>]
            ]
            [r <c=4, n=Contemporary Issues in Biology >
                [d <n=BIOL 1225>]
            ]
            [c <c=2, n=Survey of Chemistry I >
                [d <n=CHEM 1151>]
                [d <n=CHEM 1151>]
            ]
            [c <c=2, n=Survey of Chemistry II >
                [d <n=CHEM 1152>]
                [d <n=CHEM 1152>]
            ]
            [r <c=4, n=Principles of Chemistry I >
                [d <n=CHEM 1211>]
            ]
            [c <c=2, n=Principles of Chemistry II >
                [d <n=CHEM 1212>]
                [d <n=CHEM 1212>]
            ]
            [c <c=2, n=Understanding the Weather >
                [d <n=ATSC 1112>]
                [d <n=ATSC 1112>]
            ]
            [c <c=2, n=Introductory Geo-sciences I: Physical Geology >
                [d <n=GEOL 1121>]
                [d <n=GEOL 1121>]
            ]
            [c <c=2, n=Introductory Geo-sciences II: Historical Geology >
                [d <n=GEOL 1122>]
                [d <n=GEOL 1322>]
            ]
            [c <c=2, n=Introductory Physics I >
                [d <n=PHYS 1111>]
                [d <n=PHYS 1311>]
            ]
            [r <c=4, n=Introductory Physics II >
                [d <n=PHYS 1112>]
                [d <n=PHYS 2211>]
                [d <n=PHYS 1312>]
            ]
            [c <c=2, n=Physics of Color and Sound >
                [d <n=PHYS 1125>]
                [d <n=PHYS 1325>]
            ]
            [c <c=2, n=Principles of Physics I >
                [d <n=PHYS 2211>]
                [d <n=PHYS 2311>]
            ]
            [c <c=2, n=Principles of Physics II >
                [d <n=PHYS 2212>]
                [d <n=PHYS 2312>]
            ]
        ]
        [r <c=9, n=9 Credits in CPSC 3@ or 4@ or 5@ or CYBR 3@ or 4@ or 5@>
            [i <n=Insert CPSC 3@, ga=CPSC 3@ Course, gp=CPSC 3\d3[A-Z]?>]
            [i <n=Insert CPSC 4@, ga=CPSC 4@ Course, gp=CPSC 4\d3[A-Z]?>]
            [i <n=Insert CPSC 5@, ga=CPSC 5@ Course, gp=CPSC 5\d3[A-Z]?>]
            [i <n=Insert CYBR 3@, ga=CYBR 3@ Course, gp=CYBR 3\d3[A-Z]?>]
            [i <n=Insert CYBR 4@, ga=CYBR 4@ Course, gp=CYBR 4\d3[A-Z]?>]
            [i <n=Insert CYBR 5@, ga=CYBR 5@ Course, gp=CYBR 5\d3[A-Z]?>]
        ]
        [r <c=4, n=4 Credits in @ 1@ or 2@ or 3@ or 4@ or 5@U  , i=Except ENGL 1101 or 1102* or CPSC 1301* or 1302* or 2015 or 2016>
            [i <n=Insert 1@, ga=1@ Course, gp=^(?!ENGL 1101|ENGL 1102|CPSC 1301|CPSC 1302|CPSC 2015|CPSC 2016)[A-Z]{4} 1\d{3}[A-Z]?>]
            [i <n=Insert 2@, ga=2@ Course, gp=^(?!ENGL 1101|ENGL 1102|CPSC 1301|CPSC 1302|CPSC 2015|CPSC 2016)[A-Z]{4} 2\d{3}[A-Z]?>]
            [i <n=Insert 3@, ga=3@ Course, gp=^(?!ENGL 1101|ENGL 1102|CPSC 1301|CPSC 1302|CPSC 2015|CPSC 2016)[A-Z]{4} 3\d{3}[A-Z]?>]
            [i <n=Insert 4@, ga=4@ Course, gp=^(?!ENGL 1101|ENGL 1102|CPSC 1301|CPSC 1302|CPSC 2015|CPSC 2016)[A-Z]{4} 4\d{3}[A-Z]?>]
            [i <n=Insert 5@U, ga=5@U Course, gp=^(?!ENGL 1101|ENGL 1102|CPSC 1301|CPSC 1302|CPSC 2015|CPSC 2016)[A-Z]{4} 5\d{3}U>]
        ]
        [s <c=1, n=1 Class in STAT 1401@ or 1127@ or BUSA 3115* or CRJU 3107>[p <n=STAT 1401@, m=STAT 1401.*>][p <n=STAT 1127@, m=STAT 1127.*>]
            [d <n=BUSA 3115>]
            [d <n=CRJU 3107>]
        ]
        ''',
        'CPSC Web Development'
    )

    test_case_list = []

    def add_test(test_name, test_data, ex_out):
        """For each test, a dictionary is added with the following information:"""
        test_case_list.append({"test_name": test_name, "test_data": test_data, "ex_out": ex_out})

    add_test("degreeworks1.pdf", 'input_files/degreeworks1.pdf', degreeworks_input_1_ex_out)

    print('=============================== Start Degreeworks Parser Tests ===============================\n')

    for test in test_case_list:
        
        test_container = generate_degree_extraction_container(test["test_data"])
        if test_container._student_name and degreeworks_input_1_ex_out._student_name:
            print(f'test_container student name: {test_container._student_name}')
            print(f'real_container student name: {degreeworks_input_1_ex_out._student_name}')
            print()

        if test_container._student_number and degreeworks_input_1_ex_out._student_number:
            print(f'test_container student number: {test_container._student_number}')
            print(f'real_container student number: {degreeworks_input_1_ex_out._student_number}')
            print()

        if test_container._degree_plan_name and degreeworks_input_1_ex_out._degree_plan_name:
            print(f'test_container degree plan name: {test_container._degree_plan_name}')
            print(f'real_container degree plan name: {degreeworks_input_1_ex_out._degree_plan_name}')
            print()

        if test_container._courses_needed_constuction_string and degreeworks_input_1_ex_out._courses_needed_constuction_string:
            print(f'test_container courses needed construction string: {test_container._courses_needed_constuction_string}')
            print(f'real_container courses needed construction string: {degreeworks_input_1_ex_out._courses_needed_constuction_string}')
            print()

        if test_container._taken_courses and degreeworks_input_1_ex_out._taken_courses:
            print(f'test_container taken courses: {test_container._taken_courses}')
            print(f'real_container taken courses: {degreeworks_input_1_ex_out._taken_courses}')
            print()

        if test_container.__eq__(test["ex_out"]):
            print(f'The {test["test_name"]} test PASSED.')
        else:
            tests_passed = False
            print(f'The {test["test_name"]} test FAILED.')

    print('\n=============================== End Degreeworks Parser Tests ===============================\n')

    return tests_passed