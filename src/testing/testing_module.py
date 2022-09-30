# Authors: All Members
# Date: 9/21/22
# CPSC 4175 Group Project

from dag_validator_tests import dag_validator_tests
from container_tests import container_tests
from user_submitted_validator_tests import user_submitted_validator_tests
from cli_unit_testing import run_cli_unit_test

def all_tests():
    tests_passed = True
    failed_tests = []
    if not dag_validator_tests():
        tests_passed = False
        failed_tests.append('dag_validator')
    if not container_tests():
        tests_passed = False
        failed_tests.append('container')
    if not user_submitted_validator_tests():
        tests_passed = False
        failed_tests.append('user_submitted_validator')
    if not run_cli_unit_test():
        tests_passed = False
        failed_tests.append('cli')
    # ADD ALL TESTS HERE ^^^
    if not tests_passed:
        print(f'The following tests have FAILED: {failed_tests}')
    else:
        print('\nAll tests have PASSED.')
    return tests_passed

all_tests()
