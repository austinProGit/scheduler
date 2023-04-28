# Thomas Merino and Austin Lee
# 2/19/2023
# CPSC 4176 Project

from requirement_tree import *
from menu_interface_base import GeneralInterface
from help_interface import HelpMenu

# NOTE:
# This will NOT place courses intellgently if one group has a higher priority than another. This might require
# another method that trickles unneeded courses to lower priority groups to meet other requirements.

# In the event a list of courses are fed into the tree and there are multiple protocol nodes that satisfy the same ^


# TODO: Indented means possibly completed, but not thoroughly checked/tested.
    # have argument parsing ignore commas between parenthesis/bracket/brace pairs
    # Add copy and paste commands
    # Add automatic movement (to resolve all)
    # Fix traversal state starting funny
    # make traversal move print ls
    # Implement the certain course list with listing node
    # Add checks to see if the entered input is empty (string)
    # Fix the global selection (have it work for deselecting and fill outs)
    # add parameters to groups for stub generators
    # Fix validate not recognizing insertion nodes
    # Fix count filter and add credit filter
    # Enforce there being no course of the same name being filled out in a given group node (one instance per layer)
    # Check selection across whole tree (registering course A in one place selects it in other places in the tree)
    # place in the container

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
# Script nodes (even more freedom)
# Add undo (undo command and move back to working node if moved automatically)
# give container method to return all possible permutations of selections
# cannot delete multiple items (need to account for changing indices as list mutates)
# cannot copy/cut/paste multiple items
# -> Add method to return easily printable objects
# -> Already-taken filter (remove certain specified courses from aggregate)

USER_COMMAND_LIST = '''Available commands: move, back, quit, home, show, show-all, show-down, depth, info, select, \
fill, deselect, deselect-layer, deselect-all, deselect-down, stub, stub-layer, stub-top, unstub, unstub-layer, \
unstub-all, unstub-down, aggregate, admin, user, clear, clear-mode, traversal'''
ADMIN_COMMAND_LIST = '''add-exhaustive, add-deliverable, add-protocol, add-shallow-count, add-deep-count, \
add-deep-credit, add-inserter, delete, modify, validate, copy, cut, paste'''


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


MAX_LINE_LENGTH = 80


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
        top_interface = controller.get_current_interface()
        if isinstance(top_interface, NeededCoursesInterface):
            top_interface.enter_from_submenu(controller, 'Leaving modification menu.')
        else:
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
        # TODO: bad access of private
        controller.output(f'Enter you course number for "{self._node._printable_description}" or enter cancel:')
    
    def deconstruct(self, controller):
        '''Destruction method that is called upon the interface being dismissed.'''
        top_interface = controller.get_current_interface()
        if isinstance(top_interface, NeededCoursesInterface):
            top_interface.enter_from_submenu(controller, 'Leaving fill out menu.')
        else:
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
            if course_id is not None:
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
        elif result == DUPLICATE:
            controller.output_error(f'A item already set to "{value}" already exists on this layer.')
        else:
            raise ValueError('Illegal state change result')
            
        

class NeededCoursesInterface(GeneralInterface):
    
    def __init__(self, node, root_interface=None, depth=0, is_traverse_mode=False, clears_screen=CONSTANT_REFRESHING):
        self.name = 'COURSE SELECTION' # TODO: this needs to change by edit mode status (maybe via property: setters and getters)
        self._node = node
        self._root_interface = root_interface or self
        self._depth = depth
        self._is_traverse_mode = is_traverse_mode
        self._clears_screen = clears_screen

        self._admin_commands = {}
        self._user_commands = {}
        self._commands = self._user_commands
        self._clipboard_node = None
        self._in_edit_mode = False
        
        self._print_queue = []

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
        self.add_command(self.navigate_back, 'back', 'prev', 'previous')
        self.add_command(self.navigate_to_root, 'root', 'home', 'base')
        self.add_command(self.navigate_exit, 'exit', 'quit', 'done', 'leave')
                
        self.add_command(self.show_all, 'show-all', 'display-all', 'map')
        self.add_command(self.show_here, 'show-here', 'display-here', 'show', 'display', 'list', 'ls')
        self.add_command(self.show_down, 'show-down', 'displayx-down', 'down')
        self.add_command(self.show_depth, 'show-depth', 'display-depth', 'depth')
        self.add_command(self.show_info, 'show-info', 'info', 'instructions')
        
        self.add_command(self.select_course, 'select', 'choose', 's')
        self.add_command(self.fill_out_course, 'fill', 'fill-out', 'f')
        self.add_command(self.deselect_course, 'deselect', 'd')
        self.add_command(self.deselect_layer, 'deselect-layer', 'd-layer')
        self.add_command(self.deselect_all, 'deselect-all')
        self.add_command(self.deselect_down, 'deselect-down', 'd-down')
                
        self.add_command(self.stub_course, 'stub', 't')
        self.add_command(self.stub_layer, 'stub-layer', 't-layer')
        self.add_command(self.stub_all_top, 'stub-top', 't-top')
        self.add_command(self.unstub_course, 'unstub', 'u')
        self.add_command(self.unstub_layer, 'unstub-layer', 'u-layer')
        self.add_command(self.unstub_all, 'unstub-all')
        self.add_command(self.unstub_down, 'unstub-down', 'u-down')

        self.add_command(self.aggregate, 'aggregate', 'pull')
        self.add_command(self.admin_mode, 'admin', 'sudo')
        self.add_command(self.user_mode, 'user', 'student')
        self.add_command(self.clear, 'clear', 'c')
        self.add_command(self.set_clear_mode, 'toggle-clear', 'clear-mode', 'clearing')
        self.add_command(self.toggle_traversal_mode, 'traversal', 'travel', 'auto', 't')

        self.add_command(self.push_help, 'help', 'h')
        
        # Admin-level:
        self._admin_commands = self._commands.copy()
        self._commands = self._admin_commands
        
        self.add_command(self.add_exhaustive, 'add-exhaustive', 'aex', 'ae')
        self.add_command(self.add_deliverable, 'add-deliverable', 'ade', 'ad')
        self.add_command(self.add_protocol, 'add-protocol', 'apr', 'ap')
        self.add_command(self.add_shallow_count, 'add-shallow-count', 'asc', 'asn')
        self.add_command(self.add_deep_count, 'add-deep-count', 'adc', 'adn')
        self.add_command(self.add_deep_credit, 'add-deep-credit', 'add-credit', 'acr')
        self.add_command(self.add_inserter, 'add-inserter', 'ains', 'ai')
        
        self.add_command(self.delete_node, 'delete', 'del')
        self.add_command(self.modify_node, 'rename', 'modify', 'change', 'edit', 'm', 'mod')
        self.add_command(self.validate_tree, 'validate', 'valid')
        
        self.add_command(self.copy_node, 'copy', 'c')
        self.add_command(self.cut_node, 'cut', 'x')
        self.add_command(self.paste_node, 'paste', 'v')

    def was_pushed(self, controller):
        '''Method that is called upon the interface being pushed onto the interface stack.'''
        if (self._is_in_traverse_mode()):
            self._check_for_traversal(controller)
        pass
    
    def deconstruct(self, controller):
        '''Destruction method that is called upon the interface being dismissed.'''
        top_interface = controller.get_current_interface()
        if isinstance(top_interface, NeededCoursesInterface):
            top_interface._clears_screen = self._clears_screen
        

    
    def print_commands(self, controller, argument):
        # TODO: handle arguments and refine printing
        command_list_string = USER_COMMAND_LIST
        if self._commands is self._admin_commands:
            command_list_string += ', ' + ADMIN_COMMAND_LIST
        self._add_print(command_list_string, UNCHECKED_PRINT)
        self._push_print(controller)
        
    def navigate_to_nodes(self, controller, argument):
        self._set_traversal_mode(False)

        if argument:
            self._add_clear_opportunity()
            self._add_ls()

            destinations = [destination.strip() for destination in argument.split(',')]
            current_interface = self

            while destinations:
                next_destination = destinations.pop(0)
                sucess, current_interface = current_interface._navigate_to_node(self, controller, next_destination)
                if not sucess:
                    destinations = []
                    break
        else:
            self._add_error('Please enter a group to navigate to.')
        
        self._push_print(controller)
                
    def navigate_back(self, controller, argument):
        self._set_traversal_mode(False)
        self._add_clear_opportunity()
        self._add_ls()
        self._navigate_back(controller)
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
        
    def navigate_to_root(self, controller, argument):
        self._set_traversal_mode(False)
        self._add_clear_opportunity()
        self._add_ls()
        self._navigate_to_root(controller)
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)

    def navigate_exit(self, controller, argument):
        self._set_traversal_mode(False)
        self._navigate_to_root(controller)
        self._root_interface._navigate_back(controller)

    
    def show_all(self, controller, argument):
        self._add_clear_opportunity()
        self._add_print(self._get_root_interface()._node.get_deep_description(indicate_node=self._node))
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
    
    def show_here(self, controller, argument):
        if not argument:
            self._add_clear_opportunity()
            self._add_ls()
        else:
            self.show_info(controller, argument)
        self._push_print(controller)
    
    def show_down(self, controller, argument):
        self._add_clear_opportunity()
        self._add_print(self._node.get_deep_description())
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
        
    def show_depth(self, controller, argument):
        self._add_print_warning_if_arguments(argument)
        controller.output(f'Layer depth: {self._depth + 1}')
        self._push_print(controller)
    
    def show_info(self, controller, argument):
        if not argument:
            self._add_clear_opportunity()
            self._add_ls()
        else:
            child = self._get_child(argument)
            if child is not None:
                self._add_print(child.get_layer_description())
            else:
                self._add_error(f'No item immediately below matches that description "{argument}".')
        self._push_print(controller)
    
    
    def select_course(self, controller, argument):

        if argument:
            self._add_refresh_opportunity()
            for course_description in [course.strip() for course in argument.split(',')]:
                self._select_course(course_description)
            self._push_print(controller)
            self._check_for_traversal(controller)
        else:
            self._add_error('Please enter a course or courses to select.')
            self._push_print(controller)
        
    def fill_out_course(self, controller, argument):

        if argument:
            child = self._get_child(argument)
            if child is not None:
                if child.can_accept_fill_out():
                    self._add_clear_opportunity()
                    self._push_print(controller)
                    controller.push_interface(FillOutInterface(root=self._get_root_node(), parent_node=self._node, node=child))
                else:
                    self._add_error('This item cannot be filled out.')
                    self._push_print(controller)
            else:
                self._add_error(f'No item immediately below matches the description "{argument})".')
                self._push_print(controller)
        else:
            self._add_error('Please enter a course to fill.')
            self._push_print(controller)
            
    
    def deselect_course(self, controller, argument):
        self._add_refresh_opportunity()
        if argument:
            for course_description in [course.strip() for course in argument.split(',')]:
                self._deselect_course(course_description)
        else:
            self._add_error('Please enter a course or courses to deselect.')
        self._push_print(controller)

        
    def deselect_layer(self, controller, argument):
        self._add_refresh_opportunity()
        self._add_print('Entire layer deselected (those possible).')
        self._node.reset_shallow_selection()
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
        
    def deselect_all(self, controller, argument):
        self._add_refresh_opportunity()
        self._get_root_interface()._node.reset_deep_selection()
        self._add_print('All items deselected (those possible).')
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
                
    def deselect_down(self, controller, argument):
        self._add_refresh_opportunity()
        self._node.reset_deep_selection()
        self._add_print('All items deselected downward (those possible).')
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
        
        
        
    def stub_course(self, controller, argument):
        if argument:
            self._add_refresh_opportunity()
            stub_result = RESULT & self._node.enable_child_stub_by_description(argument)
            self._report_stub_enable(stub_result, argument)
            self._push_print(controller)
            self._check_for_traversal(controller)
        else:
            self._add_error('Please enter a course or group to stub.')
            self._push_print(controller)

                
    def stub_layer(self, controller, argument):
        self._add_refresh_opportunity()
        stub_result = RESULT & self._node.enable_stub()
        self._report_stub_enable(stub_result, 'self')
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
        self._check_for_traversal(controller)
            
    def stub_all_top(self, controller, argument):
        self._add_refresh_opportunity()
        for node in self._get_root_node().get_all_children_list():
            node.enable_stub()
        self._add_print('All applicable top-layer nodes stub-enabled.')
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
        self._check_for_traversal(controller)
        
        
    def unstub_course(self, controller, argument):
        self._add_refresh_opportunity()
        if argument:
            stub_result = RESULT & self._node.disable_child_stub_by_description(argument)
            self._report_stub_disable(stub_result, argument)
        else:
            self._add_error('Please enter a course or group to unstub.')
        self._push_print(controller)

    def unstub_layer(self, controller, argument):
        self._add_refresh_opportunity()
        stub_result = RESULT & self._node.disable_stub()
        self._report_stub_enable(stub_result, 'self')
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
        
    def unstub_all(self, controller, argument):
        self._add_refresh_opportunity()
        self._get_root_interface()._node.reset_deep_stub()
        self._add_print('All applicable stubs reset.')
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
                
    def unstub_down(self, controller, argument):
        self._add_refresh_opportunity()
        self._node.reset_deep_stub()
        self._add_print('All applicable stubs removed downward.')
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
        
        
    def add_exhaustive(self, controller, argument):
        self._add_refresh_opportunity()
        new_node = ExhaustiveNode()
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(argument, new_node)
            self._add_print('Group added.')
        else:
            self._add_error('The group could not be added.')
        self._push_print(controller)
    
        
    def add_deliverable(self, controller, argument):
        self._add_refresh_opportunity()
        new_node = DeliverableCourse(printable_description='New Course', credits=3)
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(argument, new_node)
            self._add_print('Course added.')
        else:
            self._add_error('The course could not be added.')
        self._push_print(controller)
    
    
    def add_protocol(self, controller, argument):
        self._add_refresh_opportunity()
        # TODO: fix this default (does not work)
        new_node = CourseProtocol(match_description=r'[A-Z]{4,5}\s?[0-9]{4}[A-Z]?', printable_description='New Course Protocol', credits=3)
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(argument, new_node)
            self._add_print('Course added.')
        else:
            self._add_error('The course could not be added.')
        self._push_print(controller)
        
    
    def add_shallow_count(self, controller, argument):
        self._add_refresh_opportunity()
        new_node = ShallowCountBasedNode(requisite_count=1)
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(argument, new_node)
            self._add_print('Group added.')
        else:
            self._add_error('The group could not be added.')
        self._push_print(controller)
    
                
    def add_deep_count(self, controller, argument):
        self._add_refresh_opportunity()
        new_node = DeepCountBasedNode(requisite_count=1)
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(argument, new_node)
            self._add_print('Group added.')
        else:
            self._add_error('The group could not be added.')
        self._push_print(controller)
    
    def add_deep_credit(self, controller, argument):
        self._add_refresh_opportunity()
        new_node = DeepCreditBasedNode(requisite_credits=3)
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(argument, new_node)
            self._add_print('Group added.')
        else:
            self._add_error('The group could not be added.')
        self._push_print(controller)
    
    def add_inserter(self, controller, argument):
        self._add_refresh_opportunity()
        new_node = CourseInserter(generator_parameter=r'[A-Z]{4,5}\s?[0-9]{4}[A-Z]?', printable_description='Insert New')
        if self._node.add_child(new_node):
            self._apply_constructor_arguments(argument, new_node)
            self._add_print('Inserter added.')
        else:
            self._add_error('The inserter could not be added.')
        self._push_print(controller)
        
    def delete_node(self, controller, argument):
        self._add_refresh_opportunity()
        if argument:
            self._delete_node(argument)
        else:
            self._add_error('Please enter a course or group to delete.')
        self._push_print(controller)

    def copy_node(self, controller, argument):
        self._add_refresh_opportunity()
        if argument:
            child = self._get_child(argument)
            if child is not None:
                self._copy_to_clipboard(child)
            else:
                self._add_error(f'No item immediately below matches the description "{argument})".')
        else:
            self._copy_to_clipboard(self._node)
        self._push_print(controller)


    def cut_node(self, controller, argument):
        self._add_refresh_opportunity()
        if argument:
            child = self._get_child(argument)
            if child is not None:
                self._cut_to_clipboard(child)
            else:
                self._add_error(f'No item immediately below matches the description "{argument})".')
        else:
            self._add_error('Please enter a course or group to cut.')
        self._push_print(controller)

    def paste_node(self, controller, argument):
        self._add_refresh_opportunity()
        if argument:
            child = self._get_child(argument)
            if child is not None:
                self._paste_from_clipboard(child)
            else:
                self._add_error(f'No item immediately below matches the description "{argument})".')
        else:
            self._paste_from_clipboard(self._node)
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)


    def modify_node(self, controller, argument):
        if not argument:
            self._add_clear_opportunity()
            self._push_print(controller)
            controller.push_interface(ArgumentInputInterface(self._node))
        else:
            child = self._get_child(argument)
            if child:
                self._add_clear_opportunity()
                self._push_print(controller)
                controller.push_interface(ArgumentInputInterface(child))
            else:
                self._add_error(f'No item immediately below matches the description "{argument}".')
            self._push_print(controller)
        

    def aggregate(self, controller, argument):
        self._add_refresh_opportunity()
        # TODO: this is temp
        self._add_print(f'Is resolved: {self._get_root_node().is_deep_resolved()}')
        self._add_print([e.course_description for e in self._get_root_node().get_aggregate()])
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
        

    
    def validate_tree(self, controller, argument):

        self._add_refresh_opportunity()

        node = None
        if not argument:
            node = self._get_root_node()
        else:
            node = self._node.get_child_by_description(argument)

        if node is not None:
            if node.can_be_deep_resolved():
                self._add_print('The requirement structure appears to be satisfiable.')
            else:
                trace = self._get_root_node().get_first_non_resolvable_stacktrace()
                trace = " -> ".join([f'|{index}: {node.get_shallow_description()}|' for (index, node) in trace])
                self._add_print(f'Problem at: {trace}')
        else:
            self._add_error('Entry point for validation not found.')
        self._push_print(controller)
        
    
    def admin_mode(self, controller, argument):
        self._add_refresh_opportunity()
        self._add_print_warning_if_arguments(argument)
        if self._commands is self._user_commands:
            self._commands = self._admin_commands
            self._add_print('Mode changed to admin mode.')
        else:
            self._add_error('Mode is already in admin mode.')
        self._push_print(controller)

    def user_mode(self, controller, argument):
        self._add_refresh_opportunity()
        self._add_print_warning_if_arguments(argument)
        if self._commands is self._admin_commands:
            self._commands = self._user_commands
            self._add_print('Mode changed to user mode.')
        else:
            self._add_error('Mode is already in user mode.')
        self._push_print(controller)

    def toggle_traversal_mode(self, controller, argument):
        if argument:

            self._add_refresh_opportunity()
            if argument in {'no', 'off', 'none', 'disable', 'disabled'}:
                self._set_traversal_mode(not self._is_traverse_mode)
                self._add_print('Traversal mode turned off.')
            elif argument in {'yes', 'on', 'enable', 'enabled'}:
                self._set_traversal_mode(not self._is_traverse_mode)
                self._add_print('Traversal mode turned on.')
            else:
                self._add_error('No mode matches passed description (use "on", "off").')
            self._push_print(controller)
            self._check_for_traversal(controller)
        
        else:
            if self._is_traverse_mode:
                self._add_print('Traversal mode set to on at the moment.')
            else:
                self._add_print('Traversal mode set to off at the moment.')
            self._push_print(controller)



    def clear(self, controller, argument):
        self._add_clear()
        self._add_print_warning_if_arguments(argument)
        self._push_print(controller)
    
    def set_clear_mode(self, controller, argument):
        if argument:
            self._add_refresh_opportunity()
            if argument in {'no', 'none'}:
                self._clears_screen = NO_CLEARING
                self._add_print('Clearing mode changed to no clearning.')
            elif argument in {'navigation', 'nav', 'move'}:
                self._clears_screen = NAVIGATION_CLEARING
                self._add_print('Clearing mode changed to navigation clearing.')
            elif argument in {'refresh', 'refreshing', 'responsive', 'constant'}:
                self._clears_screen = CONSTANT_REFRESHING
                self._add_print('Clearing mode changed to constant refreshing.')
            else:
                self._add_error('No mode matches passed description (use "none", "navigation", or "refresh").')
            self._push_print(controller)

        else:
            if self._clears_screen == NO_CLEARING:
                self._add_print('Clearing mode is set to none at the moment.')
            elif self._clears_screen == NAVIGATION_CLEARING:
                self._add_print('Clearing mode is set to navigation at the moment.')
            elif self._clears_screen == CONSTANT_REFRESHING:
                self._add_print('Clearing mode is set to refresh at the moment.')
            else:
                raise ValueError('Illegal clearing state detected.')
            self._push_print(controller)

    def push_help(self, controller, arguments):
        new_help_interface = HelpMenu()
        controller.push_interface(new_help_interface)
        if arguments:
            new_help_interface.parse_input(controller, arguments)

    # --------------------------------------- Print Management Methods --------------------------------------- #

    def _add_print(self, message, message_type=PRINT):
        self._print_queue.append((message, message_type))

    def _add_error(self, message):
        self._print_queue.append((message, ERROR))

    def _add_warning(self, message):
        self._print_queue.append((message, WARNING))

    def _add_clear_opportunity(self):
        self._add_print('', POSSIBLE_SOFT_CLEAR)

    def _add_clear(self):
        self._add_print('', HARD_CLEAR)

    def _add_refresh_opportunity(self):
        self._add_print('', POSSIBLE_LS)
    
    def _add_ls(self):
        self._add_print('', HARD_LS)

    def _add_print_warning_if_arguments(self, argument):
        if argument:
            self._add_warning('Arguments are not processed for this command.')

    def _push_print(self, controller):

        while self._print_queue:
            message, message_type = self._print_queue.pop(0)
            if message_type == PRINT:
                self.output(controller, message)
            if message_type == UNCHECKED_PRINT:
                controller.output(message)
            elif message_type == ERROR:
                controller.output_error(message)
            elif message_type == WARNING:
                controller.output_warning(message)
            elif message_type == POSSIBLE_LS:
                if self._clears_screen == CONSTANT_REFRESHING:
                    controller.output_clear()
                    self._print_top_interface(controller)
            elif message_type == HARD_LS:
                self._print_top_interface(controller)
            elif message_type == POSSIBLE_SOFT_CLEAR:
                if self._clears_screen != NO_CLEARING:
                    controller.output_clear()
            elif message_type == HARD_CLEAR:
                controller.output_clear()
            else:
                ValueError('Illegal message type push.')
    
    def _print_top_interface(self, controller):
        top_interface = controller.get_current_interface()
        if isinstance(top_interface, NeededCoursesInterface):
            top_interface._print_ls(controller)
            
    def _print_ls(self, controller):
        self.output(controller, self._node.get_layer_description())

    def output(self, controller, message):
        for line in message.split('\n'):
            # TODO: this is not a clean implementation
            # tabs, for example, changes the distance more but is not reflected in the following measure
            is_long_line = len(line.replace('\t', '')) > MAX_LINE_LENGTH
            if not is_long_line:
                controller.output(line)
            else:
                controller.output(line[:MAX_LINE_LENGTH-2] + '...')

    def enter_from_submenu(self, controller, closing_message):
        self._add_clear_opportunity()
        self._add_refresh_opportunity()
        self._add_print(closing_message)
        self._push_print(controller)
        self._check_for_traversal(controller)

    # --------------------------------------- Control Getter Methods --------------------------------------- #

    def _get_root_node(self):
        return self._get_root_interface()._node
    
    def _get_child(self, description):
            return self._node.get_child_by_description(description)

    def _get_clipboard(self):
        return self._get_root_interface()._clipboard_node

    def _copy_to_clipboard(self, node):
        self._get_root_interface()._clipboard_node = node.make_deep_live_copy()
        self._add_print('Item copied.')
    
    def _cut_to_clipboard(self, node):
        copy = node.make_deep_live_copy()

        # TODO: bad method for getting node id
        if self._node.remove_child(node._node_id):
            self._get_root_interface()._clipboard_node = copy
            self._add_print('Item cut.')
        else:
            self._add_print('The item could not be cut (if you wish, you can still copy it).')
    
    def _paste_from_clipboard(self, to_node):
        clipboard_node = self._get_clipboard()
        if to_node.add_child(clipboard_node):
            self._add_print('Item pasted.')

            # Make another copy in case the user wants to paste again
            self._get_root_interface()._clipboard_node = clipboard_node.make_deep_live_copy()
        else:
            self._add_error('The item could not be pasted.')


    # --------------------------------------- Selection and Configuring Helpers --------------------------------------- #

    def _apply_constructor_arguments(self, arguments, node):

        arguments_listing = split_assignments(arguments)
        
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
                        self._add_error(f'Could not locate contructor key "{key}"')
                
                elif key in node.get_keys():
                    duplicate_keys.add(key)
            else:
                self._add_error(f'Invalid format. Use "<key> = <value>" instead of "{argument}"')
        
        if duplicate_keys:
            self._add_warning (f'The following keys had duplicate assignement: {", ".join(duplicate_keys)}')
                

    def _select_course(self, course_description):
        selection_result, child = self._node.select_child_by_description(course_description)
        selection_result &= RESULT
        if selection_result == CHANGED:
            self._add_print('Item selected.')

            # TODO: fix getting the id and priority in a stupid way (bad practice)
            course_id = child.get_course_id()
            if course_id is not None:
                root = self._get_root_node()
                highest_priority_for_course_id = root.sync_find_deep_highest_priority(course_id, base_priority=inf)
                sync_result = root.sync_deep_selection_with_priority(child._node_id, course_id, base_priority=inf, requisite_priority=highest_priority_for_course_id)

                if sync_result == ADDITIONAL_EFFECTS:
                    self._add_print('Some other items\' selection states were changed due to this.')
                elif sync_result == SUPERSEDED:
                    self._add_print('Another selected item matching the same description has a higher priority (selection modified).')

        elif selection_result == UNCHANGED:
            self._add_error('This item is already selected.')
        elif selection_result == ILLEGAL:
            self._add_error('This item cannot be selected.')
        elif selection_result == CHILD_NOT_FOUND:
            self._add_error(f'No item immediately below matches that description "{course_description}".')
        elif selection_result == GENERATION:
            self._add_print('Item added.')
        else:
            raise ValueError('Illegal state change result')
            
    def _deselect_course(self, course_description):

        selection_result, child = self._node.deselect_child_by_description(course_description)
        selection_result &= RESULT

        if selection_result == CHANGED:
            self._add_print('Item deselected.')

            # TODO: fix getting the id in a stupid way (bad practice)
            course_id = child.get_course_id()
            if course_id is not None:
                root = self._get_root_node()
                sync_result = root.sync_deep_deselection(child._node_id, course_id)
                if sync_result == ADDITIONAL_EFFECTS:
                    self._add_print('Some other items\' selection states were changed due to this.')
                elif sync_result == UNSTRUCTURED:
                    self._add_warning('There appears to be conflicting priority.')

        elif selection_result == UNCHANGED:
            self._add_print('This item is not selected.')
        elif selection_result == ILLEGAL:
            self._add_error('This item cannot be deselected.')
        elif selection_result == CHILD_NOT_FOUND:
            self._add_error(f'No item immediately below matches the description "{course_description}".')
        else:
            raise ValueError('Illegal state change result')

    def _delete_node(self, node_description):
        child = self._get_child(node_description)
        
        if child is not None:
            if self._node.remove_child(child._node_id):
                self._add_print('Item deleted.')
            else:
                self._add_error('This item cannot be deleted.')
        else:
            self._add_error(f'No item immediately below matches that description "{node_description}".')
        
    
    # --------------------------------------- Navigation/interface Methods --------------------------------------- #

    def _is_in_traverse_mode(self):
        return self._get_root_interface()._is_traverse_mode
    
    def _set_traversal_mode(self, state):
        self._get_root_interface()._is_traverse_mode = state

    def _get_root_interface(self):
        result = None
        if self is self._root_interface:
            result = self
        else:
            result = self._root_interface._get_root_interface()
        return result
        
    def _push_node_interface(self, controller, node):
        new_menu = NeededCoursesInterface(node, root_interface=self._get_root_interface(), depth=self._depth + 1, clears_screen=self._clears_screen)
        controller.push_interface(new_menu)
        return new_menu

    def _navigate_to_node(self, initial_interface, controller, node_description):
        
        success = False
        new_menu = None
        child = self._get_child(node_description)
        
        if child is not None:
            # Check if children can be added (and hence navigated into)
            if child.can_navigate_into():
                success = True
                new_menu = self._push_node_interface(controller, child)
            else:
                initial_interface._add_error(f'That type of item cannot be navigated to (for "{node_description}").')
        else:
            initial_interface._add_error(f'No item immediately below matches the description "{node_description}".')
            
        return success, new_menu
    
    def _navigate_back(self, controller):
        controller.pop_interface(self)
        
        top_interface = controller.get_current_interface()
        if isinstance(top_interface, NeededCoursesInterface):
            top_interface._check_for_traversal(controller)
        
        
    def _navigate_to_root(self, controller):
        # TODO: add check for base menu (this would be error state)
        if self is self._root_interface:
            top_interface = controller.get_current_interface()
            while top_interface is not self:
                controller.pop_interface(top_interface)
                top_interface = controller.get_current_interface()
        else:
            self._get_root_interface()._navigate_to_root(controller)
    
    def _check_for_traversal(self, controller):
        if self._is_in_traverse_mode() and self._node.is_discovery_resolved() and not self._get_root_node().is_deep_resolved():
            found_unfinished_child = False
            for child in self._node.get_active_children_list():
                if not child.is_deep_resolved():
                    if child.can_navigate_into():
                        self._push_node_interface(controller, child)
                    found_unfinished_child = True
                    break
            if not found_unfinished_child:
                self._navigate_back(controller)
            self._add_clear_opportunity()
            self._add_ls()
            self._push_print(controller)
    

    # --------------------------------------- Report Methods --------------------------------------- #

    def _report_stub_enable(self, stub_result, argument):
        if stub_result == CHANGED:
            self._add_print('Item set to stub.')
        elif stub_result == UNCHANGED:
            self._add_error('This item is already stub enabled.')
        elif stub_result == ILLEGAL:
            self._add_error('This item does not support stub states.')
        elif stub_result == CHILD_NOT_FOUND:
            self._add_error(f'No item immediately below matches that description "{argument}".')
        else:
            raise ValueError('Illegal state change result')

    def _report_stub_disable(self, stub_result, argument):
        if stub_result == CHANGED:
            self._add_print('Removed item stub.')
        elif stub_result == UNCHANGED:
            self._add_error('This item is not in a stub state.')
        elif stub_result == ILLEGAL:
            self._add_error('This item does not support stub removal at the moment.')
        elif stub_result == CHILD_NOT_FOUND:
            self._add_error(f'No item immediately below matches that description "{argument}".')
        else:
            raise ValueError('Illegal state change result')
        
    
    
## ------------------------------------------------- Interface End ------------------------------------------------- ##

