# Thomas Merino and Austin Lee
# 2/19/2023
# CPSC 4176 Project
    
from requirement_tree import *
import pickle

# NOTE: The following are optional importants that are just used for testing:
from requirement_parser import RequirementsParser
import os
from requirement_interface import NeededCoursesInterface


class RequirementsContainer:
    
    def __init__(self, requirements_tree=None):
        self._requirements_tree = requirements_tree or ExhaustiveNode()

        # TODO: perform this using a good practice
        self._decision_tree._duplicate_priority = DEFAULT_PRIORITY
    
    def __iter__(self):
        return self.get_courses_list().__iter__()
    
    def pickle(self):
        return pickle.dumps(self)
    
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
    
    def stub_all_unresolved_nodes(self):
        self._decision_tree.stub_all_unresolved_nodes()

    def add_certain_course(self, course_string):
        added = False
        if not self._certain_courses_list.get_child_by_description(course_string):
            added = self._certain_courses_list.add_child(DeliverableCourse(course_string))
        return added
        
    def get_decision_tree(self):
        return self._decision_tree
    
    def add_top_level_node(self, node):
        return self._decision_tree.add_child(node)
    
    def is_resolved(self):
        return self._decision_tree.is_deep_resolved()

    def contains_active_stub(self):
        return self._decision_tree.has_active_deep_stub()

    def select_courses_as_taking(self, courses):
        # TODO: this is not implemented yet
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

if __name__ == '__main__':

    # tree = ExhaustiveNode()
    # listing_node = ListingNode(printable_description='Core Curriculum')
    # tree.add_child(listing_node)

    #courses_needed_container = CoursesNeededContainer("Test Plan")
    construct_string_1 = '''
    (POLS 1101,POLS 1101,STAT 1401,POLS 1101,CPSC 1302,CPSC 2105,CYBR 2159,CYBR 2160,CPSC 2108,CPSC 3125,CPSC 3131,CPSC 3165,CPSC 3175,CPSC 4000,MATH 5125,CPSC 2125,CPSC 3105,CPSC 4125,CPSC 4126,CPSC 4135,CPSC 4175,CPSC 4176,ITDS 1774,STAT 3127,DSCI 3111,ITDS 4779)
 [s <c=2, n=Choose from 2 of the following> 
	[s <c=2, n=Descriptive Astronomy>
		[d <n=ASTR 1105>]
		[d <n=ASTR 1305>]
	]
	[r <c=4, n=Principles of Biology>
		[d <n=BIOL 1225>]
	]
	[s <c=2, n=Contemporary Issues in Biology>
		[d <n=CHEM 1151>]
		[d <n=CHEM 1151L, id=CHEM 1151>]
	]

	[r <c=4, n=Introductory Physics II>
		[d <n=PHYS 1112>]
		[d <n=PHYS 2211>]
		[d <n=PHYS 1312>]
	]

	[s <c=1, n=Susatinability and the Environment>
		[d <n=ENVS 1205K>]
	]
	
]

[r <c=9, n=9 Credits in CPSC 3@ or 4@ or 5@ or CYBR 3@ or 4@>
	[i <n=Insert CPSC 3@, ga=CPSC 3@ Course, gp=CPSC 3\d{3}[A-Z]?>]
	[i <n=Insert CPSC 4@, ga=CPSC 4@ Course, gp=CPSC 4\d{3}[A-Z]?>]
	[i <n=Insert CPSC 5@, ga=CPSC 5@ Course, gp=CPSC 5\d{3}[A-Z]?>]
	[i <n=Insert CYBR 3@, ga=CYBR 3@ Course, gp=CPSC 3\d{3}[A-Z]?>]
	[i <n=Insert CYBR 4@, ga=CYBR 4@ Course, gp=CPSC 4\d{3}[A-Z]?>]
]

[r <c=4, n=9 Credits in 1@ or 2@ or 3@ or 4@ or 5@U, i=Except ENGL 1101 or 1102* or CPSC 1301* or 1302* or 2015 or 2016>
	[i <n=Insert 1@, ga=1@ Course, gp=^(?!ENGL 1101|ENGL 1102|CPSC 1301|CPSC 1302|CPSC 2015|CPSC 2016)[A-Z]{4} 1\d{3}[A-Z]?>]
	[i <n=Insert 2@, ga=2@ Course, gp=^(?!ENGL 1101|ENGL 1102|CPSC 1301|CPSC 1302|CPSC 2015|CPSC 2016)[A-Z]{4} 2\d{3}[A-Z]?>]
	[i <n=Insert 3@, ga=3@ Course, gp=^(?!ENGL 1101|ENGL 1102|CPSC 1301|CPSC 1302|CPSC 2015|CPSC 2016)[A-Z]{4} 3\d{3}[A-Z]?>]
	[i <n=Insert 4@, ga=4@ Course, gp=^(?!ENGL 1101|ENGL 1102|CPSC 1301|CPSC 1302|CPSC 2015|CPSC 2016)[A-Z]{4} 4\d{3}[A-Z]?>]
	[i <n=Insert 5@U, ga=5@U Course, gp=^(?!ENGL 1101|ENGL 1102|CPSC 1301|CPSC 1302|CPSC 2015|CPSC 2016)[A-Z]{4} [5]\d{4}U>]
]


[e <n=2 Classes in ITDS 1070>
	[d <n=ITDS 1070, id=ITDS 1070 0>]
	[d <n=ITDS 1070, id=ITDS 1070 1>]
]

[s <c=1, n=1 Class in STAT 1401@ or 1127@ or BUSA 3115* or CRJU 3107>
	[p <n=STAT 1401@, m=STAT 1401.*>]
	[p <n=STAT 1127@, m=STAT 1127.*>]
	[d <n=BUSA 3115>]
	[d <n=CRJU 3107>]
]

[r <c=3, n=3 to 6 Credits in PSEUDO>
	[i <n=Insert PSEUDO, gp=PSEUDO \d{4}[A-Z]?>]
]

    '''



    construct_string_2 = '''
    (CPSC 1301, CPSC 1302, CPSC 2105, CPSC 2108, CPSC 3125,
     CPSC 3131, CPSC 3165, CPSC 3175, CPSC 4115, CPSC 4135)

    [c <n=3 Courses, c=3>
        [d <n=CPSC 4121>]
        [c <n=2 Courses, c=2>
            [d <n=CPSC 4126>]
            [d <n=CPSC 4127>]
        ]
        [d <n=CPSC 4130>]
        [d <n=CPSC 4185>]
    ]

    [s <n=2 Selections, c=2>
        [c <n=2 Courses, c=2>
            [d <n=MATH 1100>]
            [d <n=MATH 1101>]
        ]
        [c <n=2 Courses, c=2>
            [d <n=MATH 1200>]
            [d <n=MATH 1201>]
        ]
        [d <n=MATH 1300>]
        [d <n=MATH 1400>]
    ]

    [r <n=6 Credits, c=6>
        [i <n=Insert 4___, gp=[A-Z]{4,5}\s?\d{4}[A-Z]?, ga=Fill out 4___>]
        [p <n=Fill out 4___, gp=[A-Z]{4,5}\s?\d{4}[A-Z]?>]
    ]
    '''

    parse_report = RequirementsParser.make_from_course_selection_logic_string(construct_string_2)
    # courses_needed_container = RequirementsContainer(parse_report.certain_courses, parse_report.decision_tree)
    # TODO: determine if this or the line above is correct
    courses_needed_container = RequirementsContainer(parse_report.decision_tree)
    # courses_needed_container.rename_certain_list('Certain List')

    # (POL 111, POLSE 2323) [s <n=A>[d<n=1>][d<n=2>]] [r <c=9>[p<n=p,m=p.*>][i<>][d<n=IO>]]
    # (POL 111, POLSE 2323) [s <n=A>[e<n=1> [r<>[d<>][d<>]] [d<>]][d<n=2>]] [r <c=9>[p<n=p,m=p.*>][i<>][d<n=IO>]]

#    courses_needed_container = CoursesNeededContainer.make_from_course_selection_logic_string('Course', '''
#    (123, 456)
#    [d <n=Big>]
#    [d <n=Small>]
#    ''')
    tree = courses_needed_container.get_decision_tree()
    
    controller = DummyController()
    controller.is_printing = False
    controller.push_interface(NeededCoursesInterface(tree, clears_screen=CONSTANT_REFRESHING))
    
    std_in = '''
    asc count = 1, name = Area A, duplicate priority = 10
    asc count = 2, name = Area B, duplicate priority = 20
    acr credits = 3, name = Area C, duplicate priority = 30
    cd 2
    ad name = 1000, credits = 3
    ad name = 1001, credits = 3
    ad name = 1002, credits = 3
    ap name = 11@, matching=11[0-9]{2}
    back
    cd 3
    ad name = 2000, credits = 3
    ad name = 2001, credits = 3
    ad name = 2002, credits = 4
    ad name = 1000, credits = 3
    back
    cd 4
    ad name = 3000, credits = 0
    ad name = 3001, credits = 1
    ad name = 3002, credits = 2
    ad name = 3003, credits = 3
    ad name = 3004, credits = 4
    ad name = 4001, credits = 1
    ad name = 4002, credits = 2
    back

    cd 2
    adc name=Education, count=4
    cd Education
    adc name=Core, count=2, count_bottleneck=3
    ad name=ED 1000
    ad name=ED 1001
    ad name=ED 1002
    ad name=ED 1003
    cd Core
    ad name=CR 1000
    ad name=CR 1001
    ad name=CR 1002
    ad name=CR 1003
    ad name=3000
    ad name=3002
    back
    back
    back
    
    asc name=General, count=5, duplicate priority = 100
    cd -1
    ai n=Insert 3-number, generator parameter =[0-9]{3}, aux parameter = 3-credit Course
    ai n=Insert 4-number, generator parameter =[0-9]{4}, aux parameter = 4-credit Course
    back

    cd Core*
    ad n=NEED 1001
    ad n=NEED 2001
    ad n=NEED 2002
    ad n=NEED 3001
    root
    cd 2
    s -1
    root
    '''

    # for t in std_in.split('\n'):
    #     controller.get_current_interface().parse_input(controller, t)

    # courses_needed_container.stub_all_unresolved_nodes()

    controller.is_printing = True

    controller.get_current_interface().parse_input(controller, 'ls')

    running = True
    while running:
        
        #print("current:", controller.get_current_interface()._node._node_id)
        #i = input(f'\033[93m> ')
        top = controller.get_current_interface()
        i = input(f'{top.name}: ')

        running = i != 'quit'
        if running:
            
            top.parse_input(controller, i)
