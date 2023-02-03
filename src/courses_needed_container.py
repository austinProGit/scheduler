# Thomas Merino and Austin Lee
# 2/2/2023
# CPSC 4176 Project

import re
from menu_interface_base import GeneralInterface
from typing import final
from math import inf
import pickle
import os

# The following are for bit masking and selection update results
MODIFICATION = 0x00F
SELECTION = 0x001
DESELECTION = 0x002
TOGGLE = 0x002

RESULT = 0x0F0
CHANGED = 0x010
UNCHANGED = 0x020
CHILD_NOT_FOUND = 0x030
ILLEGAL = 0x040
NOT_SATISIFACTORY = 0x050
DUPLICATE = 0x060
GENERATION = 0x070

COLLATERAL = 0xF00
SINGLE = 0x000
ADDITIONAL_EFFECTS = 0x100
SUPERSEDED = 0x200
UNSTRUCTURED = 0x300


SETTING_DELIMITTER = '='
DEFAULT_PRIORITY = 100

# The following are used for ArgumentInputInterface for specifying input types
SUCCESS = 0x01
ILLEGAL_NIL = 0x02
ILLEGAL_INTEGER = 0x03
KEY_NOT_FOUND = 0x04


# NOTE:
# This will NOT place courses intellgently if one group has a higher priority than another. This might require
# another method that trickles unneeded courses to lower priority groups to meet other requirements.

# In the event a list of courses are fed into the tree and there are multiple protocol nodes that satisfy the same ^


# TODO:
# Implement the certain course list with listing node
# Add automatic movement (to resolve all)
    # Add checks to see if the entered input is empty (string)
    # Fix the global selection (have it work for deselecting and fill outs)
    # add parameters to groups for stub generators
    # Fix validate not recognizing insertion nodes
    # Fix count filter and add credit filter
    # Enforce there being no course of the same name being filled out in a given group node (one instance per layer)
    # Check selection across whole tree (registering course A in one place selects it in other places in the tree)
    # place in the container
# -> Add method to return easily printable objects
# -> Already-taken filter (remove certain specified courses from aggregate)


# add help menu invocation
    #implement CourseInserters

# Add mode to hide "(NOT resolved labels that are not important/active)"
    # add deep credit and deep count filters (enforce a maximum amount of credits/course counts that can go up through get_deep methods)
    # Change the kind of resolve that is printed out (should be shallow)
# search down (or all) using stacktrace to track place (uses regex)--also support goto
    # add node description support
    # add description nodes (more freedom)
    # deal with course protocol's credit
# add copy and paste (this is trickier than it sounds)

# add option to show ls numbers (for easier selection)
# Add better UI (maybe with clearing screen)

# When traversing automatically, check to see if the current node or some other above is stubbed (go back if so)


# LATER:
# After-everything screening (function to check final aggregate)
# Script (even more freedom)
# Add undo (undo command and move back to working node if moved automatically)
# give container method to return all possible permutations of selections


DEFAULT_STUB_COURSE_DESCRIPTION = "COURSE XXXX"

class SchedulableItem:
    
    def __init__(self, course_description, is_stub=False):
        self.course_description = course_description
        self.is_stub = is_stub
        self.stub_availability = 'Fa Sp Su'
        self.stub_credits = 3
        
    def get_course_id(self):
        return self.course_description if not self.is_stub else None

    def get_stub_credit(self):
            return self.stub_credits
    

def default_stub_generator(credits_string=None, name=None):
    new_item = SchedulableItem(name or DEFAULT_STUB_COURSE_DESCRIPTION, is_stub=True)
    new_item.stub_credits = int(credits_string) if (credits_string is not None and credits_string.isnumeric()) else 3
    return new_item
    
def regex_course_protocol_generator(matching_description=r'.*', name=None):
    return CourseProtocol(matching_description, name or 'New Course')

def as_signed_integer(string):
    result = None
    if string:
        if string[0] == '-':
            right_side = string[1:]
            if right_side.isnumeric():
                result = -int(right_side)
        else:
            if string.isnumeric():
                result = int(string)
    return result

# We want to make a tree where at various points a decision is needed (must be resolved).
# A node (or equivalently a "child") on the tree can be in 4 possible states:
#   1. Valid enough to make decisions down the tree (shallow resolved)
#   2. Completely valid in that no decisions must be made at or below the node (deep resolved)
#   3. Invalid, meaning decisions must be made in that node to move down further (unresolved)
#   4. Is a stub (not decided upon)

# The active children of a node are those to be selected (in the decision) and influence
# the deep credit sum and deep count


# Functions of the tree:
# Adding new nodes
# Reset status
# Listing active children nodes
# Listing all children nodes
# Listing active children with ids (dict)
# Listing children with ids (dict)
# Listing entire tree (with state)
# Setting state (uses children and stub) to either
# Generate a 1-D list of all courses involved moving through the tree (may contain stubs)
# Checking if there are any stubs in the tree


## ------------------------------------------------- Interface Start ------------------------------------------------- ##

class ArgumentInputInterface(GeneralInterface):

    def __init__(self, node):
        self.name = 'KEY INPUT'
        self._node = node
        
    def was_pushed(self, controller):
        '''Method that is called upon the interface being pushed onto the interface stack.'''
        controller.output('Enter "<key> = <value>" to set a value. Enter "done" to confirm. Keys:')
        node = self._node
        for key in node.get_keys():
            row = f'   {key}'
            value = node.get_value_for_key(key)
            if value is not None:
                row += f' = {value}'
            controller.output(row)
    
    def deconstruct(self, controller):
        '''Destruction method that is called upon the interface being dismissed.'''
        controller.output('Leaving modification menu.')
    
    def parse_input(self, controller, user_input):
        '''Handle input on behalf of the program.'''

        delimiter_index = user_input.find(SETTING_DELIMITTER)

        if delimiter_index != -1:

            key = user_input[:delimiter_index].strip()
            value = user_input[delimiter_index+len(SETTING_DELIMITTER):].strip()
            result = self._node.set_value_for_key(key, value)

            if result == SUCCESS:
                controller.output('Value set for key.')
            elif result == ILLEGAL_NIL:
                controller.output_error('A value must be specified for this key.')
            elif result == ILLEGAL_INTEGER:
                controller.output_error('The value must be an integer for this key.')
            elif result == KEY_NOT_FOUND:
                controller.output_error(f'Key "{key}" not found.')
            
        else:
            stripped_input = user_input.strip()
            if not stripped_input or stripped_input == 'done':
                controller.pop_interface(self)
            else:
                controller.output_error('Invalid format. Use "<key> = <value>"')
            


class FillOutInterface(GeneralInterface):

    def __init__(self, root, parent_node, node):
        self.name = 'FILL OUT'
        self._root = root
        self._parent_node = parent_node
        self._node = node
        
    def was_pushed(self, controller):
        '''Method that is called upon the interface being pushed onto the interface stack.'''
        controller.output('Enter you course number or enter cancel:')
    
    def deconstruct(self, controller):
        '''Destruction method that is called upon the interface being dismissed.'''
        controller.output('Leaving fill out menu.')
    
    def parse_input(self, controller, user_input):
        '''Handle input on behalf of the program.'''

        value = user_input.strip()

        if value in {'', 'done', 'cancel'}:
            controller.pop_interface(self)
            return
            
        # TODO: make this performed from the parent
        report = self._parent_node.fill_out_child(self._node, value)
        result = RESULT & report
        
        if result == CHANGED:
            if MODIFICATION & report == SELECTION:
                controller.output('Fill out successful.')
            else:
                controller.output('Fill removed.')

            
            # TODO: fix getting the id and priority in a stupid way (bad practice)
            course_id = self._node.get_course_id()
            root = self._root
            highest_priority_for_course_id = root.sync_find_deep_highest_priority(course_id, base_priority=inf)
            sync_result = root.sync_deep_selection_with_priority(self._node._node_id, course_id, base_priority=inf, requisite_priority=highest_priority_for_course_id)

            if sync_result == ADDITIONAL_EFFECTS:
                controller.output('Some other items\' selection states were changed due to this.')
            elif sync_result == SUPERSEDED:
                controller.output('Another selected item matching the same description has a higher priority (selection modified).')

            controller.pop_interface(self)
        elif result == NOT_SATISIFACTORY:
            controller.output_error('That does not meet the form requirements.')
        elif result == UNCHANGED:
            controller.output_error(f'The value is already set to "{value}".')
            controller.pop_interface(self)
        elif result == DUPLICATE:
            controller.output_error(f'A item already set to "{value}" already exists on this layer.')
            controller.pop_interface(self)
        else:
            raise ValueError('Illegal state change result')
            
            


class NeededCoursesInterface(GeneralInterface):
    
    def __init__(self, node, root_interface=None, depth=0, is_traverse_mode=False):
        self.name = 'COURSE SELECTION' # TODO: this needs to change by edit mode status (maybe via property: setters and getters)
        self._node = node
        self._root_interface = root_interface or self
        self._depth = depth
        self._is_traverse_mode = is_traverse_mode

        self._admin_commands = {}
        self._user_commands = {}
        self._commands = self._user_commands
        self._clipboard_node = None
        self._in_edit_mode = False
        
        # exit
        
        # move (can accept names or listing numbers), back, root
        # show_all, show_here, show_down, show_depth, info
        # select, fill (for protocol nodes), deselect, deselect_layer, deselect_all, deselect_down
        # stub (current node), stub_all, unstub (current node), unstub_all, unstub_down (from current node)
            # go_to, search, resolve (traverse), full_resolve (traverse with no stubs)
            # edit_mode_on, edit_mode_off
        
        # add_exhaustive, add_deep_count, add_shallow_count, add_deep_credit, add_deliverable, add_protocol, add_inserter
        
        # delete, change_type, modify
            # copy, cut, paste
        # aggregate/pull
            # validate
        
            # add_script, add_description, set_screen, set_filter
        
        # Add commands to the command dictionary

        # User-level:
        self.add_command(self.print_commands, '', 'commands')
        
        self.add_command(self.navigate_to_nodes, 'move', 'cd', 'go')
        self.add_command(self.navigate_back, 'back', '..')
        self.add_command(self.navigate_to_root, 'root', 'home', 'base')
                
        self.add_command(self.show_all, 'show_all', 'display_all', 'map')
        self.add_command(self.show_here, 'show_here', 'display_here', 'show', 'display', 'ls')
        self.add_command(self.show_down, 'show_down', 'display_down', 'down')
        self.add_command(self.show_depth, 'show_depth', 'display_depth', 'depth')
        self.add_command(self.show_info, 'show_info', 'info', 'instructions')
        
        self.add_command(self.select_course, 'select', 'choose', 's')
        self.add_command(self.fill_out_course, 'fill', 'fill_out', 'f')
        self.add_command(self.deselect_course, 'deselect', 'd')
        self.add_command(self.deselect_layer, 'deselect_layer', 'd_layer')
        self.add_command(self.deselect_all, 'deselect_all')
        self.add_command(self.deselect_down, 'deselect_down', 'd_down')
                
        self.add_command(self.stub_course, 'stub', 't')
        self.add_command(self.stub_layer, 'stub_layer', 't_layer')
        self.add_command(self.stub_all_top, 'stub_top', 't_top')
        self.add_command(self.unstub_course, 'unstub', 'u')
        self.add_command(self.unstub_layer, 'unstub_layer', 'u_layer')
        self.add_command(self.unstub_all, 'unstub_all')
        self.add_command(self.unstub_down, 'unstub_down', 'u_down')

        self.add_command(self.aggregate, 'aggregate', 'pull')
        self.add_command(self.admin_mode, 'admin', 'sudo')
        self.add_command(self.user_mode, 'user', 'student')
        
        # Admin-level:
        self._admin_commands = self._commands.copy()
        self._commands = self._admin_commands
        
        self.add_command(self.add_exhaustive, 'add_exhaustive', 'aex', 'ae')
        self.add_command(self.add_deliverable, 'add_deliverable', 'ade', 'ad')
        self.add_command(self.add_protocol, 'add_protocol', 'apr', 'ap')
        self.add_command(self.add_shallow_count, 'add_shallow_count', 'asc', 'asn')
        self.add_command(self.add_deep_count, 'add_deep_count', 'adc', 'adn')
        self.add_command(self.add_deep_credit, 'add_deep_credit', 'add_credit', 'acr')
        self.add_command(self.add_inserter, 'add_inserter', 'ains', 'ai')
        
        self.add_command(self.delete_node, 'delete', 'del')
        self.add_command(self.modify_node, 'rename', 'modify', 'change', 'edit', 'm')
        self.add_command(self.validate_tree, 'validate', 'valid')
        
        # TODO: this is just a test!:
        self.add_command(self.test, 'test')
    
    def test(self, controller, arg):
        controller.output(self._node.sync_find_deep_highest_priority(arg, inf))

    def was_pushed(self, controller):
        '''Method that is called upon the interface being pushed onto the interface stack.'''
        if (self._is_in_traverse_mode()):
            # TODO: determine if resolved
            pass
        pass
    
    def deconstruct(self, controller):
        '''Destruction method that is called upon the interface being dismissed.'''
        pass

        
    def print_commands(self, controller, argument):
        # TODO: handle arguments and refine printing
        # TODO: make this determined by whether in admin mode or user mode
        controller.output('Available commands: ')
        
    def print_warning_if_arguments(self, controller, argument):
        if argument:
            controller.output_warning('Arguments are not processed for this command.')


    def navigate_to_nodes(self, controller, argument):
        # TODO: make this work recursively (fix)

        if argument:
            destinations = [destination.strip() for destination in argument.split(',')]
            current_interface = self

            while destinations:
                next_destination = destinations.pop(0)
                sucess, current_interface = current_interface._navigate_to_node(controller, next_destination)
                if not sucess:
                    destinations = []
                    break
            self._print_top_interface(controller)
        else:
            controller.output_error('Please enter a group to navigate to.')
                
    def navigate_back(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        self._navigate_back(controller)
        self._print_top_interface(controller)
        
    def navigate_to_root(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        self._navigate_to_root(controller)
        self._print_top_interface(controller)
    
    def show_all(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        controller.output(self._get_root_interface()._node.get_deep_description())
    
    def show_here(self, controller, argument):
        if not argument:
            self._print_listing(controller)
        else:
            self.show_info(controller, argument)
    
    def show_down(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        controller.output(self._node.get_deep_description())
        
    def show_depth(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        controller.output(f'Layer depth: {self._depth + 1}')
    
    def show_info(self, controller, argument):
        if not argument:
            controller.output(self._node.get_layer_description())
        else:
            child = self._get_child(argument)
            if child is not None:
                controller.output(child.get_layer_description())
            else:
                controller.output_error(f'No item immediately below matches that description "{argument}".')
    
    
    
    def select_course(self, controller, argument):
        if argument:
            for course_description in [course.strip() for course in argument.split(',')]:
                self._select_course(controller, course_description)
        else:
            controller.output_error('Please enter a course or courses to select.')
        
    def fill_out_course(self, controller, argument):
        if argument:
            child = self._get_child(argument)
            if child is not None:
                if child.can_accept_fill_out():
                    controller.push_interface(FillOutInterface(root=self._get_root_node(), parent_node=self._node, node=child))
                else:
                    controller.output_error('This item cannot be filled out.')
            else:
                controller.output_error(f'No item immediately below matches the description "{argument})".')
        else:
            controller.output_error('Please enter a course to fill.')
            
    
    def deselect_course(self, controller, argument):
        if argument:
            for course_description in [course.strip() for course in argument.split(',')]:
                self._deselect_course(controller, course_description)
        else:
            controller.output_error('Please enter a course or courses to deselect.')

        
    def deselect_layer(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        controller.output('Entire layer deselected (those possible).')
        self._node.reset_shallow_selection()
        
    def deselect_all(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        self._get_root_interface()._node.reset_deep_selection()
        controller.output('All items deselected (those possible).')
                
    def deselect_down(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        self._node.reset_deep_selection()
        controller.output('All items deselected downward (those possible).')
        
        
        
    def stub_course(self, controller, argument):
        if argument:
            stub_result = RESULT & self._node.enable_child_stub_by_description(argument)
            self._report_stub_enable(stub_result, controller, argument)
        else:
            controller.output_error('Please enter a course or group to stub.')

                
    def stub_layer(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        stub_result = RESULT & self._node.enable_stub()
        self._report_stub_enable(stub_result, controller, 'self')
            
    def stub_all_top(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        for node in self._get_root_node().get_all_children_list():
            node.enable_stub()
        controller.output('All applicable top-layer nodes stub-enabled.')
        
        
    def unstub_course(self, controller, argument):
        if argument:
            stub_result = RESULT & self._node.disable_child_stub_by_description(argument)
            self._report_stub_disable(stub_result, controller, argument)
        else:
            controller.output_error('Please enter a course or group to unstub.')

    def unstub_layer(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        stub_result = RESULT & self._node.disable_stub(argument)
        self._report_stub_enable(stub_result, controller, 'self')
        
    def unstub_all(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        self._get_root_interface()._node.reset_deep_stub()
        controller.output('All applicable stubs reset.')
                
    def unstub_down(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        self._node.reset_deep_stub()
        controller.output('All applicable stubs removed downward.')
        
        
    def add_exhaustive(self, controller, argument):
        new_node = ExhaustiveNode()
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(controller, argument, new_node)
            controller.output('Group added.')
        else:
            controller.output_error('The group could not be added.')
    
        
    def add_deliverable(self, controller, argument):
        new_node = DeliverableCourse(printable_description='New Course', credits=3)
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(controller, argument, new_node)
            controller.output('Course added.')
        else:
            controller.output_error('The course could not be added.')
    
    
    def add_protocol(self, controller, argument):
        # TODO: fix this default (does not work)
        new_node = CourseProtocol(match_description=r'[A-Z]{4, 5}\s?[0-9]{4}[A-Z]?', printable_description='New Course Protocol', credits=3)
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(controller, argument, new_node)
            controller.output('Course added.')
        else:
            controller.output_error('The course could not be added.')
        
    
    def add_shallow_count(self, controller, argument):
        new_node = ShallowCountBasedNode(requisite_count=1)
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(controller, argument, new_node)
            controller.output('Group added.')
        else:
            controller.output_error('The group could not be added.')
    
                
    def add_deep_count(self, controller, argument):
        new_node = DeepCountBasedNode(requisite_count=1)
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(controller, argument, new_node)
            controller.output('Group added.')
        else:
            controller.output_error('The group could not be added.')
    
    def add_deep_credit(self, controller, argument):
        new_node = DeepCreditBasedNode(requisite_credits=3)
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(controller, argument, new_node)
            controller.output('Group added.')
        else:
            controller.output_error('The group could not be added.')
    
    def add_inserter(self, controller, argument):
        new_node = CourseInserter(generator_parameter=r'[A-Z]{4, 5}\s?[0-9]{4}[A-Z]?', printable_description='Insert New')
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(controller, argument, new_node)
            controller.output('Inserter added.')
        else:
            controller.output_error('The inserter could not be added.')
        
           
    def delete_node(self, controller, argument):
        if argument:
            self._delete_node(controller, argument)
        else:
            controller.output_error('Please enter a course or group to delete.')
        
    def modify_node(self, controller, argument):
        if not argument:
            controller.push_interface(ArgumentInputInterface(self._node))
        else:
            child = self._get_child(argument)
            if child:
                controller.push_interface(ArgumentInputInterface(child))
            else:
                controller.output_error(f'No item immediately below matches the description "{argument}".')
        
    def aggregate(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        controller.output(f'Is resolved: {self._get_root_node().is_deep_resolved()}')
        controller.output([e.course_description for e in self._get_root_node().get_aggregate()])
        

    
    def validate_tree(self, controller, argument):
        node = None
        if not argument:
            node = self._get_root_node()
        else:
            node = self._node.get_child_by_description(argument)

        if node is not None:
            if self.can_be_deep_resolved():
                controller.output('The requirement structure appears to be satisfiable.')
            else:
                trace = self._get_root_node().get_first_non_resolvable_stacktrace()
                trace = " -> ".join([f'|{index}: {node.get_shallow_description()}|' for (index, node) in trace])
                controller.output(f'Problem at: {trace}')
        else:
            controller.output('Entry point for validation not found.')
        
    
    def admin_mode(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        if self._commands is self._user_commands:
            self._commands = self._admin_commands
            controller.output('Mode changed to admin mode.')
        else:
            controller.output_error('Mode is already in admin mode.')

    def user_mode(self, controller, argument):
        self.print_warning_if_arguments(controller, argument)
        if self._commands is self._admin_commands:
            self._commands = self._user_commands
            controller.output('Mode changed to user mode.')
        else:
            controller.output_error('Mode is already in user mode.')

    # --------------------------------------- Control Methods --------------------------------------- #
        
    def _get_root_interface(self):
        result = None
        if self is self._root_interface:
            result = self
        else:
            result = self._root_interface._get_root_interface()
        return result
        
    def _get_root_node(self):
        return self._get_root_interface()._node
    
    def _get_child(self, description):
            return self._node.get_child_by_description(description)

    def _get_clipboard(self):
        return self._get_root_interface()._clipboard_node
    
        
    def _is_in_traverse_mode(self):
        return self._get_root_interface()._is_traverse_mode
    
    def _print_listing(self, controller):
        controller.output(self._node.get_layer_description())
    
    def _apply_constructor_arguments(self, controller, arguments, node):

        arguments_listing = arguments.split(',')
        
        if len(arguments_listing) == 1 and arguments_listing[0] == '':
            return

        used_keys = set()
        duplicate_keys = set()

        for argument in arguments_listing:

            delimiter_index = argument.find(SETTING_DELIMITTER)

            if delimiter_index != -1:

                key = argument[:delimiter_index].strip()

                if key not in used_keys:
                    used_keys.add(key)
                    value = argument[delimiter_index+len(SETTING_DELIMITTER):].strip()
                    setting_result = node.set_value_for_key(key, value)

                    if setting_result != SUCCESS:
                        controller.output_error(f'Could not locate contructor key "{key}"')
                
                elif key in node.get_keys():
                    duplicate_keys.add(key)
            else:
                controller.output_error(f'Invalid format. Use "<key> = <value>" instead of "{argument}"')
        
        if duplicate_keys:
            controller.output_warning(f'The following keys had duplicate assignement: {", ".join(duplicate_keys)}')
                

    def _print_top_interface(self, controller):
        top_interface = controller.get_current_interface()
        if isinstance(top_interface, NeededCoursesInterface):
            top_interface._print_listing(controller)

    def _navigate_to_node(self, controller, node_description):
        
        success = False
        new_menu = None
        child = self._get_child(node_description)
        
        if child is not None:
            # Check if children can be added (and hence navigated into)
            if child.can_navigate_into():
                new_menu = NeededCoursesInterface(child, root_interface=self._get_root_interface(), depth=self._depth + 1)
                success = True
                controller.push_interface(new_menu)
            else:
                controller.output_error('That type of item cannot be navigated to.')
        else:
            controller.output_error(f'No item immediately below matches the description "{node_description}".')
            
        return success, new_menu
        
    
    def _navigate_back(self, controller):
        controller.pop_interface(self), 'pop interface'
        
        
    def _navigate_to_root(self, controller):
        # TODO: add check for base menu (this would be error state)
        if self is self._root_interface:
            top_interface = controller.get_current_interface()
            while top_interface is not self:
                controller.pop_interface(top_interface)
                top_interface = controller.get_current_interface()
        else:
            self._get_root_interface()._navigate_to_root(controller)
    
        
        
    def _select_course(self, controller, course_description):
        selection_result, child = self._node.select_child_by_description(course_description)
        selection_result &= RESULT
        if selection_result == CHANGED:
            controller.output('Item selected.')

            # TODO: fix getting the id and priority in a stupid way (bad practice)
            course_id = child.get_course_id()
            root = self._get_root_node()
            highest_priority_for_course_id = root.sync_find_deep_highest_priority(course_id, base_priority=inf)
            sync_result = root.sync_deep_selection_with_priority(child._node_id, course_id, base_priority=inf, requisite_priority=highest_priority_for_course_id)

            if sync_result == ADDITIONAL_EFFECTS:
                controller.output('Some other items\' selection states were changed due to this.')
            elif sync_result == SUPERSEDED:
                controller.output('Another selected item matching the same description has a higher priority (selection modified).')

        elif selection_result == UNCHANGED:
            controller.output_error('This item is already selected.')
        elif selection_result == ILLEGAL:
            controller.output_error('This item cannot be selected.')
        elif selection_result == CHILD_NOT_FOUND:
            controller.output_error(f'No item immediately below matches that description "{course_description}".')
        elif selection_result == GENERATION:
            controller.output('Item added.')
        else:
            raise ValueError('Illegal state change result')
            
    def _deselect_course(self, controller, course_description):

        selection_result, child = self._node.deselect_child_by_description(course_description)
        selection_result &= RESULT

        if selection_result == CHANGED:
            controller.output('Item deselected.')

            # TODO: fix getting the id in a stupid way (bad practice)
            root = self._get_root_node()
            sync_result = root.sync_deep_deselection(child._node_id, child.get_course_id())
            if sync_result == ADDITIONAL_EFFECTS:
                controller.output('Some other items\' selection states were changed due to this.')
            elif sync_result == UNSTRUCTURED:
                controller.output_warning('There appears to be conflicting priority')


        elif selection_result == UNCHANGED:
            controller.output_error('This item is not selected.')
        elif selection_result == ILLEGAL:
            controller.output_error('This item cannot be deselected.')
        elif selection_result == CHILD_NOT_FOUND:
            controller.output_error(f'No item immediately below matches the description "{course_description}".')
        else:
            raise ValueError('Illegal state change result')
    
    def _report_stub_enable(self, stub_result, controller, argument):
        if stub_result == CHANGED:
            controller.output('Item set to stub.')
        elif stub_result == UNCHANGED:
            controller.output_error('This item is already stub enabled.')
        elif stub_result == ILLEGAL:
            controller.output_error('This item does not support stub states.')
        elif stub_result == CHILD_NOT_FOUND:
            controller.output_error(f'No item immediately below matches that description "{argument}".')
        else:
            raise ValueError('Illegal state change result')


    def _report_stub_disable(self, stub_result, controller, argument):
        if stub_result == CHANGED:
            controller.output('Removed item stub.')
        elif stub_result == UNCHANGED:
            controller.output_error('This item is not in a stub state.')
        elif stub_result == ILLEGAL:
            controller.output_error('This item does not support stub removal at the moment.')
        elif stub_result == CHILD_NOT_FOUND:
            controller.output_error(f'No item immediately below matches that description "{argument}".')
        else:
            raise ValueError('Illegal state change result')
    # def _set_stub_state_for_course(self, controller, node_description, state):
    #     child = self._get_child(node_description)
        
    #     if child is not None:
    #         if child.set_stub_state(state):
    #             controller.output('Item stub-state updated.')
    #         else:
    #             controller.output_error('This item cannot be stub-ed.')
    #     else:
    #         controller.output_error(f'No item immediately below matches that description ({node_description}).')
    
        
    def _delete_node(self, controller, node_description):
        child = self._get_child(node_description)
        
        if child is not None:
            if self._node.remove_child(child._node_id):
                controller.output('Item deleted.')
            else:
                controller.output_error('This item cannot be deleted.')
        else:
            controller.output_error(f'No item immediately below matches that description "{node_description}".')
        
    

    # TODO: methods below need implementation
    
    def _change_node_type(self, node_id, node_type):
        # TODO: needs to understand the node type (some node cannot be switched to others)
        pass
        
    def _change_node_parameter(self, node_id, parameter):
        # TODO: needs to understand the node type
        pass
        
    
    def _cut_node(self, node_id):
        success = False
        if self._copy_node(node_id):
            success = True
        return success
    
    def _copy_node(self, node_id):
        pass
        
    def _paste_node(self):
        pass
    
## ------------------------------------------------- Interface End ------------------------------------------------- ##



# Exhaustive, DeepNum, DeepCred, ShallowNum, Deliverable, Protocol

class _NodeSuper:
    
    _next_node_id = 1000
    
    @staticmethod
    def get_new_node_id():
        _NodeSuper._next_node_id += 1
        return _NodeSuper._next_node_id - 1
    
    def __init__(self, printable_description=None, verbose_instructions=None):
        self._children = {}
        self._printable_description = printable_description # this is the name of the node
        self._node_id = _NodeSuper.get_new_node_id() # this is an int
        self._is_stub = False
        self._selection = set()
        self._destructive_selection = set() # this is a list of all nodes to remove upon being deselected
        self._children_ids = [] # This appears in the order is printing
        self._verbose_instructions = verbose_instructions

        self._max_count_propogation = None
        self._max_credits_propogation = None
        self._duplicate_priority = None
        
    ## ------------------------------ Key-value Management ------------------------------ ##
    
    # KEY_VALUE_DICT = {
    #     'name': '_course_description',
    #     'credits': '_credits'
    # }

    # KEYS_LIST = ['name', 'credits']
    # NON_NIL_KEYS = {'name'}
    # INTEGER_KEYS = {'credits'}

    def get_keys(self):
        return self.KEYS_LIST
    
    def get_value_for_key(self, key):
        value = None
        if key in self.KEY_VALUE_DICT:
            value = self.__dict__[self.KEY_VALUE_DICT[key]]
        return value
    
    def set_value_for_key(self, key, value):

        result = KEY_NOT_FOUND
            
        if key in self.KEYS_LIST:
            if value == '':
                if key in self.NON_NIL_KEYS:
                    result = ILLEGAL_NIL
                else:
                    self.__dict__[self.KEY_VALUE_DICT[key]] = None
                    result = SUCCESS
            else:
                if key in self.INTEGER_KEYS:
                    if value.isnumeric():
                        self.__dict__[self.KEY_VALUE_DICT[key]] = int(value)
                        result = SUCCESS
                    else:
                        result = ILLEGAL_INTEGER
                else:
                    self.__dict__[self.KEY_VALUE_DICT[key]] = value
                    result = SUCCESS
                
        return result
    
    ## ------------------------------ Inherent Characteristics ------------------------------ ##

    def can_accept_children(self):
        # This is also used to determine if the node can be navigated into
        return True
    
    def can_navigate_into(self):
        return self.can_accept_children()
    
    def can_accept_fill_out(self):
        return False
    
    def can_be_stub(self):
        return True
    
    ## ------------------------------ Descriptions getting ------------------------------ ##

    def get_verbose_instructions(self):
        return self._verbose_instructions
    
    def get_shallow_description(self):
        raise NotImplementedError
    
    def get_deep_description(self, depth=0, is_selected=False, maximum_depth=-1):
        
        prefix_icon = ' '
        if self.has_shallow_stub():
            prefix_icon = '~'
        elif is_selected:
            prefix_icon = '+'

        result = f'{depth*"   "}{prefix_icon} {self.get_shallow_description()}'
        
        if not self.is_shallow_resolved() or self.has_shallow_stub():

            result += ' ('

            if self.is_shallow_resolved():
                result += 'RESOLVED'
            elif self.is_discovery_resolved():
                result += 'PARTIALLY resolved'
            else:
                result += 'NOT resolved'
            
            if self.has_shallow_stub():
                result += ', STUBBED'
            
            result += ')'

        if maximum_depth != 0 and self.get_all_children_count() != 0:
            
            result += ':\n'
            rows = []
            for node_id in self._children_ids:
                child = self._children[node_id]
                child_is_selected = self.is_selecting_node_id(node_id)
                rows.append(child.get_deep_description(depth+1, is_selected=child_is_selected, maximum_depth=maximum_depth-1))
            result += '\n'.join(rows)
        
        return result
    
    def get_layer_description(self):

        description = None

        if self.get_all_children_count() != 0:
            description = self.get_deep_description(maximum_depth=1)
        else:
            description = self.get_shallow_description()
            if self.can_accept_children():
                description += ' (empty)'
        
        instructions = self.get_verbose_instructions()
        if instructions is not None:
            description += '\nABOUT: ' + instructions

        return description

    def set_printable_description(self, description):
        new_description = description if description != '' else None
        self._printable_description = new_description

    ## ------------------------------ Descriptions matching ------------------------------ ##

    def matches_description(self, description):
        '''Returns whether the passed description matches the name (printable description).'''
        # Ensure the string is non-empty and there is a match
        result = False
        if self._printable_description is not None:
                result = self._printable_description == description
                if not result:
                    wildcard_index = description.find('*')
                    if wildcard_index != -1:
                        result = self._printable_description[:wildcard_index] == description[:wildcard_index]
        return result
    
    def get_child_by_description(self, description):
        
        result = None
        children = self.get_all_children_list()
        index = as_signed_integer(description)

        if index is not None and index != 0 and -len(children) <= index and index <= len(children):
            if index > 0:
                index -= 1
            result = children[index]
        else:
            for child in children:
                if child.matches_description(description):
                    result = child
                    break
        
        return result

    ## ------------------------------ Collection Access ------------------------------ ##

    @final
    def get_all_children_ids(self):
        '''Get a copy of the ordered list of children IDs.'''
        return self._children_ids[:]
    
    def get_active_children_ids(self):
        '''Get a copy of the ordered list of children IDs that are selected.'''
        return self._selection.copy()
    
    @final
    def get_all_children_count(self):
        '''Get the count of children.'''
        return len(self._children_ids)
    
    @final
    def get_active_children_count(self):
        '''Get the count of children that are selected.'''
        return len(self.get_active_children_ids())
        
    
    @final
    def get_all_children_list(self):
        '''Make an ordered list of child nodes.'''
        return [self._children[node_id] for node_id in self._children_ids]
    
    @final
    def get_active_children_list(self):
        '''Make an ordered list of child nodes that are selected.'''
        active_ids = self.get_active_children_ids()
        return [self._children[node_id] for node_id in self._children_ids if node_id in active_ids]
        
    @final
    def get_all_children_mapping(self):
        '''Make a dictionary/mapping from node IDs to child nodes.'''
        return self._children.copy()
        
    @final
    def get_active_children_mapping(self):
        '''Make a dictionary/mapping from node IDs to child nodes that are selected.'''
        active_ids = self.get_active_children_ids(self)
        return {node_id: self._children[node_id] for node_id in self._children_ids if node_id in active_ids}
    
    ## ------------------------------ Aggregation ------------------------------ ##

    # Exhaustive, DeepNum, DeepCred, ShallowNum, Deliverable, Protocol
    def get_aggregate(self):
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''
        raise NotImplementedError
    
    def get_course_id(self):
        '''Return the unique ID this course represents or None if it is not concrete.'''
        return None

    ## ------------------------------ Child Set Mutation ------------------------------ ##

    @final
    def add_child(self, node):
        '''Attempt to add a child node and return the success of the addition.'''
        success = False
        if self.can_accept_children():
            self._children[node._node_id] = node
            self._children_ids.append(node._node_id)
            success = True
        return success

    @final
    def add_children(self, nodes):
        success = True
        for child in nodes:
            success &= self.add_child(child)
        success

    @final
    def remove_child(self, node_id):
        '''Attempt to remove a child and return the success of the removal.'''
        success = False
        if node_id in self._children and self.can_accept_children():
            del self._children[node_id]
            self._children_ids.remove(node_id)
            self._selection.discard(node_id)
            success = True
        return success
    
    ## ------------------------------ Selection ------------------------------ ##

    @final
    def is_selecting_node_id(self, node_id):
        '''Returns whether the passed node ID is selected.'''
        return node_id in self.get_active_children_ids()

    def select_child(self, node):
        result = SELECTION
        node_id = node._node_id
        if not self.is_selecting_node_id(node_id):
            generation_node = node.selection_new_node_generation()
            if generation_node is not None:
                self.add_child(generation_node)
                self._destructive_selection.add(generation_node._node_id)
                self.select_child(generation_node)
                result |= GENERATION
            else:
                self._selection.add(node_id)
                result |= CHANGED if self.is_selecting_node_id(node_id) else ILLEGAL
        else:
            result |= UNCHANGED
        return result
    
    @final
    def select_child_by_description(self, description):
        result = SELECTION
        child = self.get_child_by_description(description)
        if child:
            result = self.select_child(child)
        else:
            result |= CHILD_NOT_FOUND
        return result, child
    
    def deselect_child(self, node):  
        result = DESELECTION
        node_id = node._node_id
        if self.is_selecting_node_id(node_id):
            self._selection.remove(node._node_id)
            if not self.is_selecting_node_id(node_id):
                result |= CHANGED
                if node_id in self._destructive_selection:
                    if self.remove_child(node_id):
                        self._destructive_selection.remove(node_id)
            else:
                result |= ILLEGAL
        else:
            result |= UNCHANGED
        return result
    
    @final
    def deselect_child_by_description(self, description):
        result = DESELECTION
        child = self.get_child_by_description(description)
        if child:
            result = self.deselect_child(child)
        else:
            result |= CHILD_NOT_FOUND
        return result, child

    def reset_shallow_selection(self):
        for node in self._children.values():
            self.deselect_child(node)
        self.disable_stub()
    
    @final
    def reset_deep_selection(self):
        self.reset_shallow_selection()
        
        for node in self._children.values():
            node.reset_deep_selection()
    
    def selection_new_node_generation(self):
        # Return a new node to add to the parent if the current node is a generator or None if it is normal 
        return None

    ## ------------------------------ Selection syncing ------------------------------ ##

    def sync_find_deep_highest_priority(self, course_id, base_priority=None):
        priority = self._duplicate_priority or base_priority
        highest_priority = priority if any(child.get_course_id() == course_id for child in self.get_active_children_list()) else inf
        
        for child in self.get_all_children_list():
            highest_priority = min(highest_priority, child.sync_find_deep_highest_priority(course_id, priority))
        
        return highest_priority

    def sync_deep_selection_with_priority(self, original_node_id, course_id, base_priority, requisite_priority):
        result = SINGLE
        current_priority = self._duplicate_priority or base_priority
        #print(self.get_shallow_description(), self._duplicate_priority or base_priority, self._duplicate_priority, base_priority)
        
        for child in self.get_all_children_list():
            if child.get_course_id() == course_id:
                if self.is_selecting_node_id(child._node_id):
                    
                    if current_priority != requisite_priority:
                        self.deselect_child(child)
                        
                        if child._node_id == original_node_id:
                            result = SUPERSEDED
                        elif result == SINGLE:
                            result = ADDITIONAL_EFFECTS
                else:

                    if current_priority == requisite_priority and child._node_id != original_node_id:
                        self.select_child(child)
                        if result == SINGLE:
                            result = ADDITIONAL_EFFECTS
                
            child_result = child.sync_deep_selection_with_priority(original_node_id, course_id, current_priority, requisite_priority)

            if child_result == SUPERSEDED:
                result = SUPERSEDED
            elif result == SINGLE and child_result == ADDITIONAL_EFFECTS:
                result = ADDITIONAL_EFFECTS
        
        return result

    def sync_deep_deselection(self, original_node_id, course_id):

        result = SINGLE

        for child in self.get_all_children_list():
            if child.get_course_id() == course_id and self.is_selecting_node_id(child._node_id):
                deselection_result = RESULT & self.deselect_child(child)
                if deselection_result == CHANGED:
                    if child._node_id != original_node_id:
                        result = ADDITIONAL_EFFECTS
                else:
                    result = UNSTRUCTURED
                
            child_result = child.sync_deep_deselection(original_node_id, course_id)

            if child_result == UNSTRUCTURED:
                result = UNSTRUCTURED
            elif result == SINGLE and child_result == ADDITIONAL_EFFECTS:
                result = ADDITIONAL_EFFECTS

        return result

    ## ------------------------------ Filling out ------------------------------ ##
    
    def get_fill_out_state(self):
        return None
    
    def _set_fill_out_state(self, argument):
        result = SELECTION | ILLEGAL
        if not self.can_accept_fill_out():
            raise NotImplementedError
        return result

    @final
    def fill_out_child(self, node, argument):
        result = SELECTION | CHILD_NOT_FOUND
        if node._node_id in self.get_all_children_ids():
            # See if the child is already in the current layer (reject if so)
            if not self.get_child_by_description(argument):
                result = node._set_fill_out_state(argument)
            else:
                result = SELECTION | DUPLICATE
        return result
    
    @final
    def fill_out_child_by_description(self, description, argument):
        result = SELECTION | CHILD_NOT_FOUND
        child = self.get_child_by_description(description)
        if child:
            result = child._set_fill_out_state(argument)
        return result

    ## ------------------------------ Stub ------------------------------ ##
    
    def has_shallow_stub(self):
        '''Returns whether this node is stubbed (and hence everything below is not concrete).'''
        return self._is_stub
    
    @final
    def has_deep_stub(self):
        return self.has_shallow_stub() or any(node.has_deep_stub() for node in self.get_active_children_list())
    
    def enable_stub(self):
        result = SELECTION
        if self.can_be_stub():
            if not self.has_shallow_stub():
                self._is_stub = True
                result |= CHANGED if self.has_shallow_stub() else ILLEGAL
            else:
                result |= UNCHANGED
        else:
            result |= ILLEGAL
        return result

    @final
    def enable_child_stub_by_description(self, description):
        result = SELECTION
        child = self.get_child_by_description(description)
        if child:
            result = child.enable_stub()
        else:
            result |= CHILD_NOT_FOUND
        return result
    
    def disable_stub(self):
        result = DESELECTION
        if self.has_shallow_stub():
            self._is_stub = False
            result |= CHANGED if not self.has_shallow_stub() else ILLEGAL
        else:
            result |= UNCHANGED
        return result

    @final
    def disable_child_stub_by_description(self, description):
        result = DESELECTION
        child = self.get_child_by_description(description)
        if child:
            result = child.disable_stub()
        else:
            result |= CHILD_NOT_FOUND
        return result
    
    def reset_deep_stub(self):
        self.disable_stub()
        
        for node in self._children.values():
            node.reset_deep_stub()
        
    ## ------------------------------ Resolve Status ------------------------------ ##

    def can_be_shallow_resolved(self):
        return True
    
    @final
    def can_be_deep_resolved(self):
        result = self.can_be_shallow_resolved()

        if result:
            for child in self._children.values():
                if not child.can_be_deep_resolved():
                    result = False
                    break
                
        return result
    
    @final
    def get_first_non_resolvable_stacktrace(self, layer_index=1, stacktrace=[]):
        '''This will return nothing if acceptable/resolvable and a list of the stacktrace if a non-resolvable node is found.'''
        result = None 
        new_layer_trace = stacktrace[:] + [(layer_index, self)]

        if not self.can_be_shallow_resolved():
            result = new_layer_trace
        else:
            child_ids = self.get_all_children_ids()
            # Check if the list is empty
            if child_ids:
                # Leaf/base case is no children
                for (index, child_id) in enumerate(child_ids):
                    child = self._children[child_id]
                    trace = child.get_first_non_resolvable_stacktrace(layer_index=index+1, stacktrace=new_layer_trace)
                    if trace is not None:
                        result = trace
                        break
        return result
        
    def is_shallow_resolved(self):
        return True

    def is_discovery_resolved(self):
        '''This method returns whether enough information has been entered for the user to progress through entering values
        (less demanding than shallow resolved). This should NOT use recursion and it does not indicate whether the tree is resolved.'''
        return self.is_shallow_resolved()

    @final
    def is_deep_resolved(self):
        return self.has_shallow_stub() or (self.is_shallow_resolved() and all(node.is_deep_resolved() for node in self.get_active_children_list()))
    
    ## ------------------------------ Node Count ------------------------------ ##
        
    def get_shallow_count(self):
        return 0

    @final
    def get_all_deep_count(self):
        result = self.get_shallow_count()

        sum = 0
        for node in self.get_all_children_list():
            sum += node.get_all_deep_count()
        
        if self._max_count_propogation is not None:
            sum = min(sum, self._max_count_propogation)
        
        result += sum
        return result
    
    @final
    def get_all_layer_count(self):
        return sum([node.get_all_deep_count() for node in self.get_all_children_list()])

    @final
    def get_active_deep_count(self):
        result = self.get_shallow_count()

        sum = 0
        for node in self.get_active_children_list():
            sum += node.get_active_deep_count()

        if self._max_count_propogation is not None:
            sum = min(sum, self._max_count_propogation)

        result += sum
        return result
    
    @final
    def get_active_layer_count(self):
        return sum([node.get_active_deep_count() for node in self.get_active_children_list()])

    ## ------------------------------ Node Credit ------------------------------ ##
    
    def get_shallow_credits(self):
        return 0
    
    @final
    def get_all_deep_credits(self):
        result = self.get_shallow_credits()

        sum = 0
        for node in self._children.values():
            sum += node.get_all_deep_credits()
        
        if self._max_credits_propogation is not None:
            sum = min(sum, self._max_credits_propogation)

        result += sum
        return result
        
    @final
    def get_all_layer_credits(self):
        return sum([node.get_all_deep_credits() for node in self.get_all_children_list()])

    @final
    def get_active_deep_credits(self):
        result = self.get_shallow_credits()

        sum = 0
        for node in self.get_active_children_list():
            sum += node.get_active_deep_credits()

        if self._max_credits_propogation is not None:
            sum = min(sum, self._max_credits_propogation)

        result += sum
        return result
        
    @final
    def get_active_layer_credits(self):
        return sum([node.get_active_deep_credits() for node in self.get_active_children_list()])


# Note that this is also a kind of node in a CoursesNeededContainer (a leaf node).
class DeliverableCourse(_NodeSuper):
    
    KEY_VALUE_DICT = {
        'name': '_printable_description',
        'course id': '_course_description',
        'instructions': '_verbose_instructions',
        'credits': '_credits',
        'deliver name': '_course_description',
        'duplicate priority': '_duplicate_priority'
    }

    KEYS_LIST = ['name', 'instructions', 'credits', 'deliver name', 'duplicate priority']
    NON_NIL_KEYS = {'name', 'credits'}
    INTEGER_KEYS = {'credits', 'duplicate priority'}

    def __init__(self, course_description=None, credits=3, printable_description=None):
        super().__init__(printable_description or course_description)
        self._course_description = course_description
        self._credits = credits
    
    def can_accept_children(self):
        return False
    
    def can_be_stub(self):
        return False

    def get_shallow_description(self):
        return f'{self._printable_description or self._course_description or "Course"} - {self.get_shallow_credits()}'
        
    def get_active_children_ids(self):
        return []
    
    def get_aggregate(self):
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''
        return [SchedulableItem(self._course_description or self._printable_description or "Course")]
    
    def get_course_id(self):
        '''Return the unique ID this course represents or None if it is not concrete.'''
        return self._course_description or self._printable_description  
    
    def get_shallow_count(self):
        return 1
        
    def get_shallow_credits(self):
        return self._credits
        
    

# Note that this is also a kind of node in a CoursesNeededContainer (a leaf node).
class CourseProtocol(_NodeSuper):
    
    DEFAULT_CREDIT = 3

    KEY_VALUE_DICT = {
        'name': '_printable_description',
        'instructions': '_verbose_instructions',
        'credits': '_credits',
        'matching': '_match_description',
        'rejection': '_reject_description',
        'stub_name': '_stub_description',
        'duplicate priority': '_duplicate_priority'
    }

    KEYS_LIST = ['name', 'instructions', 'credits', 'matching', 'rejection', 'stub_name', 'duplicate priority']
    NON_NIL_KEYS = {'name', 'credits', 'matching'}
    INTEGER_KEYS = {'credits', 'duplicate priority'}
    
    def __init__(self, match_description='.*', printable_description=None, credits=None,
                 reject_description=None, stub_description=None):
        super().__init__(printable_description)
        
        self._match_description = match_description
        self._credits = credits
        self._reject_description = reject_description
        self._stub_description = stub_description
        
        self._selected_course = None

    def does_match(self, course):
        regex_match = re.fullmatch(self._match_description, course) is not None
        if regex_match:
            regex_match = self._reject_description is None or re.fullmatch(self._reject_description, course) is None
        return regex_match
        
    
    def can_accept_children(self):
        return False
    
    def can_accept_fill_out(self):
        return True


    def get_shallow_description(self):
        description = self._printable_description or self._match_description
        if self._selected_course:
            description += f' [{self._selected_course}]'
        else:
            description += ' [NOT FILLED]'
        if self._credits is not None:
            description += f' - {self.get_shallow_credits()}'
        return description
    
    def matches_description(self, description):
        return super().matches_description(description) or self._match_description == description or self._selected_course == description

    def get_aggregate(self):
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''
        
        if not self.has_shallow_stub() and self.is_shallow_resolved():
            return [SchedulableItem(self._selected_course or self._printable_description)]
        else:
            return [SchedulableItem(self._stub_description or self._printable_description, is_stub=True)]

    def get_course_id(self):
        '''Return the unique ID this course represents or None if it is not concrete.'''
        return self._selected_course

    def reset_shallow_selection(self):
        super().reset_shallow_selection()
        self._selected_course = None
        self._credits = None

    def get_fill_out_state(self):
        return self._selected_course

    def _set_fill_out_state(self, argument):
        # This return the success of the fill out
        success = SELECTION
        if argument:
            if self.does_match(argument):
                if self._selected_course != argument:
                    self._selected_course = argument
                    success |= CHANGED
                else:
                    success |= UNCHANGED
            else:
                success |= NOT_SATISIFACTORY
        else:
            success = DESELECTION
            if self._selected_course is not None:
                self._selected_course = None
                success |= CHANGED
            else:
                success |= UNCHANGED
        return success
    
    def is_shallow_resolved(self):
        '''This should NOT use recursion and it does not indicate whether the tree is resolved.'''
        return self._selected_course is not None
    
    def get_shallow_count(self):
        return 1
    
    def get_shallow_credits(self):
        return self._credits or CourseProtocol.DEFAULT_CREDIT
    

class CourseInserter(_NodeSuper):

    GENERATORS_MAPPING = {
        'regex_course_protocol_generator': regex_course_protocol_generator,
        'disabled': None
    }

    KEY_VALUE_DICT = {
        'name': '_printable_description',
        'instructions': '_verbose_instructions',
        'generator parameter': '_generator_parameter',
        'aux parameter': '_aux_generator_parameter',
        'generator': '_generator_name'
    }

    KEYS_LIST = ['name', 'instructions', 'generator parameter', 'aux parameter', 'generator']
    NON_NIL_KEYS = {'name', 'generator'}
    INTEGER_KEYS = {'duplicate priority'}

    def __init__(self, printable_description=None, generator_parameter=r'.*',
                 node_generator_name='regex_course_protocol_generator'):
        super().__init__(printable_description, verbose_instructions='Select this to add a new course.')
        
        self._node_generator = None
        if node_generator_name in CourseInserter.GENERATORS_MAPPING:
            self._node_generator = CourseInserter.GENERATORS_MAPPING[node_generator_name]

        self._generator_parameter = generator_parameter
        self._aux_generator_parameter = None
        self._generator_name = node_generator_name
        
    
    def set_value_for_key(self, key, value):
        result = super().set_value_for_key(key, value)
        if self._generator_name in CourseInserter.GENERATORS_MAPPING:
            self._node_generator = CourseInserter.GENERATORS_MAPPING[self._generator_name]
        return result
    
    def can_accept_children(self):
        return False
    
    def can_be_stub(self):
        return False
    
    def get_shallow_description(self):
        return f'{self._printable_description or "Course Insertion"} [select to insert]'

    def selection_new_node_generation(self):
        node = None
        if self._node_generator is not None:
            node = self._node_generator(self._generator_parameter, self._aux_generator_parameter)
        return node
    
    def get_shallow_count(self):
        return inf
    
    def get_shallow_credits(self):
        return inf
        

class ListingNode(_NodeSuper):

    # TODO: allow for more overrides to make this node more optimized!

    KEY_VALUE_DICT = {
        'name': '_printable_description',
        'instructions': '_verbose_instructions'
    }

    KEYS_LIST = ['name', 'instructions']
    NON_NIL_KEYS = {'name'}
    INTEGER_KEYS = set()
    
    def __init__(self, printable_description=None):
        super().__init__(printable_description)
        self._duplicate_priority = 0

    def can_be_stub(self):
        return False

    def get_shallow_description(self):
        return self._printable_description or 'Listing section'

    def get_deep_description(self, depth=0, is_selected=False, maximum_depth=-1):
        result = f'{depth*"   "}+ {self.get_shallow_description()} [{self.get_all_layer_count()} item(s)]'
        return result
    
    # def get_layer_description(self):
    #     # TODO: Redo
    #     description = None

    #     if self.get_all_children_count() != 0:
    #         description = self.get_deep_description(maximum_depth=1)
    #     else:
    #         description = self.get_shallow_description()
    #         if self.can_accept_children():
    #             description += ' (empty)'
        
    #     instructions = self.get_verbose_instructions()
    #     if instructions is not None:
    #         description += '\nABOUT: ' + instructions

    #     return description
    
    def get_active_children_ids(self):
        '''Get a copy of the ordered list of children IDs that are selected.'''
        return self.get_all_children_ids()

    def get_aggregate(self):
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''
        result = []
        for child in self.get_all_children_list():
            result += child.get_aggregate()
        return result

    def select_child(self, node):
        return SELECTION | UNCHANGED
    
    def deselect_child(self, node):
        return DESELECTION | ILLEGAL
    
    def has_shallow_stub(self):
        return False


class _GroupNode(_NodeSuper):

    GENERATORS_MAPPING = {
        'credit_stub_generator': default_stub_generator,
    }

    def set_value_for_key(self, key, value):
        result = super().set_value_for_key(key, value)
        self._refresh_generator()
        return result

    def _refresh_generator(self):
        if self._stub_generator_name in _GroupNode.GENERATORS_MAPPING:
            self._stub_generator = _GroupNode.GENERATORS_MAPPING[self._stub_generator_name]

class ExhaustiveNode(_GroupNode):

    KEY_VALUE_DICT = {
        'name': '_printable_description',
        'instructions': '_verbose_instructions',
        'count bottleneck': '_max_count_propogation',
        'credits bottleneck': '_max_credits_propogation',
        'duplicate priority': '_duplicate_priority'
    }

    KEYS_LIST = ['name', 'instructions', 'count bottleneck', 'credits bottleneck', 'duplicate priority']
    NON_NIL_KEYS = {'name'}
    INTEGER_KEYS = {'count bottleneck', 'credits bottleneck', 'duplicate priority'}
    
    def __init__(self, printable_description=None):
        super().__init__(printable_description)

    def can_be_stub(self):
        return False

    def get_shallow_description(self):
        return self._printable_description or 'Requirment section'
    
    def get_active_children_ids(self):
        '''Get a copy of the ordered list of children IDs that are selected.'''
        return self.get_all_children_ids()

    def get_aggregate(self):
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''
        result = []
        for child in self.get_all_children_list():
            result += child.get_aggregate()
        return result

    def select_child(self, node):
        result = SELECTION | UNCHANGED
        node_id = node._node_id
        if node_id in self.get_all_children_ids():
            generation_node = node.selection_new_node_generation()
            if generation_node is not None:
                self.add_child(generation_node)
                self._destructive_selection.add(generation_node._node_id)
                result |= GENERATION
        return result
    
    def deselect_child(self, node):  
        result = DESELECTION
        node_id = node._node_id
        if self.is_selecting_node_id(node_id):
            if node_id in self._destructive_selection:
                if self.remove_child(node_id):
                    self._destructive_selection.remove(node_id)
                    result |= CHANGED
                else:
                    result |= UNCHANGED
            else:
                result |= ILLEGAL
        else:
            result |= CHILD_NOT_FOUND
        return result
    

    def has_shallow_stub(self):
        return False
    
class ShallowCountBasedNode(_GroupNode):

    KEY_VALUE_DICT = {
        'name': '_printable_description',
        'instructions': '_verbose_instructions',
        'count': '_requisite_count',
        'count bottleneck': '_max_count_propogation',
        'credits bottleneck': '_max_credits_propogation',
        'generator name': '_stub_generator_name',
        'generator parameter': '_generator_parameter',
        'aux parameter': '_aux_generator_parameter',
        'duplicate priority': '_duplicate_priority'
    }

    KEYS_LIST = ['name', 'instructions', 'count', 'count bottleneck', 'credits bottleneck',
    'generator name', 'generator parameter', 'aux parameter', 'duplicate priority']
    NON_NIL_KEYS = {'name', 'count', 'generator name'}
    INTEGER_KEYS = {'count', 'count bottleneck', 'credits bottleneck', 'duplicate priority'}
    
    
    def __init__(self, requisite_count=1, printable_description=None, stub_generator_name='credit_stub_generator'):
        super().__init__(printable_description)
        self._requisite_count = requisite_count

        self._stub_generator_name = stub_generator_name
        self._refresh_generator()
        self._generator_parameter = None
        self._aux_generator_parameter = None
        

    def get_shallow_description(self):
        result = self._printable_description or "Section"
        if self._requisite_count != 0:
            count = sum(course.get_shallow_count() for course in self.get_active_children_list())
            count_string = None
            if count != inf:
                count_string = str(count)
            else:
                count_string = f'{self._requisite_count}+'
            result += f' [{count_string} / {self._requisite_count} selections]'
        return result
    
    def get_aggregate(self):
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''

        result = []

        if not self.has_shallow_stub():
            for child in self.get_active_children_list():
                result += child.get_aggregate()
        else:
            for _ in  range(self._requisite_count):
                new_schedulable = self._stub_generator(self._generator_parameter, self._aux_generator_parameter)
                result.append(new_schedulable)
        
        return result
    
    def can_be_shallow_resolved(self):
        count = sum(course.get_shallow_count() for course in self.get_all_children_list())
        return count >= self._requisite_count
    
    def is_shallow_resolved(self):
        return len(self._selection) >= self._requisite_count
    
    
class DeepCountBasedNode(_GroupNode):
    
    KEY_VALUE_DICT = {
        'name': '_printable_description',
        'instructions': '_verbose_instructions',
        'count': '_requisite_count',
        'count bottleneck': '_max_count_propogation',
        'credits bottleneck': '_max_credits_propogation',
        'generator name': '_stub_generator_name',
        'generator parameter': '_generator_parameter',
        'aux parameter': '_aux_generator_parameter',
        'duplicate priority': '_duplicate_priority'
    }

    KEYS_LIST = ['name', 'instructions', 'count', 'count bottleneck', 'credits bottleneck',
    'generator name', 'generator parameter', 'aux parameter', 'duplicate priority']
    NON_NIL_KEYS = {'name', 'count', 'generator name'}
    INTEGER_KEYS = {'count', 'count bottleneck', 'credits bottleneck', 'duplicate priority'}
    
    def __init__(self, requisite_count=1, printable_description=None, stub_generator_name='credit_stub_generator'):
        super().__init__(printable_description)
        self._requisite_count = requisite_count

        self._stub_generator_name = stub_generator_name
        self._refresh_generator()
        self._generator_parameter = None
        self._aux_generator_parameter = None
    
    def get_shallow_description(self):
        result = self._printable_description or "Section"
        if self._requisite_count != 0:
            count = self.get_active_layer_count()
            count_string = None
            if count != inf:
                count_string = str(count)
            else:
                count_string = f'{self._requisite_count}+'
            result += f' [{count_string} / {self._requisite_count} courses]'
        return result

    def get_aggregate(self):
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''

        result = []

        if not self.has_shallow_stub():
            for child in self.get_active_children_list():
                result += child.get_aggregate()
        else:
            for _ in  range(self._requisite_count):
                new_schedulable = self._stub_generator(self._generator_parameter, self._aux_generator_parameter)
                result.append(new_schedulable)
        
        return result
        
    def can_be_shallow_resolved(self):
        return self.get_all_layer_count() >= self._requisite_count

    def is_shallow_resolved(self):
        # TODO: remove print
        # print(self._printable_description, self.get_active_deep_count() >= self._requisite_count, self.get_active_deep_count(), self._requisite_count)
        return self.get_active_layer_count() >= self._requisite_count

    def is_discovery_resolved(self):
        result = True
        if not self.has_shallow_stub():
            sum = self.get_active_layer_count()
            # # TODO: remove print
            # print(self._printable_description)
            # for child in self.get_active_children_list():
            #     sum += child.get_all_deep_count()
            #     # TODO: remove print
            #     print(child._printable_description, child.get_all_deep_count())
            # # TODO: remove print
            # print("SUM         ", sum)
            result = sum >= self._requisite_count
        return result
    
class DeepCreditBasedNode(_GroupNode):

    KEY_VALUE_DICT = {
        'name': '_printable_description',
        'instructions': '_verbose_instructions',
        'credits': '_requisite_credits',
        'count bottleneck': '_max_count_propogation',
        'credits bottleneck': '_max_credits_propogation',
        'generator name': '_stub_generator_name',
        'generator parameter': '_generator_parameter',
        'aux parameter': '_aux_generator_parameter',
        'duplicate priority': '_duplicate_priority'
    }

    KEYS_LIST = ['name', 'instructions', 'credits', 'count_bottleneck', 'credits_bottleneck',
    'generator name', 'generator parameter', 'aux parameter', 'duplicate priority']
    NON_NIL_KEYS = {'name', 'credits', 'generator name'}
    INTEGER_KEYS = {'credits', 'count bottleneck', 'credits bottleneck', 'duplicate priority'}
    
    def __init__(self, requisite_credits, printable_description=None, stub_generator_name='credit_stub_generator'):
        super().__init__(printable_description)
        self._requisite_credits = requisite_credits

        self._stub_generator_name = stub_generator_name
        self._refresh_generator()
        self._generator_parameter = None
        self._aux_generator_parameter = None
    

    def get_aggregate(self):
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''
        result = []
        if not self.has_shallow_stub():

            for child in self.get_active_children_list():
                result += child.get_aggregate()
        else:
            running_credits = 0
            fail_safe = 100 # TODO: find a logical way of implementing this
            while running_credits < self._requisite_credits and fail_safe > 0:
                new_schedulable = self._stub_generator(self._generator_parameter, self._aux_generator_parameter)
                result.append(new_schedulable)
                running_credits += new_schedulable.get_stub_credit()
                fail_safe -= 1
        return result
        
    def get_shallow_description(self):
        result = self._printable_description or "Section"
        if self._requisite_credits != 0:
            credits = self.get_active_layer_credits()
            credits_string = None
            if credits != inf:
                credits_string = str(credits)
            else:
                credits_string = f'{self._requisite_credits}+'
            result += f' [{credits_string} / {self._requisite_credits} credit]'
        return result

    def can_be_shallow_resolved(self):
        return self.get_all_layer_credits() >= self._requisite_credits
    
    def is_shallow_resolved(self):
        return self.get_active_layer_credits() >= self._requisite_credits

    def is_discovery_resolved(self):
        result = True
        if not self.has_shallow_stub():
            sum = self.get_active_layer_credits()
            # for child in self.get_active_children_list():
            #     sum += child.get_all_deep_credits()
            result = sum >= self._requisite_credits
        return result
    
    

class CoursesNeededContainer:
    
    def __init__(self, degree_plan, certain_courses_list=None, decision_tree=None):
        self._degree_plan = degree_plan
        self._certain_courses_list = certain_courses_list if certain_courses_list is not None else []
        self._decision_tree = decision_tree or ExhaustiveNode()

        # TODO: perform this using a good practice
        self._decision_tree._duplicate_priority = DEFAULT_PRIORITY
    
    def __iter__(self):
        return self.get_courses_set().__iter__()
    
    # def __getitem__(self, index):
    #     # TODO: this might be bad practice because access is not complete and, therefore, may lead to erroneous loops
    #     return self.course_list[index]
    
    def pickle(self):
        return pickle.dumps(self)
    
    def get_degree_plan(self):
        return self.degree_plan

    def get_courses_set(self):
        '''Get a set containing all courses and a bool indicating if the listing is stub-free.'''
        if not self.is_resolved(self):
            raise ValueError('Attempted to aggregate course list with unresolved tree. Check tree status using "is_resolved()"')
        result = set(self._certain_courses_list)
        result = result.union(self._decision_tree.get_aggregate())
        is_stubbed_free = not self._decision_tree.has_deep_stub()
        return result, is_stubbed_free
        
    def get_certain_courses(self):
        return self.certain_courses_list
    
    def add_certain_course(self, course):
        added = False
        if course not in self.certain_courses_list:
            self.certain_courses_list.append(course)
            added = True
        return added
        
    def get_decision_tree(self):
        return self._decision_tree
    
    def add_top_level_node(self, node):
        return self._decision_tree.add_child(node)
    
    def is_resolved(self):
        return self._decision_tree.is_deep_resolved()

    def select_courses_as_taking(self, courses):
        for course in courses:
            self._decision_tree.deep_select_child_by_description(course)

    


class DummyController:
    def __init__(self):
        self.stack = []
        self.is_printing = True
        
    def output(self, message):
        if self.is_printing:
            print(message)
    
    def output_error(self, message):
        if self.is_printing:
            print(f'ERROR: {message}')
    
    def output_warning(self, message):
        if self.is_printing:
            print(f'WARNING: {message}')
    
    def get_current_interface(self):
#        print("stack", [e for e in self.stack])
#        print("stack_id", [e._node._node_id for e in self.stack])
#        print("top", self.stack[-1]._node._node_id)
        return self.stack[-1]
    
    def push_interface(self, interface):
        self.stack.append(interface)
        interface.was_pushed(self)

    def pop_interface(self, interface):
        if self.stack[-1] is interface:
            self.stack.pop()
            interface.deconstruct(self)
            return True
        else:
            raise ValueError()


if __name__ == '__main__':
    tree = ExhaustiveNode()
    
    controller = DummyController()
    controller.is_printing = False
    controller.push_interface(NeededCoursesInterface(tree))
    
    controller.get_current_interface().parse_input(controller, 'asc count = 1, name = Area A, duplicate priority = 10')
    controller.get_current_interface().parse_input(controller, 'asc count = 2, name = Area B, duplicate priority = 20')
    controller.get_current_interface().parse_input(controller, 'acr credits = 3, name = Area C, duplicate priority = 30')
    controller.get_current_interface().parse_input(controller, 'cd 1')
    controller.get_current_interface().parse_input(controller, 'ad name = 1000, credits = 3')
    controller.get_current_interface().parse_input(controller, 'ad name = 1001, credits = 3')
    controller.get_current_interface().parse_input(controller, 'ad name = 1002, credits = 3')
    controller.get_current_interface().parse_input(controller, 'ap name = 11@, matching=11[0-9]{2}')
    controller.get_current_interface().parse_input(controller, '..')
    controller.get_current_interface().parse_input(controller, 'cd 2')
    controller.get_current_interface().parse_input(controller, 'ad name = 2000, credits = 3')
    controller.get_current_interface().parse_input(controller, 'ad name = 2001, credits = 3')
    controller.get_current_interface().parse_input(controller, 'ad name = 2002, credits = 4')
    controller.get_current_interface().parse_input(controller, 'ad name = 1000, credits = 3')
    controller.get_current_interface().parse_input(controller, '..')
    controller.get_current_interface().parse_input(controller, 'cd 3')
    controller.get_current_interface().parse_input(controller, 'ad name = 3000, credits = 0')
    controller.get_current_interface().parse_input(controller, 'ad name = 3001, credits = 1')
    controller.get_current_interface().parse_input(controller, 'ad name = 3002, credits = 2')
    controller.get_current_interface().parse_input(controller, 'ad name = 3003, credits = 3')
    controller.get_current_interface().parse_input(controller, 'ad name = 3004, credits = 4')
    controller.get_current_interface().parse_input(controller, 'ad name = 4001, credits = 1')
    controller.get_current_interface().parse_input(controller, 'ad name = 4002, credits = 2')
    controller.get_current_interface().parse_input(controller, '..')

    
    controller.get_current_interface().parse_input(controller, 'cd 1')
    controller.get_current_interface().parse_input(controller, 'adc name=Education, count=4')
    controller.get_current_interface().parse_input(controller, 'cd Education')
    controller.get_current_interface().parse_input(controller, 'adc name=Core, count=2, count_bottleneck=3')
    controller.get_current_interface().parse_input(controller, 'ad name=ED 1000')
    controller.get_current_interface().parse_input(controller, 'ad name=ED 1001')
    controller.get_current_interface().parse_input(controller, 'ad name=ED 1002')
    controller.get_current_interface().parse_input(controller, 'ad name=ED 1003')
    controller.get_current_interface().parse_input(controller, 'cd Core')
    controller.get_current_interface().parse_input(controller, 'ad name=CR 1000')
    controller.get_current_interface().parse_input(controller, 'ad name=CR 1001')
    controller.get_current_interface().parse_input(controller, 'ad name=CR 1002')
    controller.get_current_interface().parse_input(controller, 'ad name=CR 1003')
    controller.get_current_interface().parse_input(controller, 'ad name=3000')
    controller.get_current_interface().parse_input(controller, 'ad name=3002')
    controller.get_current_interface().parse_input(controller, '..')
    controller.get_current_interface().parse_input(controller, '..')
    controller.get_current_interface().parse_input(controller, '..')
    

    controller.get_current_interface().parse_input(controller, 'asc name=General, count=5, duplicate priority = 100')
    controller.get_current_interface().parse_input(controller, 'cd -1')
    controller.get_current_interface().parse_input(controller, r'ai generator parameter =[0-9]{3}, aux parameter = 3-credit Course')
    controller.get_current_interface().parse_input(controller, r'ai generator parameter =[0-9]{4}, aux parameter = 4-credit Course')
    controller.get_current_interface().parse_input(controller, '..')

    # controller.get_current_interface().parse_input(controller, 'ap name=B, matching=12.*')
    # controller.get_current_interface().parse_input(controller, 'ad name=1234')

    controller.get_current_interface().parse_input(controller, 'ap name = @99@, matching=[0-9]*99[0-9]*')

    # controller.get_current_interface().parse_input(controller, 'acr name=Credit Group, count=9')
    # controller.get_current_interface().parse_input(controller, 'cd Credit Group')
    # controller.get_current_interface().parse_input(controller, 'acr name=Credit Group, count=9')
    # controller.get_current_interface().parse_input(controller, 'acr name=Credit Group, count=9')

    controller.is_printing = True
    running = True
    while running:
        
#        print("current:", controller.get_current_interface()._node._node_id)
        #i = input(f'\033[93m> ')
        i = input('> ')

        # TODO: add this in somewhere for better printing
        # if os.name == 'nt':
        #     os.system('cls')
        # else:
        #     os.system('clear')
        
        running = i != 'quit'
        if running:
            top = controller.get_current_interface()
            top.parse_input(controller, i)
