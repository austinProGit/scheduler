# Max Lewis
# 9/27/22
# CPSC 4175 Group Project

import sys

sys.path.append('../src') # this depends on your directory names and path
import pandas as pd
from course_info_container import CourseInfoContainer # gives 'could not be resolved'; maybe different directory causes this
# But still works when we use the sys.path.append

# ================================ Unit Tests =======================================================

def container_tests() :
    tests_passed = True
    headers = ['courseID', 'courseName', 'availability', 'prerequisites',
              'co-requisites', 'recommended', 'note', 'hours']

    data = [['CPSC 1111', 'Intro', 'Fa Sp Su', 'MATH 1111', 'MATH 0000', 'CPSC 0000', 'Start', '((1-3)-0-(1-3))'], 
            ['CPSC 2222', 'Second', 'Fa Sp Su', 'CPSC 1111, MATH 1111', 'MATH 2222', 'CPSC 0001', 'Middle', '(3-0-1)'],
            ['CPSC 3333', None, None, None, None, None, None, '8'],
            ['CPSC 4444', 'Four', 'Fa -- --', 'none', None, '??', None, 2]]

    excused_prereqs = ['MISM 3145', 'MISM 3115', 'MISM 3109', 'MATH 1111', 'MATH 1131', 'MATH 1132']

    df = pd.DataFrame(data, columns = headers)
    container = CourseInfoContainer(df, excused_prereqs) #Updated to include excused_prereqs by Austin Lee
    print(df)
    print()
    

    print('=============================== Start Container Tests ===============================')

    c1, c2, c3, c4 = 'CPSC 1111', 'CPSC 2222','CPSC 3333','CPSC 4444'

    if container.get_courseIDs() == [c1, c2, c3, c4]:
        print('courseIDs test passed')
    else:
        tests_passed = False
        print('courseIDs test failed')
    
    if container.get_name(c1) == 'Intro':
        print('name test passed')
    else:
        tests_passed = False
        print('name test failed')

    if container.get_availability(c3) == ['Fa', 'Sp', '--']:
        print('avail test passed')
    else:
        tests_passed = False
        print('avail test failed')

    if container.get_prereqs(c2) == ['CPSC 1111', 'MATH 1111']:
        print('prereq test passed')
    else:
        tests_passed = False
        print('prereq test failed')

    if container.get_coreqs(c3) == []:
        print('coreq test passed')
    else:
        tests_passed = False
        print('coreq test failed')

    if container.get_recommended(c3) == []:
        print('recommended test passed')
    else:
        tests_passed = False
        print('recommended test failed')

    if container.get_note(c1) == 'Start':
        print('note test passed')
    else:
        tests_passed = False
        print('note test failed')

    if container.get_hours(c1) == 3 and container.get_hours(c2) == 1 and container.get_hours(c3) == 8 and container.get_hours(c4) == 2:
        print('hour test passed')
    else:
        tests_passed = False
        print('hour test failed')

    if container.get_isElective(c1) == False:
        print('is elective test passed')
    else:
        tests_passed = False
        print('is elective test failed')

    if container.get_electives() == []:
        print('get all electives test passed')
    else:
        tests_passed = False
        print('get all electives test failed')

    if container.validate_header('courseID') == True and container.validate_header('bullshit') == False:
        print('validate header test passed')
    else:
        tests_passed = False
        print('validate header test failed')

    if container.validate_course(c1) == True and container.validate_course('bullshit') == False:
        print('validate course test passed')
    else:
        tests_passed = False
        print('validate course test failed')


    print('=============================== End Container Tests ===============================\n')
    return tests_passed