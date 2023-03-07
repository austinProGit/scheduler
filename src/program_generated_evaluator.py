# Author: Austin Lee
# 9/21/22
# CPSC 4175 Group Project

# Used to create and process a directed acyclic graph from a Course Info .xlsx input file.
import networkx as nx

class NonDAGCourseInfoError(Exception):
    """
    Custom exception raised if cycles found in Course Info input. Stops execution and 
    forces user into error menu if raised.

    """
    pass

# 
class InvalidCourseError(Exception):
    """
    Custom exception raised if invalid prereq found in Course Info input. Stops execution and 
    forces user into error menu if raised.

    """
    pass

class CourseInfoEvaluationReport: # Lew added graph to Report
    """
    Report is used to export the graph object of the Course Info input and 
    the number of descendants of each course in the given path.

    Constructor Parameters
    ----------
    arg1 : dictionary
        Course descendants, where keys are courses in a given path, and 
        values are the number of descendants (courses that are unlocked 
        by taking a given course) are the values.
    arg2 : graph object
        Networkx graph object created from processing the Course Info input
        as a Directed Acyclic Graph.

    """
    def __init__(self, course_descendants_dict, graph):
        self.course_descendants = course_descendants_dict
        self.graph = graph

def make_graph(container, courseids):
    """
    Makes Networkx graph object.

    Instantiate a new networkx directed acyclic graph object. For every course in 
    course ids, get the course's prerequisites. For each prerequisite, check if it 
    is a known (valid) course. If it is not, append the prereq to a list of invalid 
    prereqs. Otherwise, add an edge to the graph object between the prereq and the 
    current course being processed. After all prereqs and courses have been processed,
    raise an exception and stop execution, conveying to the user the invalid prereqs 
    found. If no invalid prereqs found, continue to search the graph for cycles. After 
    checking the graph for cycles, raise an error containing all cycles found if any
    cycles found.

    Parameters
    ----------
    arg1 : container
        This container object is created by the course_info_container module/file. 
        Inside this object is all of the info from the Course Info input. Furthermore,
        has a dictionary with the number of descendants of each coruse, a directed 
        acyclic graph, and excused prereqs.
    arg2 : courseids
        A list of every course id from the Course Info excel input.

    Returns
    -------
    networkx graph
        Returns a networkx directed acyclic graph object, or raises an error if the 
        graph is unable to be made from the Course Info input.

    """
    is_valid_course_path = True # Assume that the course path will be valid

    
    G = nx.DiGraph() # Instantiate a new directed graph
    
    excused_prereqs = container.get_excused_prereqs() # Get all the valid prereqs not listed as courses

    invalid_prereqs = []

    for course in courseids: 
        prereqs = container.get_prereqs(course)
        for prereq in prereqs:
            if prereq in courseids or prereq in excused_prereqs:
                if is_valid_course_path:
                    G.add_edge(prereq, course) # Add a directed edge from the prereq to the course
            else:
                is_valid_course_path = False # If invalid course is found, course path is invalid
                invalid_prereqs.append(prereq)
    
    if not is_valid_course_path: #If any invalid prereq has been found
        raise InvalidCourseError(f'Invalid course(s) {", ".join(invalid_prereqs) } has been found.')
    
    cycles_list = [] #Stores any cycles found

    cycles_list = sorted(nx.simple_cycles(G))

    cycles_strings = [] #Stores the display string for found cycles

    # Networkx returns cycles in an unpredictable order given the same graph input. This section
    # guarantees predictable and consistent output of cycles.
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
    """Takes a networkx directed acyclic graph as an argument and returns a dictionary of the number
    of descendants for each node in the graph."""
    nodes_in_graph = graph.nodes()
    course_descendants_dict = {key: 0 for key in nodes_in_graph}
    for key in course_descendants_dict.keys():
        course_descendants_dict[key] = len(list(nx.descendants(graph, key)))
    return course_descendants_dict

def evaluate_container(container):
    """Takes a course info container object as an argument. Creates and returns a Report object 
    that wraps a course descendants dictionary and a graph object."""
    courseids = container.get_courseIDs()
    graph = make_graph(container, courseids)
    dict = make_course_descendants_dict(graph)
    return CourseInfoEvaluationReport(dict, graph)

# df = load_course_info('src/input_files/Course Info.xlsx')
# lst = load_course_info_excused_prereqs('src/input_files/Course Info.xlsx')
# evaluate_container(CourseInfoContainer(df, lst))