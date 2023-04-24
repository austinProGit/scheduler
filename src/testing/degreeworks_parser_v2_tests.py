# Author: Austin Lee
# 4/6/2023
# CPSC 4175 Group Project

import sys
import os
import difflib

current = os.path.dirname(os.path.realpath(__file__)) # Gets the name of the directory where this file is present.
parent = os.path.dirname(current) # Gets the parent directory name where the current directory is present.
sys.path.append(parent) # Adds the parent directory to the sys.path.

from degreeworks_parser_v2 import *
from degree_extraction_container import DegreeExtractionContainer

def degreeworks_parser_v2_tests():

    tests_passed = True # Boolean to track if all tests pass

    #==============================================Test Cases==============================================

    # Test Case 1
    degreeworks_input_1_ex_out = DegreeExtractionContainer(
        ['BIOL 2221K', 'MATH 1111', 'KINS 1105', 'MATH 1113', 'PSYC 2103', 
         'MATH 1111', 'HIST 1112', 'HESC 2***', '*** 1***', 'CPSC 1301K', 
         'HIST 1111', 'PSYC 1101', 'POLS 1101', 'HIST 2112', 'STAT 1401', 
         'BIOL 1215K', 'ARTH 1100', 'ENGL 2112', 'LEAD 1705', 'SPAN 1001I', 
         'ENGL 1102', 'ENGL 1101'],

        '''
        (CPSC 1302,CPSC 2105,CYBR 2159,CYBR 2160,MATH 2125,KINS 2105,ITDS 2106,HESC 2105,KINS 1105,KINS 3126,KINS 3135,KINS 4131,KINS 4331,KINS 4232,KINS 4133,KINS 4137,KINS 4146,KINS 5212U,KINS 4698,CPSC 2108,CPSC 3125,CPSC 3131,CPSC 3165,CPSC 3175,CPSC 4000,MATH 5125U,MATH 2125,CPSC 3121,CPSC 5115U,CPSC 4175,CPSC 4176)

[s <c=1, n=Choose from 1 of the following:>
[s <c=2, n=2 Classes in ASTR 1105 and 1305>
[d <n=ASTR 1105>]
[d <n=ASTR 1305>]
]
[r <c=4, n=4 Credits in BIOL 1225K>
[d <n=BIOL 1225K>]
]
[s <c=2, n=2 Classes in CHEM 1151  and 1151L>
[d <n=CHEM 1151>]
[d <n=CHEM 1151L>]
]
[s <c=2, n=2 Classes in CHEM 1152  and 1152L>
[d <n=CHEM 1152>]
[d <n=CHEM 1152L>]
]
[r <c=4, n=4 Credits in CHEM 1211@>
[p <n=CHEM 1211@, m=CHEM 1211.*>]
]
[s <c=2, n=2 Classes in CHEM 1212  and 1212L>
[d <n=CHEM 1212>]
[d <n=CHEM 1212L>]
]
[s <c=2, n=2 Classes in ATSC 1112 and 1112L>
[d <n=ATSC 1112>]
[d <n=ATSC 1112L>]
]
[s <c=2, n=2 Classes in GEOL 1121  and 1121L>
[d <n=GEOL 1121>]
[d <n=GEOL 1121L>]
]
[d <n=GEOL 1121K>]
[s <c=2, n=2 Classes in GEOL 1122  and 1322>
[d <n=GEOL 1122>]
[d <n=GEOL 1322>]
]
[d <n=GEOL 2225>]
[s <c=2, n=2 Classes in PHYS 1111  and 1311>
[d <n=PHYS 1111>]
[d <n=PHYS 1311>]
]
[r <c=4, n=4 Credits in PHYS 1112  or 2211  or 1312>
[d <n=PHYS 1112>]
[d <n=PHYS 2211>]
[d <n=PHYS 1312>]
]
[s <c=2, n=2 Classes in PHYS 1125  and 1325>
[d <n=PHYS 1125>]
[d <n=PHYS 1325>]
]
[s <c=2, n=2 Classes in PHYS 2211  and 2311>
[d <n=PHYS 2211>]
[d <n=PHYS 2311>]
]
[s <c=2, n=2 Classes in PHYS 2212  and 2312>
[d <n=PHYS 2212>]
[d <n=PHYS 2312>]
]
[d <n=ENVS 1205K>]
]
[r <c=2, n=Still needed: 2 Credits in KINS 1106 or PHED 1205 or 1206>
[d <n=KINS 1106>]
[d <n=PHED 1205>]
[d <n=PHED 1206>]
]
[s <c=1, n=Still needed:
1 Class in PEDS 1@ or 2375  or 2376  or 2377 or 2378 or
DANC 1310 or MSAL 4419 or THEA 1375>
[i <n=Insert PEDS 1@, ga=PEDS 1@ Course, gp=PEDS 1\d{3}[A-Z]?>]
[d <n=PEDS 2375>]
[d <n=PEDS 2376>]
[d <n=PEDS 2377>]
[d <n=PEDS 2378>]
[d <n=DANC 1310>]
[d <n=MSAL 4419>]
[d <n=THEA 1375>]
]
[r <c=4, n=Still needed:
4 Credits in BIOL 2221K>
[d <n=BIOL 2221K>]
]
[r <c=4, n=Still needed:
4 Credits in BIOL 2222K>
[d <n=BIOL 2222K>]
]
[r <c=5, n=Still needed:
5 Credits in ANTH 1145 or ASTR 1105 or 1106  or 1305
or BIOL 1125 or 1215K or 1225K or CHEM 1151 or
1152  or 1211  or 1212  or CPSC 1301
or ENVS 1105 or EXSC 1105 or GEOG 2215 or GEOL 1110
or 1112 or 1121 or 1122 or 2225 or
MATH 1111  or 1113  or 1131  or 1132  or
2@ or PHIL 2500 or PHYS 1111  or 1112  or 1125
or 2211 or 2212 or PSYC 1101 or SOCI 1101 or
STAT 1401>
[d <n=ANTH 1145>]
[d <n=ASTR 1105>]
[d <n=ASTR 1106>]
[d <n=ASTR 1305>]
[d <n=BIOL 1125>]
[d <n=BIOL 1215K>]
[d <n=BIOL 1225K>]
[d <n=CHEM 1151>]
[d <n=CHEM 1152>]
[d <n=CHEM 1211>]
[d <n=CHEM 1212>]
[d <n=CPSC 1301>]
[d <n=ENVS 1105>]
[d <n=EXSC 1105>]
[d <n=GEOG 2215>]
[d <n=GEOL 1110>]
[d <n=GEOL 1112>]
[d <n=GEOL 1121>]
[d <n=GEOL 1122>]
[d <n=GEOL 2225>]
[d <n=MATH 1111>]
[d <n=MATH 1113>]
[d <n=MATH 1131>]
[d <n=MATH 1132>]
[i <n=Insert MATH 2@, ga=MATH 2@ Course, gp=MATH 2\d{3}[A-Z]?>]
[d <n=PHIL 2500>]
[d <n=PHYS 1111>]
[d <n=PHYS 1112>]
[d <n=PHYS 1125>]
[d <n=PHYS 2211>]
[d <n=PHYS 2212>]
[d <n=PSYC 1101>]
[d <n=SOCI 1101>]
[d <n=STAT 1401>]
]
[r <c=3, n=Still needed:
3 Credits in KINS 3232  or 4135>
[d <n=KINS 3232>]
[d <n=KINS 4135>]
]
[r <c=9, n=Still needed:
9 Credits in KINS 3107 or 4147 or 4498 or 5133U or 5135U or
5136U  or 5137U  or 5545U>
[d <n=KINS 3107>]
[d <n=KINS 4147>]
[d <n=KINS 4498>]
[d <n=KINS 5133U>]
[d <n=KINS 5135U>]
[d <n=KINS 5136U>]
[d <n=KINS 5137U>]
[d <n=KINS 5545U>]
]
[s <c=1, n=Still needed:
1 Class in CPSC 4135  or 5135U>
[d <n=CPSC 4135>]
[d <n=CPSC 5135U>]
]
[s <c=1, n=Still needed:
1 Class in CPSC 4148  or 5128U>
[d <n=CPSC 4148>]
[d <n=CPSC 5128U>]
]
[s <c=1, n=Still needed:
1 Class in CPSC 4155  or 5155U>
[d <n=CPSC 4155>]
[d <n=CPSC 5155U>]
]
[s <c=1, n=Still needed:
1 Class in CPSC 4157  or 5157U>
[d <n=CPSC 4157>]
[d <n=CPSC 5157U>]
]
[r <c=6, n=Still needed: 6 Credits in CPSC 3@ or 4@ or 5@ or CYBR  3@ or 4@ or 5@>
[i <n=Insert CPSC 3@, ga=CPSC 3@ Course, gp=CPSC 3\d{3}[A-Z]?>]
[i <n=Insert CPSC 4@, ga=CPSC 4@ Course, gp=CPSC 4\d{3}[A-Z]?>]
[i <n=Insert CPSC 5@, ga=CPSC 5@ Course, gp=CPSC 5\d{3}[A-Z]?>]
[i <n=Insert CYBR 3@, ga=CYBR 3@ Course, gp=CYBR 3\d{3}[A-Z]?>]
[i <n=Insert CYBR 4@, ga=CYBR 4@ Course, gp=CYBR 4\d{3}[A-Z]?>]
[i <n=Insert CYBR 5@, ga=CYBR 5@ Course, gp=CYBR 5\d{3}[A-Z]?>]
]
        ''',
        'Kinesiology - NONE, Computer Science - Systems',
        '909123456',
        'AAA, BBB',
        '1.85'
    )

    # Test Case 2
    degreeworks_input_2_ex_out = DegreeExtractionContainer(
        ['*** 3***', 'MATH 1111', 'MATH 1001', 'FYRS 1***', 'MATH 2125', 'MATH 1113', 'CPSC 3131', 'CYBR 2160', 'CYBR 2159', 'CPSC 2105', 'CPSC 1302', 'CPSC 1301K', 'GEOG 1101I', 'PSYC 1101', 'POLS 1101', 'HIST 2111', 'STAT 1401', 'ARTH 1100', 
        'GERM 1001', 'ENGL 1102', 'ENGL 1101'],
        '''
        (CPSC 2108,CPSC 3125,CPSC 3165,CPSC 3175,CPSC 4000,MATH 5125U,
        CPSC 3121,CPSC 5115U,CPSC 4175,CPSC 4176)

        [r <c=1, n=Still needed: 1 Credit in ITDS 1779@ or LEAD 1705 or PERS 1506 or 1507>
            [p <n=ITDS 1779@, m=ITDS 1779@.*>]    
            [d <n=LEAD 1705>]
            [d <n=PERS 1506>]
            [d <n=PERS 1507>]
        ]

        [s <c=1, n=Still needed: 1 Class in ENGL 2111@ or 2112@ or 2131  or 2132  or ITDS 1145  
        or 1155  or 1774 or 2125 or PHIL 2010>
            [p <n=ENGL 2111@, m=ENGL 2111@.*>]    
            [p <n=ENGL 2112@, m=ENGL 2112@.*>]    
            [d <n=ENGL 2131>]
            [d <n=ENGL 2132>]
            [d <n=ITDS 1145>]
            [d <n=ITDS 1155>]
            [d <n=ITDS 1774>]
            [d <n=ITDS 2125>]
            [d <n=PHIL 2010>]
        ]

        [s <c=2, n=Choose from 2 of the following:>
            [s <c=2, n=2 Classes in ASTR 1105 and 1305>
                [d <n=ASTR 1105>]
                [d <n=ASTR 1305>]
            ]
            [r <c=4, n=4 Credits in BIOL 1215K>  
                [d <n=BIOL 1215K>]
            ]
            [r <c=4, n=4 Credits in BIOL 1225K>  
                [d <n=BIOL 1225K>]
            ]
            [s <c=2, n=2 Classes in CHEM 1151  and 1151L>
                [d <n=CHEM 1151>]
                [d <n=CHEM 1151L>]
            ]
            [s <c=2, n=2 Classes in CHEM 1152  and 1152L>
                [d <n=CHEM 1152>]
                [d <n=CHEM 1152L>]
            ]
            [r <c=4, n=4 Credits in CHEM 1211@>  
                [p <n=CHEM 1211@, m=CHEM 1211@.*>]    
            ]
            [s <c=2, n=2 Classes in CHEM 1212  and 1212L>
                [d <n=CHEM 1212>]
                [d <n=CHEM 1212L>]
            ]
            [s <c=2, n=2 Classes in ATSC 1112 and 1112L>
                [d <n=ATSC 1112>]
                [d <n=ATSC 1112L>]
            ]
            [s <c=2, n=2 Classes in GEOL 1121  and 1121L>
                [d <n=GEOL 1121>]
                [d <n=GEOL 1121L>]
            ]
            [d <n=GEOL 1121K>]
            [s <c=2, n=2 Classes in GEOL 1122  and 1322>
                [d <n=GEOL 1122>]
                [d <n=GEOL 1322>]
            ]
            [d <n=GEOL 2225>]
            [s <c=2, n=2 Classes in PHYS 1111  and 1311>
                [d <n=PHYS 1111>]
                [d <n=PHYS 1311>]
            ]
            [r <c=4, n=4 Credits in PHYS 1112  or 2211  or 1312>
                [d <n=PHYS 1112>]
                [d <n=PHYS 2211>]
                [d <n=PHYS 1312>]
            ]
            [s <c=2, n=2 Classes in PHYS 1125  and 1325>
                [d <n=PHYS 1125>]
                [d <n=PHYS 1325>]
            ]
            [s <c=2, n=2 Classes in PHYS 2211  and 2311>
                [d <n=PHYS 2211>]
                [d <n=PHYS 2311>]
            ]
            [s <c=2, n=2 Classes in PHYS 2212  and 2312>
                [d <n=PHYS 2212>]
                [d <n=PHYS 2312>]
            ]
            [d <n=ENVS 1205K>]
        ]
        [s <c=1, n=Still needed:1 Class in CPSC 4135  or 5135U>
            [d <n=CPSC 4135>]
            [d <n=CPSC 5135U>]
        ]
        [s <c=1, n=Still needed:1 Class in CPSC 4148  or 5128U>
            [d <n=CPSC 4148>]
            [d <n=CPSC 5128U>]
        ]
        [s <c=1, n=Still needed:1 Class in CPSC 4155  or 5155U>
            [d <n=CPSC 4155>]
            [d <n=CPSC 5155U>]
        ]
        [s <c=1, n=Still needed:1 Class in CPSC 4157  or 5157U>
            [d <n=CPSC 4157>]
            [d <n=CPSC 5157U>]
        ]
        [r <c=6, n=Still needed: 6 Credits in CPSC 3@ or 4@ or 5@ or CYBR  3@ or 
        4@ or 5@>
            [p <n=CPSC 3@, m=CPSC 3@.*>]
            [p <n=CPSC 4@, m=CPSC 4@.*>]
            [p <n=CPSC 5@, m=CPSC 5@.*>]
            [p <n=CYBR 3@, m=CYBR 3@.*>]
            [p <n=CYBR 4@, m=CYBR 4@.*>]
            [p <n=CYBR 5@, m=CYBR 5@.*>]
        ]
        ''',
        'Computer Science - Systems',
        '123456789',
        'AAA, BBB',
        '3.40'
    )

    # Test Case 3
    degreeworks_input_2_ex_out = DegreeExtractionContainer(
        ['MATH 1111', 'ITDS 1779H', 'MATH 2125', 'MATH 1113', 'MATH 5125U', 
         'CPSC 3131', 'CPSC 2108', 'CYBR 2106', 'CYBR 2159', 'CPSC 2105', 
         'CPSC 1302', 'CPSC 1301K', 'PEDS 2378', 'KINS 1106', 'SOCI 1101', 
         'POLS 1101', 'HIST 2111', 'STAT 1401', 'GEOL 1121K', 'BIOL 1215K', 
         'ARTH 1100', 'PHIL 2010', 'PERS 1506', 'COMM 1110', 'ENGL 1102', 
         'ENGL 1101'],
         '''
         (CPSC 3125,CPSC 3165,CPSC 3175,CPSC 4000,CPSC 3121,CPSC 5115U,CPSC 4175,CPSC 4176)

        [s <c=1, n=Still needed:1 Class in ANTH 1105@ or 1107 or 2105 or 2136 or 
        ENGL 2136 or GEOG 1101 or HIST 1111 or 1112 or INTS 2105@ or ITDS 1146 or 1156>
            [p <n=ANTH 1105@, m=ANTH 1105.*>]
            [d <n=ANTH 1107>]
            [d <n=ANTH 2105>]
            [d <n=ANTH 2136>]
            [d <n=ENGL 2136>]
            [d <n=GEOG 1101>]
            [d <n=HIST 1111>]
            [d <n=HIST 1112>]
            [p <n=INTS 2105@, m=INTS 2105.*>]
            [d <n=ITDS 1146>]
            [d <n=ITDS 1156>]
        ]
        [s <c=1, n=Still needed:1 Class in CPSC 4135  or 5135U>
            [d <n=CPSC 4135>]
            [d <n=CPSC 5135U>]
        ]
        [s <c=1, n=Still needed:1 Class in CPSC 4148  or 5128U>
            [d <n=CPSC 4148>]
            [d <n=CPSC 5128U>]
        ]
        [s <c=1, n=Still needed:1 Class in CPSC 4155  or 5155U>
            [d <n=CPSC 4155>]
            [d <n=CPSC 5155U>]
        ]
        [s <c=1, n=Still needed:1 Class in CPSC 4157  or 5157U>
            [d <n=CPSC 4157>]
            [d <n=CPSC 5157U>]
        ]
        [r <c=6, n=Still needed: 6 Credits in CPSC 3@ or 4@ or 5@ or CYBR  3@ or 4@ or 5@>
            [p <n=CPSC 3@, m=CPSC 3.*>]
            [p <n=CPSC 4@, m=CPSC 4.*>]
            [p <n=CPSC 5@, m=CPSC 5.*>]
            [p <n=CYBR 3@, m=CYBR 3.*>]
            [p <n=CYBR 4@, m=CYBR 4.*>]
            [p <n=CYBR 5@, m=CYBR 5.*>]
        ]
        [r <c=5, n=Still needed: 5 Credits in @ 1@ or 2@ or 3@ or 4@ or 5@U Except  ENGL 1101  or    
        1102>
            [p <n= @  1@, m= @  1.*>]
            [p <n= @  2@, m= @  2.*>]
            [p <n= @  3@, m= @  3.*>]
            [p <n= @  4@, m= @  4.*>]
            [p <n= @  5@, m= @  5.*>]
            [d <n=ENGL 1101>]
            [d <n=ENGL 1102>]
        ]
         ''',
         'Computer Science - Systems',
         '123456789',
         'AAA, BBB',
         '3.11'
    )

    test_case_list = []
    # def find_and_display_difference(ex_out, test_out):


    # def find_first_difference(s1, s2):
    #     for idx, (c1, c2) in enumerate(zip(s1, s2)):
    #         if c1 != c2:
    #             return idx
    #     return min(len(s1), len(s2)) if len(s1) != len(s2) else -1

    # def print_difference_chunks(s1, s2, chunk_size=20):
    #     index = find_first_difference(s1, s2)
    #     if index != -1:
    #         s1_chunk = s1[index:index + chunk_size]
    #         s2_chunk = s2[index:index + chunk_size]
    #         print("The index of the first difference is:", index)
    #         print(f"String 1 chunk: {s1_chunk}")
    #         print(f"String 2 chunk: {s2_chunk}")
    #     else:
    #         print("The strings are identical.")

    def add_test(test_name, test_data, ex_out):
        """For each test, a dictionary is added with the following information:"""
        test_case_list.append({"test_name": test_name, "test_data": test_data, "ex_out": ex_out})

    add_test("S1.pdf", './input_files/updated_degreeworks/S1.pdf', degreeworks_input_1_ex_out)
    # add_test("S2.pdf", './input_files/updated_degreeworks/S2.pdf', degreeworks_input_2_ex_out)


    print('=============================== Start Degreeworks Parser Tests ===============================\n')

    for test in test_case_list:
        
        test_container = generate_degree_extraction_container(test["test_data"])
        if test_container._student_name and test["ex_out"]._student_name:
            print(f'test_container student name: {test_container._student_name}')
            print(f'control_container student name: {test["ex_out"]._student_name}')
            print()

        if test_container._student_number and test["ex_out"]._student_number:
            print(f'test_container student number: {test_container._student_number}')
            print(f'control_container student number: {test["ex_out"]._student_number}')
            print()

        if test_container._degree_plan_name and test["ex_out"]._degree_plan_name:
            print(f'test_container degree plan name: {test_container._degree_plan_name}')
            print(f'control_container degree plan name: {test["ex_out"]._degree_plan_name}')
            print()

        if test_container._courses_needed_constuction_string and test["ex_out"]._courses_needed_constuction_string:
            print(f'test_container courses needed construction string: {test_container._courses_needed_constuction_string}')
            print(f'control_container courses needed construction string: {test["ex_out"]._courses_needed_constuction_string}')
            print()

        if test_container._taken_courses and test["ex_out"]._taken_courses:
            print(f'test_container taken courses: {test_container._taken_courses}')
            print(f'control_container taken courses: {test["ex_out"]._taken_courses}')
            print()

        if test_container.__eq__(test["ex_out"]):
            print(f'The {test["test_name"]} test PASSED.')
        else:
            tests_passed = False
            print(f'The {test["test_name"]} test FAILED.')
            # print('The following are the differences between the expected\
            #       output and the generated output:')
            # differ = difflib.Differ()
            # diff = list(differ.compare(str(test_container), str(test["ex_out"])))
            # for line in diff:
            #     if line.startswith("+") or line.startswith("-"):
            #         print(line)
            # print(diff)
    print('\n=============================== End Degreeworks Parser Tests ===============================\n')

    return tests_passed