# Authors: All Members
# Date: 9/21/22
# CPSC 4175 Group Project

from program_generated_validator_tests import program_generated_validator_tests
from course_info_container_tests import course_info_container_tests
from user_submitted_validator_tests import user_submitted_validator_tests
from cli_unit_testing import run_cli_unit_test
from degreeworks_parser_v2_tests import degreeworks_parser_v2_tests
from scheduler_driver_testing import validation_and_scheduling_unit_test
from traceback import print_exc
import traceback
import datetime
from driver_fs_functions import *

def all_tests():
    
    tests = []

    def add_test(test_name, test_func):
        tests.append((test_name, test_func))
    
    # Add all tests below as add_test('test_name', test_func)
    add_test('program_generated_validator', program_generated_validator_tests)
    add_test('container', course_info_container_tests)
    add_test('cli', run_cli_unit_test)
    # add_test('user_submitted_validator', user_submitted_validator_tests)
    add_test('degreeworks_parser_v2', degreeworks_parser_v2_tests)
    add_test('validator and scheduling minimum', validation_and_scheduling_unit_test)

    tests_passed = True
    
    failed_tests = []
    test_reports = []

    for test_name, test_func in tests:

        report = TestReport()
        report.name = test_name + " test"

        try:
            if not test_func():
                tests_passed = False
                failed_tests.append(test_name)
        except Exception as error:
            print_exc()
            tests_passed = False
            failed_tests.append(test_name)
            failed = "*************** FAILED *************** FAILED *************** FAILED ***************"
            traceback_text = traceback.format_exc()
            report.passed = failed
            report.trace = traceback_text

        test_reports.append(report)

    persist = True
    if persist: write_reports(test_reports)

    if not tests_passed:
        print(f'The following tests have FAILED: {failed_tests}')
    else:
        print('\nAll tests have PASSED.')



    return tests_passed


class TestReport:

    def __init__(self):
        self.name = None
        self.passed = "*************** PASSED *************** PASSED *************** PASSED ***************"
        self.trace = "*************** PASSED *************** PASSED *************** PASSED ***************"


    def __str__(self):
        attribute_strings = ""
        for attribute_name, attribute_value in vars(self).items():
            attribute_strings += (f"\n{attribute_value}\n")
        return attribute_strings


def write_reports(test_reports):
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file0 = get_source_path()
    file0 = get_source_relative_path(file0, f"testing/test_reports/{current_datetime}.txt")

    with open(file0, "w") as file:
        for report in test_reports:
            file.write(str(report))

        print("Please comment to correct errors in display.")
        comment = input()
        file.write(f"\nComments: {comment}\n")


# Allow for local execution
if __name__ == '__main__':
    all_tests()
