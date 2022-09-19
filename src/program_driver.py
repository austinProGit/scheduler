# Thomas Merino
# 9/19/22
# CPSC 4175 Group Project

# NOTE: there needs to be a file called "config" in the same directory as this file.
#   The config file stores in the first line the name of the course info filename. This is what's passed into the parser as input. The
#   The second line detemines whether to load the gui (if "YES" is in the second line)

# TO THOSE INTERESTED: place YES as the second line of the "config" file to try out the GUI. This has fewer features right now, but it should give you a taste of what QT can provide (or least the minimum). I would still need to add labels and instructions, of course.

# TODO: Finish unit testing.
# TODO: Maybe add session data so the program can recover from a crash
# TODO: Have the last directory used for saving stored in the config
# TODO: Ensure the directories in the config file work no matter the OS (if not implement).
# TODO: Maybe make the name of the help file included in config
# TODO: Ensure exception raising is implemented in other modules (e.g. NonDAGCourseInfoError)
# TODO: Create the driver-level interface for getting item selection (e.g. for selecting electives)
# TODO: Ensure support for course info being in a different directoy (and different OS)
# TODO: Set up error codes or boolean return (other modules)
# TODO: Add status command that prints scheduling parameters
# TODO: Add confirmation menu that shows warnings when a large number of hours per semester is entered or a file will be overriden
# TODO: Implement saving destination in the driver (not just GUIs)
# TODO: Fix the unit tests to reflect the change in CLI user interface
# TODO: Determine if we need os.path and pathlib.Path
# TODO: Fix program icon appearing for browser (default Python icon)

from PySide6 import QtWidgets, QtGui

from sys import exit
from pathlib import Path
from os import path

from cli_interface import MainMenuInterface, GraphicalUserInterfaceMenu, ErrorMenu



DEFAULT_CATALOG_NAME = 'catalog.xlsx'           # The name of the catalog/course info file
CONFIG_FILENAME = 'config'                      # The name of the configuration file
DEFAULT_SCHEDULE_NAME = 'Path to Graduation'    # The default filename to export schedules with

PATH_TO_GRADUATION_EXPORT_TYPE = 0x00
PLAIN_TEXT_EXPORT_TYPE = 0x01

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

# This exception is used when an issue with config file is encountered.
class ConfigFileError(Exception):
    pass

# This class manages the interactions between the interface of the program and the model (mostly the scheduler).
# The class also manages the destination directory and filename.
class SmartPlannerController:

    def __init__(self, graphics_enabled=True):
        self.setup(graphics_enabled)
        
    def setup(self, graphics_enabled=True):
        '''Perform setup for scheduling, general configuration, and user interface'''
        
        # Initialize important variables
        self._scheduler = Scheduler()
        self._destination_directory = Path.home()
        self._destination_filename = DEFAULT_SCHEDULE_NAME
        self._export_types = [PATH_TO_GRADUATION_EXPORT_TYPE]
        self._interface_stack = []

        try:
            # Attempt to get program parameters from the config file
            course_info_filename, is_graphical = self.load_config_parameters()
            is_graphical = is_graphical and graphics_enabled
            
            # Load the course info file
            self.load_course_info(course_info_filename)
            
            # Load the user interface -- the program will
            self.load_interface(is_graphical)
            
        except (ConfigFileError, FileNotFoundError, IOError, NonDAGCourseInfoError):
            # Some error was encountered during loading (enter the error menu)
            self.output_error('A problem was encountered while during loading--Entering error menu...')
            self.enter_error_menu()
    
    
    def load_config_parameters(self):
        try:
            # Get the config file (the first line of which should be the catalog/course info filename)
            with open(CONFIG_FILENAME, 'r') as configuration_file:
            
                course_info_filename = configuration_file.readline()
                is_graphical_line = configuration_file.readline()
                
                # Check if both lines exist and are not empty strings
                if course_info_filename and is_graphical_line:
                    is_graphical = 'YES' in is_graphical_line
                    return (course_info_filename, is_graphical)
                else:
                    # Configuration is missing important data (report to the user and raise a config error)
                    self.output_error('Invalid config file contents. Please see instructions on how to reconfigure.')
                    raise ConfigFileError()
                
        except (FileNotFoundError, IOError):
            # Configuration file could not be found (report to the user and raise a config error)
            self.output_error('Could not get config file. Please see instructions on how to reconfigure.')
            raise ConfigFileError()
    
    
    def load_course_info(self, course_info_filename):
        '''Configure the scheduler with the course info file with the passed filename.'''
        
        # Attempt to load the course info data
        try:
            course_info_container = get_course_info(course_info_filename)
            
        except (FileNotFoundError, IOError) as file_error:
            # Course info could not be found (report to the user and re-raise the error to enter error menu)
            self.output_error('Invalid course catalog file. Please rename the catalog to {} and reload the catalog (enter "reload").'.format(course_info_filename))
            raise file_error
            
        except NonDAGCourseInfoError as non_dag_error:
            # The catalog was/is invalid (report to the user and re-raise the error to enter error menu)
            self.output_error('Course catalog contains invalid data. Please correct all issues and reload the catalog (enter "reload").')
            raise non_dag_error
    
    
    def load_interface(self, is_graphical):
        '''Load the program's interface (this should be called only once).'''
        bottom_interface = GraphicalUserInterfaceMenu() if is_graphical else MainMenuInterface()
        self.push_interface(bottom_interface)
    

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
        interface.was_pushed(self)

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
        '''Push an error menu onto the menu stack so the user can correct errors before reloading.
        This blocks execution until the error menu exits.'''
        new_error_menu = ErrorMenu()
        self.push_interface(new_error_menu)
        while new_error_menu in self._interface_stack:
                self.run_top_interface()
                
    ## ----------- Info getting ----------- ##
    
    def get_hours_per_semester(self):
        return self._scheduler.get_hours_per_semester()
    
    def get_destination_filename(self):
        return self._destination_filename
    
    def get_destination_directory(self):
        return self._destination_directory
    
    def is_using_export_type(self, export_type):
        return export_type in self._export_types
    
    ## ----------- Scheduling procedure configuration ----------- ##

    def load_courses_needed(self, filename):
        '''Load the courses that must be scheduled into the scheduler (from a filename). This return the success of the load.'''
        success = False
        try:
            courses_needed_list = get_courses_needed(filename)                          # Get the needed courses from the file
            self._scheduler.configure_courses_needed(courses_needed_list)               # Load the course list into the scheduler
            self.output('Course requirements loaded from {0}.'.format(filename))        # Report success to the user
            success = True                                                              # Set success to true
        except (FileNotFoundError, IOError):
            output_error('Sorry, {0} could not be found.'.format(filename))             # Report if the file was not found
        return success
        
    
    def configure_hours_per_semester(self, number_of_hours):
        '''Set the number of hours that are scheduled per semester.'''
        self._scheduler.configure_hours_per_semester(number_of_hours)
        self.output('Hours per semester set to {0}.'.format(number_of_hours))
        
    def configure_destination_filename(self, filename):
        '''Set the destination filename (what to name the schedule).'''
        self._destination_filename = filename
        self.output('Result filename set to {0}.'.format(filename))
        
    def configure_destination_directory(self, directory):
        '''Set the destination directory (where to save the schedule).'''
        self._destination_directory = directory
        self.output('Destination set to {0}.'.format(directory))
        
    def set_export_types(self, export_types):
        '''Set the types of formats to export with (schedule formatters to use).'''
        self._export_types = export_types[:]
        
    def generate_schedule(self, filename):
        '''Generate the schedule with a given filename.'''
        self.output('Generating schedule...')
        self._scheduler.generate_schedule(filename)
        print(filename) # TODO: Remove this test
        self.output('Schedule complete.')
        
    def configure_user_interface_mode(self, is_graphical):
        '''Set the user interface mode to GUI is passed true and CLI if passed false.'''
        try:
            # Get the config file (the first line of which should be the course info filename)
            config_lines = []
            with open(CONFIG_FILENAME, 'r') as configuration_file:
                config_lines = configuration_file.readlines()
                
            is_graphical_string = 'YES' if is_graphical else 'NO'
            config_lines[1] = 'GUI: {0}\n'.format(is_graphical_string)
            
            with open(CONFIG_FILENAME, 'w') as configuration_file:
                configuration_file.writelines(config_lines)
                
        except (FileNotFoundError, IOError):
            self.output_error('Failed to access config file.')
        
    def create_default_config_file(self, catalog_name):
        '''Create a default config file for the program. This uses DEFAULT_CATALOG_NAME if
        catalog name is empty or None, and saves the config file to the working '''
        
        # TODO: TEST - this still has not been tested enough
        
        catalog_field = catalog_name
        
        # Check if catalog_name is None or ''
        if not catalog_name:
            catalog_field = DEFAULT_CATALOG_NAME
        
        config_filename = path.join(path.dirname(__file__), CONFIG_FILENAME)
        with open(config_filename, 'w') as config_file:
            config_file.write(catalog_field + '\n')
            config_file.write('GUI: NO\n')
    
    def run_top_interface(self):
        '''Gets input from the user and passed that input into the presenting interface/menu. The method then returns whether there are any interfaces left presenting. In the case there aren't any, the method should not be called again. This may act as the program's entire loop.'''
        user_input = self.get_input()                            # Get input from the user
        current_interface = self.get_current_interface()         # Get the current interface/menu
        current_interface.parse_input(self, user_input)          # Pass the user's input to the current menu
        return len(self._interface_stack) != 0                   # return whether there are still any interfaces presenting


## --------------------------------------------------------------------- ##
## --------------------------- Program Setup  -------------------------- ##
## --------------------------------------------------------------------- ##


# Testing:
if __name__ == "__main__":

    planner = SmartPlannerController()
    if planner.has_interface():
        while planner.run_top_interface(): pass
