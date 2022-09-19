# Thomas Merino
# 9/19/22
# CPSC 4175 Group Project

# TODO: Maybe make the name of the help file included in config
# TODO: Make importing PySide components optional in case the user does not have them installed
# TODO: Ensure help file parser ends predictably (no extra blank lines)
# TODO: Create a file browser sub-mod

from PySide6 import QtCore, QtWidgets, QtGui
from sys import exit
from os import path
from pathlib import Path

from graphical_interface import MainProgramWindow

HELP_FILENAME = 'help'
HELP_TERMINATOR = '<END>'
ICON_FILENAME = 'icon.png'                      # The filename of the program's icon (when GUI)


# TODO: Add these to a constants file so they are not defined in both driver and here
PATH_TO_GRADUATION_EXPORT_TYPE = 0x00
PLAIN_TEXT_EXPORT_TYPE = 0x01

# The hope here is to move all command line interface management to a single object that the driving controller presents:

#class CommandLineController:
#
#    def __init__(self):
#        self._interface_stack = [MainMenuInterface()]

# Interfaces are expected to have a parse_input method that takes as input the controller and the user input and a deconstruct method that takes as input the controller. It is also expected to have a "name" property.

# TODO: Make the command dictionary statically set (may be a better approach).

# The following is base for interface objects.

class GeneralInterface:
    
    def add_command(self, callback, *command_names):
        '''Adds a command (the provided callback) to the menu. The method add the command to the _commands dictionary using the names provided after the callback.'''
        for command_name in command_names:
            self._commands[command_name] = callback
        
    def was_pushed(self, controller):
        '''Method that is called upon the interface being pushed onto the interface stack.'''
        pass
    
    def deconstruct(self, controller):
        '''Destruction method that is called upon the interface being dismissed.'''
        pass
    
    def report_invalid_command_error(self, controller, command_string):
        '''Report when an unsupported command is entered (this may be overridden to provide relevant tools/help).'''
        controller.output_error('Sorry, no command matching "{0}" was found.'.format(command_string))
    
    def parse_input(self, controller, user_input):
        '''Handle input on behalf of the program.'''
        input_string = user_input.strip()                       # Strip the input
        first_space_index = input_string.find(' ')              # Get the position of the first space in the input string
        command_key = input_string                              # Set the key (string) for the command to the entire input by default
        argument = ''                                           # Set the command arguments to an empty string by default
        
        # Check if the input has multiple words
        if first_space_index != -1:
            command_key = input_string[0:first_space_index]     # Set the command key to just the first word
            argument = input_string[first_space_index:].strip() # Set the arguements to the rest (without extra spaces)
        
        # Check if the command key is valid
        if command_key in self._commands:
            command = self._commands[command_key]               # Get the command (function) to execute
            command(controller, argument)                       # Invoke the command with the controller and passed arguments
        else:
            # Report invalid input
            self.report_invalid_command_error(controller, command_key)


## --------------------------------------------------------------------- ##
## ------------------------- Interface Objects ------------------------- ##
## --------------------------------------------------------------------- ##


# The following is the main menu for the program. It handles loading the needed courses,
# configuring scheduling parameters, and generating the schedule.

class MainMenuInterface(GeneralInterface):
    
    def __init__(self):
        self.name = 'MAIN MENU'
        self._commands = {}
        
        # Add commands to the command listing
        self.add_command(list_available_commands_command, '', 'commands', 'list')
        self.add_command(load_needed_courses_command, 'load', 'needed', 'set')
        self.add_command(browse_need_courses_command, 'browse', 'browser', 'load-b', 'needed-b', 'set-b')
        self.add_command(load_destination_directory_command, 'destination', 'dest', 'to', 'directory')
        self.add_command(browse_destination_directory_command, 'destination-b', 'dest-b', 'to-b', 'directory-b')
        self.add_command(set_hours_per_semster_command, 'hours', 'per', 'count')
        self.add_command(select_export_command, 'export', 'as', 'type', 'types')
        self.add_command(list_parameters_command, 'status', 'parameters', 'stat', 'info')
        self.add_command(generate_schedule_command, 'schedule', 'generate', 'done', 'save')
        self.add_command(set_gui_interface_command, 'gui')
        self.add_command(set_cli_interface_command, 'lui', 'cli')
        self.add_command(gui_interface_immediate_command, 'gui-i', 'window', 'graphical')
        self.add_command(help_command, 'help')
        self.add_command(quit_command, 'quit', 'exit')
        
    def report_invalid_command_error(self, controller, command_string):
        '''Report when an unsupported command is entered (this may be overridden to provide relevant tools/help).'''
        controller.output_error('Sorry, no command matching "{0}" was found. Use "commands" or "help" to find the command you are looking for.'.format(command_string))
        
# The following is the main menu for the program. It handles loading the needed courses,
# configuring scheduling parameters, and generating the schedule.

class ItemSelectionInterface(GeneralInterface):
    
    # TODO: determine and then clarify the purpose of callback return values
    
    def __init__(self, options_list, modification_callback, completion_callback, cancellation_callback):
        self.name = 'SELECTION (ADD)'
        self._commands = {}
        
        # Save callback references
        self._modification_callback = modification_callback
        self._completion_callback = completion_callback
        self._cancellation_callback = cancellation_callback
        
        # Create editing state properties
        self._options_list = options_list          # Reference to the list (this should not be modified)
        self._selected_options_set = set()         # This is a set of the indices used/selected
        self._options_count = len(options_list)    # The number of options
        self._is_adding = True                     # Create a variable to track whether the interface is in adding mode
        self._is_completed = False                 # Create a variable to track whether the interface has finished processing the input
        
        # Add commands (these work in conjuction with entering numbers)
        self.add_command(self._switch_to_adding, 'add', 'append', 'include', '+')
        self.add_command(self._switch_to_removal, 'remove', 'subtract', 'exclude', 'rm', '-')
        self.add_command(self._list_commands, 'commands')
        self.add_command(self.list_progress, '', 'list', 'progress')
        self.add_command(self._complete, 'done', 'complete', 'finish')
        self.add_command(self._cancel, 'cancel', 'exit', 'quit')
    
    def deconstruct(self, controller):
        '''Destruction method that is called upon the interface being dismissed.'''
        if self._is_completed:
            # If the interface had finished, execute the completion callback
            self._completion_callback(controller, self._selected_options_set)
        else:
            # If the interface was interupted, execute the cancellation callback
            self._cancellation_callback(controller, self._selected_options_set)
    
    def _switch_to_adding(self, controller):
        '''Change the editing mode to adding items to the selection.'''
        if not self._is_adding:
            controller.output('Switching to adding mode.')
            self._is_adding = True
            self.name = 'SELECTION (ADD)'
        else:
            controller.output_error('Already on adding mode.')
    
    def _switch_to_removal(self, controller):
        '''Change the editing mode to removing items from the selection.'''
        if self._is_adding:
            controller.output('Switching to removal mode.')
            self._is_adding = False
            self.name = 'SELECTION (REMOVE)'
        else:
            controller.output_error('Already on removal mode.')
    
    def _list_commands(self, controller):
        '''List the available commands.'''
        # TODO: produce a more in-depth output
        controller.output('add, remove, commands, list, cancel')
        
    def _complete(self, controller):
        '''Finish processing the selection (dismiss the interface and attempt to execute the completion callback).'''
        self._is_completed = True
        controller.pop_interface(self)
    
    def _cancel(self, controller):
        '''Finish processing the selection (dismiss the interface and execute the cancellation callback).'''
        controller.pop_interface(self)
    
    def list_progress(self, controller):
        '''List the items and whether they are selected or not.'''
        controller.output('Items:')
        for index in range(self._options_count):
            selected_indicator = '+' if index in self._selected_options_set else ' '
            controller.output('{0} {1}: {2}'.format(selected_indicator, (index + 1), self._options_list[index]))
    
    def _process_item(self, controller, index):
        '''Preform addition or removal (depending on the current mode) of the item at the passed index (not label number).'''
        if self._is_adding:
            if index in self._selected_options_set:
                controller.output_error('That item is already selected.')
            elif index < 0 or self._options_count <= index:
                controller.output_error('That is not a valid index. Please enter a number between or equal to {0} and {1}'.format(1, self._options_count))
            else:
                self._selected_options_set.add(index)
                self._modification_callback(controller, self._selected_options_set)
        else:
            if index not in self._selected_options_set:
                controller.output_error('That is item is not selected (to add an item, switch to add mode with the "add" command),')
            else:
                self._selected_options_set.remove(index)
                self._modification_callback(controller, self._selected_options_set)
    
    def set_selected(self, selected_options_set):
        self._selected_options_set = selected_options_set.copy()
    
    def parse_input(self, controller, user_input):
        '''Handle input on behalf of the program.'''
        command_key = user_input.strip()                        # Strip the input
        
        # Determine if the input is a valid command (is so, execute it, and if not, attempt to cast it to an integer)
        if command_key in self._commands:
            command = self._commands[command_key]               # Get the command (function) to execute
            command(controller)                                 # Invoke the command on self (implicitly)
        else:
            try:
                number = int(user_input)                        # Attempt to cast the input to an integer
                self._process_item(controller, number - 1)      # Process the index (which is the number minus 1)
            except ValueError:
                # The input was not valid (report to the user)
                controller.output_error('Sorry, that is not a valid input. Please use a number or a valid command (enter "commands" to list valid commands).')
    

# The following is the help menu for the program. It handles presenting and searching for
# program documentation.

class HelpMenu(GeneralInterface):

    # TODO: make help loading the documentation happen only once and only when needed (static and lazy)
    # TODO: add code comments
    
    def __init__(self):
        self.name = 'HELP MENU'
        self.headers = []
        self.keywords = []
        self.articles = []
        self.article_count = 0
        
        with open(HELP_FILENAME, 'r') as documentation:
            header = documentation.readline()
            while HELP_TERMINATOR not in header and header:
                self.headers.append(header[:-1])
                self.keywords.append(documentation.readline().split())
                self.articles.append(documentation.readline())
                documentation.readline()    # Consume separation line
                self.article_count += 1
                header = documentation.readline()
            
    def deconstruct(self, controller):
        '''Destruction method that is called upon the interface being dismissed.'''
        # TODO: if any files are openned, close them here
        pass
        
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
            controller.output('Now searching for "{0}"...'.format(input))
            self._search_for_keywords(controller, input)
            
    def _search_for_keywords(self, controller, query):
        possible_article_indices = []
        for article_index in range(self.article_count):
            for keyword in self.keywords[article_index]:
                if keyword in query:
                    possible_article_indices.append(article_index)
                    break
        possible_articles_count = len(possible_article_indices)
        if possible_articles_count == 0:
            controller.output('Sorry, no matches found. Please try using different keywords.\n')
        elif possible_articles_count == 1:
            controller.output('This might help:\n')
            controller.output(self.headers[possible_article_indices[0]])
            controller.output(self.articles[possible_article_indices[0]])
        else:
            # TODO: We may introduce an article selection menu here
                    
            controller.output('This might help:\n')
            for article_index in possible_article_indices:
                controller.output(self.headers[article_index])
                controller.output(self.articles[article_index])
    

# The following is the error menu for the program. It handles illegal program states and
# lets reload configuration data.

class ErrorMenu(GeneralInterface):
    
    def __init__(self):
        self.name = 'ERROR MENU'
        self._commands = {}
        
        self.add_command(attempt_error_resolve, 'reload', 'retry', 'start')
        self.add_command(create_default_config_command, 'config')
        self.add_command(quit_command, 'quit', 'exit', 'cancel')
        

class GraphicalUserInterfaceMenu(GeneralInterface):

    def was_pushed(self, controller):
        application = QtWidgets.QApplication.instance()
        if not application:
            application = QtWidgets.QApplication([])
        application.setWindowIcon(QtGui.QIcon(ICON_FILENAME))
        main_window = MainProgramWindow(controller)
        main_window.resize(450, 300)
        main_window.show()
        application.exec()
        if controller.has_interface() and controller.get_current_interface() == self:
            controller.pop_interface(self)
    
        
    def deconstruct(self, controller):
        '''Destruction method that is called upon the interface being dismissed.'''
        application = QtWidgets.QApplication.instance()
        application.exit(0)


## --------------------------------------------------------------------- ##
## ------------------------ Interface Callbacks ------------------------ ##
## --------------------------------------------------------------------- ##


def list_available_commands_command(controller, argument):
    '''Output the commands that may be entered.'''
    controller.output('Here are the commands available:')
    # TODO: use a listing from help resourses.

def load_helper(controller, is_directory, filename):
    load_type_description = 'directory' if is_directory else 'file'
    if filename == '':
        controller.output_error('Please enter the {0}\'s path.'.format(load_type_description))
    else:
        file_path = filename
        
        if filename[0] == '~':
            file_path = str(Path.home()) + filename[1:]
        
        if path.exists(file_path):
            if is_directory:
                controller.configure_destination_directory(file_path)
            else:
                controller.load_courses_needed(file_path)
        else:
            controller.output_error('Sorry, that {0} could not be found (try entering an absolute path).'.format(load_type_description))

def load_needed_courses_command(controller, filename):
    '''Ask the provided caller to load needed courses via the provided filename.'''
    load_helper(controller, False, filename)
    

def load_destination_directory_command(controller, directory):
    '''Ask the provided caller to change the destination directory to the provided directory (the directory's existence i checked first).'''
    load_helper(controller, True, directory)

def set_hours_per_semster_command(controller, argument):
    '''Ask the provided caller to set the number of hours per semester.'''
    try:
        number = int(argument)                              # Attempt to cast the input to an integer
        controller.configure_hours_per_semester(number)     # If successful, set the number of
    except ValueError:
        # The argument was not valid (report to the user)
        controller.output_error('Sorry, that is not a valid input (please use a number).')
    
def generate_schedule_command(controller, filename):
    '''Ask the provided caller to generate a schedule.'''
    if filename != '':
        controller.generate_schedule(filename)
    else:
        controller.output_error('Please enter a filename.')

def help_command(controller, argument):
    '''Push a help menu object onto the caller's stack and pass any arguments (if any) to the new menu as user input.'''
    controller.output('Welcome to the help menu.')              # Welcome the user to the menu
    new_help_interface = HelpMenu()                             # Initialize the new interface
    controller.push_interface(new_help_interface)               # Push the new interface onto the controller's stack
    
    # Check if there was any argument(s) provided
    if argument != '':
        new_help_interface.parse_input(controller, argument)    # Have the new menu process the arguements

def gui_interface_immediate_command(controller, arguements):
    '''Enter a GUI interface (this does not change the program config, though).'''
    if arguements == '':
        controller.push_interface(GraphicalUserInterfaceMenu())
    else:
        controller.output_error('Arguments are not supported for this command.')

def set_gui_interface_command(controller, arguements):
    '''Change the user interface mode to GUI (this does not reload the interface, though).'''
    if arguements == '':
        controller.configure_user_interface_mode(is_graphical=True)
        controller.output('Deafault UI mode set to graphical (enter gui-i to enter immediately).')
    else:
        controller.output_error('Arguments are not supported for this command.')

def set_cli_interface_command(controller, arguements):
    '''Change the user interface mode to CLI (this does not reload the interface, though).'''
    if arguements == '':
        controller.configure_user_interface_mode(is_graphical=False)
        controller.output('Default UI mode set to commandline.')
    else:
        controller.output_error('Arguments are not supported for this command.')

def quit_command(controller, arguements):
    '''Terminate the program.'''
    if arguements == '':
        controller.clear_all_interfaces()          # Pop all interfaces in the controller's stack
        controller.output('Thank you. Goodbye.')   # Output goodbye message
    else:
        controller.output_error('Arguments are not supported for this command.')

def list_parameters_command(controller, arguements):
    '''List the current scheduling parameters (destination directory, hours per semester, etc.).'''
    if arguements == '':
        controller.output('Scheduling Parameter:\n')
        controller.output('Destination: {0}\n'.format(controller.get_destination_directory()))
        controller.output('Hourse per semester: {0}\n'.format(controller.get_hours_per_semester()))
    else:
        controller.output_error('Arguments are not supported for this command.')

def attempt_error_resolve(controller, argument):
    '''Attempt to reload the course info data and pop the top menu (expected to be an error menu).'''
    
    # TODO: this is broken when encountering error in gui-i
    if argument == '':
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
    
def create_default_config_command(controller, argument):
    '''Command to create a default config file for the program.'''
    controller.create_default_config_file(argument.strip())



## ----------- The following are more or less for testing ----------- ##

def browse_need_courses_command(controller, argument):
    '''Command to create a new QT application for the purpose of loading the needed courses file.'''
    # TODO: polish this (probably not in final version)
    # TODO: acknowledge arg.
    
    # This gets the application (launches if there is none) and uses it to present a file selection dialog
    application = QtWidgets.QApplication.instance()
    if not application:
        application = QtWidgets.QApplication([])
    file_loader_dialog = QtWidgets.QFileDialog()
    file_loader_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
    filename = None
    
    if file_loader_dialog.exec():
        filename = file_loader_dialog.selectedFiles()[0]
        load_needed_courses_command(controller, filename)
    if filename == None:
        controller.output('Load cancelled.')
        
    application.quit()
    
def browse_destination_directory_command(controller, argument):
    '''Command to create a new QT application for the purpose of setting the destination directory.'''
    # TODO: polish this (probably not in final version)
    # TODO: acknowledge arg.
    
    # This gets the application (launches if there is none) and uses it to present a file selection dialog
    application = QtWidgets.QApplication.instance()
    if not application:
        application = QtWidgets.QApplication([])
    file_loader_dialog = QtWidgets.QFileDialog()
    file_loader_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
    directory_name = None
    
    if file_loader_dialog.exec():
        directory_name = file_loader_dialog.selectedFiles()[0]
        load_destination_directory_command(controller, directory_name)
    if directory_name == None:
        controller.output('Load cancelled.')
        
    application.quit()

def select_export_command(controller, argument):

    # TODO: make this not so stupid
    
    available_export_types = ['Path to Graduation Excel', 'Plain txt']
    
    def modify(controler, export_types_selected):
        if len(export_types_selected) == 0:
            controller.output('WARNING: make sure you have at least one export mode selected.')
        
    def complete(controler, export_types_selected):
        # TODO: clean this up a bit (maybe use dictionaries)
        export_types = []
        
        if 0 in export_types_selected:
            export_types.append(PATH_TO_GRADUATION_EXPORT_TYPE)
                
        if 1 in export_types_selected:
            export_types.append(PLAIN_TEXT_EXPORT_TYPE)
            
        controller.set_export_types(export_types)
        controller.output('Export type(s) set.')
    
    def cancel(controler, export_types_selected):
        controller.output('Export type(s) selection cancelled...')
        
    currently_selected = set()
    if controller.is_using_export_type(PATH_TO_GRADUATION_EXPORT_TYPE):
        currently_selected.add(0)
        
    if controller.is_using_export_type(PLAIN_TEXT_EXPORT_TYPE):
        currently_selected.add(1)
        
    list_interface = ItemSelectionInterface(available_export_types, modify, complete, cancel)
    list_interface.set_selected(currently_selected)
    controller.push_interface(list_interface)
    
    controller.output('Please select from the following export types:')
    list_interface.list_progress(controller)

