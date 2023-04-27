# Thomas Merino and Austin Lee
# 4/2/2023
# CPSC 4176 Project

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional

from requirement_tree import *


class CNLogicParsingError(SyntaxError):
    '''An error during courses needed logic string parsing.'''
    pass


class RequirementsParser:

    @staticmethod
    def _make_node_from_string(node_type_string: str, parameter_sequence_string: str) -> RequirementsTree:
        
        # Create the new node

        new_node: Optional[RequirementsTree] = None

        # Intermediate node keys: 
        # shallow course    s
        # deep course       c
        # deep credit       r
        # exhaustive        e
        # list              l
        # deliverable       d
        # protocol:         p
        # inserter:         i

        if node_type_string == 's':
            new_node = ShallowCountBasedNode(requisite_count=1)
        elif node_type_string == 'c':
            new_node = DeepCountBasedNode(requisite_count=1)
        elif node_type_string == 'r':
            new_node = DeepCreditBasedNode(requisite_credits=3)
        elif node_type_string == 'e':
            new_node = ExhaustiveNode()
        elif node_type_string == 'd':
            new_node = DeliverableCourse(printable_description='New Course', credits=3)
        elif node_type_string == 'p':
            new_node = CourseProtocol(match_description=r'[A-Z]{4,5}\s?[0-9]{4}[A-Z]?', printable_description='New Course Protocol', credits=3)
        elif node_type_string == 'i':
            new_node = CourseInserter(generator_parameter=r'[A-Z]{4,5}\s?[0-9]{4}[A-Z]?', printable_description='Insert New')
        else:
            raise CNLogicParsingError(f'Illegal node type key: {node_type_string}.')
        
        # Set the key values for the new node

        arguments_listing: list[str] = split_assignments(parameter_sequence_string)
        
        if len(arguments_listing) == 1 and arguments_listing[0] == '':
            arguments_listing = []
            
        argument: str
        for argument in arguments_listing:

            delimiter_index: int = argument.find(SETTING_DELIMITTER)

            if delimiter_index != -1:

                key: str = argument[:delimiter_index].strip()
                
                value: str = argument[delimiter_index+len(SETTING_DELIMITTER):].strip()
                # NOTE: value == '' is completely valid and will result in the key's value being set to None
                
                new_node.set_value_for_key(key, value)

            else:
                raise CNLogicParsingError(f'Expected to find assignment operator "{SETTING_DELIMITTER}" in construction argument list: {parameter_sequence_string}.')
        
        return new_node
        
    @staticmethod
    def _pull_index(working_string: str, character: str) -> int:
        index: int = working_string.find(character)
        if index == -1:
            raise CNLogicParsingError(f'Did not find expected "{character}" in "{working_string}".')
        return index

    
    @staticmethod
    def _parse_subnodes(working_string: str) -> tuple[list[str], int]:
        '''This returns a list of node strings "[ ... ]" and the end index of that list. Parsing will stop when a hanging "]" is encountered.
        The end index will be the position before the last hanging "]" or the final index of the string.'''

        depth: int = 0
        working_start_index: int = 0
        last_index: int = 0
        results: list[str] = []

        index: int
        character: str
        for index, character in enumerate(working_string):
            
            if character == '[':
                if depth == 0:
                    working_start_index = index
                depth += 1

            elif character == ']':
                depth -= 1
                if depth == 0:
                    last_index = index
                    results.append(working_string[working_start_index : index + 1])
                elif depth == -1:
                    break

            elif depth <= 0 and not character.isspace():
                 raise CNLogicParsingError(f'Found unexpected character "{character}" while parsing "{working_string}".')

            else:
                last_index = index

        if depth > 0:
            raise CNLogicParsingError(f'Reached the end of the line while looking for "]" in "{working_string}".')

        return results, last_index

    @staticmethod
    def _make_node_from_course_selection_logic_string(string: str, artificial_exhaustive: bool = False) -> RequirementsTree:
        
        # if artificial_exhaustive is set to true, exhaustive nodes will be replaced by shallow count nodes with the right size

        working_string: str = (string or '').strip() # NOTE: this is a backup fro when None is passed in (possible)
        
        working_string = working_string[RequirementsParser._pull_index(working_string, '[') + 1:]

        trianlge_bracket_start: int = RequirementsParser._pull_index(working_string, '<')
        node_type: str = working_string[:trianlge_bracket_start].strip()
        working_string = working_string[trianlge_bracket_start + 1:]
        
        trianlge_bracket_end: int = RequirementsParser._pull_index(working_string, '>')
        parameter_sequence: str = working_string[:trianlge_bracket_end]
        working_string = working_string[trianlge_bracket_end + 1:]

        # Perform a check if the exhaustive node should be replaced by a shallow selection node (and calculate count if so)
        if artificial_exhaustive and node_type == 'e':
            node_type = 's'
            subnode_count: int = 0
            if '[' in working_string:
                subnodes: list[str]
                subnodes, _ = RequirementsParser._parse_subnodes(working_string)
                subnode_count = len(subnodes)
            parameter_sequence += f', c={subnode_count}'


        new_node: RequirementsTree = RequirementsParser._make_node_from_string(node_type, parameter_sequence)

        if '[' in working_string:
            subnodes: list[str]
            subnodes, _ = RequirementsParser._parse_subnodes(working_string)

            construction_string: str
            for construction_string in subnodes:
                new_node.add_child(RequirementsParser._make_node_from_course_selection_logic_string(construction_string,
                    artificial_exhaustive=artificial_exhaustive))
            
        
        return new_node
            
        
    
    @staticmethod
    def make_from_course_selection_logic_string(logic_string: str, artificial_exhaustive: bool = False) -> RequirementsParser.RequirementsParseReport:

        certain_courses: list[str] = []
        string: str = (logic_string or '').strip() # NOTE: this is a backup fro when None is passed in (possible)

        if string and string[0] == '(':
            end_index = RequirementsParser._pull_index(string, ')')
            courses = string[1 : end_index].split(',')
            string = string[end_index + 1:]
            certain_courses = [course.strip() for course in set(courses)]

            # Check if the certain courses will be added into the rest of the requirements so list nodes are not present
            if artificial_exhaustive:
                string += ''.join(f'[d <n={course_number}, dn={course_number}>]' for course_number in certain_courses)
                certain_courses = []

        
        encapsulated_string = f'[e<name=Requirements>{string}]'
        
        decision_tree = RequirementsParser._make_node_from_course_selection_logic_string(encapsulated_string, artificial_exhaustive)
        
        return RequirementsParser.RequirementsParseReport(certain_courses, decision_tree)

    def make_unified_from_course_selection_logic_string(logic_string: str, artificial_exhaustive: bool = False) -> RequirementsTree:

        parse_report = RequirementsParser.make_from_course_selection_logic_string(logic_string, artificial_exhaustive)
        result: RequirementsTree = parse_report.decision_tree
        
        # TODO: perform this using a good practice
        result._duplicate_priority = DEFAULT_PRIORITY

        # Add all of the certain courses (convert from a string to a deliverable as well)
        if len(parse_report.certain_courses) != 0:
            certain_courses_list: ListingNode = ListingNode(printable_description='Required Course')
            result.add_child(certain_courses_list)
            result.reorder_child(-1, 0)
            course_string: str
            for course_string in parse_report.certain_courses:
                if not certain_courses_list.get_child_by_description(course_string):
                    certain_courses_list.add_child(DeliverableCourse(course_string))

        return result

    class RequirementsParseReport:

        def __init__(self, certain_courses: list[str], decision_tree: RequirementsTree):
            self.certain_courses: list[str] = certain_courses
            self.decision_tree: RequirementsTree = decision_tree
