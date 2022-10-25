# Authors: All Members
# Date: 9/21/22
# CPSC 4175 Group Project

from program_generated_validator_tests import program_generated_validator_tests
from container_tests import container_tests
from user_submitted_validator_tests import user_submitted_validator_tests
from cli_unit_testing import run_cli_unit_test
import traceback

def all_tests():

    tests = []

    def add_test(test_name, test_func):
        tests.append((test_name, test_func))
    
    # Add all tests below as add_test('test_name', test_func)
    add_test('program_generated_validator', program_generated_validator_tests)
    add_test('container', container_tests)
    add_test('user_submitted_validator', user_submitted_validator_tests)
    add_test('cli', run_cli_unit_test)

    tests_passed = True

    failed_tests = []

    for test_name, test_func in tests:
        try:
            if not test_func():
                tests_passed = False
                failed_tests.append(test_name)
        except Exception as error:
            traceback.print_exc()
            tests_passed = False
            failed_tests.append(test_name)
    if not tests_passed:
        print(f'The following tests have FAILED: {failed_tests}')
    else:
        print('\nAll tests have PASSED.')

    return tests_passed

if __name__ == '__main__':
    all_tests()