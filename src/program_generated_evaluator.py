# Author: Austin Lee
# 9/21/22
# CPSC 4175 Group Project

# from course_info_container import *
import networkx as nx #Source for a DAG data strcture that is then used to check the course info requirements
#for invalid prerequisite requirements. 

# Errors that stop execution and force the user into error menu if raised.
class NonDAGCourseInfoError(Exception):
    pass

class InvalidCourseError(Exception):
    pass

class Report:
    def __init__(self,course_descendants_dict):
        self.course_descendants = course_descendants_dict

def make_graph(container, courseids):
    # Assume that the course path will be valid
    is_valid_course_path = True

    # Instantiate a new directed graph
    G = nx.DiGraph()
    # Get all the courseIDs as a list of IDs
    # courseids = container.get_courseIDs()

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
    return G

def make_course_descendants_dict(graph):
    nodes_in_graph = graph.nodes()
    course_descendants_dict = {key: 0 for key in nodes_in_graph}
    for key in course_descendants_dict.keys():
        course_descendants_dict[key] = len(list(nx.descendants(graph, key)))
    print(course_descendants_dict)
    return course_descendants_dict

def evaluate_container(container):
    courseids = container.get_courseIDs()
    graph = make_graph(container, courseids)
    make_course_descendants_dict(graph)
    return Report(make_course_descendants_dict)

# df = load_course_info('src/input_files/Course Info.xlsx')
# lst = load_course_info_excused_prereqs('src/input_files/Course Info.xlsx')
# evaluate_container(CourseInfoContainer(df, lst))