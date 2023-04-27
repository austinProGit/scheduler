# Thomas Merino
# 4/25/23
# CPSC 4175 Group Project

# TODO: add final semester rule
# TODO: change the name of the Expert System to "schedule_evaluator"
# TODO: File existence check does not consider the to-be file extensions (fix this) -- we could do this with Path.with_suffix('') and Path.suffix

# POTENTIAL GOALS FOR NEXT CYCLE:
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
# - Be able to manage config file with text editor (from software)
# - Make the content panel better
#           Have the content panel display the output schedule (so there aren't hundreds of windows opening during batch)
# - Add a log file (tracks commands entered and outputs generated)
# - Handle missing package errors better
# - Fix program icon appearing for file explorer (default Python icon)
# - Handle permission check when setting output directory
# - Implement weakref into the GUI widgets and item selection callbacks to prevent strong reference cycles
# - Add working popup warning/verifying GUI->CLI switch (adding this at the moment is bug-laden)
#           this creates an issue where the GUI sometimes dones not dismiss when changing to CLI (after switching back and forth)


# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable, Optional, Union
    from pandas import DataFrame
    from menu_interface_base import GeneralInterface
    from program_generated_evaluator import CourseInfoEvaluationReport
    from PySide6.QtWidgets import QApplication


# NOTE: Set this to True if you want to run memory profiling/check for memory leaks (this requires loading in cli)
IS_TESTING_MEMORY = False

if IS_TESTING_MEMORY:
    from guppy import hpy
    # Create a guppy heap tracking object if in memeory testing mode
    heap = hpy() 


# Project imports
# --------------------------------------

# General functionality and IO
from alias_module import *
import auto_update
from configuration_manager import *
from driver_fs_functions import *
from general_utilities import *


# UX
from cli_interface import MainMenuInterface, GraphicalUserMenuInterface, ErrorMenu

# Containers
from course_info_container import *
from courses_needed_container import CoursesNeededContainer
from scheduling_parameters_container import ConstructiveSchedulingParametersContainers
from degree_extraction_container import DegreeExtractionContainer 

# Scheduling
#from batch_process import batch_process
from scheduler_driver import ConstuctiveScheduler as Scheduler


# Parsers
from CSU_public_data_parser import update_course_info
from degreeworks_parser_v2 import generate_degree_extraction_container
from path_to_grad_parser import parse_path_to_grad

# Validators
#from batch_validation import batch_validation
from program_generated_evaluator import evaluate_container, NonDAGCourseInfoError, InvalidCourseError
from user_submitted_validator import validate_user_submitted_path

# Formatters
from excel_formatter import excel_formatter
from pdf_formatter import pdf_export
from plain_text_formatter import plain_text_export

#CBR Imports
#James Code
import cbr_driver
import Result
import results_analysis
import adaptation
import cbr_excel_output_handler
import insertion



# Other imports
# --------------------------------------

from PySide6 import QtWidgets

import platform
from sys import exit
from pathlib import Path
from os import path




# Used for controlling console window display
OPERATING_SYSTEM: str = platform.system()

# Flag that is true when running on Windows OS.
WIN_CONTROL_FLAG: bool = False

if OPERATING_SYSTEM == "Windows":
    try:
        # Windows OS-specific imports
        import pywintypes, win32gui, win32con, win32api
        TITLE = win32api.GetConsoleTitle()
        HWND = win32gui.FindWindow(None, TITLE)
        WIN_CONTROL_FLAG = True
    except ModuleNotFoundError:
        pass

# Used for auto-updating the program
VERSION = "v2.0.1"
RELEASE_URL = "https://api.github.com/repos/austinProGit/scheduler/releases/latest"
INSTALLER_INFO_FILE = "installer_info.txt"



## --------------------------------------------------------------------- ##
## ---------------------- Smart Planner Controller --------------------- ##
## --------------------------------------------------------------------- ##


class InterfaceProcedureError(Exception):
    '''This exception is used when an issue with interface presentation is encountered.
    Handling one should only be done for the sake of saving important data.'''
    pass

class SmartPlannerController:
    '''This class manages the interactions between the interface of the program and the model (mostly the scheduler).
    The class also manages the destination directory and filename.
    Menuing is performed by having an interface stack--alike chain of responsibility and/or state machine.
    '''
    
    def __init__(self, graphics_enabled=True):

        # Hide console window if running Windows OS
        if OPERATING_SYSTEM == "Windows" and WIN_CONTROL_FLAG:
            win32gui.ShowWindow(HWND, win32con.SW_HIDE)

        # Check for updates
        if auto_update.update(VERSION, RELEASE_URL, INSTALLER_INFO_FILE):
            exit(0)
        
        # Perform the controller's setup routine
        self.setup(graphics_enabled)
        
        if IS_TESTING_MEMORY:
            # Initialize information regarding the heap.
            # This is done after setup to simplify the deltas.
            heap.setrelheap()
    
    def setup(self, graphics_enabled: bool = True) -> None:
        '''Perform setup for scheduling, general configuration, and user interface. Setting graphics_enabled to false will
        only suppress the graphical interface during setup.'''
        
        # Initialize important variables

        parameter_container: ConstructiveSchedulingParametersContainers = \
            ConstructiveSchedulingParametersContainers(path=Path.home(), export_types=[PATH_TO_GRADUATION_EXPORT_TYPE])
        '''A scheduler parameter container where the destination directory is defaulted to export to the home directory.
        Configuration should be inspected for validity. Do not set properties purely based on user input.'''
        
        # Setup the scheduler--object for heading the model.
        # The scheduler functions as the program's model. It may be serialized to save the save of the process.
        self._scheduler: Scheduler = Scheduler(course_info_container=None, parameters_container=parameter_container)
        ''''''

        # In this context, an 'interface' is an object that handles user input and performs actions on the passed
        # controller given those inputs. Interfaces are not expected to directly interact with the user (input or
        # output) unless the interface presents graphical UI elements. Interfaces are covered more in
        # menu_interface_base.py and cli_interface.py.

        # Create a stack (list) for storing the active interfaces
        self._interface_stack: list[GeneralInterface] = []
        
        # The following are IO listeners that respond to process output. Only one listener per channel can be active; these should only
        # be used for adding custom GUI elements and for testing.
        self._output_callbacks: dict[str, Callable[[str], None]] = {} # A dict of keys to callbacks that are invoked when output is presented to the user
        self._warning_callbacks: dict[str, Callable[[str], None]] = {} # A dict of keys to callbacks that are invoked when a warning is presented to the user
        self._error_callbacks: dict[str, Callable[[str], None]] = {} # A dict of keys to callbacks that are invoked when a error is presented to the user
        
        # The following variables will be assigned (attempt to) in the following try block
        # The values are set to acceptable defaults
        self.session_configuration: SessionConfiguration = SessionConfiguration.make_default()

        #Create result variable to hold cbr result
        self._result = Result.Result("default", "default", "default", "default")

        try:
            # Attempt to get the program parameters from the config file
            self.session_configuration = self.load_config_parameters()
            
            # Load the course info file via the session configuration (SessionConfiguration)
            self.load_course_info(self.session_configuration)
            
            # Set the default destination filename (used when relevant)
            parameter_container.set_destination_filename(self.session_configuration.initial_schedule_name)
            
            # Load the user interface -- this should only block execution if graphics are presented
            self.load_interface(self.session_configuration.is_graphical and graphics_enabled) # Override conifg settings if graphics are suppressed

        except ConfigFileError as config_error:
            # Some config file error was encountered during loading (enter the error menu)
            self.output_error(f'A problem was encountered during loading: "{str(config_error)}"--entering error menu...')
            self.enter_error_menu()

        except (FileNotFoundError, IOError) as file_error:
            # Some IO error was encountered during loading (enter the error menu)
            self.output_error('A I/O error was encountered during loading--entering error menu...')
            self.enter_error_menu()

        except (NonDAGCourseInfoError, InvalidCourseError) as data_error:
            # Some data error was encountered during loading (enter the error menu)
            self.output_error(f'A data error was encountered during loading: "{str(data_error)}"--entering error menu...')
            self.enter_error_menu()

        except ValueError as value_error:
            # A value error was encountered during loading (enter the error menu)
            self.output_error(f'A data error was encountered during loading--entering error menu...')
            self.enter_error_menu()
    
    
    ## ----------- Process configuration ----------- ##
    
    
    def load_config_parameters(self) -> SessionConfiguration:
        '''Load program configuration information from the config file. This returns a SessionConfiguration object or raises a
        ConfigFileError if the file is invalid.'''
        
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
    
    
    def load_course_info(self, session_configuration: SessionConfiguration) -> None:
        '''Configure the scheduler with the course info file from the passes session object. This may re-raise a
        NonDAGCourseInfoError if one was raised during loading the course info.'''
        
        course_info_filename: str = session_configuration.course_info_filename
        excused_prereqs_filename: str = session_configuration.excused_prereqs
        alias_filename: str = session_configuration.alias_filename
        
        # Get the filepaths relative to the source path
        source_code_path: Path = get_source_path()
        course_info_relative_path: Path = get_source_relative_path(source_code_path, course_info_filename)
        excused_prereqs_relative_path: Path = get_source_relative_path(source_code_path, excused_prereqs_filename)
        alias_relative_path: Path = get_source_relative_path(source_code_path, alias_filename)
        
        # TODO: this is NOT in use at the moment (neither is availability in general...)
        #course_availability_relative_path = get_source_relative_path(source_code_path, course_availability_filename)
        
        # Attempt to load the course info data and pass it to the scheduler
        try:
            setup_aliases(alias_relative_path)

            course_info: Optional[DataFrame] = load_course_info(course_info_relative_path)
            course_info_container: CourseInfoContainer = CourseInfoContainer(course_info)
            
            # This raises an exception i0-f Course Info Container contains invalid data
            # evaluation_report: CourseInfoEvaluationReport = evaluate_container(course_info_container)
            # course_info_container.load_report(evaluation_report)
            
            self._scheduler.configure_course_info(course_info_container)
            
        except (FileNotFoundError, IOError) as file_error:
            # Course info could not be found/read (report to the user and re-raise the error to enter error menu)
            self.output_error(f'Invalid course catalog file. Please rename the catalog to {course_info_relative_path}, make sure it is accessible, and reload the catalog (enter "reload").')
            raise file_error
            
        except ValueError as config_error:
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
    
    
    def load_interface(self, is_graphical: bool) -> None:
        '''Load the process's interface. This should be called only once during the lifecycle of the process--unless the
        process is reloaded from the error menu.'''
        
        # Set the bottom/first interface to be either a GUI menu or CLI main menu instance
        bottom_interface: GeneralInterface = GraphicalUserMenuInterface() if is_graphical else MainMenuInterface()
        
        # Push the new menu
        self.push_interface(bottom_interface)
    
    
    ## ----------- User interface methods (CLI) ----------- ##
    
    # Notes:
    # Both warnings and error send their message through output.
    # Warnings are acceptable, but the user should still be notified in some way.
    # Errors cannot be ignored, but there is not as much of an emphasis placed on notifying the user.
    
    def output(self, message: str) -> None:
        '''Output a message to the user.'''
        callback: Callable[[str], None]
        for callback in self._output_callbacks.values():
            callback(message)
        print(message)
    
    
    def output_warning(self, message: str) -> None:
        '''Output a warning message to the user.'''
        callback: Callable[[str], None]
        for callback in self._warning_callbacks.values():
            callback(message)
        self.output(f'WARNING: {message}')
    
    
    def output_error(self, message: str) -> None:
        '''Output an error message to the user.'''
        callback: Callable[[str], None]
        for callback in self._error_callbacks.values():
            callback(message)
        self.output(f'ERROR: {message}')
    

    def output_clear(self) -> None:
        '''Clear the terminal of content (intended for CLI interface).'''
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
    

    def get_input(self) -> str:
        '''Get input text from the user with the current interface's/menu's name in the prompt.'''
        current_interface: GeneralInterface = self.get_current_interface()
        
        if IS_TESTING_MEMORY:
            print(heap.heap())
        
        return input(f'{current_interface.name}: ')
    
    
    def add_output_listener(self, key: str, output_callback: Callable[[str], None]) -> None:
        '''Add a callback that's invoked when output is about to be presented to the user (that may only be one at a time for the passed key).'''
        self._add_callback_listener(key, output_callback, self._output_callbacks)
    
    def remove_output_listener(self, key: str) -> bool:
        '''Remove the output callback for the passed key. The success of the removal is returned.'''
        return self._remove_callback_listener(key, self._output_callbacks)


    def add_warning_listener(self, key: str, warning_callback: Callable[[str], None]) -> None:
        '''Add a warning callback that's invoked when a warning is about to be presented to the user (that may only be one at a time for the passed key).'''
        self._add_callback_listener(key, warning_callback, self._warning_callbacks)
    
    def remove_warning_listener(self, key: str) -> bool:
        '''Remove the warning callback for the passed key. The success of the removal is returned.'''
        return self._remove_callback_listener(key, self._warning_callbacks)


    def add_error_listener(self, key: str, warning_callback: Callable[[str], None]) -> None:
        '''Add a error callback that's invoked when an error is about to be presented to the user (that may only be one at a time for the passed key).'''
        self._add_callback_listener(key, warning_callback, self._error_callbacks)
    
    def remove_error_listener(self, key: str) -> bool:
        '''Remove the error callback for the passed key. The success of the removal is returned.'''
        return self._remove_callback_listener(key, self._error_callbacks)


    def _add_callback_listener(self, key: str, callback: Callable[[str], None], callback_map: dict[str, Callable[[str], None]]) -> None:
        '''Internal method for modifying a callback mapping.'''
        callback_map[key] = callback
    
    def _remove_callback_listener(self, key: str, callback_map: dict[str, Callable[[str], None]]) -> bool:
        '''Internal method to remove the callback for the passed key. The success of the removal is returned.'''
        will_remove = key in callback_map
        if will_remove:
            del callback_map[key]
        return will_remove
    
    
    ## ----------- Interface/menu control ----------- ##
    

    def has_interface(self) -> bool:
        '''Gets whether the is an interface in the interface stack.'''
        return len(self._interface_stack) != 0
    

    def get_current_interface(self) -> GeneralInterface:
        '''Get the interface/menu that is presenting. This may raise an InterfaceProcedureError if there
        is no interfaces left.'''
        
        # Ensure the is a interface (if not, raise a InterfaceProcedureError)
        if len(self._interface_stack) == 0:
            raise InterfaceProcedureError('')
            
        # Return the top interface
        return self._interface_stack[-1]
    
    
    def push_interface(self, interface: GeneralInterface) -> None:
        '''Push a given interface to the top of the interface stack.'''
        self._interface_stack.append(interface)
        interface.was_pushed(self)
    
    
    def pop_interface(self, interface: GeneralInterface) -> GeneralInterface:
        '''Pop the provided interface if it on top of the interface stack. Otherwise, raise a
        InterfaceProcedureError.'''
        
        # Check if the passed interface resides on the top of the stack
        if interface is self.get_current_interface():
            top_interface: GeneralInterface = self._interface_stack.pop() # Pop the passed interface
            top_interface.deconstruct(self) # Call the interface's deconstruct method
            return top_interface
        else:
            raise InterfaceProcedureError() # Raise an error about the illegal procedure
    
    
    def clear_all_interfaces(self) -> None:
        '''Clear the interface stack (this dismisses all interface in order from highest to lowest).'''
        while self.has_interface():
            self.pop_interface(self.get_current_interface())
    
    
    def reload_in_cli(self) -> None:
        '''Clear the interface stack (this dismisses all interface in order from highest to lowest) and push a cli menu.'''
        self.clear_all_interfaces()
        self.push_interface(MainMenuInterface())
    
    
    def get_graphical_application(self) -> Optional[QApplication]:
        '''Get the current graphical application object. If it does not exist, create a new one.'''
        application: Optional[QApplication] = QtWidgets.QApplication.instance()
        if application is None:
            # There is no application (create one)
            application = QtWidgets.QApplication([])
        return application
    
    
    def enter_error_menu(self) -> None:
        '''Push an error menu onto the menu stack so the user can correct errors before reloading.
        This blocks execution until the error menu exits.'''
        new_error_menu: ErrorMenu = ErrorMenu()
        self.push_interface(new_error_menu)
        
        # While the new error message is in the stack, run the top interface (most likely the error menu)
        while new_error_menu in self._interface_stack:
                self.run_top_interface()
    
    
    ## ----------- Scheduling parameter getting ----------- ##
    

    def get_courses_needed(self) -> Optional[CoursesNeededContainer]:
        '''Get the coursed needed that have been loaded into the scheduler. This return a list of strings (IDs).'''
        return self._scheduler.get_courses_needed_container()
        
    
    def get_hours_per_semester(self) -> Optional[range]:
        '''Get the hours per semester to use.'''
        parameters: ConstructiveSchedulingParametersContainers = self._scheduler.get_parameter_container()
        return parameters.get_hours_for(FALL)
    
    
    def get_export_type(self) -> list[ExportType]:
        '''Get a set of the enabled export types.'''
        parameters: ConstructiveSchedulingParametersContainers = self._scheduler.get_parameter_container()
        return parameters.get_export_types()
    
    
    def get_destination_directory(self) -> Path:
        '''Get the path that the resulting schedule file will be exported to. This should always return a real directory.'''
        parameters: ConstructiveSchedulingParametersContainers = self._scheduler.get_parameter_container()
        return parameters.get_destination_directory()
    
    
    def get_destination_filename(self) -> str:
        '''Get string that will be used to name the resulting schedule file.'''
        parameters: ConstructiveSchedulingParametersContainers = self._scheduler.get_parameter_container()
        return parameters.get_destination_filename()
            
    
    def get_destination(self) -> Path:
        '''Get the full path of the schedule destination. This should always return a valid destination.'''
        return Path(self.get_destination_directory(), self.get_destination_filename())
    
    
    ## ----------- Scheduling parameter configuration ----------- ##
    

    def load_courses_needed(self, filename: str) -> bool:
        '''Load the courses that must be scheduled into the scheduler (from the passed filename).
        This return the success of the load.'''
        success: bool = False
        try:
            filepath: Optional[Path] = get_real_filepath(filename) # Get the file's path and check if it exists
            if filepath is not None:
                # Load degree extraction / courses needed contents here:
                degree_extraction: DegreeExtractionContainer = generate_degree_extraction_container(filepath) # Get the needed courses from the file
                self._scheduler.configure_degree_extraction(degree_extraction) # Load the course container / degree extraction into the scheduler

                courses_needed_container: Optional[CoursesNeededContainer] = self._scheduler.get_courses_needed_container()
                if courses_needed_container is None:
                    raise ValueError('Errror ecnounted while configuring degree extractino container')
                courses_needed_container.stub_all_unresolved_nodes()

                # for node in self._scheduler._courses_needed_container._decision_tree.get_all_children_list():
                #     node.enable_stub()

                #self._scheduler.configure_courses_needed(courses_needed_container) 
                self.output('Course requirements loaded from {0}.'.format(filepath)) # Report success to the user
                success = True # Set success to true
            else:
                self.output_error('Sorry, {0} file could not be found.'.format(filename)) # Report if the file could not be found
        except IOError:
            self.output_error('Sorry, {0} file could not be openned.'.format(filename)) # Report if the file could not be openned

        return success
    
    def create_empty_courses_needed(self) -> None:
        '''Load a new, blank degree extraction container into the scheduler'''
        degree_extraction: DegreeExtractionContainer = DegreeExtractionContainer(curr_taken_courses=[], courses_needed_constuction_string='',
            degree_plan_name=None, student_number=None, student_name=None, gpa=None)
        self._scheduler.configure_degree_extraction(degree_extraction)
        self.output('New blank degree plan / course tree created.')
        
    
    def configure_hours_per_semester(self, number_of_hours: int) -> bool:
        '''Set the number of hours that are scheduled per semester. This return the success of the load.'''

        success: bool = True
        
        if number_of_hours <= self.session_configuration.strong_hours_minimum \
            or self.session_configuration.strong_hours_limit < number_of_hours:
            
            # The user has entered an amount of credits above or below what us acceptable (output a warning)
            strong_minimum: int = self.session_configuration.strong_hours_minimum
            strong_maximum: int = self.session_configuration.strong_hours_limit
            self.output_warning(f'Please enter between {strong_minimum} and {strong_maximum} hours per semester.')
            success = False

        else:
            if number_of_hours > self.session_configuration.normal_hours_limit:
                self.output_warning(f'Taking over {self.session_configuration.normal_hours_limit} credit hours per semester is not recommended.')
            
            self._scheduler.configure_hours_per_semester(number_of_hours)
            self.output(f'Hours per semester set to {number_of_hours}.')
        return success
        

    def configure_hours_per_summer(self, number_of_hours: int) -> bool:
        '''Set the number of hours that are scheduled per Summer semester. This return the success of the load.'''

        success: bool = True
        
        if number_of_hours < 0 or self.session_configuration.strong_hours_limit < number_of_hours:
            
            # The user has entered an amount of credits above or below what us acceptable (output a warning)
            strong_maximum: int = self.session_configuration.strong_hours_limit
            self.output_warning(f'Please enter between {0} and {strong_maximum} hours per semester.')
            success = False

        else:
            self._scheduler.configure_hours_per_summer(number_of_hours)
            self.output(f'Hours per Summer set to {number_of_hours}.')
        return success
        
    
    def set_export_types(self, export_types: list[ExportType]) -> None:
        '''Set the types of formats to export with (schedule formatters to use).'''
        #self._export_types = export_types[:]
        parameters: ConstructiveSchedulingParametersContainers = self._scheduler.get_parameter_container()
        parameters.set_export_type(export_types)
    
    
    def configure_destination_directory(self, directory: Union[str, Path]) -> bool:
        '''Set the destination directory (where to save the schedule). This return the success of the configuration.'''
        success = False
                
        # Verify the passed directory exists and is indeed a directory
        directory_path: Optional[Path] = get_real_filepath(directory)   # Get the verified path (this is a Path object that exists, but it is not necessarily a directory)
        if directory_path is not None and directory_path.is_dir():
            parameters: ConstructiveSchedulingParametersContainers = self._scheduler.get_parameter_container()
            parameters.set_destination_directory(directory_path)
            # self._destination_directory = directory_path
            self.output('Destination directory set to {0}.'.format(directory_path))
            success = True
        else:
            # Report if the directory could not be found
            self.output_error('Sorry, {0} directory could not be found.'.format(directory))
            
        return success
        
    
    def set_destination_filename(self, filename: str) -> None:
        '''Simply set the destination filename (what to name the schedule).'''
        # self._destination_filename = filename
        parameters: ConstructiveSchedulingParametersContainers = self._scheduler.get_parameter_container()
        parameters.set_destination_filename(filename)
    
    
    def configure_destination_filename(self, filename: str) -> None:
        '''Set the destination filename (what to name the schedule). This should invoked when configuring output parameter, but
        it should not be invoked just before exporting. Do not use this for modifying _destination_filename in all cases. This is
        like the user interface method of changing the export filename.'''
        
        # Set the destination filename (not verified)
        self.set_destination_filename(filename)
        self.output('Result filename set to {0}.'.format(filename))
        
        # Check if a file already exists with the current destination
        filepath: Optional[Path] = get_real_filepath(self.get_destination())
        if filepath:
            self.output_warning('A file already exists with that name. The exported files will have slightly different names.')
    
    
    ## ----------- Program configuration ----------- ##
    
    
    # TODO: TEST - this still has not been tested enough
    def create_default_config_file(self, catalog_name: Optional[str] = None, availability_name: Optional[str] = None):
        '''Create a default config file for the program. This uses the default catalog name if
        catalog name is empty or None and saves the config file to this file's directory '''
        
        new_session_configuration: SessionConfiguration = SessionConfiguration.make_default()
        
        # Set catalog name field to catalog_name unless it is None or '' (falsey)
        # Leaving the parameter None means the default value is used (from SessionConfiguration.make_default)
        if catalog_name:
            new_session_configuration.course_info_filename = catalog_name
        
        # Set availability name field to availability_name unless it is None or '' (falsey)
        # Leaving the parameter None means the default value is used (from SessionConfiguration.make_default)
        if availability_name:
            new_session_configuration.availability_filename = availability_name
        
        missing_attributes: list[str] = save_configuration_session(new_session_configuration)
        
        if missing_attributes:
            self.output_error(f'Error encountered while saving default config file. Missing attributes: {", ".join(missing_attributes)}.')
        else:
            self.output('Config file created.')
    
    
    def configure_user_interface_mode(self, is_graphical: bool) -> None:
        '''Set the user interface mode to GUI is passed true and CLI if passed false.'''
        try:
            # Get the config file as a list of strings/lines
            new_session_configuration: SessionConfiguration = self.load_config_parameters()
            new_session_configuration.is_graphical = is_graphical
            missing_attributes: list[str] = save_configuration_session(new_session_configuration)
            
            if missing_attributes:
                self.output_error(f'Error encountered while saving config file. Missing attributes: {", ".join(missing_attributes)}.')
            else:
                self.output('Config modified.')
            
        except ConfigFileError:
            self.output_error('Some program has made illegal changes to the config file. Please correct those changes before proceeding.')
        except (FileNotFoundError, IOError):
            self.output_error('Failed to access config file.')
        
    
    def fetch_catalog(self, fetch_parameters=None) -> None:
        dept_pattern = r"[A-Z]{3}[A-Z]?"
        file0 = get_source_path()
        file0 = get_source_relative_path(file0, 'input_files/Course Info.xlsx')
        
        self.output('Fetching data...')
        
        if fetch_parameters == None:
            new_container = update_course_info(self, None)           
            if new_container != None:
                write_df_dict_xlsx(new_container, file0)

        else:
            fetch_parameters = fetch_parameters.upper()
            course_list = re.findall(dept_pattern, fetch_parameters)
            if course_list != []:                
                new_container = update_course_info(self, course_list)
                if new_container != None:
                    df_dict = load_course_info(file0)
                    old_container = CourseInfoContainer(df_dict)
                    old_container.update_container_keeping_external_duplicates(new_container)
                    write_df_dict_xlsx(old_container, file0)
            else:
                self.output("Format incorrect: Must be in form XXX or XXXX")
        
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
                error_reports = validate_user_submitted_path(self._scheduler.get_course_info(), schedule,
                    excused_courses = self._scheduler._taken_course).error_list
                if not error_reports:
                    self.output('Path valid.')
                else:
                    self.output_warning('Invalid path! Please correct the following errors.')
                    for infraction in error_reports:
                        self.output(str(infraction))
                
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
        if not self._scheduler.get_courses_needed_container():
            self.output_warning('No schedule exported.')
            self.output_error('No needed courses loaded.')
            return

        export_types = self._scheduler.get_parameter_container().get_export_types()
        
        # Check if no export types are selected (empty)
        if not export_types:
            self.output_warning('No schedule exported.')
            self.output_error('No export type selected.')
            return 
        
        
        self.output('Generating schedule...')
        
        # Create a confidence variable to return (-1 means failed)
        confidence_factor = -1
        
        # Set _destination_filename to the passed filename if one was passed
        if filename:
            self.set_destination_filename(filename)
        
        desired_destination = self.get_destination()
        
        try:
            self._scheduler.prepare_schedulables()
            container = self._scheduler.generate_schedule(prequisite_ignored_courses=[])

            confidence_factor = container.get_confidence_level()
            
            #semesters_listing, confidence_factor = self._scheduler.generate_schedule()
            self.output('Path generated with confidence value of {0:.1f}%'.format(confidence_factor*100))
            
            template_path = Path(get_source_path(), 'input_files')
             
            if PATH_TO_GRADUATION_EXPORT_TYPE in export_types:
                unique_ptg_destination = get_next_free_filename(desired_destination.with_suffix('.xlsx'))
                excel_formatter(Path(template_path), unique_ptg_destination, container, self._scheduler.get_course_info())
                self.output('Schedule (Path to Graduation) exported as {0}'.format(unique_ptg_destination))
                if os.name == 'nt':
                    os.startfile(unique_ptg_destination)
                else:
                    os.system(f'open {str(unique_ptg_destination.absolute())}')
            
            if PLAIN_TEXT_EXPORT_TYPE in export_types:
                unique_ptext_destination = get_next_free_filename(desired_destination.with_suffix('.txt'))
                plain_text_export(Path(unique_ptext_destination), container, FALL, 2022)
                self.output('Schedule (plain text) exported as {0}'.format(unique_ptext_destination))
                if os.name == 'nt':
                    os.startfile(unique_ptext_destination)
                else:
                    os.system(f'open {str(unique_ptext_destination.absolute())}')

            if PDF_EXPORT_TYPE in export_types:
                unique_pdf_destination = get_next_free_filename(desired_destination.with_suffix('.pdf'))
                pdf_export(Path(unique_pdf_destination), container, FALL, 2022)
                self.output('Schedule (PDF) exported as {0}'.format(unique_pdf_destination))
                if os.name == 'nt':
                    os.startfile(unique_pdf_destination)
                else:
                    os.system(f'open {str(unique_pdf_destination.absolute())}')
                
                
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
    
        #James CBR stuff

    def get_cbr_result(self):
        return self._result
    
    def set_cbr_result(self, target, retrieved, recommended_electives, similarity_measure):
        self._result = Result.Result(target, retrieved, recommended_electives, similarity_measure)
    
    def run_cbr(self, selected_file):
        result = cbr_driver.run_cbr_option(selected_file)
        self.set_cbr_result(result.get_target_case(), result.get_retrieved_case(), result.get_recommended_electives(), result.get_similarity_measure())

    def run_cbr_reasoning(self):
        if self._result.get_target_case() != "default":
            return results_analysis.results_driver_new(self._result)
        else:
            return "Error! Please run the CBR before asking about results analysis"
        
    def get_elective_count_for_adapt(self):
        return adaptation.get_elective_count(self._result)
    
    def adaptation_recommendation(self):
        return adaptation.resolve_differences_new(adaptation.get_elective_count(self._result))
    
    def output_cbr_result_to_excel(self, selected_file):
        working_elective_list = self._result.get_recommended_electives()
        return cbr_excel_output_handler.write_to_file(selected_file, working_elective_list)
    
    def insert_result_into_case_base(self):
        insertion.insert_into_case_base_problem(self._result)
        insertion.insert_into_case_base_solution(self._result)
    

# End of SmartPlannerController definition
