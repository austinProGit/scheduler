# Thomas Merino
# 9/9/22
# CPSC 4175 Group Project

# NOTE: there needs to be a file called "config" in the same directory as this file. The config file stores the name of the course info filename. This is what's passed into the parser as input.

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
        pass
        
    def configure_course_info(self, container):
        pass
        
    def configure_courses_needed(self, container):
        pass
        
    def configure_courses_per_semester(self, number_of_courses):
        pass
        
    def generate_schedule(self, filename):
        pass

## --------------------------------------------------------------------- ##
## ---------------------- Smart Planner Interface ---------------------- ##
## --------------------------------------------------------------------- ##

# This exception is used when an issue with interface presentation is encountered.
# Handling one should only be done for the sake of saving important data.
class InterfaceProcedureError(Exception):
    pass
    

# The following class is used as the controller for the program and provides the
# functions for interfacing with the user.

class SmartPlannerController:

    ## ----------- Setup ----------- ##
    
    def __init__(self):
        self.setup()
    
    def setup(self):
        '''Perform setup for scheduling, general configuration, and user interface'''
        
        # Initialize instance variables
        self._interface_stack = [MainMenuInterface()]
        self._scheduler = Scheduler()
        
        # Load the course info file
        self.load_course_info()
    
    def load_course_info(self):
        '''Load the course info file and use it to configure the scheduler. If the process fails, an error menu is pushed onto the interface stack.'''
        # Create a variable to track where the course info file should be
        course_info_filename = ''
        
        # Attempt to load the course info data
        try:
            # Get the config file (the first line of which should be the course info filename)
            with open('config') as configuration_file:
                course_info_filename = configuration_file.read()
                course_info_container = get_course_info(course_info_filename)
                
        except FileNotFoundError:
            # Course info could not be found (report to the user and enter the error menu)
            self.output_error('Invalid course catalog file. Please rename the catalog to {} and reload the catalog (enter "reload").'.format(course_info_filename))
            self.enter_error_menu()
            
        except NonDAGCourseInfoError:
            # The catalog was/is invalid (report to the user and enter the error menu)
            output_error('Course catalog contains invalid data. Please correct all issues and reload the catalog (enter "reload").')
            self.enter_error_menu()
            
        
    ## ----------- User interface methods ----------- ##
    
    def output(self, message):
        '''Output a message to the user.'''
        print(message)
        
    def output_error(self, message):
        '''Output an error message to the user.'''
        self.output('ERROR: {0}'.format(message))
        
    def get_input(self):
        '''Get input text from the user with the current interface's/menu's name in the prompt.'''
        current_interface = self.get_current_interface()
        return input('{0}: '.format(current_interface.name))
    
    # NOTE: the following is not used in the current version--I am adding it just in case we want a
    # value-by-value data entry interface. Also, it would more readable if recursion were used. Let
    # me know if we should change the implementation.
    def get_input_integer(self):
        '''Get an integer input from the user with the current interface's/menu's name in the prompt. This will loop until a valid number is entered.'''
        
        got_valid_input = False
        user_number = -1
        
        # Attempt to get an integer input
        try:
            user_number = int(self.get_input())     # Get user input and attempt to construct an integer from it
            got_valid_input = True                  # If the input converted successfully, mark input status as successful
        except ValueError:
            pass                                    # Continue if the input was invalid (to get a new input)
        
        # If the input was not valid, loop until a valid number is entered
        while not got_valid_input:
            output_error('That is not a valid input. Please try again.')
            # Attempt to get an integer input
            try:
                user_number = int(self.get_input()) # Get another input and attempt to construct an integer from it
                got_valid_input = True              # If the input converted successfully, mark input status as successful
            except ValueError:
                pass
            
        return user_number
            
    ## ----------- Interface/menu control ----------- ##
    
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
    
    def enter_error_menu(self):
        '''Push an error menu onto the menu stack so the user can correct errors before reloading.'''
        self.push_interface(ErrorMenu())
    
                
    ## ----------- Scheduling procedure configuration ----------- ##
    
    def load_courses_needed(self, filename):
        '''Load the courses that must be scheduled into the scheduler (from a filename).'''
        try:
            courses_needed_list = self._scheduler.configure_courses_needed(filename)    # Get the needed courses from the file
            self._scheduler.configure_courses_needed(courses_needed_list)               # Load the course list into the scheduler
        except FileNotFoundError:
            output_error('Sorry, {0} could not be found.'.format(filename))             # Report if the file was not found
    
    def configure_courses_per_semester(self, number_of_courses):
        '''Set the number of courses that are scheduled per semester.'''
        self._scheduler.configure_courses_per_semester(number_of_courses)
        
    def generate_schedule(self, filename):
        '''Generate the schedule with a given filename.'''
        self.output('Generating schedule...')
        self._scheduler.generate_schedule(filename)
        self.output('Schedule complete.')
        
    def run_top_interface(self):
        '''Gets input from the user and passed that input into the presenting interface/menu. The method then returns whether there are any interfaces left presenting. In the case there aren't any, the method should not be called again. This may act as the program's entire loop.'''
        user_input = self.get_input()                       # Get input from the user
        current_interface = self.get_current_interface()    # Get the current interface/menu
        current_interface.parse_input(self, user_input)     # Pass the user's input to the current menu
        return len(self._interface_stack) != 0              # return whether there are still any interfaces presenting

    
# Interfaces are expected to have a parse_input method that takes as input the controller and the user input
# and a deconstruct method that takes as input the controller. It is also expected to have a "name" property.
   
# The following is base for interface objects.

class GeneralInterface:
                    
    def add_command(self, callback, *command_names):
        '''Adds a command (the provided callback) to the menu. The method add the command to the _commands dictionary using the names provided after the callback.'''
        for command_name in command_names:
            self._commands[command_name] = callback
            
    def deconstruct(self, caller):
        '''Destruction method that is called upon the interface being dismissed.'''
        pass


# The following is the main menu for the program. It handles loading the needed courses,
# configuring scheduling parameters, and generating the schedule.

class MainMenuInterface(GeneralInterface):
    
    def __init__(self):
        self.name = 'MAIN MENU'
        self._commands = {}
        
        # Add commands to the command listing
        self.add_command(load_needed_courses_command, 'load', 'needed', 'set')
        self.add_command(list_available_commands_command, 'commands', 'list')
        self.add_command(set_courses_per_semster_command, 'courses', 'per', 'count')
        self.add_command(generate_schedule_command, 'schedule', 'generate', 'done', 'save')
        self.add_command(help_command, 'help')
        self.add_command(quit_command, 'quit', 'exit')
        
        
    def parse_input(self, caller, user_input):
        '''Handle input on behalf of the passed caller (controller).'''
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
            command(caller, argument)                           # Invoke the command with the caller and passed arguments
        else:
            # Report invalid input
            caller.output_error('Sorry, no command matching "{0}" was found. Use "commands" or "help" to find the command you are looking for.'.format(command_key))
        
def list_available_commands_command(caller, argument):
    '''Output the commands that may be entered.'''
    caller.output('Here are the commands available:')
    # TODO: use a listing from help resourses.


def load_needed_courses_command(caller, filename):
    '''Ask the provided caller to load needed courses via the provided filename.'''
    if filename != '':
        caller.load_courses_needed(filename)
    else:
        caller.output_error('Please enter a filename.')

def set_courses_per_semster_command(caller, argument):
    '''Ask the provided caller to set the number of courses per semester.'''
    try:
        number = int(argument)                           # Attempt to cast the input to an integer
        caller.configure_courses_per_semester(number)    # If successful, set the number of
    except(ValueError):
        # The argument was not valid (report to the user)
        caller.output_error('Sorry, that is not a valid input (please use a number).')
    
def generate_schedule_command(caller, filename):
    '''Ask the provided caller to generate a schedule.'''
    if filename != "":
        caller.generate_schedule(filename)
    else:
        caller.output_error('Please enter a filename.')

def help_command(caller, argument):
    '''Push a help menu object onto the caller's stack and pass any arguments (if any) to the new menu as user input.'''
    caller.output('Welcome to the help menu.')              # Welcome the user to the menu
    new_help_interface = HelpMenu()                         # Initialize the new interface
    caller.push_interface(new_help_interface)               # Push the new interface onto the controller's stack
    
    # Check if there was any argument(s) provided
    if argument != "":
        new_help_interface.parse_input(caller, argument)    # Have the new menu process the arguements
        
def quit_command(caller, argument):
    '''Terminate the program.'''
    while caller.has_interface():
        caller.pop_interface(caller.get_current_interface())     # Pop all interfaces in the controller's stack
    caller.output('Thank you. Goodbye.')                         # Output goodbye message
    

# The following is the help menu for the program. It handles presenting and searching for
# program documentation.

class HelpMenu(GeneralInterface):

    # TODO: implement help resourses into the menu.
    
    def __init__(self):
        self.name = 'HELP MENU'
        
    def parse_input(self, caller, input):
        '''Handle input on behalf of the passed caller (controller).'''
        
        # TODO: make some searching behavior for input parsing.
        if 'exit' in input or 'quit' in input:
            caller.pop_interface(self)
        else:
            caller.output('Now searching for "{0}"...'.format(input))
    

# The following is the error menu for the program. It handles illegal program states and
# lets reload configuration data.

class ErrorMenu(GeneralInterface):
    
    def __init__(self):
        self.name = 'ERROR MENU'
        
    def parse_input(self, caller, input):
        '''Handle input on behalf of the passed caller (controller).'''
        # TODO: give this more interface.
        
        caller.output('Reloading configuration files...')
        caller.pop_interface(self)
        caller.load_course_info()


# Testing:
if __name__ == "__main__":
    s = SmartPlannerController()
    while s.run_top_interface(): pass
