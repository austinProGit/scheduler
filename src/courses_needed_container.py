# Thomas Merino and Austin Lee
# 3/4/2023
# CPSC 4176 Project

# TODO: type annotations are not complete
    
# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING, Iterator
if TYPE_CHECKING:
    from typing import Optional

from requirement_tree import *
from requirement_interface import NeededCoursesInterface
from requirement_parser import *
import os
import pickle



class CoursesNeededContainer:
    
    def __init__(self, degree_plan: str, certain_courses_list: Optional[list[str]] = None, decision_tree: Optional[ExhaustiveNode] = None) -> None:
        self._degree_plan: str = degree_plan
        self._decision_tree: ExhaustiveNode = decision_tree or ExhaustiveNode()
        self._certain_courses_list: ListingNode = ListingNode(printable_description='Required Course')
        self._decision_tree.add_child(self._certain_courses_list)
        self._decision_tree.reorder_child(-1, 0)

        # TODO: perform this using a good practice
        self._decision_tree._duplicate_priority = DEFAULT_PRIORITY

        if certain_courses_list:
            course_string: str
            for course_string in certain_courses_list:
                self.add_certain_course(course_string)
    
    def __iter__(self):
        return self.get_courses_list().__iter__()
    
    def pickle(self) -> bytes:
        return pickle.dumps(self)
    
    def get_degree_plan_name(self):
        return self._degree_plan

    def get_courses_list(self):
        '''Get a set containing all courses.'''

        if not self.is_resolved():
            raise ValueError('Attempted to aggregate course list with unresolved tree. Check tree status using "is_resolved()"')

        #result = set(self._certain_courses_list)
        #result = result.union(self._decision_tree.get_aggregate())
        result = self._decision_tree.get_aggregate()
        return result
        
    def get_courses_string_list(self):
        return [str(deliverable) for deliverable in self.get_courses_list()]
    
    def get_certain_courses(self):
        return self._certain_courses_list.get_aggregate()
    
    def stub_all_unresolved_nodes(self) -> None:
        self._decision_tree.stub_all_unresolved_nodes()

    def add_certain_course(self, course_string: str) -> bool:
        added: bool = False
        if not self._certain_courses_list.get_child_by_description(course_string):
            added = self._certain_courses_list.add_child(DeliverableCourse(course_string))
        return added
        
    def get_decision_tree(self):
        return self._decision_tree
    
    def add_top_level_node(self, node):
        return self._decision_tree.add_child(node)
    
    def rename_certain_list(self, name):
        self._certain_courses_list.set_value_for_key('name', name)

    def is_resolved(self):
        return self._decision_tree.is_deep_resolved()

    def contains_active_stub(self):
        return self._decision_tree.has_active_deep_stub()

    def select_courses_as_taking(self, courses):
        # TODO: this is not implemented yet. This may be needed in feature versions, though.
        raise NotImplemented
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
    
    def output_clear(self):
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def output_warning(self, message):
        if self.is_printing:
            print(f'WARNING: {message}')
    
    def get_current_interface(self):
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

