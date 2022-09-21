# Thomas Merino
# 9/21/22
# CPSC 4175 Group Project

# NOTE: you must have PySide6 (QT) installed. To use the GUI, use the gui-i command.

# NOTE: the config file needs to be in the same directory as this file.
#   The config file stores in the first line the name of the course info filename. This is what's passed into the parser as input. The
#   The second line detemines whether to load the gui (if "YES" is in the second line)

# TODO: Maybe add session data so the program can recover from a crash
# TODO: Have the last directory used for saving stored in the config
#           This may be changed just for the current session with something like ("temp dirname")
#           Using the feature may be optional: having no directory means to start with home
# TODO: Maybe make the name of the help file included in config
# TODO: Fix program icon appearing for browser (default Python icon)
# TODO: Make importing PySide components optional in case the user does not have them installed
# TODO: Maybe add permission check when setting output directory


# TODO: Finish unit testing.
# TODO: Maybe add batch support for handling multiple users
# TODO: Ensure the directories in the config file work no matter the OS (if not, implement)
# TODO: Ensure support for course info being in a different directoy (and different OS)
# TODO: It might be good to clean up by replacing os.path functions with pathlib.Path methods.
# TODO: Maybe have the listeners completely consume IO (otherwise, why not just use a notification pattern?)


# TODO: Setting the directory does not check to see if it is indeed a directory (and not just a file); the same is true with getting files (fix this)
#       --this can be done with Path.is_dir() and Path.is_file()
# TODO: Hook up all commands
# TODO: File existence check does not consider the to-be file extensions (fix this) -- we could do this with Path.with_suffix('')
# TODO: Update status command to provide more scheduling parameters
# TODO: Ensure exception raising is implemented in other modules (e.g. NonDAGCourseInfoError)
# TODO: Set up error codes or boolean return (other modules)
# TODO: clean up the mixing of string and Path objects (it is not clear what is what right now)

from PySide6 import QtWidgets, QtGui

from sys import exit
from pathlib import Path
from os import path

from cli_interface import MainMenuInterface, GraphicalUserMenuInterface, ErrorMenu

DEFAULT_CATALOG_NAME = 'catalog.xlsx'           # The default name for the catalog/course info file
CONFIG_FILENAME = 'config'                      # The name of the config file
DEFAULT_SCHEDULE_NAME = 'Path to Graduation'    # The default filename for exporting schedules
NORMAL_HOURS_LIMIT = 18                         # The upper limit of credit hours students can take per semester (recommended)

# Constants for export types
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
        self.h = 15
        
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
## ---------------------- Smart Planner Controller --------------------- ##
## --------------------------------------------------------------------- ##

# This exception is used when an issue with interface presentation is encountered.
# Handling one should only be done for the sake of saving important data.
class InterfaceProcedureError(Exception):
    pass


# This exception is used when an issue with the config file is encountered.
class ConfigFileError(Exception):
    pass


def get_real_filepath(filepath):
    '''Function to verify the existence of a file/directory and change any "~" prefix into the user's home directory. This
    returns the corrected path if it exists and None if it does not.'''
    corrected_filepath = Path(filepath).expanduser()                        # Change "~" to the user's home address if present
    return corrected_filepath if corrected_filepath.exists() else None      # Return the path if it exists (otherwise None)


# TODO: Make the function take the file's extension into account
# TODO: We need to apply some TLC (Testing the Little Crap)
def get_next_free_filename(filepath):
    '''Function that checks if the passed filepath already has a file/directory. If it doesn't, simply return the passed path,
    and if it does, return the next filepath that is free (by changing the trailing number in the filename). Please note this
    is not optimized for large batches because there would be too many FS system calls (slow).'''
    
    # NOTE: if we want to use this for batch work, it would be better to simply store a file number and feed the filenames.
    
    if path.exists(filepath):
        
        # The filepath is already being used (find the next reasonable name)
        
        # Get the index where the digits suffix begins
        end_digit_index = len(filepath)
        # This checks if end_digit_index has reached the zero and if the checked character is numeric
        while end_digit_index and filepath[end_digit_index - 1].isdigit():
            end_digit_index -= 1
        
        # Seperate the filepath into its digit and non-digit section
        path_digit_section = filepath[end_digit_index:]
        
        # If there is no digit at the end of the filename, just add a "2"
        number = int(filepath[end_digit_index:]) + 1 if path_digit_section else 2
        pre_digit_path = filepath[:end_digit_index]
        working_filepath = pre_digit_path + str(number)
        
        # Increase the suffix number until no collision is found
        while path.exists(working_filepath):
            number += 1
            working_filepath = pre_digit_path + str(number)
        
        return working_filepath
    
    else:
        # The filepath is free (return it)
        return filepath


# This class manages the interactions between the interface of the program and the model (mostly the scheduler).
# The class also manages the destination directory and filename.
# Menuing is performed by having an interface stack--alike chain of responsibility and/or state machine.
class SmartPlannerController:
    
    
    def __init__(self, graphics_enabled=True):
        self.setup(graphics_enabled)
    
    
    def setup(self, graphics_enabled=True):
        '''Perform setup for scheduling, general configuration, and user interface. Setting graphics_enabled to false will
        only suppress the graphical interface during setup.'''
        
        # Initialize important variables
        self._scheduler = Scheduler()                           # Create a scheduler object for heading the model
        self._destination_directory = Path.home()               # Create the default directoty to export to (set initially to home directory)
                                                                # This is always expected to be an existing path. Do not set it purely based on user input
        self._destination_filename = DEFAULT_SCHEDULE_NAME      # Create the default destination filename (used when relevant)
        self._export_types = [PATH_TO_GRADUATION_EXPORT_TYPE]   # Create a list to track the export methods to use
        self._interface_stack = []                              # Create a stack (list) for storing the active interfaces
        
        # The following are IO listeners that respond to process output. Only one listener per channel can be active; these should only
        # be used for adding custom GUI elements and for testing.
        self.output_callback = None                             # A callback that is invoked when output is presented to the user
        self.warning_callback = None                            # A callback that is invoked when a warning is presented to the user
        
        # In this context, an 'interface' is an object that handles user input and performs actions on the passed
        # controller given those inputs. Interfaces are not expected to directly interact with the user (input or
        # output) unless the interface presents graphical UI elements. Interfaces are covered more in
        # menu_interface_base.py and cli_interface.py.

        try:
            # Attempt to get the program parameters from the config file
            course_info_filename, is_graphical = self.load_config_parameters()
            is_graphical = is_graphical and graphics_enabled    # Override conifg settings if graphics are suppressed
            
            # Load the course info file
            self.load_course_info(course_info_filename)
            
            # Load the user interface -- this should only block execution if graphics are presented
            self.load_interface(is_graphical)
            
        except (ConfigFileError, FileNotFoundError, IOError, NonDAGCourseInfoError):
            # Some error was encountered during loading (enter the error menu)
            self.output_error('A problem was encountered while during loading--entering error menu...')
            self.enter_error_menu()
    
    
    ## ----------- Process configuration ----------- ##
    
    
    def load_config_parameters(self):
        '''Load program configuration information from the config file. The goal of this method is to load the config file
        and ensure information about setup is not missing (if so, raise a ConfigFileError).'''
        
        try:
            # Get the config file
            with open(CONFIG_FILENAME, 'r') as configuration_file:
                
                # Get the first two lines of the file (location of the catalog and whether presenting graphics initially)
                course_info_filename = configuration_file.readline()
                is_graphical_line = configuration_file.readline()
                
                # Check if both lines exist and are not empty strings
                if course_info_filename and is_graphical_line:
                    is_graphical = 'YES' in is_graphical_line       # Get boolean meaning from the second line
                    return (course_info_filename, is_graphical)     # Return the results
                else:
                    # Configuration is missing important data (report to the user and raise a config error)
                    self.output_error('Invalid config file contents. Please see instructions on how to reconfigure.')
                    raise ConfigFileError()
                
        except (FileNotFoundError, IOError):
            # Configuration file could not be found (report to the user and raise a ConfigFileError)
            self.output_error('Could not get config file. Please see instructions on how to reconfigure.')
            raise ConfigFileError()
    
    
    def load_course_info(self, course_info_filename):
        '''Configure the scheduler with the course info file with the passed filename. This may re-raise a
        NonDAGCourseInfoError if one was raised during loading the course info.'''
        
        # Attempt to load the course info data and pass it to the scheduler
        try:
            course_info_container = get_course_info(course_info_filename)
            self._scheduler.configure_course_info(course_info_container)
            
        except (FileNotFoundError, IOError) as file_error:
            # Course info could not be found/read (report to the user and re-raise the error to enter error menu)
            self.output_error('Invalid course catalog file. Please rename the catalog to {}, make sure it is accessible, and reload the catalog (enter "reload").'.format(course_info_filename))
            raise file_error
            
        except NonDAGCourseInfoError as non_dag_error:
            # The catalog was/is invalid (report to the user and re-raise the error to enter error menu)
            self.output_error('Course catalog contains invalid data. Please correct all issues and reload the catalog (enter "reload").')
            raise non_dag_error
    
    
    def load_interface(self, is_graphical):
        '''Load the process's interface. This should be called only once during the lifecycle of the process--unless the
        process is reloaded from the error menu.'''
        
        # Set the bottom/first interface to be either a GUI menu or CLI main menu instance
        bottom_interface = GraphicalUserMenuInterface() if is_graphical else MainMenuInterface()
        
        # Push the new menu
        self.push_interface(bottom_interface)
    
    
    ## ----------- User interface methods (CLI) ----------- ##
    
    # Notes:
    # Both warnings and error send their message through output.
    # Warnings are acceptable, but the user should still be notified in some way.
    # Errors cannot be ignored, but there is not as much of an emphasis placed on notifying the user.
    
    
    def output(self, message):
        '''Output a message to the user.'''
        if self.output_callback:
            self.output_callback(message)
        print(message)
    
    
    def output_warning(self, message):
        '''Output a warning message to the user.'''
        if self.warning_callback:
            self.warning_callback(message)
        self.output('WARNING: {0}'.format(message))
    
    
    def output_error(self, message):
        '''Output an error message to the user.'''
        self.output('ERROR: {0}'.format(message))
    
    
    def get_input(self):
        '''Get input text from the user with the current interface's/menu's name in the prompt.'''
        current_interface = self.get_current_interface()
        return input('{0}: '.format(current_interface.name))
    
    
    def set_output_listener(self, output_callback=None):
        '''Set the callback that's invoked when output is about to be presented to the user (that may only be one at a time).'''
        self.output_callback = output_callback
    
    
    def set_warning_listener(self, warning_callback=None):
        '''Set the callback that's invoked when a warning is about to be presented to the user (that may only be one at a time).'''
        self.warning_callback = warning_callback
    
    
    ## ----------- Interface/menu control ----------- ##
    
    
    def has_interface(self):
        '''Gets whether the is an interface in the interface stack.'''
        return len(self._interface_stack) != 0
    
    
    def get_current_interface(self):
        '''Get the interface/menu that is presenting.'''
        
        # Ensure the is a interface (if not, raise a InterfaceProcedureError)
        if len(self._interface_stack) == 0:
            raise InterfaceProcedureError()
            
        # Return the top interface
        return self._interface_stack[-1]
    
    
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
    
    
    def get_graphical_application(self):
        '''Get the current graphical application object. If it does not exist, create a new one.'''
        application = QtWidgets.QApplication.instance()
        if not application:
            # There is no application (create one)
            application = QtWidgets.QApplication([])
        return application
    
    
    def enter_error_menu(self):
        '''Push an error menu onto the menu stack so the user can correct errors before reloading.
        This blocks execution until the error menu exits.'''
        new_error_menu = ErrorMenu()
        self.push_interface(new_error_menu)
        
        # While the new error message is in the stack, run the top interface (most likely the error menu)
        while new_error_menu in self._interface_stack:
                self.run_top_interface()
    
    
    ## ----------- Scheduling parameter getting ----------- ##
    
    
    def get_hours_per_semester(self):
        '''Get the hours per semester to use.'''
        return self._scheduler.get_hours_per_semester()
    
    
    def is_using_export_type(self, export_type):
        '''Get whether the passed export type is enabled.'''
        return export_type in self._export_types
    
    
    def get_destination_directory(self):
        '''Get the path that the resulting schedule file will be exported to. This should always return a real directory.'''
        return self._destination_directory
    
    
    def get_destination_filename(self):
        '''Get string that will be used to name the resulting schedule file.'''
        return self._destination_filename
            
    
    def get_destination(self):
        '''Get the full path of the schedule destination. This should always return a valid destination.'''
        return path.join(self._destination_directory, self._destination_filename)
    
    
    ## ----------- Scheduling parameter configuration ----------- ##
    
    
    def load_courses_needed(self, filename):
        '''Load the courses that must be scheduled into the scheduler (from the passed filename).
        This return the success of the load.'''
        success = False
        try:
            filepath = get_real_filepath(filename)                                          # Get the file's path and check if it exists
            if filepath:
                courses_needed_list = get_courses_needed(filepath)                          # Get the needed courses from the file
                self._scheduler.configure_courses_needed(courses_needed_list)               # Load the course list into the scheduler
                self.output('Course requirements loaded from {0}.'.format(filepath))        # Report success to the user
                success = True                                                              # Set success to true
            else:
                self.output_error('Sorry, {0} file could not be found.'.format(filename))   # Report if the file could not be found
        except IOError:
            self.output_error('Sorry, {0} file could not be openned.'.format(filename))     # Report if the file could not be openned
        return success
    
    
    def configure_hours_per_semester(self, number_of_hours):
        '''Set the number of hours that are scheduled per semester. This return the sucess of the load.'''
        
        if number_of_hours <= 0:
            self.output_warning('Please enter a minimum of 1 hour per semester')
            return False
        
        if number_of_hours > NORMAL_HOURS_LIMIT:
            self.output_warning('Taking over {0} credit hours per semester is not recommended.'.format(NORMAL_HOURS_LIMIT))
            # TODO: we may or may not want to return from here if this is off limits
        
        self._scheduler.configure_hours_per_semester(number_of_hours)
        self.output('Hours per semester set to {0}.'.format(number_of_hours))
        return True
        
    
    def set_export_types(self, export_types):
        '''Set the types of formats to export with (schedule formatters to use).'''
        self._export_types = export_types[:]
    
    
    def configure_destination_directory(self, directory):
        '''Set the destination directory (where to save the schedule). This return the sucess of the configuration.'''
        success = False
                
        # Verify the passed directory exists
        directory_path = get_real_filepath(directory)
        if directory_path:
            self._destination_directory = directory_path
            self.output('Destination directory set to {0}.'.format(directory_path))
            sucess = True
        else:
            # Report if the directory could not be found
            self.output_error('Sorry, {0} directory could not be found.'.format(directory))
            
        return sucess
    
    
    def configure_destination_filename(self, filename):
        '''Set the destination filename (what to name the schedule). This should invoked when configuring output parameter, but
        it should not be invoked just before exporting. Do not use this for modifying _destination_filename in all cases.'''
        
        # Set the destination filename (not verified)
        self._destination_filename = filename
        self.output('Result filename set to {0}.'.format(filename))
        
        # Check if a file already exists with the current destination
        filepath = get_real_filepath(self.get_destination())
        if filepath:
            self.output_warning('A file already exists with that name. The exported files will have slightly different names.')
    
    
    ## ----------- Program configuration ----------- ##
    
    
    # TODO: TEST - this still has not been tested enough
    def create_default_config_file(self, catalog_name):
        '''Create a default config file for the program. This uses DEFAULT_CATALOG_NAME if
        catalog name is empty or None and saves the config file to this file's directory '''
        
        # Set catalog_field to catalog_name unless it is None or '' (set catalog_field to the default value if so)
        catalog_field = catalog_name if catalog_name else DEFAULT_CATALOG_NAME
        
        # Save the config file to this file's directory
        config_filename = path.join(path.dirname(__file__), CONFIG_FILENAME)
        with open(config_filename, 'w') as config_file:
            
            # Write config contents
            config_file.write(catalog_field + '\n')
            config_file.write('GUI: NO\n')
    
    
    def configure_user_interface_mode(self, is_graphical):
        '''Set the user interface mode to GUI is passed true and CLI if passed false.'''
        try:
            # Get the config file as a list of strings/lines (the first of which should be the course info filename)
            config_lines = []
            with open(CONFIG_FILENAME, 'r') as configuration_file:
                config_lines = configuration_file.readlines()
                
            # Change the second line to reflect is_graphical
            is_graphical_string = 'YES' if is_graphical else 'NO'
            config_lines[1] = 'GUI: {0}\n'.format(is_graphical_string)
            
            # Save/overwrite the file
            with open(CONFIG_FILENAME, 'w') as configuration_file:
                configuration_file.writelines(config_lines)
                
        except (FileNotFoundError, IOError):
            self.output_error('Failed to access config file.')
        
    
    def fetch_catalog(self, fetch_parameters=None):
        
        self.output('Fetching data...')
        
        # TODO: add implementation if needed
        
        self.output('Course catalog info updated.')
        
    
    ## ----------- Execution ----------- ##
    
    def generate_schedule(self, filename=None):
        '''Generate the schedule with a given filename or the current default filename if nothing is provided.'''
        
        self.output('Generating schedule...')
        
        # Set _destination_filename to the passed filename if one was passed
        if filename:
            self._destination_filename = filename
        
        desired_destination = self.get_destination()
        unique_destination = get_next_free_filename(desired_destination)
        
        try:
            self._scheduler.generate_schedule(unique_destination)
            self.output('Schedule exported as {0}'.format(unique_destination))
        except (FileNotFoundError, IOError):
            # This code will probably execute when file system permissions/organization change after setting parameters
            self.output_error('File system error ecountered while attempting to export (please try re-entering parameters).')
        
    
    def batch_schedule(self, inputs_directory, filename_prefix):
        
        # This may or may not be implemented (because of the testing requirements, I would say we should wait)
        """
        pseudo code:
        NOTE: we may be able to create multiple schedulers and run them on different threads
        
        get list of files in inputs_directory
        loop in files list:
            load file as courses needed
            schedule as filename_prefix + filename (this is saved to working directory)
        """
        pass
    
    
    def run_top_interface(self):
        '''Gets input from the user and passed that input into the presenting interface/menu. The method then returns whether
        there are any interfaces left presenting. In the case there aren't any, the method should not be called again. This may
        act as the process's entire loop.'''
        user_input = self.get_input()                            # Get input from the user
        current_interface = self.get_current_interface()         # Get the current interface/menu
        current_interface.parse_input(self, user_input)          # Pass the user's input to the current menu
        return len(self._interface_stack) != 0                   # return whether there are still any interfaces presenting


# End of SmartPlannerController definition

## --------------------------------------------------------------------- ##
## --------------------------- Process Setup  -------------------------- ##
## --------------------------------------------------------------------- ##


# Testing:
if __name__ == "__main__":

    planner = SmartPlannerController()
    if planner.has_interface():
        while planner.run_top_interface(): pass
