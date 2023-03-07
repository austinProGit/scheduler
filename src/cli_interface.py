# Thomas Merino
# 2/20/23
# CPSC 4175 Group Project

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable, Optional
    from program_driver import SmartPlannerController as Controller
    from PySide6.QtWidgets import QApplication
    from menu_interface_base import ControllerCommand


# TODO: (ENSURE) help file parser ends predictably at "<END>" (no extra blank lines)
# TODO: (ORGANIZE) Remove redundant file explorer code
# TODO: (WISH) make help loading the documentation happen only once and only when needed (static and lazy)

from courses_needed_container import NeededCoursesInterface, CONSTANT_REFRESHING

from PySide6 import QtWidgets, QtGui
from sys import exit


from driver_fs_functions import *
from graphical_interface import MainProgramWindow
from item_selection_interface import ItemSelectionInterface
from menu_interface_base import GeneralInterface
from help_interface import HelpMenu

ICON_FILENAME: str = 'icon.png' # The filename of the program's icon (when GUI)



## --------------------------------------------------------------------- ##
## ------------------------- Interface Objects ------------------------- ##
## --------------------------------------------------------------------- ##


# The following is the main menu for the program. It handles loading the needed courses,
# configuring scheduling parameters, generating the schedule, etc.
class MainMenuInterface(GeneralInterface):
    
    def __init__(self) -> None:
        self.name: str = 'MAIN MENU'
        self._commands: dict[str, ControllerCommand] = {}
        
        # e: explorer
        # i: immediate
        
        # Add commands to the command dictionary
        self.add_command(list_available_commands_command, '', 'commands', 'list-commands')
        self.add_command(load_needed_courses_command, 'load', 'needed', 'set')
        self.add_command(explore_needed_courses_command, 'load-e', 'needed-e', 'set-e')
        self.add_command(load_destination_directory_command, 'destination', 'dest', 'to', 'directory')
        self.add_command(explore_destination_directory_command,'destination-e', 'dest-e', 'to-e', 'directory-e')
        self.add_command(set_hours_per_semster_command, 'hours', 'set-hours', 'per', 'count', 'set-count')
        self.add_command(select_export_command, 'as', 'exports', 'set-exports', 'type', 'types', 'set-types',)
        self.add_command(list_parameters_command, 'courses', 'list-courses', 'parameters', 'list-parameters', 'arguments', 'list-arguments', 'args')
        self.add_command(generate_schedule_command, 'schedule', 'generate', 'done', 'save')
        self.add_command(batch_schedule_command, 'batch-schedule', 'batch', 'group-schedule', 'group')
        self.add_command(schedule_verify_command, 'verify', 'validate', 'check')
        self.add_command(explore_schedule_verify_command, 'verify-e', 'validate-e', 'check-e')
        self.add_command(batch_schedule_verify_command, 'batch-verify', 'group-verify', 'batch-validate', 'group-validate', 'batch-check', 'group-check')
        self.add_command(set_gui_interface_command, 'gui')
        self.add_command(set_cli_interface_command, 'cli', 'lui')
        self.add_command(gui_interface_immediate_command, 'gui-i', 'window', 'graphical', 'graphics')
        self.add_command(help_command, 'help', 'info')
        self.add_command(fetch_catalog_command, 'fetch', 'update', 'catalog')
        self.add_command(edit_courses_needed_container_command, 'select', 'choose', 'tree')
        self.add_command(quit_command,'quit', 'exit')
    
    
    def report_invalid_command_error(self, controller: Controller, command_string: str) -> None:
        '''Report when an unsupported command is entered (this may be overridden to provide relevant tools/help).'''
        controller.output_error(f'Sorry, no command matching "{command_string}" was found. Use "commands" or "help" to find the command you are looking for.')
        

# This a special menu that, once pushed, presents the user with a graphical user interface for interfacing with
# the process. This will block execution until the GUI is closed, which will trigger the menu to pop itself. The
# menu has no real value in the CLI and cannot even be dismissed via input parsing.

class GraphicalUserMenuInterface(GeneralInterface):
    
    
    def __init__(self) -> None:
        self.name: str = 'GUI MENU'
    
    
    def was_pushed(self, controller: Controller) -> None:
        '''Method that is called upon the interface being pushed onto the interface stack.'''
        
        application: Optional[QApplication] = controller.get_graphical_application() # Get the application object from the controller
        # TODO: This is not sustainable (using __file__)
        icon: QtGui.QIcon = QtGui.QIcon(str(os.path.join(os.path.dirname(__file__), ICON_FILENAME)))
        #application.setWindowIcon(icon)   # Set the window icon
        main_window = MainProgramWindow(controller) # Create a new window for the application to present
        main_window.resize(800, 400) # Set the initial window size
        main_window.show() # Present the window
        application.exec() # Execute the application until closed (block execution)
        
        # At this point, the GUI has been closed and the program should resume normal execution
        # Since that menu has served its purpose, it will be popped if still in the stack
        
        # Ensure the controller has an interface and that the current interface is indeed this menu
        # This check is required in case of future changes and when an error menu interrupts execution
        if controller.has_interface() and controller.get_current_interface() is self:
            controller.pop_interface(self)
    
        
    def deconstruct(self, controller: Controller):
        '''Destruction method that is called upon the interface being dismissed.'''
        # Disconnect program IO from graphics
        controller.remove_output_listener("GUIOutput")
        controller.remove_warning_listener("GUIWarning")
        
        # Get and terminate the graphical application component
        application = QtWidgets.QApplication.instance()
        application.closeAllWindows()
        application.exit(0)  # This may also be "application.quit()" in most cases


# The following is the error menu for the program. It handles illegal program states and
# lets reload configuration data.

class ErrorMenu(GeneralInterface):
    
    def __init__(self):
        self.name = 'ERROR MENU'
        self._commands = {}
        
        # Add commands to the command dictionary
        self.add_command(attempt_error_resolve, 'reload', 'retry', 'start', 'restart')
        self.add_command(create_default_config_command, 'config')
        self.add_command(quit_command, 'quit', 'exit', 'cancel')
        

## --------------------------------------------------------------------- ##
## ------------------------ Interface Callbacks ------------------------ ##
## --------------------------------------------------------------------- ##


def list_available_commands_command(controller: Controller, argument: str):
    '''Output the commands that may be entered.'''
    
    controller.output('Here are the commands available:\ncommands, load, load-e, destination, destination-e, set-hours, set-exports, list-parameters, schedule, verify, verify-e, batch, batch-verify, gui, cli, gui-i, help, quit')
    # TODO: maybe use a listing from help resourses or the main menu interface class.


def help_command(controller, argument):
    '''Push a help menu object onto the caller's stack and pass any arguments (if any) to the new menu as user input.'''
    controller.output('Welcome to the help menu. Type keywords to search for a help article. Type "all" to see all articles and "exit" to exit the help menu.')
    new_help_interface = HelpMenu()                             # Initialize the new interface
    controller.push_interface(new_help_interface)               # Push the new interface onto the controller's stack
    
    # Check if there was any argument(s) provided
    if argument:
        new_help_interface.parse_input(controller, argument)    # Have the new menu process the arguements


def load_needed_courses_command(controller, filename):
    '''Ask the provided caller to load needed courses via the provided filename.'''
    if filename:
        controller.load_courses_needed(filename)
    else:
        controller.output_error('Please enter the file\'s path.')


def load_destination_directory_command(controller, directory):
    '''Ask the provided caller to change the destination directory to the provided directory (the directory's existence i checked first).'''
    if directory:
        controller.configure_destination_directory(directory)
    else:
        controller.output_error('Please enter the directory\'s path.')

def explore_needed_courses_command(controller, argument):
    '''Command to create a new QT file explorer application so the user can load the needed courses file.'''
    
    # Check if the user passed some argument(s) (report error and return if so)
    if argument:
        controller.output_error('Arguments are not supported for this command.')
        return
    
    # This gets the application (launches if there is none) and uses it to present a file selection dialog
    application = controller.get_graphical_application()
    file_loader_dialog = QtWidgets.QFileDialog()
    file_loader_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
    filename = None
    
    if file_loader_dialog.exec():
        filename = file_loader_dialog.selectedFiles()[0]
        load_needed_courses_command(controller, filename)
    if filename == None:
        controller.output('File load cancelled.')
        
    application.quit()
    

def explore_destination_directory_command(controller, argument):
    '''Command to create a new QT file explorer application so the user can set the destination directory.'''
    
    # Check if the user passed some argument(s) (report error and return if so)
    if argument:
        controller.output_error('Arguments are not supported for this command.')
        return
    
    # This gets the application (launches if there is none) and uses it to present a directory selection dialog
    application = controller.get_graphical_application()
    directory_loader_dialog = QtWidgets.QFileDialog()
    directory_loader_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
    directory_name = None
    
    if directory_loader_dialog.exec():
        directory_name = directory_loader_dialog.selectedFiles()[0]
        load_destination_directory_command(controller, directory_name)
    if directory_name == None:
        controller.output('Destination load cancelled.')
        
    application.quit()


def set_hours_per_semster_command(controller, argument):
    '''Ask the provided caller to set the number of hours per semester.'''
    
    # Check if the argument is numeric
    if argument.isdigit():
        number = int(argument)                              # Attempt to cast the input to an integer
        controller.configure_hours_per_semester(number)     # Set the number of hours per semester
    else:
        # The argument was not valid (report to the user)
        controller.output_error('Sorry, that is not a valid input (please use a number).')


def select_export_command(controller, argument):
    '''Command to present a new item selection interface so the user can select the export methods.'''
    
    # Define the function that's called when items selection is modified
    def modify(controler, export_types_selected):
        # Check if the user has unchecked all types
        if len(export_types_selected) == 0:
            controller.output_warning('Make sure you have at least one export mode selected.')
    
    # Define the function that's called when the user indicates completion
    def complete(controler, export_types_selected):
        # Construct a list of/from the selected export types
        export_types_list = list(EXPORT_TYPE_DESCRIPTIONS.keys())
        selected_export_types = [export_types_list[selection_index] for selection_index in export_types_selected]
        
        # Apply the selection to the controller
        controller.set_export_types(selected_export_types)
        controller.output('Export type(s) set.')
    
    # Define the function that's called when the user cancels
    def cancel(controler, export_types_selected):
        controller.output('Export type(s) selection cancelled...')
        
    # Initialize and construct the item selection menu
    list_interface = ItemSelectionInterface(list(EXPORT_TYPE_DESCRIPTIONS.values()), modify, complete, cancel)
    list_interface.set_selected(set(controller.get_export_type()))
    controller.push_interface(list_interface)
    
    controller.output('Please select from the following export types:') # Output the initial prompt
    list_interface.list_progress(controller)                            # Output the current selection


def list_parameters_command(controller, arguements):
    '''List the current scheduling parameters (destination directory, hours per semester, needed courses, etc.).'''
    if not arguements:
        controller.output('Scheduling Parameter:\n')
        controller.output('Destination: {0}'.format(controller.get_destination_directory()))

        hours_range: Optional[range] = controller.get_hours_per_semester()
        if hours_range is not None:
            controller.output(f'Hourse per semester: {hours_range.start} to {hours_range.stop}')
        else:
            controller.output('Unspecified')
        
        courses_needed = [str(s) for s in controller.get_courses_needed().get_courses_list()]
        
        if courses_needed:
            controller.output('Courses:')
            course: str
            for course in courses_needed:
                controller.output('  {0}'.format(course))
        else:
            controller.output('No needed courses loaded.')
    else:
        controller.output_error('Arguments are not supported for this command.')
    

def create_default_config_command(controller, argument):
    '''Command to create a default config file for the program.'''
    # TODO: Maybe have the argument become the filenames in the config (split via spaces into 0, 1, or 2 filepaths)
    controller.create_default_config_file(catalog_name=None, availability_name=None)


def set_gui_interface_command(controller, arguements):
    '''Change the user interface mode to GUI (this does not reload the interface, though).'''
    if not arguements:
        controller.configure_user_interface_mode(is_graphical=True)
        controller.output('Default UI mode set to graphical (enter gui-i to enter immediately).')
    else:
        controller.output_error('Arguments are not supported for this command.')


def set_cli_interface_command(controller, arguements):
    '''Change the user interface mode to CLI (this does not reload the interface, though).'''
    if not arguements:
        controller.configure_user_interface_mode(is_graphical=False)
        controller.output('Default UI mode set to commandline.')
    else:
        controller.output_error('Arguments are not supported for this command.')


def gui_interface_immediate_command(controller, arguements):
    '''Enter a GUI interface (this does not change the program config, though).'''
    if arguements == '':
        controller.push_interface(GraphicalUserMenuInterface())
    else:
        controller.output_error('Arguments are not supported for this command.')


def schedule_verify_command(controller, filename):
    '''Verify the schedule for prequisite cycles and correct availability.'''
    if filename:
        controller.check_schedule(filename)
    else:
        controller.output_error('Please enter the file\'s path.')


def explore_schedule_verify_command(controller, argument):
    '''Verify the schedule for prequisite cycles (with file explorer).'''
    
    # Check if the user passed some argument(s) (report error and return if so)
    if argument:
        controller.output_error('Arguments are not supported for this command.')
        return
    
    # This gets the application (launches if there is none) and uses it to present a file selection dialog
    application = controller.get_graphical_application()
    file_loader_dialog = QtWidgets.QFileDialog()
    file_loader_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
    filename = None
    
    if file_loader_dialog.exec():
        filename = file_loader_dialog.selectedFiles()[0]
        schedule_verify_command(controller, filename)
    if filename == None:
        controller.output('File load cancelled.')
        
    application.quit()


def generate_schedule_command(controller, filename):
    '''Ask the provided caller to generate a schedule with the passed filename.'''
    if filename:
        controller.generate_schedule(filename)
    else:
        controller.output_error('Please enter a filename.')

def batch_schedule_command(controller, arguments):
    '''Ask the provided caller to generate schedules with the passed directory (assumed needed-courses files) and possibly an output name (after comma).'''
    
    if arguments:
        comma_position = arguments.find(',')
        directory_name = arguments
        if comma_position != -1:
            controller.set_destination_filename(arguments[comma_position+1:].strip())
            directory_name = arguments[:comma_position].strip()
        controller.batch_schedule(directory_name)
    else:
        controller.output_error('Please enter a file or directory path/name .')

def batch_schedule_verify_command(controller, directory_name):
    '''Ask the provided caller to verify the schedules for prequisite cycles and correct availability in the passed directory (assumed to contain paths to  graduation).'''
    
    if directory_name:
        controller.batch_validate(directory_name)
    else:
        controller.output_error('Please enter the directory\'s path.')
    

def quit_command(controller, arguements):
    '''Terminate the program.'''
    if not arguements:
        controller.clear_all_interfaces() # Pop all interfaces in the controller's stack
        controller.output('Thank you. Goodbye.') # Output goodbye message
    else:
        controller.output_error('Arguments are not supported for this command.')


def attempt_error_resolve(controller, argument):
    '''Attempt to reload the course info data and pop the top menu (expected to be an error menu).'''
    
    if not argument:
        controller.output('Reloading configuration files...')
        
        # Deconstruct all active interfaces on the stack
        controller.clear_all_interfaces()
        
        # Exit the QT application if active
        application = QtWidgets.QApplication.instance()
        if application:
            exit(application)
                
        # Reload the program
        controller.setup()
    else:
        controller.output_error('Arguments are not supported for this command.')
    

def edit_courses_needed_container_command(controller, argument):
    if not argument:
        controller.output('Editing courses needed and course selection...')
        
        new_interface = NeededCoursesInterface(controller.get_courses_needed().get_decision_tree())

        # Deconstruct all active interfaces on the stack
        controller.push_interface(new_interface)

    else:
        controller.output_error('Arguments are not supported for this command.')


## ----------- The following are more or less still in development (not in the current implementation) ----------- ##


def fetch_catalog_command(controller, argument):
    if argument:
        controller.fetch_catalog(argument)
    else:
        controller.fetch_catalog()
