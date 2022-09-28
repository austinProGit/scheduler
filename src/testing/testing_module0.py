# Authors: All Members
# Date: 9/27/22
# CPSC 4175 Group Project

from dag_validator_tests import dag_validator_tests
from container_tests import container_tests

def all_tests():
    tests_passed = True
    failed_tests = []
    #if not dag_validator_tests():
    #    tests_passed = False
    #    failed_tests.append('dag_validator')
    # ADD ALL TESTS HERE ^^^
    if not container_tests():
        tests_passed = False
        failed_tests.append('container')
    if not tests_passed:
        print(f'The following tests have failed: {failed_tests}')
    else:
        print('All tests have passed.')
    return tests_passed

all_tests()
