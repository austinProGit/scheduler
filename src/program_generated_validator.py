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

    # Get all the valid prereqs not listed as courses
    excused_prereqs = container.get_excused_prereqs()

# We want the program to store a list of invalid prereqs. 
# We need to create an errorList[] that stores all of the errors found during execution. (a list of strings)

    for course in courseids:                                    # Iterate through the list of course IDs
        prereqs = container.get_prereqs(course)                 # Get the prereqs for each course ID
        for prereq in prereqs:                                  # For each prereq for a given course
            if prereq in courseids or prereq in excused_prereqs:  # Check if the prereq is found in the list of courses
                if is_valid_course_path:
                    G.add_edge(prereq, course)                  # Add a directed edge from the prereq to the course
            else:
                is_valid_course_path = False                    # If invalid course is found, course path is invalid
                excused_prereqs.append(prereq)
    
    if not is_valid_course_path:
        raise InvalidCourseError(f'Invalid course(s) {", ".join(excused_prereqs) } has been found.')
    
    cycles_list = []

    cycles_list = sorted(nx.simple_cycles(G))
    cycles_strings = []
    for cycle in cycles_list:
        cycle.reverse()
        new_first_index = next((cycle.index(id) for id in courseids if id in cycle))
        cycle = cycle[new_first_index:] + cycle[:new_first_index]
        cycle.append(cycle[0])
        cycles_strings.append('-->'.join(cycle))

    if len(cycles_list) > 0:
        raise NonDAGCourseInfoError(f'Cycle list: {cycles_strings}')
    
        
