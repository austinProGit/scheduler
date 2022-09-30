# Thomas Merino
# 9/30/22
# CPSC 4175 Group Project

# NOTE: you must have PySide6 (QT) installed. To use the GUI, use the gui-i command.

# NOTE: the config file needs to be in the same directory as this file.
#   The config file stores in the first line the name of the course info filename. This is what's passed into the parser as input.
#   The third line detemines whether to load the gui (if "YES" is in the second line)

# POTENTIAL GOALS FOR NEXT CYCLE:
# - General refactoring
# - Use AI for scheduling algorithm
# - Use UI text dictionary (maybe langauges support)
# - Maybe add session data so the program can recover from a crash
# - Have the last directory used for saving stored in the config
#           This may be changed just for the current session with something like ("temp dirname")
#           Using the feature may be optional: having no directory means to start with home
# - Make importing PySide optional in case the user does not have them installed (maybe other packages as well)
# - Add drag and drog support for easier file import
# - Support more export/import types
# - Manually setting courses setting
#           Adding specified course (via scheduler)
#           Adding scheduling constraints (maybe via AI)
#           Adding custom classes: specify name, availability, hours (via course info container buffer)
#           NOTE: this might mean serializing the course info container when preserving session data
# - Display help menu contents in GUI mode via a web browser
# - Add aliases (course ID) Excel file
# - Allow use of the web crawler (fetch)
# - Add batch work functionality (schedule multiple students by running through multiple requirements)
#           The would be a good place for multithreading
# - Use number of courses OR number of credit hours
# - Open finished schedule once generated
# - Easy openning (PATH and/or desktop shortcut)

# - Accept any/all courses
# - Make path to graduation start on any semester
# - Handle missing package errors better
# - Maybe make the name of the help file included in config (probably not)
# - Fix program icon appearing for file explorer (default Python icon)
# - Handler permission check when setting output directory
# - Implement weakref into the GUI widgets and item selection callbacks to prevent strong reference cycles
# - Add working popup warning/verifying GUI->CLI switch (adding this at the moment is bug-laden)
#           this creates an issue where the GUI sometimes dones not dismiss when changing to CLI (after switching back and forth)
# - Figure out role of admin vs. user as far as program configuration is concerned
# - Fix relative path issue for getting files (make sure working directory does not influence)


# To-do Legend:
#   Ensure: something that should work or should be fixed but has not been tested enough
#   Organize: stuff that should be cleaned up but is not necessary
#   Fix: suprise feature
#   Wish: something that should be implemented but is not necessary
#   Ask: something that needs to be decided upon
#   Need: something that needs to be done

# TODO: (ORGANIZE) It might be good to clean up by replacing os.path functions with pathlib.Path methods.
# TODO: (ORGANIZE) Maybe have the listeners completely consume IO (otherwise, why not just use a notification pattern?)
# TODO: (ORGANIZE) Consider useing f'{variable}' for formatting
# TODO: (ORGANIZE) Consider using := operator for cleaner code (probably not for compatibility's sake)
# TODO: (ORGANIZE) Clean up the mixing of string and Path objects (it is not clear what is what right now)
# TODO: (ENSURE) the directories in the config file work no matter the OS (if not, implement)
# TODO: (ENSURE) support for course info being in a different directoy (and different OS)
# TODO: (ENSURE) exception raising is implemented in other modules (e.g. NonDAGCourseInfoError)
# TODO: (ENSURE) proper setup of error codes or boolean return (other modules)
# TODO: (ENSURE) ensure permission settings work
# TODO: (ENSURE) File existence check does not consider the to-be file extensions (fix this) -- we could do this with Path.with_suffix('') and Path.suffix
# TODO: (ENSURE) Add two filepaths to config file
# TODO: (ENSURE) Add command to display needed courses
# TODO: (ENSURE) Fix error message when entering empty string for export name in gui
# TODO: (ENSURE) Add text export
# TODO: (ENSURE) Does not work when loaded courses or catalog file is bad extension/format
# TODO: (ENSURE) Make GUI update needed courses data when loading
# TODO: (ENSURE) Open config from src not the working the directory
# TODO: (ENSURE/WISH) Allow switching to CLI from GUI (adding confirmation popup breaks this)
# TODO: (WISH) Add README and seperate file for general tasks (or maybe just have that external)
# TODO: (WISH) No warning about filename collision because of extension (take all selected export types into consideration)
# TODO: (WISH) Have the GUI display errors (like warnings)
# TODO: (FIX) Add "silient=True" to tabula calls so there are no error print outs
# TODO: (FIX) Fix issue with no availability for Sample Input3 (add default value?)
# TODO: (FIX) Fix searching empty string in help (should print how to exit and how to search)
# TODO: (ASK) Decide if course_info_parser.py can be removed
# TODO: (ASK) Ask how file extension are handled by module methods/functions
# TODO: (NEED) Need to select/handle electives
# TODO: (NEED) Iron out summer scheduling issue (lower hours per summer)
# TODO: (NEED) Add hours per course to Course Info.xlsx
# TODO: (NEED) Finish unit testing.

from PySide6 import QtWidgets, QtGui

# MERINO: Uncomment this if you want to run memory profiling
#from guppy import hpy; heap = hpy() # MERINO: added this for testing! (memory leak detecting; this requires loading in cli)

# MERINO: added imports
from sys import exit
from pathlib import Path
from os import path
from subprocess import CalledProcessError   # This is used for handling errors raised by tabula parses

from driver_fs_functions import *
from cli_interface import MainMenuInterface, GraphicalUserMenuInterface, ErrorMenu
from scheduler_class import Scheduler
from course_info_container import *
from courses_needed_parser import get_courses_needed
from dag_validator import validate_course_path, NonDAGCourseInfoError
from excel_formatter import excel_formatter
from plain_text_formatter import plain_text_export
from user_submitted_validator import validate_user_submitted_path
from path_to_grad_parser import parse_path_to_grad 

# MERINO: Added min constant
DEFAULT_CATALOG_NAME = 'input_files/Course Info.xlsx'           # The default name for the catalog/course info file
DEFAULT_AVAILABILITY_FILENAME = 'input_files/Course Info.xlsx'  # The default name for the catalog/course availability file
CONFIG_FILENAME = 'config'                                      # The name of the config file
DEFAULT_SCHEDULE_NAME = 'Path to Graduation'                    # The default filename for exporting schedules
NORMAL_HOURS_LIMIT = 18                                         # The upper limit of credit hours students can take per semester (recommended)
STRONG_HOURS_LIMIT = 30                                         # The absolute limit of credit hours students can take per semester (cannot exceed)
STRONG_HOURS_MINIMUM = 4                                        # The absolute minimum of credit hours students can take per semester (cannot be below)

# MERINO: removed redefinition of export types

# MERINO: removed dummies

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


def get_source_path():
    '''Get the path of the program's directory.'''
    return path.dirname(__file__)
    

# This class manages the interactions between the interface of the program and the model (mostly the scheduler).
# The class also manages the destination directory and filename.
# Menuing is performed by having an interface stack--alike chain of responsibility and/or state machine.
class SmartPlannerController:
    
    
    def __init__(self, graphics_enabled=True):
        self.setup(graphics_enabled)
        # MERINO: adding this for testing! (set size for relative heap comparison; you must launch in cli mode to use this)
        # MERINO: Uncomment this if you want to run memory profiling
        #heap.setrelheap()
    
    
    def setup(self, graphics_enabled=True):
        '''Perform setup for scheduling, general configuration, and user interface. Setting graphics_enabled to false will
        only suppress the graphical interface during setup.'''
        
        # The scheduler functions as the program's model. It may be serialized to save the save of the process.
        
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
            course_info_filename, course_availability_filename, is_graphical = self.load_config_parameters()
            is_graphical = is_graphical and graphics_enabled    # Override conifg settings if graphics are suppressed
            
            # Load the course info file
            self.load_course_info(course_info_filename, course_availability_filename)
            
            # Load the user interface -- this should only block execution if graphics are presented
            self.load_interface(is_graphical)
            
        except (ConfigFileError, FileNotFoundError, IOError, NonDAGCourseInfoError, ValueError):
            # Some error was encountered during loading (enter the error menu)
            self.output_error('A problem was encountered during loading--entering error menu...')
            self.enter_error_menu()
    
    
    ## ----------- Process configuration ----------- ##
    
    
    def load_config_parameters(self):
        '''Load program configuration information from the config file. The goal of this method is to load the config file
        and ensure information about setup is not missing (if so, raise a ConfigFileError).'''
        
        try:
            # Get the config file
            config_filename = path.join(get_source_path(), CONFIG_FILENAME)
            with open(config_filename, 'r') as configuration_file:
                
                # MERINO: fixed reading escape character
                # Get the first three lines of the file (locations of the catalog and whether presenting graphics initially)
                course_info_filename = configuration_file.readline()[:-1]
                course_availability_filename = configuration_file.readline()[:-1]
                is_graphical_line = configuration_file.readline()
                
                
                # Check if all lines exist and are not empty strings
                if course_info_filename and course_availability_filename and is_graphical_line:
                    is_graphical = 'YES' in is_graphical_line                                   # Get boolean meaning from the second line
                    return (course_info_filename, course_availability_filename, is_graphical)   # Return the results
                else:
                    # Configuration is missing important data (report to the user and raise a config error)
                    self.output_error('Invalid config file contents. Please see instructions on how to reconfigure.')
                    raise ConfigFileError()
                
        except (FileNotFoundError, IOError):
            # Configuration file could not be found (report to the user and raise a ConfigFileError)
            self.output_error('Could not get config file. Please see instructions on how to reconfigure.')
            raise ConfigFileError()
    
    
    def load_course_info(self, course_info_filename, course_availability_filename):
        '''Configure the scheduler with the course info file with the passed filename. This may re-raise a
        NonDAGCourseInfoError if one was raised during loading the course info.'''
        
        # Get the filepaths relative to the source path
        source_code_path = get_source_path()
        course_info_relative_path = get_source_relative_path(source_code_path, course_info_filename)
        course_availability_relative_path = get_source_relative_path(source_code_path, course_availability_filename)
        
        # Attempt to load the course info data and pass it to the scheduler
        try:
            # TODO: IMPLEMENT HERE ->
            # MERINO: implemented changes
            course_info_container = CourseInfoContainer(load_course_info(course_info_relative_path))
            validate_course_path(course_info_container)
            self._scheduler.configure_course_info(course_info_container)
            
        except (FileNotFoundError, IOError) as file_error:
            # Course info could not be found/read (report to the user and re-raise the error to enter error menu)
            self.output_error('Invalid course catalog file. Please rename the catalog to {0}, make sure it is accessible, and reload the catalog (enter "reload").'.format(course_info_relative_path))
            raise file_error
            
        except (NonDAGCourseInfoError, ValueError) as config_error: # MERINO: added exception handling
            # The catalog was/is invalid (report to the user and re-raise the error to enter error menu)
            # NonDAGCourseInfoError is raised when a prequisite cycle is detected
            # ValueError is raised when the table has an invalid format or is the wrong type of file (check extension)
            self.output_error('Course catalog contains invalid data. Please correct all issues and reload the catalog (enter "reload").')
            raise config_error
    
    
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
        # MERINO: Added this for testing! Uncomment to print new heap allocations at every input
        # MERINO: Uncomment this if you want to run memory profiling
        #print(heap.heap())
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
    
    
    def reload_in_cli(self):
        '''Clear the interface stack (this dismisses all interface in order from highest to lowest) and push a cli menu.'''
        self.clear_all_interfaces()
        self.push_interface(MainMenuInterface())
    
    
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
    
    def get_courses_needed(self):
        '''Get the coursed needed that have been loaded into the scheduler. This return a list of strings (IDs).'''
        return self._scheduler.get_courses_needed()
        
    
    def get_hours_per_semester(self):
        '''Get the hours per semester to use.'''
        return self._scheduler.get_hours_per_semester()
    
    
    def get_export_type(self):
        '''Get a set of the enabled export types.'''
        return self._export_types.copy()
    
    
    def get_destination_directory(self):
        '''Get the path that the resulting schedule file will be exported to. This should always return a real directory.'''
        return self._destination_directory
    
    
    def get_destination_filename(self):
        '''Get string that will be used to name the resulting schedule file.'''
        return self._destination_filename
            
    
    def get_destination(self):
        '''Get the full path of the schedule destination. This should always return a valid destination.'''
        return Path(self._destination_directory, self._destination_filename)
    
    
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
        except CalledProcessError: # MERINO: added exception handling
            # MERINO: fixed spelling
            self.output_error('Sorry, invalid format while parsing {0}.'.format(filename))  # Report if the file could not be openned
        return success
    
    
    def configure_hours_per_semester(self, number_of_hours):
        '''Set the number of hours that are scheduled per semester. This return the success of the load.'''
        
        # MERINO: added minimum hours
        if number_of_hours <= STRONG_HOURS_MINIMUM or STRONG_HOURS_LIMIT < number_of_hours:
            self.output_warning('Please enter between {0} and {1} hours per semester.'.format(STRONG_HOURS_MINIMUM, STRONG_HOURS_LIMIT))
            return False
        
        if number_of_hours > NORMAL_HOURS_LIMIT:
            self.output_warning('Taking over {0} credit hours per semester is not recommended.'.format(NORMAL_HOURS_LIMIT))
            
        
        self._scheduler.configure_hours_per_semester(number_of_hours)
        self.output('Hours per semester set to {0}.'.format(number_of_hours))
        return True
        
    
    def set_export_types(self, export_types):
        '''Set the types of formats to export with (schedule formatters to use).'''
        self._export_types = export_types[:]
    
    
    def configure_destination_directory(self, directory):
        '''Set the destination directory (where to save the schedule). This return the success of the configuration.'''
        success = False
                
        # Verify the passed directory exists and is indeed a directory
        directory_path = get_real_filepath(directory)   # Get the verified path (this is a Path object that exists, but it is not necessarily a directory)
        if directory_path and directory_path.is_dir():
            self._destination_directory = directory_path
            self.output('Destination directory set to {0}.'.format(directory_path))
            success = True
        else:
            # Report if the directory could not be found
            self.output_error('Sorry, {0} directory could not be found.'.format(directory))
            
        return success
    
    
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
    def create_default_config_file(self, catalog_name=None, availability_name=None):
        '''Create a default config file for the program. This uses DEFAULT_CATALOG_NAME if
        catalog name is empty or None and saves the config file to this file's directory '''
        
        # Set catalog_field to catalog_name unless it is None or '' (set catalog_field to the default value if so)
        catalog_field = catalog_name if catalog_name else DEFAULT_CATALOG_NAME
        availability_field = availability_name if availability_name else DEFAULT_AVAILABILITY_FILENAME
        
        
        # Save the config file to this file's directory
        config_filename = path.join(get_source_path(), CONFIG_FILENAME)
        with open(config_filename, 'w') as config_file:
            
            # Write config contents
            config_file.write(catalog_field + '\n')
            config_file.write(availability_field + '\n')
            config_file.write('GUI: NO\n')
            
        # MERINO: added output
        self.output('Config file created.')
    
    
    def configure_user_interface_mode(self, is_graphical):
        '''Set the user interface mode to GUI is passed true and CLI if passed false.'''
        try:
            # Get the config file as a list of strings/lines
            config_lines = []
            with open(CONFIG_FILENAME, 'r') as configuration_file:
                config_lines = configuration_file.readlines()
                
            # Change the third line to reflect is_graphical
            is_graphical_string = 'YES' if is_graphical else 'NO'
            config_lines[2] = 'GUI: {0}\n'.format(is_graphical_string)
            
            # Save/overwrite the file
            with open(CONFIG_FILENAME, 'w') as configuration_file:
                configuration_file.writelines(config_lines)
                
        except (FileNotFoundError, IOError):
            self.output_error('Failed to access config file.')
        
    
    def fetch_catalog(self, fetch_parameters=None):
        
        self.output('Fetching data...')
        
        # TODO: add implementation if/when needed
        
        self.output('Course catalog info updated.')
        
    
    ## ----------- Execution ----------- ##
    
    def check_schedule(self, filename):
        '''Check the schedule at the passed filename for prerquisites cycles.'''
        error_reports = None
                
        # Verify the passed filename exists
        filepath = get_real_filepath(filename)   # Get the verified path (this is a Path object that exists, but it is not necessarily a directory)
        if filepath:
            try:
                schedule = parse_path_to_grad(filepath)
                
                # This is list (empty is valid)
                error_reports = validate_user_submitted_path(self._scheduler.get_course_info(), schedule)
                if not error_reports:
                    self.output('Path valid.')
                else:
                    self.output_warning('Invalid path! Please correct the following errors.')
                    for infraction in error_reports:
                        self.output(infraction)
                
            except (ConfigFileError, IOError, ValueError):
                self.output_error('Sorry, {0} file does not have the correct format.'.format(filename))
        else:
            # Report if the directory could not be found
            self.output_error('Sorry, {0} file could not be found.'.format(filename))
            
        return error_reports
        
    
    def generate_schedule(self, filename=None):
        '''Generate the schedule with a given filename or the current default filename if nothing is provided.'''
        
        # MERINO: added needed courses and export types check (empty)
        # Check if any courses are loaded
        if not self._scheduler.get_courses_needed():
            self.output_warning('No schedule exported.')
            self.output_error('No needed courses loaded.')
            return
           
        # Check if no export types are selected (empty)
        if not self._export_types:
            self.output_warning('No schedule exported.')
            self.output_error('No export type selected.')
            return
        
        self.output('Generating schedule...')
        
        # Set _destination_filename to the passed filename if one was passed
        if filename:
            self._destination_filename = filename
            
        # MERINO: moved unique destination
        desired_destination = self.get_destination()
        
        try:
            # TODO: IMPLEMENT HERE ->
            # MERINO: implemented changes
            if self._export_types:
                semesters_listing = self._scheduler.generate_schedule()
                template_path = Path(get_source_path(), 'input_files')
                
                if PATH_TO_GRADUATION_EXPORT_TYPE in self._export_types:
                    unique_ptg_destination = get_next_free_filename(desired_destination.with_suffix('.xlsx'))
                    excel_formatter(Path(template_path, 'Path To Graduation Y.xlsx'), unique_ptg_destination, semesters_listing, self._scheduler.get_course_info())
                    self.output('Schedule (Path to Graduation) exported as {0}'.format(unique_ptg_destination))
                
                if PLAIN_TEXT_EXPORT_TYPE in self._export_types:
                    unique_ptext_destination = get_next_free_filename(desired_destination.with_suffix('.txt'))
                    plain_text_export(unique_ptext_destination, semesters_listing, 'Spring', 2022)
                    self.output('Schedule (plain text) exported as {0}'.format(unique_ptext_destination))
                
            else:
                self.output_error('Please select an export type.')
        except (FileNotFoundError, IOError):
            # This code will probably execute when file system permissions/organization change after setting parameters
            self.output_error('File system error ecountered while attempting an export (please try re-entering parameters). Some files may have exported.')
        
    
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

# MERINO: removed main entrance (that's main.py's job now)
