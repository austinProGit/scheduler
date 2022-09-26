# Thomas Merino
# 9/23/22
# CPSC 4175 Group Project

# TODO: (ENSURE) help file parser ends predictably at "<END>" (no extra blank lines)
# TODO: (ORGANIZE) Remove redundant file explorer code
# TODO: (WISH) make help loading the documentation happen only once and only when needed (static and lazy)

from PySide6 import QtCore, QtWidgets, QtGui
from sys import exit
from difflib import SequenceMatcher

from driver_fs_functions import *
from graphical_interface import MainProgramWindow
from item_selection_interface import ItemSelectionInterface
from menu_interface_base import GeneralInterface


HELP_FILENAME = 'help'                          # The filename of the program's help documentation (this must be kept in a specific format)
HELP_TERMINATOR = '<END>'                       # The string that ends help documentation parsing
ICON_FILENAME = 'icon.png'                      # The filename of the program's icon (when GUI)
HELP_QUERY_ACCEPTANCE = 0.7                     # Level of tolerance (0.0 to 1.0) while searching help documentation



## --------------------------------------------------------------------- ##
## ------------------------- Interface Objects ------------------------- ##
## --------------------------------------------------------------------- ##


# The following is the main menu for the program. It handles loading the needed courses,
# configuring scheduling parameters, generating the schedule, etc.
class MainMenuInterface(GeneralInterface):
    
    def __init__(self):
        self.name = 'MAIN MENU'
        self._commands = {}
        
        # e: explorer
        # i: immediate
        
        # MERINO: added command aliases
        # Add commands to the command dictionary
        self.add_command(list_available_commands_command,       '', 'commands', 'list-commands')
        self.add_command(load_needed_courses_command,           'load', 'needed', 'set')
        self.add_command(explore_needed_courses_command,         'load-e', 'needed-e', 'set-e')
        self.add_command(load_destination_directory_command,    'destination', 'dest', 'to', 'directory')
        self.add_command(explore_destination_directory_command, 'destination-e', 'dest-e', 'to-e', 'directory-e')
        self.add_command(set_hours_per_semster_command,         'hours', 'set-hours', 'per', 'count', 'set-count')
        self.add_command(select_export_command,                 'as', 'exports', 'set-exports', 'type', 'types', 'set-types',)
        self.add_command(list_parameters_command,               'courses', 'list-courses', 'parameters', 'list-parameters', 'arguments', 'list-arguments', 'args')
        self.add_command(generate_schedule_command,             'schedule', 'generate', 'done', 'save')
        self.add_command(set_gui_interface_command,             'gui')
        self.add_command(set_cli_interface_command,             'cli', 'lui')
        self.add_command(gui_interface_immediate_command,       'gui-i', 'window', 'graphical', 'graphics')
        self.add_command(help_command,                          'help', 'info')
        self.add_command(fetch_catalog_command,                 'fetch', 'update', 'catalog')
        self.add_command(quit_command,                          'quit', 'exit')
    
    
    def report_invalid_command_error(self, controller, command_string):
        '''Report when an unsupported command is entered (this may be overridden to provide relevant tools/help).'''
        controller.output_error('Sorry, no command matching "{0}" was found. Use "commands" or "help" to find the command you are looking for.'.format(command_string))
        

# The following is the help menu for the program. It handles presenting and searching for program documentation. It loads
# the contents of the help file upon being intialized. It stores the articles' headers, keywords (for searching), and content.
# Searching does accept slightly misspelled words.

class HelpMenu(GeneralInterface):

    # TODO: add code comments
    
    def __init__(self):
        self.name = 'HELP MENU'
        self.headers = []           # List of help article headers (for displaying the title of the article)
        self.keywords = []          # List of help article keywords (what is used to search for articles)
        self.articles = []          # List of article contents
        self.article_count = 0      # The number of articles loaded into the object
        
        # Open the help file and extract the headers, keywords, and articles
        # The help file is expected to have the following format (breaks are indicated by \n escapes):
        # Header \n Keywords seperated by white spaces \n Article contents \n Line seperator (for easier editing) \n ... \n <END>
        
        with open(HELP_FILENAME, 'r') as documentation:
            header = documentation.readline()
            while HELP_TERMINATOR not in header and header:
                self.headers.append(header[:-1])
                self.keywords.append(documentation.readline().split())
                self.articles.append(documentation.readline())
                documentation.readline()    # Consume separation line
                self.article_count += 1
                header = documentation.readline()
    
    # MERINO: removed deconstruct method
    
    def parse_input(self, controller, input):
        '''Handle input on behalf of the program.'''
        
        # TODO: make exit and all command better (make sense).
        if 'exit' in input or 'quit' in input:
            # Exit the help menu
            controller.pop_interface(self)
        
        elif 'all' in input:
            # List all articles
            for article_index in range(self.article_count):
                controller.output(self.headers[article_index])
                controller.output(self.articles[article_index])
        else:
            # The input did not match a command (search for an article)
            controller.output('Now searching for "{0}"...'.format(input))
            possible_article_indices = self._search_for_keywords(input)
            self.list_articles(controller, possible_article_indices)
    
    
    def _search_for_keywords(self, query):
        '''Get a list of article indices that match the passed query.'''
        
        # TODO: add comments/documentation
        
        possible_article_indices = []
        matcher = SequenceMatcher()
        query_words = set(query.split())
        
        # Helper function for determining if the article matches the query (close enough, anyhow)
        def article_matches_query(keyword):
            matcher.set_seq1(keyword)
            for query_word in query_words:
                matcher.set_seq2(query_word)
                if matcher.ratio() >= HELP_QUERY_ACCEPTANCE:
                    return True
            return False
        
        for article_index in range(self.article_count):
            for keyword in self.keywords[article_index]:
                if article_matches_query(keyword):
                    possible_article_indices.append(article_index)
                    break
        
        return possible_article_indices
    
    
    def list_articles(self, controller, possible_article_indices):
        '''List the articles from the passed list of indices (as the result of a search).'''
        
        # TODO: add comments/documentation
        
        possible_articles_count = len(possible_article_indices)
        
        if possible_articles_count == 0:
            controller.output('Sorry, no matches found. Please try using different keywords.\n')
        elif possible_articles_count == 1:
            controller.output('This might help:\n')
            controller.output(self.headers[possible_article_indices[0]])
            controller.output(self.articles[possible_article_indices[0]])
        else:
            # TODO: We may introduce an article selection menu here
                    
            controller.output('These might help:\n')
            for article_index in possible_article_indices:
                controller.output(self.headers[article_index])
                controller.output(self.articles[article_index])
    
# End of HelpMenu definition


# This a special menu that, once pushed, presents the user with a graphical user interface for interfacing with
# the process. This will block execution until the GUI is closed, which will trigger the menu to pop itself. The
# menu has no real value in the CLI and cannot even be dismissed via input parsing.

class GraphicalUserMenuInterface(GeneralInterface):
    
    
    def __init__(self):
        self.name = 'GUI MENU'
    
    
    def was_pushed(self, controller):
        '''Method that is called upon the interface being pushed onto the interface stack.'''
        
        application = controller.get_graphical_application()    # Get the application object from the controller
        application.setWindowIcon(QtGui.QIcon(ICON_FILENAME))   # Set the window icon
        main_window = MainProgramWindow(controller)             # Create a new window for the application to present
        main_window.resize(800, 400)                            # Set the initial window size
        main_window.show()                                      # Present the window
        application.exec()                                      # Execute the application until closed (block execution)
        
        # At this point, the GUI has been closed and the program should resume normal execution
        # Since that menu has served it's purpose, it will be popped if still in the stack
        
        # Ensure the controller has an interface and that the current interface is indeed this menu
        # This check is required in case of future changes and when an error menu interrupts execution
        if controller.has_interface() and controller.get_current_interface() == self:
            controller.pop_interface(self)
    
        
    def deconstruct(self, controller):
        '''Destruction method that is called upon the interface being dismissed.'''
        # Disconnect program IO from graphics
        controller.set_output_listener(None)
        controller.set_warning_listener(None)
        
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
        self.add_command(attempt_error_resolve,         'reload', 'retry', 'start', 'restart')
        self.add_command(create_default_config_command, 'config')
        self.add_command(quit_command,                  'quit', 'exit', 'cancel')
        

## --------------------------------------------------------------------- ##
## ------------------------ Interface Callbacks ------------------------ ##
## --------------------------------------------------------------------- ##


def list_available_commands_command(controller, argument):
    '''Output the commands that may be entered.'''
    # MERINO: corrected commands
    controller.output('Here are the commands available:\ncommands, load, load-e, destination, destination-e, set-hours, set-exports, list-parameters, schedule, gui, cli, gui-i, help, quit')
    # TODO: maybe use a listing from help resourses or the main menu interface class.


def help_command(controller, argument):
    '''Push a help menu object onto the caller's stack and pass any arguments (if any) to the new menu as user input.'''
    controller.output('Welcome to the help menu. Type keywords to search for a help article.')
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
    # TODO: polish this a bit
    # TODO: combine this with explore_destination_directory_command
        
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
    # TODO: polish this a bit
    # TODO: combine this with explore_needed_courses_command
        
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
    # MERINO: corrected this line's call
    list_interface.set_selected(set(controller.get_export_type()))
    controller.push_interface(list_interface)
    
    controller.output('Please select from the following export types:') # Output the initial prompt
    list_interface.list_progress(controller)                            # Output the current selection


def list_parameters_command(controller, arguements):
    '''List the current scheduling parameters (destination directory, hours per semester, needed courses, etc.).'''
    if not arguements:
        controller.output('Scheduling Parameter:\n')
        controller.output('Destination: {0}'.format(controller.get_destination_directory()))
        controller.output('Hourse per semester: {0}'.format(controller.get_hours_per_semester()))
        
        courses_needed = controller.get_courses_needed()
        
        if courses_needed:
            controller.output('Courses:')
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
        # MERINO: fixed spelling
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


def generate_schedule_command(controller, filename):
    '''Ask the provided caller to generate a schedule with the passed filename.'''
    if filename:
        controller.generate_schedule(filename)
    else:
        controller.output_error('Please enter a filename.')


def quit_command(controller, arguements):
    '''Terminate the program.'''
    if not arguements:
        controller.clear_all_interfaces()          # Pop all interfaces in the controller's stack
        controller.output('Thank you. Goodbye.')   # Output goodbye message
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
    

## ----------- The following are more or less still in development (not in the current implementation) ----------- ##


def fetch_catalog_command(controller, argument):
    if argument:
        controller.fetch_catalog(argument)
    else:
        controller.fetch_catalog()
