import networkx as nx #Source for a DAG data strcture that is then used to check the course info requirements
#for invalid prerequisite requirements. 

#This is a hard-coded dictionary of the course info, including course ids as keys and prerequisites as values.
course_info = {
            'MATH 1113': [],
            'MATH 2125': ['MATH 1113'],
            'MATH 5125': ['MATH 2125'],
            'CPSC 2108': ['CPSC 1302'],
            'CPSC 1301K': [],
            'CPSC 1302': ['CPSC 1301K'],
            'CPSC 2105': ['CPSC 1301K'],
            'CYBR 2159': ['CPSC 1301K'],
            'CYBR 2106': ['CPSC 1301K'],
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

#This class simulates the course info container. It has access to the same methdos as does the real container.
#The container needs to be updated to include the same return types for the methods used below.
class dummy_course_info_dataframe_container:

    # constructor
    def __init__(self) -> None:
        pass

# Accesses the dataframe's course IDs and returns them as a list of strings.
    def dummy_get_courseids(self):
        courseids = []
        courseids = list(course_info.keys())
        return courseids

# Accesses the dataframe's prerequisites for a given course and returns the prereqs as a list of strings.
    def dummy_get_prereqs(self, courseid):
        prereqs = []
        try:
            for prereq in course_info.get(courseid):
                prereqs.append(prereq)
        except:
            prereqs = 'courseID not found'
        return prereqs

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
    print(is_valid_course_path)
    for edge in G.edges:
        print(edge)
    return is_valid_course_path

validate_course_path(dummy_course_info_dataframe_container())