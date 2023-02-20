# Thomas Merino and Austin Lee
# 2/20/2023
# CPSC 4176 Project

from requirement_tree import *


class CNLogicParsingError(SyntaxError):
    '''An error during courses needed logic string parsing.'''
    pass


class RequirementsParser:

    @staticmethod
    def _make_node_from_string(node_type_string, parameter_sequence_string):
        
        # Create the new node

        new_node = None

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

        arguments_listing = split_assignments(parameter_sequence_string)
        
        if len(arguments_listing) == 1 and arguments_listing[0] == '':
            arguments_listing = []
        
        for argument in arguments_listing:

            delimiter_index = argument.find(SETTING_DELIMITTER)

            if delimiter_index != -1:

                key = argument[:delimiter_index].strip()
                
                value = argument[delimiter_index+len(SETTING_DELIMITTER):].strip()
                # NOTE: value == '' is completely valid and will result in being set to None

                new_node.set_value_for_key(key, value)

            else:
                raise CNLogicParsingError(f'Expected to find assignment operator "{SETTING_DELIMITTER}" in construction argument list: {parameter_sequence_string}.')
        
        return new_node
        
    @staticmethod
    def _pull_index(working_string, character):
        index = working_string.find(character)
        if index == -1:
            raise CNLogicParsingError(f'Did not find expected "{character}" in "{working_string}".')
        return index

    
    @staticmethod
    def _parse_subnodes(working_string):
        '''This returns a list of node strings "[ ... ]" and the end index of that list. Parsing will stop when a hanging "]" is encountered.
        The end index will be the position before the last hanging "]" or the final index of the string.'''

        depth = 0
        working_start_index = 0
        last_index = 0
        results = []

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

        # print(results)
        return results, last_index

    @staticmethod
    def _make_node_from_course_selection_logic_string(string):
        
        working_string = string.strip()
        
        working_string = working_string[RequirementsParser._pull_index(working_string, '[') + 1:]

        trianlge_bracket_start = RequirementsParser._pull_index(working_string, '<')
        node_type = working_string[:trianlge_bracket_start].strip()
        working_string = working_string[trianlge_bracket_start + 1:]
        
        trianlge_bracket_end = RequirementsParser._pull_index(working_string, '>')
        parameter_sequence = working_string[:trianlge_bracket_end]
        working_string = working_string[trianlge_bracket_end + 1:]

        new_node = RequirementsParser._make_node_from_string(node_type, parameter_sequence)

        if '[' in working_string:
            subnodes, _ = RequirementsParser._parse_subnodes(working_string)

            for construction_string in subnodes:
                new_node.add_child(RequirementsParser._make_node_from_course_selection_logic_string(construction_string))
            
        # next_bracket_index = working_string.find('[')

        # while next_bracket_index != -1:
        #     end_bracket_index = CoursesNeededContainer._pull_index(working_string, ']')
        #     construction_string = working_string[next_bracket_index : end_bracket_index + 1]
        #     working_string = working_string[end_bracket_index + 1:]

        #     new_node.add_child(CoursesNeededContainer._make_node_from_course_selection_logic_string(construction_string))
            
        #     next_bracket_index = working_string.find('[')
        
        return new_node
            
        
    
    @staticmethod
    def make_from_course_selection_logic_string(logic_string):

        certain_courses = []
        string = logic_string.strip()

        if string and string[0] == '(':
            end_index = RequirementsParser._pull_index(string, ')')
            courses = string[1 : end_index].split(',')
            string = string[end_index + 1:]
            certain_courses = [course.strip() for course in set(courses)]
        
        encapsulated_string = f'[e<name=Requirements>{string}]'
        decision_tree = RequirementsParser._make_node_from_course_selection_logic_string(encapsulated_string)
        
        return RequirementsParser.RequirementsParseReport(certain_courses, decision_tree)


    class RequirementsParseReport:

        def __init__(self, certain_courses, decision_tree):
            self.certain_courses = certain_courses
            self.decision_tree = decision_tree
