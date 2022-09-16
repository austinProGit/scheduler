import networkx as nx #Source for a DAG data strcture that is then used to check the course info requirements
#for invalid prerequisite requirements. 

# Main method for validating that the course path input by the user is valid.
# Returns a boolean of whether or not path is valid.
def validate_course_path(container):
    # Assume that the course path will be valid
    is_valid_course_path = True

    # Instantiate a new directed graph
    G = nx.DiGraph()

    # Get all the courseIDs as a list of IDs
    courseids = container.dummy_get_courseids()

    for course in courseids:                           # Iterate through the list of course IDs
        if not is_valid_course_path:                   # Check if an invalid course has been found
            break
        prereqs = container.dummy_get_prereqs(course)  # Get the prereqs for each course ID
        for prereq in prereqs:                         # For each prereq for a given course
            if prereq in courseids:                    # Check if the prereq is found in the list of courses
                G.add_edge(prereq, course)             # Add a directed edge from the prereq to the course
            else:
                is_valid_course_path = False           # If invalid course is found, course path is invalid
                print(f'Invalid course {prereq} has been found.')
                break
    
    # Check to see if the created DAG has cycles; return result
    is_valid_course_path = is_valid_course_path and nx.is_directed_acyclic_graph(G)
    # print(is_valid_course_path)
    # for edge in G.edges:
    #     print(edge)
    return is_valid_course_path

# ================================ Unit Tests =======================================================

def dag_validator_tests() :

    # Boolean to track if all tests pass
    tests_passed = True

    #This class simulates the course info container. It has access to the same methdos as does the real container.
    #The container needs to be updated to include the same return types for the methods used below.
    class dummy_course_info_dataframe_container:

        # constructor
        def __init__(self, course_path):
            self.course_path = course_path

    # Accesses the dataframe's course IDs and returns them as a list of strings.
        def dummy_get_courseids(self):
            courseids = []
            courseids = list(self.course_path.keys())
            return courseids

    # Accesses the dataframe's prerequisites for a given course and returns the prereqs as a list of strings.
        def dummy_get_prereqs(self, courseid):
            prereqs = []
            try:
                for prereq in self.course_path.get(courseid):
                    prereqs.append(prereq)
            except:
                prereqs = 'courseID not found'
            return prereqs
    
    # Our current required path, which is known to be valid.
    current_path = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': [],
        'CPSC 1302': ['CPSC 1301'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # shortest cycle: CPSC 1302 requires itself as a prerequisite.
    shortest_cycle = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113', 'MATH 5125'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': [],
        'CPSC 1302': ['CPSC 1301', 'CPSC 1302'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # short cycle: MATH 2125 and MATH 5125 require each other as prerequisites
    short_cycle = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113', 'MATH 5125'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': [],
        'CPSC 1302': ['CPSC 1301'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # MATH 2125 requires CPSC 5128 as a prerequisite, creating a long cycle.
    long_cycle = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113', 'CPSC 5128'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': [],
        'CPSC 1302': ['CPSC 1301'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # cycle 1: CPSC 2105 requires CPSC 5155 as a prerequisite. 
    # cycle 2: CPSC 2108 requires CPSC 4175 as a prerequisite.
    # cycle 3: CPSC 1301 requires CPSC 4176 as a prerequisite.
    # cycle 4: CPSC 1302 requires CPSC 5115 as a prerequisite.
    # cycle 5: CPSC 3175 requires CPSC 4175 as a prerequisite.
    multiple_cycles = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302', 'CPSC 4175'],
        'CPSC 1301': ['CPSC 4176'],
        'CPSC 1302': ['CPSC 1301', 'CPSC 5115'],
        'CPSC 2105': ['CPSC 1301', 'CPSC 5155'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108', 'CPSC 4175'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # invalid course: CPSC 1300 as a prerequisite for CPSC 1301
    single_invalid_course_prereq = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': ['CPSC 1300'],
        'CPSC 1302': ['CPSC 1301'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': [],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': []
    }

    # invalid course 1: BLAH 3000 as prerequisite for CPSC 3165
    # invalid course 2: MATH 2158 as prerequisite for CPSC 4000
    multiple_invalid_courses_prereqs = {
        'MATH 1113': [],
        'MATH 2125': ['MATH 1113'],
        'MATH 5125': ['MATH 2125'],
        'CPSC 2108': ['CPSC 1302'],
        'CPSC 1301': [],
        'CPSC 1302': ['CPSC 1301'],
        'CPSC 2105': ['CPSC 1301'],
        'CYBR 2159': ['CPSC 1301'],
        'CYBR 2106': ['CPSC 1301'],
        'CPSC 3175': ['CPSC 2108'],
        'CPSC 3125': ['CPSC 2108', 'CPSC 2105'],
        'CPSC 3131': ['CPSC 1302'],
        'CPSC 5135': ['CPSC 3175'],
        'CPSC 3165': ['BLAH 3000'],
        'CPSC 3121': ['CPSC 2105'],
        'CPSC 5155': ['CPSC 3121'],
        'CPSC 5157': ['CYBR 2159', 'CPSC 2108'],
        'CPSC 4175': ['CPSC 3175'],
        'CPSC 5115': ['MATH 5125', 'CPSC 2108'],
        'CPSC 5128': ['CPSC 5115'],
        'CPSC 4176': ['CPSC 4175'],
        'CPSC 4000': ['MATH 2158']
    }

    print('=============================== Start Dag Validator Tests ===============================\n')
    
    # Test the current path.
    if validate_course_path(dummy_course_info_dataframe_container(current_path)):
        print('Current path test passed.\n')
    else:
        tests_passed = False
        print('Current path test failed.\n')
    if not validate_course_path(dummy_course_info_dataframe_container(short_cycle)):
        print('Short cycle test passed.\n')
    else:
        tests_passed = False
        print('Short cycle test failed.\n')
    if not validate_course_path(dummy_course_info_dataframe_container(long_cycle)):
        print('Long cycle test passed.\n')
    else:
        test_passed = False
        print('Long cycle test failed.\n')
    if not validate_course_path(dummy_course_info_dataframe_container(multiple_cycles)):
        print('Multiple cycles test passed.\n')
    else:
        tests_passed = False
        print('Multiple cycles test failed.\n')
    if not validate_course_path(dummy_course_info_dataframe_container(single_invalid_course_prereq)):
        print('Single invalid course prereq test passed\n')
    else: 
        tests_passed = False
        print('Single invalid course prereq failed.\n')
    if not validate_course_path(dummy_course_info_dataframe_container(multiple_invalid_courses_prereqs)):
        print('Multiple invalid courses prereqs test passed.\n')
    else:
        tests_passed = False
        print('Multiple invalid courses prereqs test failed.\n')
    
    if tests_passed:
        print('Dag validator tests all passed.')
    else:
        print('At least one dag validator test failed.')

    print('=============================== End Dag Validator Tests ===============================\n')
    return tests_passed
