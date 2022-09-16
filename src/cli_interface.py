# Thomas Merino
# 9/16/22
# CPSC 4175 Group Project

# TODO: Maybe make the name of the help file included in config
# TODO: Make importing PySide components optional in case the user does not have them installed
# TODO: Fix help file parser not ending predictably

from PySide6 import QtCore, QtWidgets, QtGui
from sys import exit

HELP_FILENAME = 'help'
HELP_TERMINATOR = '<END'

# Interfaces are expected to have a parse_input method that takes as input the controller and the user input and a deconstruct method that takes as input the controller. It is also expected to have a "name" property.

# TODO: Making the command dictionary statically set may be a better approach.

# The following is base for interface objects.

class GeneralInterface:
    
    def add_command(self, callback, *command_names):
        '''Adds a command (the provided callback) to the menu. The method add the command to the _commands dictionary using the names provided after the callback.'''
        for command_name in command_names:
            self._commands[command_name] = callback
        
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
        self.add_command(load_needed_courses_command, 'load', 'needed', 'set')
        self.add_command(browse_command, 'browse', 'browser')
        self.add_command(test_listing_command, 'testl')
        self.add_command(list_available_commands_command, '', 'commands', 'list')
        self.add_command(set_hours_per_semster_command, 'hours', 'per', 'count')
        self.add_command(generate_schedule_command, 'schedule', 'generate', 'done', 'save')
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
        self.add_command(self._switch_to_removal, 'remove', 'subtract', 'exclude', '-')
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
        controller.output('List:')
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
        
        # TODO: make exit command better (make sense).
        if 'exit' in input or 'quit' in input:
            controller.pop_interface(self)
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
        


## --------------------------------------------------------------------- ##
## ------------------------ Interface Callbacks ------------------------ ##
## --------------------------------------------------------------------- ##


def list_available_commands_command(controller, argument):
    '''Output the commands that may be entered.'''
    controller.output('Here are the commands available:')
    # TODO: use a listing from help resourses.


def load_needed_courses_command(controller, filename):
    '''Ask the provided caller to load needed courses via the provided filename.'''
    if filename != '':
        controller.load_courses_needed(filename)
    else:
        controller.output_error('Please enter a filename.')

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


def quit_command(controller, argument):
    '''Terminate the program.'''
    if argument == '':
        controller.clear_all_interfaces()          # Pop all interfaces in the controller's stack
        controller.output('Thank you. Goodbye.')   # Output goodbye message
    else:
        controller.output_error('Arguments are not supported for this command.')

def attempt_error_resolve(controller, argument):
    '''Attempt to reload the course info data and pop the top menu (expected to be an error menu).'''
    if argument == '':
        controller.output('Reloading configuration files...')
        controller.clear_all_interfaces()
        controller.push_interface(MainMenuInterface())
        controller.load_course_info()
    else:
        controller.output_error('Arguments are not supported for this command.')
        
def create_default_config_command(controller, argument):

    # TODO: TEST - this has not been tested
    
    catalog_name = argument.strip()
    if catalog_name == '':
        catalog_name = DEFAULT_CATALOG_NAME
    
    with open(CONFIG_FILENAME, 'w') as config_file:
        config_file.write(catalog_name + '\n')
        config_file.write('GUI: NO\n')

## ----------- The following are more or less for testing ----------- ##

def browse_command(controller, argument):
    '''Command to create a new QT application for the purpose '''
    # TODO: polish this (probably not in final version)
    
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
    

def test_listing_command(controller, argument):

    # NOTE: this is just a test
    l = ['1113', '1301', '1302', '4175', '1234', '4321']
    
    def modify(c, s):
        print('Modified to {0}'.format(s))
        
    def complete(c, s):
        print('Completed with {0}'.format(s))
    
    def cancel(c, s):
        print('Cancelled with {0}'.format(s))
        
    list_interface = ItemSelectionInterface(l, modify, complete, cancel)
    controller.push_interface(list_interface)
    
    controller.output('Please select from the following:')
    list_interface.list_progress(controller)

