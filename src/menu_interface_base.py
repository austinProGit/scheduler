# Thomas Merino
# 2/27/23
# CPSC 4175 Group Project

# TL;DR: Interfaces are expected to have a parse_input method that takes as input the controller and
# the user input and a deconstruct method that takes as input the controller. It is also expected
# to have a "name" property.

# The program utilizes menu objects that are feed the user's input via the parse_input method

# name: the string name of the menu. It is convention for it to be uppercase and end with the word "menu."
# _commands: a dictionary with string keys and ((controller, string) -> void) function values. This is only used
#            by the default implement of the parse_input method
# was_pushed(self, controller): the method that is called when a menu is pushed to the interface stack. This is
#                               where model-dependent state is set
# deconstruct(self, controller): the method called when the interface is popped. This is where clean up and saving
#                                should be done.
# parse_input(self, string): the method that processes input on behalf of the passed controller. The default implementation
#                            just looks for and executes functions from _commands, passing the extra input as the argumen.t
# _report_invalid_command_error: this is the default handler for invalid commands when using the default implementation of parse_input


# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable, Any
    from program_driver import SmartPlannerController
    InterfaceCommand = Callable[[SmartPlannerController, str], None]


# TODO: Maybe make the command dictionary statically set (may be a better approach).


# The following is the base class for interface objects.
class GeneralInterface:

    _commands: dict[str, InterfaceCommand]
    name: str = 'MENU'
    
    def add_command(self, callback: InterfaceCommand, *command_names: str) -> None:
        '''Adds a command (the provided callback) to the menu. The method add the command to the _commands dictionary using the names provided after the callback.'''
        command_name: str
        for command_name in command_names:
            self._commands[command_name] = callback
    
    
    def was_pushed(self, controller: SmartPlannerController) -> None:
        '''Method that is called upon the interface being pushed onto the interface stack.'''
        pass
    
    def deconstruct(self, controller: SmartPlannerController) -> None:
        '''Destruction method that is called upon the interface being dismissed.'''
        pass
    
    def parse_input(self, controller: SmartPlannerController, user_input: str) -> None:
        '''Handle input on behalf of the program.'''
        input_string: str = user_input.strip() # Strip the input
        first_space_index: int = input_string.find(' ') # Get the position of the first space in the input string
        command_key: str = input_string # Set the key (string) for the command to the entire input by default
        argument: str = '' # Set the command arguments to an empty string by default
        
        # Check if the input has multiple words
        if first_space_index != -1:
            command_key = input_string[0:first_space_index] # Set the command key to just the first word
            argument = input_string[first_space_index:].strip() # Set the arguements to the rest (without extra spaces)
        
        # Check if the command key is valid
        if command_key in self._commands:
            command: InterfaceCommand = self._commands[command_key] # Get the command (function) to execute
            command(controller, argument) # Invoke the command with the controller and passed arguments
        else:
            # Report invalid input
            self._report_invalid_command_error(controller, command_key)
    
    
    def _report_invalid_command_error(self, controller, command_string) -> None:
        '''Report when an unsupported command is entered (this may be overridden to provide relevant tools/help).'''
        controller.output_error('Sorry, no command matching "{0}" was found.'.format(command_string))
    
