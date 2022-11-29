# Thomas Merino
# 9/21/22
# CPSC 4175 Group Project

from menu_interface_base import GeneralInterface

# The following is the main menu for the program. It handles loading the needed courses,
# configuring scheduling parameters, and generating the schedule.

class ItemSelectionInterface(GeneralInterface):
    
    
    def __init__(self, options_list, modification_callback, completion_callback, cancellation_callback):
        self.name = 'SELECTION (ADD)'
        self._commands = {}
        
        # Save callback references
        self._modification_callback = modification_callback
        self._completion_callback = completion_callback
        self._cancellation_callback = cancellation_callback
        
        # Create editing state properties
        self._options_list = options_list # Reference to the list (this should not be modified)
        self._selected_options_set = set() # This is a set of the indices used/selected
        self._options_count = len(options_list) # The number of options
        self._is_adding = True # Create a variable to track whether the interface is in adding mode
        self._is_completed = False # Create a variable to track whether the interface has finished processing the input
        
        # Add commands (these work in conjuction with entering numbers)
        
        self.add_command(self._list_commands, '', 'list-commands', 'commands')
        self.add_command(self._switch_to_adding, 'add', 'append', 'include', '+')
        self.add_command(self._switch_to_removal, 'remove', 'subtract', 'exclude', 'rm', '-')
        self.add_command(self.list_progress, 'list-selection', 'progress', 'list')
        self.add_command(self._complete, 'done', 'complete', 'finish')
        self.add_command(self._cancel, 'cancel', 'exit', 'quit')
    
            
    def was_pushed(self, controller):
        '''Method that is called upon the interface being pushed onto the interface stack.'''
        self._is_adding = True
        self._is_completed = False
    
    
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
        controller.output('add, remove, commands, list, done, cancel')
        
    
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
            # Determine if the index is selected (print a leading "+" if so)
            selected_indicator = '+' if index in self._selected_options_set else ' '
            controller.output('{0} {1}: {2}'.format(selected_indicator, (index + 1), self._options_list[index]))
    
    
    def _process_item(self, controller, index):
        '''Preform addition or removal (depending on the current mode) of the item at the passed index (not label number).'''
        
        if self._is_adding:
            # Determine if the entered index is already selected, too large, or valid
            if index in self._selected_options_set:
                controller.output_error('That item is already selected.')
            elif index < 0 or self._options_count <= index:
                controller.output_error('That is not a valid index. Please enter a number between or equal to {0} and {1}'.format(1, self._options_count))
            else:
                self._selected_options_set.add(index)
                self._modification_callback(controller, self._selected_options_set)
        else:
            # Determine if the entered index is even selected
            if index not in self._selected_options_set:
                
                controller.output_error('That item is not selected (to add an item, switch to add mode with the "add" command),')
            else:
                self._selected_options_set.remove(index)
                self._modification_callback(controller, self._selected_options_set)
    
    
    def set_selected(self, selected_options_set):
        '''Set the menu's selected items.'''
        self._selected_options_set = selected_options_set.copy()
    
    def parse_input(self, controller, user_input):
        '''Handle input on behalf of the program.'''
        command_key = user_input.strip() # Strip the input
        
        # Determine if the input is a valid command (is so, execute it, and if not, attempt to cast it to an integer)
        if command_key in self._commands:
            command = self._commands[command_key] # Get the command (function) to execute
            command(controller) # Invoke the command on self (implicitly)
        else:
            if user_input.isdigit():
                number = int(user_input) # Attempt to cast the input to an integer
                self._process_item(controller, number - 1) # Process the index (which is the number minus 1)
            else:
                # The input was not valid (report to the user)
                controller.output_error('Sorry, that is not a valid input. Please use a number or a valid command (enter "commands" to list valid commands).')
    
# End of ItemSelectionInterface definition
