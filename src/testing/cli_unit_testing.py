# Thomas Merino
# 9/30/22
# CPSC 4175 Group Project


# Unit testing for CLI and controller/driver

# NOTE: this uses the ":=" operator, so you must be using a more recent version of Python to run testing

import sys
import os
import re
 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)


from program_driver import SmartPlannerController

# TODO: (WISH) Use built-in listener from controller instead of setting output method

def run_cli_unit_test():
    '''Returns true if all test passes.'''
    
    tests = []

    def add_test(command, expected_pattern):
        tests.append({"name": 'CLI Test{0}({1})'.format(len(tests) + 1, command),
                      "command":command,
                      "expected_pattern":expected_pattern})
    
    add_test('commands',                                r'(?i)(.*)(\bcommands available\b)(.*?)')
    add_test('load',                                    r'(?i)(.*)(\bplease enter\b)(.*?)')
    add_test('load input',                              r'(.*)(\bloaded\b)(.*?)')
    add_test('needed input file',                       r'(.*)(\bloaded\b)(.*?)')
    add_test('set input file',                          r'(.*)(\bloaded\b)(.*?)')
    add_test('dest',                                    r'(?i)(.*)(\bplease enter\b)(.*?)')
    add_test('dest ~',                                  r'(?i)(.*)(\bset to\b)(.*?)')
    add_test('hours',                                   r'(?i)(.*)(\bsorry, that is not a valid input\b)(.*?)')
    add_test('hours 14',                                r'(.*)(\b14\b)(.*?)')
    add_test('hours nine',                              r'(?i)(.*)(\bsorry, that is not a valid input\b)(.*?)')
    add_test('types',                                   r'(?i)(.*)(\b1: path to graduation\b)(.*?)')
    add_test('2',                                       None)
    add_test('2',                                       r'(?i)(.*)(\balready selected\b)(.*?)')
    add_test('rm',                                      r'(?i)(.*)(\bremoval mode\b)(.*?)')
    add_test('1',                                       None)
    add_test('1',                                       r'(?i)(.*)(\bnot selected\b)(.*?)')
    add_test('list',                                    r'(?i)(.*)(\bpath to graduation\b)(.*?)')
    add_test('done',                                    r'(?i)(.*)(\btype\(s\) set\b)(.*?)')
    add_test('schedule',                                r'(?i)(.*)(\bplease enter a filename\b)(.*?)')
    add_test('schedule file',                           r'(?i)(.*)(\bno needed courses\b)(.*?)')
    add_test('help',                                    r'(?i)(.*)(\bhelp\b)(.*?)')
    add_test('exit',                                    None)
    add_test('help load',                               r'(?i)(.*)(\bmight help\b)(.*?)')
    add_test('quit',                                    None)
    add_test('abcdef',                                  r'(?i)(.*)(\bsorry, no command\b)(.*?)')
    add_test('quit',                                    r'(?i)(.*)(\bgoodbye\b)(.*?)')
    
    
    # Output monitoring
    working_output = ['']   # This a one-item list so it behaves like a pointer
    output_stream_list = [] # This is not used in the current implementation, but can be printed for better debugging
    def flush_working_output():
        output_stream_list.append(working_output[0])
        working_output[0] = ''
    
    # Define some overriding functions to replace program IO (these functions capture input/output)
    
    def pipe_output_to_stream(self, message):
        working_output[0] += message + ' '
    
    input_index = [0]   # This a one-item list so it behaves like a pointer
    def get_input_from_stream(self):
        value = tests[input_index[0]]['command']
        input_index[0] += 1
        return value
    
    def dummy_load_courses_needed(self, filename):
        self.output('loaded')
        return True
    
    
    # Helper function to get latest expected regex
    def get_test_arguments_dictionary():
        return tests[input_index[0] - 1]


    # Save the old IO functions
    old_output = SmartPlannerController.output
    old_get_input = SmartPlannerController.get_input
    old_load_courses = SmartPlannerController.load_courses_needed

    # Override existing IO functions
    SmartPlannerController.output = pipe_output_to_stream
    SmartPlannerController.get_input = get_input_from_stream
    SmartPlannerController.load_courses_needed = dummy_load_courses_needed

    planner = SmartPlannerController(graphics_enabled=False)
    all_tests_have_passed = True


    #  Execute an entire session until it quits, applying tests as it goes
    while planner.run_top_interface():
        test_arguments_dictionary = get_test_arguments_dictionary()
        test_name = test_arguments_dictionary['name']
        test_command = test_arguments_dictionary['command']
        test_expected_pattern = test_arguments_dictionary['expected_pattern']
        
        if test_expected_pattern:
            
            matches_pattern = re.match(test_expected_pattern, working_output[0])
            if matches_pattern:
                print('{0}: pass'.format(test_name))
            else:
                print('{0}: FAIL - {1} - got "{2}"'.format(test_name, test_command, working_output[0]))
                all_tests_have_passed = False
        flush_working_output()
        
    # Set the IO functions back as they were
    SmartPlannerController.output = old_output
    SmartPlannerController.get_input = old_get_input
    SmartPlannerController.load_courses_needed = old_load_courses
    
    return all_tests_have_passed

