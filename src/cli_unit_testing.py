# Thomas Merino
# 9/19/22
# CPSC 4175 Group Project

from program_driver import SmartPlannerController
import re

# Unit testing for CLI and controller/driver

# TODO: Add more tests and load a different file (not icon.png).
# TODO: Fix weird 'resulthelp' print upon running the tests.


# Create stream lists to hold/capture interface input/output
output_stream_list = []
input_stream_list = [
    'load', 'load icon.png', 'set icon.png', 'set icon.png',
    'commands',
    'hours', 'hours 14', 'hours nine',
    'schedule', 'schedule result'
    'help', 'exit', 'help load', 'quit',
    'quit'
]

# Define some overriding functions to replace program IO (these functions capture input/output)
def pipe_output_to_stream(self, message): output_stream_list.append(message)
def get_input_from_stream(self):
    value = input_stream_list[0]
    del input_stream_list[0]
    return value

# Save the old IO functions
old_output = SmartPlannerController.output
old_get_input = SmartPlannerController.get_input

# Override existing IO functions
SmartPlannerController.output = pipe_output_to_stream
SmartPlannerController.get_input = get_input_from_stream

planner = SmartPlannerController(graphics_enabled=False)

#  Execute an entire session until it quits
while planner.run_top_interface(): pass

# The following is a list of regex expressions that should describe each line of output
# That is, the first item in the list should reflect the first line of output
expected_patterns = [
    r'(?i)(.*)(\bplease enter\b)(.*?)',
    r'(.*)(\bloaded\b)(.*?)',
    r'(.*)(\bloaded\b)(.*?)',
    r'(.*)(\bloaded\b)(.*?)',
    r'(?i)(.*)(\bcommands available\b)(.*?)',
    r'(?i)(.*)(\bsorry, that is not a valid input\b)(.*?)',
    r'(.*)(\b14\b)(.*?)',
    r'(?i)(.*)(\bsorry, that is not a valid input\b)(.*?)',
    r'(?i)(.*)(\bplease enter a filename\b)(.*?)',
    r'(?i)(.*)(\bgenerating schedule\b)(.*?)',
    r'(?i)(.*)(\bschedule complete\b)(.*?)',
    r'(?i)(.*)(\bgoodbye\b)(.*?)',
]

# Perform tests on each line of output
for test_index in range(len(output_stream_list)):
    stream_output = output_stream_list[test_index]
    matches_pattern = re.match(expected_patterns[test_index], stream_output)
    if matches_pattern:
        print('General UX test {0}: pass'.format(test_index + 1))
    else:
        print('General UX test {0}: FAIL - got "{1}"'.format(test_index + 1, stream_output))

# Set the IO functions back as they were
SmartPlannerController.output = old_output
SmartPlannerController.get_input = old_get_input

