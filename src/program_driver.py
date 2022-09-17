# Thomas Merino
# 9/16/22
# CPSC 4175 Group Project

# NOTE: there needs to be a file called "config" in the same directory as this file.
#   The config file stores in the first line the name of the course info filename. This is what's passed into the parser as input. The
#   The second line detemines whether to load the gui (if "YES" is in the second line)

# TO THOSE INTERESTED: place YES as the second line of the "config" file to try out the GUI. This has fewer features right now, but it should give you a taste of what QT can provide (or least the minimum). I would still need to add labels and instructions, of course.

# TODO: Finish unit testing.
# TODO: Maybe add session data so the program can recover from a crash
# TODO: Have the user store/set in the config file whether to open in GUI or CLI (this may be changed in either interface)
# TODO: Have the last directory used for saving stored in the config
# TODO: Maybe make the name of the help file included in config
# TODO: Ensure exception raising is implemented in other modules (e.g. NonDAGCourseInfoError)
# TODO: Create the driver-level interface for getting item selection (e.g. for selecting electives)
# TODO: Add support for course info being in a different directoy (and different OS)
# TODO: Set up error codes or boolean return (other modules)
# TODO: Add status command that prints scheduling parameters
# TODO: Add confirmation menu that shows warnings when a large number of hours per semester is entered or a file will be overriden

from sys import exit
from cli_interface import *
from graphical_interface import *

DEFAULT_CATALOG_NAME = 'catalog.xlsx'
CONFIG_FILENAME = 'config'

## --------------------------------------------------------------------- ##
## ----------- The following are dummy classes and functions ----------- ##
## --------------------------------------------------------------------- ##


class CourseInfoDataframeContainer:
    def __init__(self, df):
        pass

    def display(self):
        pass

    def get_name(self, courseid):
        pass
   
    def get_availability(self, courseid):
        pass

    def get_prereqs(self, courseid):
        pass

    def get_coreqs(self, courseid):
        pass

    def get_recommended(self, courseid):
        pass

class NonDAGCourseInfoError(Exception):
    pass

def get_course_info(file_name):
   return None
   
def get_courses_needed(file_name):
    return []

class Scheduler:
    def __init__(self):
        self.h = 14
        
    def get_hours_per_semester(self):
        return self.h
        
    def configure_course_info(self, container):
        pass
        
    def configure_courses_needed(self, container):
        pass
    
    def configure_hours_per_semester(self, number_of_hours):
        self.h = number_of_hours
    
    def generate_schedule(self, filename):
        pass

## --------------------------------------------------------------------- ##
## ------------------------ Smart Planner Driver ----------------------- ##
## --------------------------------------------------------------------- ##

# This exception is used when an issue with interface presentation is encountered.
# Handling one should only be done for the sake of saving important data.
class InterfaceProcedureError(Exception):
    pass
    
    
class SmartPlannerController:

    def __init__(self):
        self.setup()
        
    def setup(self):
        '''Perform setup for scheduling, general configuration, and user interface'''
        
        # Initialize important variables
        self._scheduler = Scheduler()

        # Load the course info file
        self.load_course_info()
        
        # Load the user interface
        self.load_interface()
    
    def load_course_info(self):
        '''Load the course info file and use it to configure the scheduler. If the process fails, an error menu is pushed onto the interface stack.'''
        # Create a variable to track where the course info file should be
        course_info_filename = None
        
        # Attempt to load the course info data
        try:
            # Get the config file (the first line of which should be the course info filename)
            with open(CONFIG_FILENAME) as configuration_file:
                course_info_filename = configuration_file.readline()
                course_info_container = get_course_info(course_info_filename)
                
        except FileNotFoundError:
            if course_info_filename == None:
                # Configuration file could not be found (report to the user and enter the error menu)
                self.output_error('Invalid config file. Please see instructions on how to reconfigure.')
            else:
                # Course info could not be found (report to the user and enter the error menu)
                self.output_error('Invalid course catalog file. Please rename the catalog to {} and reload the catalog (enter "reload").'.format(course_info_filename))
            self.enter_error_menu()
            
        except NonDAGCourseInfoError:
            # The catalog was/is invalid (report to the user and enter the error menu)
            self.output_error('Course catalog contains invalid data. Please correct all issues and reload the catalog (enter "reload").')
            self.enter_error_menu()
    
    def load_interface(self):
        '''Load the program's interface (this should be called only once).'''
        try:
            # TODO: prevent reloading of config file
            
            # Get the config file (the second line of which should be UI type)
            with open(CONFIG_FILENAME) as configuration_file:
                configuration_file.readline()
                is_graphical = 'YES' in configuration_file.readline()
                if is_graphical:
                    application = QtWidgets.QApplication.instance()
                    if not application:
                        application = QtWidgets.QApplication([])
                    new_main_menu = MainMenuWidget(self)
                    self._interface_stack = [new_main_menu]
                    new_main_menu.resize(300, 300)
                    new_main_menu.show()
                    exit(application.exec())
                else:
                    self._interface_stack = [MainMenuInterface()]
                
        except FileNotFoundError:
            # Configuration file could not be found (report to the user and enter the error menu)
            self.output_error('Invalid config file. Please see instructions on how to reconfigure.')
            self.enter_error_menu()
        

    ## ----------- User interface methods ----------- ##

    def output(self, message):
        '''Output a message to the user.'''
        print(message)

    def output_error(self, message):
        '''Output an error message to the user.'''
        self.output('ERROR: {0}'.format(message))

    ## ----------- Interface/menu control ----------- ##
    
    
    def get_input(self):
        '''Get input text from the user with the current interface's/menu's name in the prompt.'''
        current_interface = self.get_current_interface()
        return input('{0}: '.format(current_interface.name))

    def get_current_interface(self):
        '''Get the interface/menu that is presenting.'''
        
        # Ensure the is a interface (if not, raise a InterfaceProcedureError)
        if len(self._interface_stack) == 0:
            raise InterfaceProcedureError()
            
        # Return the top interface
        return self._interface_stack[-1]

    def has_interface(self):
        '''Gets whether the is an interface in the interface stack.'''
        return len(self._interface_stack) != 0

    def push_interface(self, interface):
        '''Push a given interface to the top of the interface stack.'''
        self._interface_stack.append(interface)

    def pop_interface(self, interface):
        '''Pop the provided interface if it on top of the interface stack. Otherwise, raise a InterfaceProcedureError.'''
        
        # Check if the passed interface resides on the top of the stack
        if interface == self.get_current_interface():
            top_interface = self._interface_stack.pop()     # Pop the passed interface
            top_interface.deconstruct(self)                 # Call the interface's deconstruct method
            return top_interface
        else:
            raise InterfaceProcedureError()                 # Raise an error about the illegal procedure
            
    def clear_all_interfaces(self):
        '''Clear the interface stack (this dismisses all interface in order from highest to lowest).'''
        while self.has_interface():
            self.pop_interface(self.get_current_interface())

    def enter_error_menu(self):
        '''Push an error menu onto the menu stack so the user can correct errors before reloading.'''
        self.push_interface(ErrorMenu())
                
    ## ----------- Info getting ----------- ##
    
    def get_hours_per_semester(self):
        return self._scheduler.get_hours_per_semester()
                
    ## ----------- Scheduling procedure configuration ----------- ##

    def load_courses_needed(self, filename):
        '''Load the courses that must be scheduled into the scheduler (from a filename). This return the success of the load.'''
        success = False
        try:
            courses_needed_list = get_courses_needed(filename)                          # Get the needed courses from the file
            self._scheduler.configure_courses_needed(courses_needed_list)               # Load the course list into the scheduler
            self.output('Course requirements loaded from {0}.'.format(filename))        # Report success to the user
            success = True                                                              # Set success to true
        except FileNotFoundError:
            output_error('Sorry, {0} could not be found.'.format(filename))             # Report if the file was not found
        return success
        
    
    def configure_hours_per_semester(self, number_of_hours):
        '''Set the number of hours that are scheduled per semester.'''
        self._scheduler.configure_hours_per_semester(number_of_hours)
        self.output('Hours per semester set to {0}.'.format(number_of_hours))
        
    def generate_schedule(self, filename):
        '''Generate the schedule with a given filename.'''
        self.output('Generating schedule...')
        self._scheduler.generate_schedule(filename)
        print(filename) # TODO: Remove this test
        self.output('Schedule complete.')
        
    def run_top_interface(self):
        '''Gets input from the user and passed that input into the presenting interface/menu. The method then returns whether there are any interfaces left presenting. In the case there aren't any, the method should not be called again. This may act as the program's entire loop.'''
        user_input = self.get_input()                            # Get input from the user
        current_interface = self.get_current_interface()         # Get the current interface/menu
        current_interface.parse_input(self, user_input)          # Pass the user's input to the current menu
        return len(self._interface_stack) != 0                   # return whether there are still any interfaces presenting


## --------------------------------------------------------------------- ##
## --------------------- Program Setup and Testing --------------------- ##
## --------------------------------------------------------------------- ##


def test_driver_and_interface():
    '''Unit test for UX and driver.'''
    
    # TODO: This may be a bad practice
    import re
    
    # Create stream lists to hold/capture interface input/output
    output_stream_list = []
    input_stream_list = [
        'load', 'load file1', 'set file2', 'set file3',
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
    
    planner = SmartPlannerController()
    
    #  Execute an entire session until it quits
    while planner.run_top_interface(): pass
    
    # The following is a list of regex expressions that should describe each line of output
    # That is, the first item in the list should reflect the first line of output
    expected_patterns = [
        r'(?i)(.*)(\bplease enter a filename\b)(.*?)',
        r'(.*)(\bfile1\b)(.*?)',
        r'(.*)(\bfile2\b)(.*?)',
        r'(.*)(\bfile3\b)(.*?)',
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


# Testing:
if __name__ == "__main__":

    test_driver_and_interface()
    
    planner = SmartPlannerController()
    while planner.run_top_interface(): pass
