# Thomas Merino and Austin Lee
# 2/4/2023
# CPSC 4176 Project

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional

import re

from typing import final, Union
from math import inf
from general_utilities import *

# from cli_interface import HelpMenu

# TODO: Add check for coreq.s
# TODO: Add some sort of handling for "3 to 6 hours"


# TODO: make the commands similar in spacers ("_" vs "-" to seperate words)
# TODO: add help menu back!
# TODO: add documentation
# TODO: pull credit count into protocol node when filling out
# TODO: add generating functions that sepcialize in groups (if you have select one group, that does not always mean 3 credits)
# TODO: perform memory test for leaks
# TODO: Add a method for checking if there are groups that have no real choices (for example, asc c=3 with 3 subnodes)
#           and make them selected automatically (don't change the node type)
# TODO: Add method to generate a logical intermediate string from a tree
# TODO: Add a method that ingests courses (already taken by the user, but those need to be selected and/or removed)
# TODO: put the list object as the first node in the root tree (when constructed)
# TODO: add more command clarity (in CLI and here) - such as adding exit, quit, and done

# Intermediate node keys: 
# shallow course    s
# deep course       c
# deep credit       r
# exhaustive        e
# list              l
# deliverable       d
# protocol:         p
# inserter:         i


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


NO_CLEARING = 0x00
NAVIGATION_CLEARING = 0x01
CONSTANT_REFRESHING = 0x02

PRINT = 0x00
ERROR = 0x01
WARNING = 0x02
POSSIBLE_LS = 0x03
HARD_LS = 0x04
POSSIBLE_SOFT_CLEAR = 0x05
HARD_CLEAR = 0x06
UNCHECKED_PRINT = 0x07


DEFAULT_COURSE_DESCRIPTION = "Course XXXX"
DEFAULT_STUB_AVAILABILITY = set([FALL, SPRING])
DEFAULT_STUB_CREDITS = 3



class SchedulableParameters:
    
    def __init__(self, course_number: Optional[str] = None, course_name: Optional[str] = None, is_stub: bool = False):
        self.course_number: Optional[str] = course_number
        self.course_name: str = course_name or DEFAULT_COURSE_DESCRIPTION
        self.is_stub: bool = is_stub
        self.stub_availability: set[SemesterType] = DEFAULT_STUB_AVAILABILITY
        self.stub_hours: int = DEFAULT_STUB_CREDITS
        self.stub_prereqs_logic_string: str = ''
        self.stub_coreqs_logic_string: str = ''
        self.stub_recommended_set: set[str] = set()
        
    def __str__(self) -> str:
        return self.course_number or self.course_name
    
    



def default_stub_generator(credits_string=None, name=None):
    new_item = SchedulableParameters(course_name = name or DEFAULT_COURSE_DESCRIPTION, is_stub = True)
    new_item.stub_hours = int(credits_string) if (credits_string is not None and credits_string.isnumeric()) else 3
    return new_item
    
def regex_course_protocol_generator(matching_description=r'.*', name=None):
    '''Course generator function that creates protocol nodes with the passed regex (defaults to ".*") and name (defaults to "New Course").'''
    return CourseProtocol(matching_description, name or 'New Course')

def as_signed_integer(string):
    '''Returns a signed integer if the passed string can be converted or None if it cannot.'''
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

def print_format_number(number):
    '''Format the passes number for displaying in the UI. This returns a string.'''
    result = None
    if number != inf:
        result = str(number)
    else:
        result = 'Limitless'
    return result


def split_assignments(line):
    result = []
    line_length = len(line)
    if line:
        parenthesis_depth = 0
        last_index = 0
        working_index = 0

        while working_index < line_length:
            current_character = line[working_index]
            if current_character == ',':
                if parenthesis_depth == 0:
                    result.append(line[last_index:working_index])
                    last_index = working_index + 1
            elif current_character in {'(', '[', '{'}:
                parenthesis_depth += 1
            elif current_character in {')', ']', '}'}:
                parenthesis_depth -= 1
            working_index += 1
        
        if last_index != working_index:
            result.append(line[last_index:])

    return result



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

        self._is_track_elective = 'no'
        
    
    ## ------------------------------ Clipboard ------------------------------ ##

    def transfer_base_properties(self, to_node):
        to_node._is_stub = self._is_stub
        for key in self.KEYS_LIST:
            self_value = self.get_value_for_key(key)
            self_value_string = ''
            if self_value is not None:
                self_value_string = str(self_value)
            to_node.set_value_for_key(key, self_value_string)
    
    def make_shallow_live_copy(self):
        raise NotImplemented()
    
    def make_deep_live_copy(self):
        copy = self.make_shallow_live_copy()
        for child_id, child in self._children.items():
            child_copy = child.make_deep_live_copy()
            child_copy_id = child_copy._node_id
            copy._children[child_copy_id] = child_copy
            copy._children_ids.append(child_copy_id)

            if child_id in self._selection:
                copy._selection.add(child_copy_id)

            if child_id in self._destructive_selection:
                copy._destructive_selection.add(child_copy_id)
            
        return copy

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
            if value == '' or value == 'null':
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
        else:
            if key in self.KEY_ALIASES:
                result = self.set_value_for_key(self.KEY_ALIASES[key], value)
                
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
    
    def is_delete_protected(self):
        return False

    def is_available_concurrent(self) -> bool:
        '''Whether the node may be taken concurrently (in the context of selection for prerequisite requirement trees).'''
        return False

    ## ------------------------------ Descriptions getting ------------------------------ ##

    def get_verbose_instructions(self):
        return self._verbose_instructions
    
    def get_shallow_description(self):
        raise NotImplementedError
    
    def get_deep_description(self, depth=0, is_selected=False, maximum_depth=-1, indicate_node=None):
        
        prefix_icon = ' '
        if self.has_shallow_stub():
            prefix_icon = '~'
        elif is_selected:
            prefix_icon = '+'

        indent = depth*'   '
        if indicate_node is not None and self._node_id == indicate_node._node_id:
            indent = depth*'-->'

        result = f'{indent}{prefix_icon} {self.get_shallow_description()}'
        
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
                rows.append(child.get_deep_description(depth+1, is_selected=child_is_selected, maximum_depth=maximum_depth-1, indicate_node=indicate_node))
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

    @final
    def matches_course_id(self, course_id: str) -> bool:
        return self._printable_description == course_id

    def matches_description(self, description):
        '''Returns whether the passed description matches the name (printable description).'''
        # Ensure the string is non-empty and there is a match
        result = False
        if self._printable_description is not None:

                # Check for exact match
                result = self.matches_course_id(description)

                # Check for wildcard matching if not matching
                if not result:
                    wildcard_index = description.find('*')
                    if wildcard_index != -1:
                        search_lhs = description[:wildcard_index]
                        search_rhs = description[wildcard_index+1:]
                        result = self._printable_description.startswith(search_lhs) and \
                            self._printable_description.endswith(search_rhs) and \
                            len(self._printable_description) >= len(search_lhs) + len(search_rhs)
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

    @final
    def get_deep_child_parent_by_course_id(self, course_id: str) -> Optional[RequirementsTree]:
        '''Gets the parent of the child matching the passed course_number (uses DFS search).'''

        result: Optional[RequirementsTree] = None
        children: list[RequirementsTree] = self.get_all_children_list()

        child: RequirementsTree
        for child in children:

            result = child.get_deep_child_parent_by_course_id(course_id)

            if result is None and child.matches_course_id(course_id):
                result = self
            
            if result:
                break
        
        return result

    @final
    def has_deep_child_by_course_id(self, course_id: str) -> bool:
        '''(Note: this does not search itself for a match)'''
        result: bool = False
        children: list[RequirementsTree] = self.get_all_children_list()

        child: RequirementsTree
        for child in children:
            result = child.has_deep_child_by_course_id(course_id) or \
                self.matches_course_id(course_id)
            if result:
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
    def get_aggregate(self) -> list[SchedulableParameters]:
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''
        raise NotImplementedError

    def get_as_schedulable_list(self):
        return []

    def get_all_aggragate(self):
        result = self.get_as_schedulable_list()
        if self.can_accept_children():
            for child in self.get_all_children_list():
                result += child.get_all_aggragate()
        return result


    def get_all_track_elective_aggragate(self):
        result = []
        if self._is_track_elective:
            result = self.get_all_aggragate()
        else:
            if self.can_accept_children():
                for child in self.get_all_children_list():
                    result += child.get_all_track_elective_aggragate()
        return result

    
    def get_course_id(self):
        '''Return the unique ID this course represents or None if it is not concrete.'''
        return None

    ## ------------------------------ Child Set Mutation ------------------------------ ##

    def can_take_child(self, node):
        return True

    @final
    def add_child(self, node):
        '''Attempt to add a child node and return the success of the addition.'''
        success = False
        if self.can_accept_children() and self.can_take_child(node):
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
        if node_id in self._children and self.can_accept_children() and not self._children[node_id].is_delete_protected():
            del self._children[node_id]
            self._children_ids.remove(node_id)
            self._selection.discard(node_id)
            success = True
        return success
    
    @final
    def reorder_child(self, from_index, to_index):

        # NOTE: this will
        mutated = False
        try:
                child_id = self._children_ids.pop(from_index)
                self._children_ids.insert(to_index, child_id)
                mutated = True
        except IndexError:
            raise IndexError(f'Invalid child index in child relocation. Index: {from_index}.')
        return mutated

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
    
    @final
    def deep_select_all_satified_children(self) -> None:
        # TODO: check the validity of this!!
        child_id: str
        for child_id in self.get_all_children_ids():
            child: RequirementsTree = self._children[child_id]
            child.deep_select_all_satified_children()
            if child.is_deep_resolved() and child.can_accept_children():
                self.select_child(child)
            


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

    @final
    def sync_deep_selection(self, course_id: str) -> int:
        # TODO: the return value does not make sense (possible return whether modifications were made)

        child: RequirementsTree
        for child in self.get_all_children_list():
            if child.get_course_id() == course_id:
                if not self.is_selecting_node_id(child._node_id):
                    self.select_child(child)
                
            child.sync_deep_selection(course_id)
        
        return ADDITIONAL_EFFECTS


    def sync_deep_concurrent_selection(self, course_id: str) -> int:
        # TODO: the return value does not make sense (possible return whether modifications were made)

        child: RequirementsTree
        for child in self.get_all_children_list():
            if child.is_available_concurrent() and child.get_course_id() == course_id:
                if not self.is_selecting_node_id(child._node_id):
                    self.select_child(child)
                
            child.sync_deep_concurrent_selection(course_id)
        
        return ADDITIONAL_EFFECTS
        
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


    def sync_deep_deselection(self, course_id: str, original_node_id: Optional[int] = None) -> int:

        result: int = SINGLE

        child: RequirementsTree
        for child in self.get_all_children_list():
            if child.get_course_id() == course_id and self.is_selecting_node_id(child._node_id):
                deselection_result: int = RESULT & self.deselect_child(child)
                if deselection_result == CHANGED:
                    if child._node_id != original_node_id:
                        result = ADDITIONAL_EFFECTS
                else:
                    result = UNSTRUCTURED
                
            child_result: int = child.sync_deep_deselection(course_id, original_node_id)

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
    def has_active_deep_stub(self):
        return self.has_shallow_stub() or any(node.has_active_deep_stub() for node in self.get_active_children_list())
    
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
        
    @final
    def stub_all_unresolved_nodes(self):
        
        if self.is_discovery_resolved():
            for child in self.get_active_children_list():
                child.stub_all_unresolved_nodes()
        else:
            self.enable_stub()
    
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
        return self.has_shallow_stub() or self.is_shallow_resolved()

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




## ------------------------------ End of Node Super ------------------------------ ##


# Note that this is also a kind of node in a CoursesNeededContainer (a leaf node).
class DeliverableCourse(_NodeSuper):
    
    KEY_VALUE_DICT = {
        'name': '_printable_description',
        'instance id': '_explicit_id',
        'instructions': '_verbose_instructions',
        'credits': '_credits',
        'deliver name': '_course_description',
        'duplicate priority': '_duplicate_priority',
        'track elective': '_is_track_elective',
        'may be taken concurrently': '_may_be_taken_concurrently',
        'fallback prereq logic': '_fallback_prereq_logic',
        'fallback coreq logic': '_fallback_coreq_logic'
    }
    KEY_ALIASES = {
        'n': 'name',
        'id': 'instance id',
        'i': 'instructions',
        'c': 'credits',
        'dn': 'deliver name',
        'p': 'duplicate priority',
        'te': 'track elective',
        'mbtc': 'may be taken concurrently',
        'fpl': 'fallback prereq logic',
        'fcl': 'fallback coreq logic'
    }
    KEYS_LIST = ['name', 'instance id', 'instructions', 'credits', 'deliver name', 'duplicate priority',
    'track elective', 'may be taken concurrently', 'fallback prereq logic', 'fallback coreq logic']
    NON_NIL_KEYS = {'name', 'credits', 'fallback prereq logic', 'fallback coreq logic'}
    INTEGER_KEYS = {'credits', 'duplicate priority'}

    def __init__(self, course_description=None, credits=3, printable_description=None):
        super().__init__(printable_description or course_description)
        self._course_description = course_description
        self._credits = credits
        self._explicit_id = None
        self._may_be_taken_concurrently: Optional[str] = None
        self._fallback_prereq_logic = ''
        self._fallback_coreq_logic = ''
    
    def set_value_for_key(self, key, value):
        super().set_value_for_key(key, value)
        if key == 'n' and self._course_description is None:
            super().set_value_for_key('dn', value)

    def make_shallow_live_copy(self):
        copy = DeliverableCourse()
        self.transfer_base_properties(copy)
        return copy
        

    def can_accept_children(self):
        return False
    
    def can_be_stub(self):
        return False

    def is_available_concurrent(self) -> bool:
        '''Whether the node may be taken concurrently (in the context of selection for prerequisite requirement trees).'''
        return self._may_be_taken_concurrently is not None and self._may_be_taken_concurrently != 'no'

    def get_shallow_description(self):
        return f'{self._printable_description or self._course_description or "Course"} - {self.get_shallow_credits()}'
        
    def get_active_children_ids(self):
        return []
    
    def get_aggregate(self) -> list[SchedulableParameters]:
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''
        result: list[SchedulableParameters] = []
        if self._course_description:
            result.append(SchedulableParameters(course_number=self._course_description, course_name=self._printable_description or DEFAULT_COURSE_DESCRIPTION))
        else:
            result.append(SchedulableParameters(course_name=self._printable_description or DEFAULT_COURSE_DESCRIPTION))
        return result
    
    def get_as_schedulable_list(self) -> list[SchedulableParameters]:
        return self.get_aggregate()

    def get_course_id(self):
        '''Return the unique ID this course represents or None if it is not concrete.'''
        return self._explicit_id or self._course_description or self._printable_description
    
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
        'duplicate priority': '_duplicate_priority',
        'track elective': '_is_track_elective',
        'concurrency available': '_concurrency_available'
    }
    KEY_ALIASES = {
        'n': 'name',
        'i': 'instructions',
        'c': 'credits',
        'm': 'matching',
        'r': 'rejection',
        's': 'stub_name',
        'p': 'duplicate priority',
        'te': 'track elective',
        'mbtc': 'concurrency available'
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
        self._concurrency_available = False
        
        self._selected_course = None

    def make_shallow_live_copy(self):
        copy = CourseProtocol()
        copy._selected_course = self._selected_course
        self.transfer_base_properties(copy)
        return copy

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
            return [SchedulableParameters(course_number = self._selected_course or self._printable_description)]
        else:
            return [SchedulableParameters(course_name = self._stub_description or self._printable_description, is_stub=True)]

    def get_as_schedulable_list(self):
        return [SchedulableParameters(course_name = self._stub_description or self._printable_description, is_stub=True)]

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
    KEY_ALIASES = {
        'n': 'name',
        'i': 'instructions',
        'gp': 'generator parameter',
        'ga': 'aux parameter',
        'gn': 'generator'
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
        
    
    def make_shallow_live_copy(self):
        copy = CourseInserter()
        self.transfer_base_properties(copy)
        return copy
    
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
    KEY_ALIASES = {
        'n': 'name',
        'i': 'instructions'
    }
    KEYS_LIST = ['name', 'instructions']
    NON_NIL_KEYS = {'name'}
    INTEGER_KEYS: set[str] = set()
    
    def __init__(self, printable_description=None, is_delete_protected=True):
        super().__init__(printable_description)
        self._duplicate_priority = 0
        self._is_delete_protected = is_delete_protected

    def make_shallow_live_copy(self):
        copy = ExhaustiveNode()
        copy._printable_description = self._printable_description
        copy._verbose_instructions = self._verbose_instructions
        copy._duplicate_priority = self._duplicate_priority
        copy._is_delete_protected = self._is_delete_protected
        copy._stub_generator = None
        return copy

    def make_deep_live_copy(self):
        copy = self.make_shallow_live_copy()
        for child_id, child in self._children.items():
            child_copy = child.make_deep_live_copy()
            child_copy_id = child_copy._node_id
            copy._children[child_copy_id] = child_copy
            copy._children_ids.append(child_copy_id)
        return copy

    
    def can_be_stub(self):
        return False

    def is_delete_protected(self):
        return self.is_delete_protected

    def get_shallow_description(self):
        return self._printable_description or 'Listing section'

    def get_deep_description(self, depth=0, is_selected=False, maximum_depth=-1, indicate_node=None):
        count_string = print_format_number(self.get_all_layer_count())

        # TODO: this is redundant
        indent = depth*'   '
        if indicate_node is not None and self._node_id == indicate_node._node_id:
            indent = depth*'-->'
        
        result = f'{indent}+ {self.get_shallow_description()} - {count_string} item{"s" if count_string != "1" else ""}'
        return result

    def get_layer_description(self):
        description = None

        if self.get_all_children_count() != 0:
            description = super().get_deep_description(maximum_depth=1)
        else:
            description = f'{self.get_shallow_description()} (empty)'
        
        instructions = self.get_verbose_instructions()
        if instructions is not None:
            description += '\nABOUT: ' + instructions

        return description
    
    def get_active_children_ids(self):
        '''Get a copy of the ordered list of children IDs that are selected.'''
        return self.get_all_children_ids()

    def get_aggregate(self):
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''
        result = []
        for child in self.get_all_children_list():
            result += child.get_aggregate()
        return result

    def can_take_child(self, node):
        return not node.can_accept_children()

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
        'duplicate priority': '_duplicate_priority',
        'track elective': '_is_track_elective'
    }
    KEY_ALIASES = {
        'n': 'name',
        'i': 'instructions',
        'cb': 'count bottleneck',
        'rb': 'credits bottleneck',
        'dp': 'duplicate priority',
        'te': 'track elective'
    }
    KEYS_LIST = ['name', 'instructions', 'count bottleneck', 'credits bottleneck', 'duplicate priority']
    NON_NIL_KEYS = {'name'}
    INTEGER_KEYS = {'count bottleneck', 'credits bottleneck', 'duplicate priority'}
    
    def __init__(self, printable_description=None, is_delete_protected=False):
        super().__init__(printable_description)
        self._is_delete_protected = is_delete_protected
        self._stub_generator_name = None

    def make_shallow_live_copy(self):
        copy = ExhaustiveNode()
        self.transfer_base_properties(copy)
        copy._is_delete_protected = False
        return copy

    def can_be_stub(self):
        return False

    def is_delete_protected(self):
        return self.is_delete_protected

    def get_shallow_description(self):
        return self._printable_description or 'Requirement section'
    
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
        'duplicate priority': '_duplicate_priority',
        'track elective': '_is_track_elective'
    }
    KEY_ALIASES = {
        'n': 'name',
        'i': 'instructions',
        'c': 'count',
        'cb': 'count bottleneck',
        'rb': 'credits bottleneck',
        'gn': 'generator name',
        'gp': 'generator parameter',
        'ga': 'aux parameter',
        'dp': 'duplicate priority',
        'te': 'track elective'
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
        
    def make_shallow_live_copy(self):
        copy = ShallowCountBasedNode()
        self.transfer_base_properties(copy)
        return copy

    def get_shallow_description(self):
        result = self._printable_description or "Section"
        if self._requisite_count != 0:
            count = len(self._selection) #sum(course.get_shallow_count() for course in self.get_active_children_list())
            count_string = print_format_number(count)
            result += f' - {count_string} / {self._requisite_count} selections'
        return result
    
    def get_aggregate(self):
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''

        result = []

        if not self.has_shallow_stub():
            for child in self.get_active_children_list():
                result += child.get_aggregate()
        else:
            for _ in range(self._requisite_count):
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
        'duplicate priority': '_duplicate_priority',
        'track elective': '_is_track_elective'
    }
    KEY_ALIASES = {
        'n': 'name',
        'i': 'instructions',
        'c': 'count',
        'cb': 'count bottleneck',
        'rb': 'credits bottleneck',
        'gn': 'generator name',
        'gp': 'generator parameter',
        'ga': 'aux parameter',
        'dp': 'duplicate priority',
        'te': 'track elective'
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
    
    def make_shallow_live_copy(self):
        copy = DeepCountBasedNode()
        self.transfer_base_properties(copy)
        return copy

    def get_shallow_description(self):
        result = self._printable_description or "Section"
        if self._requisite_count != 0:
            count = self.get_active_layer_count()
            count_string = print_format_number(count)
            result += f' - {count_string} / {self._requisite_count} courses'
        return result

    def get_aggregate(self):
        '''This gets a list of SchedulableItem objects from the node and all of its children.'''

        result = []

        if not self.has_shallow_stub():
            for child in self.get_active_children_list():
                result += child.get_aggregate()
        else:
            for _ in range(self._requisite_count):
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
        'duplicate priority': '_duplicate_priority',
        'track elective': '_is_track_elective'
    }
    KEY_ALIASES = {
        'n': 'name',
        'i': 'instructions',
        'c': 'credits',
        'cb': 'count bottleneck',
        'rb': 'credits bottleneck',
        'gn': 'generator name',
        'gp': 'generator parameter',
        'ga': 'aux parameter',
        'dp': 'duplicate priority',
        'te': 'track elective'
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

    def make_shallow_live_copy(self):
        copy = DeepCreditBasedNode()
        self.transfer_base_properties(copy)
        return copy
    
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
                running_credits += new_schedulable.stub_hours
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
            result += f' - {credits_string} / {self._requisite_credits} credits'
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
    

RequirementsTree = Union[_NodeSuper, ShallowCountBasedNode, DeepCountBasedNode, DeepCreditBasedNode, ExhaustiveNode, DeliverableCourse, CourseProtocol, CourseInserter]
