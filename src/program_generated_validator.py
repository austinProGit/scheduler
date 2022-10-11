# Author: Austin Lee
# 9/21/22
# CPSC 4175 Group Project


import networkx as nx #Source for a DAG data strcture that is then used to check the course info requirements
#for invalid prerequisite requirements. 

# Errors that stop execution and force the user into error menu if raised.
class NonDAGCourseInfoError(Exception):
    pass

class InvalidCourseError(Exception):
    pass

# Main method for validating that the course path input by the user is valid.
# Returns a boolean of whether or not path is valid.
def validate_course_path(container):
    # Assume that the course path will be valid
    is_valid_course_path = True

    # Instantiate a new directed graph
    G = nx.DiGraph()

    # Get all the courseIDs as a list of IDs
    courseids = container.get_courseIDs()

    # List to store all invalid prereqs
    invalid_prereq_list = set()

# We want the program to store a list of invalid prereqs. 
# We need to create an errorList[] that stores all of the errors found during execution. (a list of strings)

    for course in courseids:                           # Iterate through the list of course IDs
        prereqs = container.get_prereqs(course)        # Get the prereqs for each course ID
        for prereq in prereqs:                         # For each prereq for a given course
            if prereq in courseids:                    # Check if the prereq is found in the list of courses
                if is_valid_course_path:
                    G.add_edge(prereq, course)             # Add a directed edge from the prereq to the course
            else:
                is_valid_course_path = False           # If invalid course is found, course path is invalid
                invalid_prereq_list.add(prereq)
                # raise InvalidCourseError(f'Invalid course {prereq} has been found.')
    
    if not is_valid_course_path:
        raise InvalidCourseError(f'Invalid course(s) {", ".join(invalid_prereq_list) } has been found.')
    
    cycle_list = []

    cycle_list = sorted(nx.simple_cycles(G))
    # note from thomas: "->".join(cycles) + "->" + cycles[-1]

    if len(cycle_list) > 0:
        raise NonDAGCourseInfoError(f'Cycle list: {cycle_list}')

    # Check to see if the created DAG has cycles; return result
    # is_valid_course_path = is_valid_course_path and nx.is_directed_acyclic_graph(G)
    # print(is_valid_course_path)
    # for edge in G.edges:
    #     print(edge)
    
    # MERINO: added this check with raise if test failed (note that the return value is kind of useless then; maybe refactor)
    # if not is_valid_course_path:
    #     raise NonDAGCourseInfoError('Invalid course prerequisite cycle has been found.')
    
    # return is_valid_course_path
    
        
