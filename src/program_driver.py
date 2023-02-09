# Thomas Merino
# 11/23/22
# CPSC 4175 Group Project

# TODO: add final semester rule
# TODO: change the name of the ES to "schedule_evaluator"

# POTENTIAL GOALS FOR NEXT CYCLE:
# - General refactoring
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
# - Use number of courses OR number of credit hours
# - Open finished schedule once generated
# - Easy openning (PATH and/or desktop shortcut)
# - Be able to manage config file with text editor (from software)
# - Make the content panel better
#           Have the content panel display the output schedule (so there aren't hundreds of windows opening during batch)
# - Add a log file (tracks commands entered and outputs generated)
# - Accept any/all courses
# - Handle missing package errors better
# - Fix program icon appearing for file explorer (default Python icon)
# - Handler permission check when setting output directory
# - Implement weakref into the GUI widgets and item selection callbacks to prevent strong reference cycles
# - Add working popup warning/verifying GUI->CLI switch (adding this at the moment is bug-laden)
#           this creates an issue where the GUI sometimes dones not dismiss when changing to CLI (after switching back and forth)

# To-do Legend:
#   Ensure: something that should work or should be fixed but has not been tested enough
#   Organize: stuff that should be cleaned up (is not necessary to do)
#   Fix: something that should be fixed ("suprise feature")
#   Wish: something that should be implemented (is not necessary to do)
#   Need: something that needs to be done

# TODO: (ORGANIZE) Maybe have the listeners completely consume IO (otherwise, why not just use a notification pattern?)
# TODO: (ORGANIZE) Consider useing f'{variable}' for formatting
# TODO: (ORGANIZE) Clean up the mixing of string and Path objects (it is not clear what is what right now)
# TODO: (ENSURE) File existence check does not consider the to-be file extensions (fix this) -- we could do this with Path.with_suffix('') and Path.suffix


from PySide6 import QtWidgets, QtGui

# NOTE: Uncomment this if you want to run memory profiling
#from guppy import hpy; heap = hpy() # NOTE: added this for testing! (memory leak detecting; this requires loading in cli)

from sys import exit
from pathlib import Path
from os import path


from alias_module import *
from catalog_parser import update_course_info
from batch_process import batch_process
from batch_validation import batch_validation
from configuration_manager import *
from driver_fs_functions import *
from cli_interface import MainMenuInterface, GraphicalUserMenuInterface, ErrorMenu
from scheduler import Scheduler
from course_info_container import *
from courses_needed_parser import get_courses_needed
from program_generated_evaluator import evaluate_container, NonDAGCourseInfoError, InvalidCourseError
from excel_formatter import excel_formatter
from plain_text_formatter import plain_text_export
from user_submitted_validator import validate_user_submitted_path
from path_to_grad_parser import parse_path_to_grad


## --------------------------------------------------------------------- ##
## ---------------------- Smart Planner Controller --------------------- ##
## --------------------------------------------------------------------- ##

# This exception is used when an issue with interface presentation is encountered.
# Handling one should only be done for the sake of saving important data.
class InterfaceProcedureError(Exception):
    pass


# This class manages the interactions between the interface of the program and the model (mostly the scheduler).
# The class also manages the destination directory and filename.
# Menuing is performed by having an interface stack--alike chain of responsibility and/or state machine.
class SmartPlannerController:
    
    
    def __init__(self, graphics_enabled=True):
        self.setup(graphics_enabled)
        # NOTE: adding this for testing! (set size for relative heap comparison; you must launch in cli mode to use this)
        # NOTE: Uncomment this if you want to run memory profiling
        #heap.setrelheap()
    
    
    def setup(self, graphics_enabled=True):
        '''Perform setup for scheduling, general configuration, and user interface. Setting graphics_enabled to false will
        only suppress the graphical interface during setup.'''
        
        # The scheduler functions as the program's model. It may be serialized to save the save of the process.
        
        # Initialize important variables
        self._scheduler = Scheduler() # Create a scheduler object for heading the model
        # Create the default directoty to export to (set initially to home directory) This is always
        # expected to be an existing path. Do not set it purely based on user input
        self._destination_directory = Path.home()
        self._export_types = [PATH_TO_GRADUATION_EXPORT_TYPE] # Create a list to track the export methods to use
        self._interface_stack = [] # Create a stack (list) for storing the active interfaces
        
        # The following are IO listeners that respond to process output. Only one listener per channel can be active; these should only
        # be used for adding custom GUI elements and for testing.
        self.output_callback = None # A callback that is invoked when output is presented to the user
        self.warning_callback = None # A callback that is invoked when a warning is presented to the user
        
        # In this context, an 'interface' is an object that handles user input and performs actions on the passed
        # controller given those inputs. Interfaces are not expected to directly interact with the user (input or
        # output) unless the interface presents graphical UI elements. Interfaces are covered more in
        # menu_interface_base.py and cli_interface.py.

        try:
            # Attempt to get the program parameters from the config file
            self.session_configuration = self.load_config_parameters()
            
            # Load the course info file
            self.load_course_info(self.session_configuration)
            
            # Create the default destination filename (used when relevant)
            self._destination_filename = self.session_configuration.initial_schedule_name
            
            # Load the user interface -- this should only block execution if graphics are presented
            self.load_interface(self.session_configuration.is_graphical and graphics_enabled) # Override conifg settings if graphics are suppressed
        except (ConfigFileError, FileNotFoundError, IOError, NonDAGCourseInfoError, InvalidCourseError, ValueError) as e:
            # Some error was encountered during loading (enter the error menu)
            print(e)
            self.output_error('A problem was encountered during loading--entering error menu...')
            self.enter_error_menu()
    
    
    ## ----------- Process configuration ----------- ##
    
    
    def load_config_parameters(self):
        '''Load program configuration information from the config file. This returns a SessionConfiguration object or raises a ConfigFileError if the file is invalid.'''
        
        try:
            # Return the session object
            return load_configuration_session()
            
        except ConfigFileError as config_file_error:
            # Configuration is missing important data (report to the user and raise a config error)
            self.output_error(f'Invalid config file contents. Please see instructions on how to reconfigure. {str(config_file_error)}')
            raise config_file_error
                    
        except (FileNotFoundError, IOError):
            # Configuration file could not be found (report to the user and raise a ConfigFileError)
            self.output_error('Could not get config file. Please see instructions on how to reconfigure.')
            raise ConfigFileError()
    
    
    def load_course_info(self, session_configuration):
        '''Configure the scheduler with the course info file from the passes session object. This may re-raise a
        NonDAGCourseInfoError if one was raised during loading the course info.'''
                    
        course_info_filename = session_configuration.course_info_filename
        excused_prereqs_filename = session_configuration.excused_prereqs
        alias_filename = session_configuration.alias_filename
        
        # Get the filepaths relative to the source path
        source_code_path = get_source_path()
        course_info_relative_path = get_source_relative_path(source_code_path, course_info_filename)
        excused_prereqs_relative_path = get_source_relative_path(source_code_path, excused_prereqs_filename)
        alias_relative_path = get_source_relative_path(source_code_path, alias_filename)
        
        # TODO: this is NOT in use at the moment (neither is availability in general...)
        #course_availability_relative_path = get_source_relative_path(source_code_path, course_availability_filename)
        
        # Attempt to load the course info data and pass it to the scheduler
        try:
            setup_aliases(alias_relative_path)

            course_info = load_course_info(course_info_relative_path)
            course_info_container = CourseInfoContainer(course_info)
            
            # This raises an exception if Course Info Container contains invalid data
            evaluation_report = evaluate_container(course_info_container)
            course_info_container.load_report(evaluation_report)
            
            self._scheduler.configure_course_info(course_info_container)
            
        except (FileNotFoundError, IOError) as file_error:
            # Course info could not be found/read (report to the user and re-raise the error to enter error menu)
            self.output_error('Invalid course catalog file. Please rename the catalog to {0}, make sure it is accessible, and reload the catalog (enter "reload").'.format(course_info_relative_path))
            raise file_error
            
        except ValueError:
            # ValueError is raised when the table has an invalid format or is the wrong type of file (check extension)
            self.output_error('Course catalog is not in the correct format. Please correct all issues and reload the catalog (enter "reload").')
            raise config_error
        except (NonDAGCourseInfoError, InvalidCourseError) as config_error:
            # The catalog was/is invalid (report to the user and re-raise the error to enter error menu)
            # NonDAGCourseInfoError is raised when a prequisite cycle is detected
            # InvalidCourseError is raised when an unrecognized prequisite cycle is encountered
            
            self.output_error('Course catalog contains invalid data. Please correct all issues and reload the catalog (enter "reload").')
            self.output_error(str(config_error))
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
    
    
    def output_clear(self):
        '''Clear the terminal of content (intended for CLI interface).'''
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
    
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
            top_interface = self._interface_stack.pop() # Pop the passed interface
            top_interface.deconstruct(self) # Call the interface's deconstruct method
            return top_interface
        else:
            raise InterfaceProcedureError() # Raise an error about the illegal procedure
    
    
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
            filepath = get_real_filepath(filename) # Get the file's path and check if it exists
            if filepath:
                courses_needed_container = get_courses_needed(filepath) # Get the needed courses from the file
                self._scheduler.configure_courses_needed(courses_needed_container) # Load the course container into the scheduler
                self.output('Course requirements loaded from {0}.'.format(filepath)) # Report success to the user
                success = True # Set success to true
            else:
                self.output_error('Sorry, {0} file could not be found.'.format(filename)) # Report if the file could not be found
        except IOError:
            self.output_error('Sorry, {0} file could not be openned.'.format(filename)) # Report if the file could not be openned
        return success
    
    
    def configure_hours_per_semester(self, number_of_hours):
        '''Set the number of hours that are scheduled per semester. This return the success of the load.'''
        
        if number_of_hours <= self.session_configuration.strong_hours_minimum \
           or self.session_configuration.strong_hours_limit < number_of_hours:
           
            self.output_warning('Please enter between {0} and {1} hours per semester.'.format(self.session_configuration.strong_hours_minimum, self.session_configuration.strong_hours_limit))
            return False
        
        if number_of_hours > self.session_configuration.normal_hours_limit:
            self.output_warning('Taking over {0} credit hours per semester is not recommended.'.format(self.session_configuration.normal_hours_limit))
            
        
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
        
    
    def set_destination_filename(self, filename):
        '''Simply set the destination filename (what to name the schedule).'''
        self._destination_filename = filename
    
    
    def configure_destination_filename(self, filename):
        '''Set the destination filename (what to name the schedule). This should invoked when configuring output parameter, but
        it should not be invoked just before exporting. Do not use this for modifying _destination_filename in all cases.'''
        
        # Set the destination filename (not verified)
        self.set_destination_filename(filename)
        self.output('Result filename set to {0}.'.format(filename))
        
        # Check if a file already exists with the current destination
        filepath = get_real_filepath(self.get_destination())
        if filepath:
            self.output_warning('A file already exists with that name. The exported files will have slightly different names.')
    
    
    ## ----------- Program configuration ----------- ##
    
    
    # TODO: TEST - this still has not been tested enough
    def create_default_config_file(self, catalog_name=None, availability_name=None):
        '''Create a default config file for the program. This uses the default catalog name if
        catalog name is empty or None and saves the config file to this file's directory '''
        
        new_session_configuration = SessionConfiguration.make_default()
        
        # Set catalog_field to catalog_name unless it is None or ''
        if catalog_name:
            new_session_configuration.course_info_filename = catalog_name
        
        if availability_name:
            new_session_configuration.availability_filename = availability_name
        
        missing_attributes = save_configuration_session(new_session_configuration)
        
        if missing_attributes:
            self.output_error(f'Error encountered while saving default config file. Missing attributes: {", ".join(missing_attributes)}.')
        else:
            self.output('Config file created.')
    
    
    def configure_user_interface_mode(self, is_graphical):
        '''Set the user interface mode to GUI is passed true and CLI if passed false.'''
        try:
            # Get the config file as a list of strings/lines
            new_session_configuration = self.load_config_parameters()
            new_session_configuration.is_graphical = is_graphical
            missing_attributes = save_configuration_session(new_session_configuration)
            
            if missing_attributes:
                self.output_error(f'Error encountered while saving config file. Missing attributes: {", ".join(missing_attributes)}.')
            else:
                self.output('Config modified.')
            
        except ConfigFileError:
            self.output_error('Some program has made illegal changes to the config file. Please correct those changes before proceeding.')
        except (FileNotFoundError, IOError):
            self.output_error('Failed to access config file.')
        
    
    def fetch_catalog(self, fetch_parameters=None):
        
        self.output('Fetching data...')
        
        update_course_info()
        
        self.output('Course catalog info updated.')
        
    
    ## ----------- Execution ----------- ##
    
    def check_schedule(self, filename):
        '''Check the schedule at the passed filename for prerquisites cycles.'''
        error_reports = None
                
        # Verify the passed filename exists
        filepath = get_real_filepath(filename) # Get the verified path (this is a Path object that exists, but it is not necessarily a directory)
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
        
    def batch_validate(self, pathname):
        '''Perform validation batching using the files in the passed pathname.'''
                
        # Verify the passed filename exists
        filepath = get_real_filepath(pathname) # Get the verified path (this is a Path object that exists, but it is not necessarily a directory)
        
        if filepath:
            course_info_container = self._scheduler.get_course_info()
            schedule_evaluator = self._scheduler.get_schedule_evaluator()
            
            try:
                if filepath.is_dir():
                    
                    self.output('Starting batch validation...')
                    
                    # The path is a directory (iterate over the file inside)
                    graduation_paths = []
                    for graduation_path in filepath.iterdir():
                        graduation_paths.append(graduation_path)
                    
                    # TODO: resolve pickling issue with ES functions
                    results = batch_validation(graduation_paths, course_info_container)
                    
                    # TODO: make the print appear in the same order as delivered (maybe do this from within the batch method)
                    
                    # Print the results
                    for result in results:
                        if result.is_valid():
                            self.output('{0} appears to be correct. The confidence value for this schedule is {1:.1f}%\n'.format(result.file_description, result.confidence_factor*100))
                        else:
                            self.output_warning(f'{result.file_description} is invalid!:')
                            
                            for infraction in result.error_list:
                                self.output(infraction)
                            
                            self.output(f'Please correct these issues.\n')
                    
                elif filepath.is_file():
                    # TODO: Implement this
                    self.output('Not supported yet')
                    
            except IOError:
                self.output_error('File system error encountered while attempting batch validation.')
        self.output('Batch concluded.')
        
    
    def generate_schedule(self, filename=None):
        '''Generate the schedule with a given filename or the current default filename if nothing is provided.'''
        
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
        
        # Create a confidence variable to return (-1 means failed)
        confidence_factor = -1
        
        # Set _destination_filename to the passed filename if one was passed
        if filename:
            self._destination_filename = filename
        
        desired_destination = self.get_destination()
        
        try:
            if self._export_types:
                container = self._scheduler.generate_schedule()
                confidence_factor = container.get_cf()
                semesters_listing = container.get_schedule()
                
                #semesters_listing, confidence_factor = self._scheduler.generate_schedule()
                self.output('Path generated with confidence value of {0:.1f}%'.format(confidence_factor*100))
                
                template_path = Path(get_source_path(), 'input_files')
                
                if PATH_TO_GRADUATION_EXPORT_TYPE in self._export_types:
                    unique_ptg_destination = get_next_free_filename(desired_destination.with_suffix('.xlsx'))
                    # Lew erased 'Path To Graduation' from here to work with excel_formatter
                    excel_formatter(Path(template_path), unique_ptg_destination, semesters_listing, self._scheduler.get_course_info())
                    self.output('Schedule (Path to Graduation) exported as {0}'.format(unique_ptg_destination))
                
                if PLAIN_TEXT_EXPORT_TYPE in self._export_types:
                    unique_ptext_destination = get_next_free_filename(desired_destination.with_suffix('.txt'))
                    plain_text_export(unique_ptext_destination, semesters_listing, 'Spring', 2022)
                    self.output('Schedule (plain text) exported as {0}'.format(unique_ptext_destination))
                
            else:
                self.output_error('Validation over a file list is not supported yet.')
                
        except (FileNotFoundError, IOError):
            # This code will probably execute when file system permissions/organization change after setting parameters
            self.output_error('File system error encountered while attempting an export (please try re-entering parameters). Some files may have exported.')
        
        return confidence_factor
        
    
    def batch_schedule(self, pathname):
        
        # TODO: add documentation
        
        # Verify the passed filename exists
        filepath = get_real_filepath(pathname) # Get the verified path (this is a Path object that exists, but it is not necessarily a directory)
        
        template_path = Path(get_source_path(), 'input_files')
                
        if filepath:
            course_info_container = self._scheduler.get_course_info()
            
            try:
                if filepath.is_dir():
                    
                    self.output('Starting batch output...')
                    
                    # The path is a directory (iterate over the file inside)
                    course_info_paths = []
                    for course_info in filepath.iterdir():
                        course_info_paths.append(course_info)
                    
                    # *Verification may here*
                    
                    unique_destination_directory = get_next_free_filename(self.get_destination())
                    unique_destination_directory.mkdir()
                                            
                    batch_process(filepath, unique_destination_directory, template_path, course_info_container)
                    
                elif filepath.is_file():
                    # TODO: Implement this
                    self.output_error('Export via a file list is not supported yet.')
                    
            except IOError:
                self.output_error('File system error encountered while attempting batch export.')
        
        self.output('Batch concluded.')
    
    
    def run_top_interface(self):
        '''Gets input from the user and passed that input into the presenting interface/menu. The method then returns whether
        there are any interfaces left presenting. In the case there aren't any, the method should not be called again. This may
        act as the process's entire loop.'''
        user_input = self.get_input() # Get input from the user
        current_interface = self.get_current_interface() # Get the current interface/menu
        current_interface.parse_input(self, user_input) # Pass the user's input to the current menu
        return len(self._interface_stack) != 0 # return whether there are still any interfaces presenting

# End of SmartPlannerController definition
