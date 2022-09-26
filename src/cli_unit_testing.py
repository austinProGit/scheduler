# Thomas Merino
# 9/24/22
# CPSC 4175 Group Project

from program_driver import SmartPlannerController
import re

# MERINO: reworked this whole thing

# Unit testing for CLI and controller/driver

# NOTE: this uses the ":=" operator, so you must be using a more recent version of Python to run testing

# TODO: (WISH) Use built-in listener from controller instead of setting output method
# TODO: (NEED) Finish adding testing cases

# The following is a list pairings where the first item is the input and the next is a regex expression that should describe the output.
# That is, the first item in the list should provide the first input and reflect the first lines of output.
# An expected pattern of None means no check is done.
pairing_stream = [
    ('commands',                                r'(?i)(.*)(\bcommands available\b)(.*?)'),
    ('load',                                    r'(?i)(.*)(\bplease enter\b)(.*?)'),
    ('load input_files/Sample Input1.pdf',      r'(.*)(\bloaded\b)(.*?)'),
    ('needed input_files/Sample Input2.pdf',    r'(.*)(\bloaded\b)(.*?)'),
    ('set input_files/Sample Input3.pdf',       r'(.*)(\bloaded\b)(.*?)'),
    ('dest',                                    r'(?i)(.*)(\bplease enter\b)(.*?)'),
    ('dest ~',                                  r'(?i)(.*)(\bset to\b)(.*?)'),
    ('hours',                                   r'(?i)(.*)(\bsorry, that is not a valid input\b)(.*?)'),
    ('hours 14',                                r'(.*)(\b14\b)(.*?)'),
    ('hours nine',                              r'(?i)(.*)(\bsorry, that is not a valid input\b)(.*?)'),
    ('types',                                   r'(?i)(.*)(\b1: path to graduation\b)(.*?)'),
    ('2',                                       None),
    ('2',                                       r'(?i)(.*)(\balready selected\b)(.*?)'),
    ('rm',                                      r'(?i)(.*)(\bremoval mode\b)(.*?)'),
    ('1',                                       None),
    ('1',                                       r'(?i)(.*)(\bnot selected\b)(.*?)'),
    ('list',                                    r'(?i)(.*)(\bpath to graduation\b)(.*?)'),
    ('done',                                    r'(?i)(.*)(\btype\(s\) set\b)(.*?)'),
    ('schedule',                                r'(?i)(.*)(\bplease enter a filename\b)(.*?)'),
    ('schedule file',                           r'(?i)(.*)(\bno needed courses\b)(.*?)'),
    ('help',                                    r'(?i)(.*)(\bhelp\b)(.*?)'),
    ('exit',                                    None),
    ('help load',                               r'(?i)(.*)(\bmight help\b)(.*?)'),
    ('quit',                                    None),
    ('abcdef',                                  r'(?i)(.*)(\bsorry, no command\b)(.*?)'),
    ('quit',                                    r'(?i)(.*)(\bgoodbye\b)(.*?)'),
]

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
    value = pairing_stream[input_index[0]][0]
    input_index[0] += 1
    return value

def dummy_load_courses_needed(self, filename):
    self.output('loaded')
    return True


# Helper function to get latest expected regex
def get_expected_regex():
    return pairing_stream[input_index[0] - 1][1]


# Save the old IO functions
old_output = SmartPlannerController.output
old_get_input = SmartPlannerController.get_input
old_load_courses = SmartPlannerController.load_courses_needed

# Override existing IO functions
SmartPlannerController.output = pipe_output_to_stream
SmartPlannerController.get_input = get_input_from_stream
SmartPlannerController.load_courses_needed = dummy_load_courses_needed

planner = SmartPlannerController(graphics_enabled=False)


#  Execute an entire session until it quits, applying tests as it goes
while planner.run_top_interface():
    
    if (expected_pattern := get_expected_regex()):
        
        matches_pattern = re.match(expected_pattern, working_output[0])
        if matches_pattern:
            print('General UX test {0}: pass'.format(input_index[0]))
        else:
            print('General UX test {0}: FAIL - {1} - got "{2}"'.format(input_index[0], pairing_stream[input_index[0] - 1][0], working_output[0]))
    flush_working_output()

# Perform tests on each line of output
#for test_index in range(len(output_stream_list)):
#    stream_output = output_stream_list[test_index]
#    matches_pattern = re.match(expected_patterns[test_index], stream_output)
#    if matches_pattern:
#        print('General UX test {0}: pass'.format(test_index + 1))
#    else:
#        print('General UX test {0}: FAIL - got "{1}"'.format(test_index + 1, stream_output))

# Set the IO functions back as they were
SmartPlannerController.output = old_output
SmartPlannerController.get_input = old_get_input
SmartPlannerController.load_courses_needed = old_load_courses

