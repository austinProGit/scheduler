# Austin 09/15/22
# CPSC 4175 Project
import networkx as nx

# Returns a boolean of whether or not path is valid.
def validate_course_path(container):
    is_valid_course_path = True
    G = nx.DiGraph()
    courseids = container.get_courseIDs()

    for course in courseids:                           # Iterate through the list of course IDs
        if not is_valid_course_path:                   # Check if an invalid course has been found
            break
        prereqs = container.get_prereqs(course)  # Get the prereqs for each course ID
        for prereq in prereqs:                         # For each prereq for a given course
            if prereq in courseids:                    # Check if the prereq is found in the list of courses
                G.add_edge(prereq, course)             # Add a directed edge from the prereq to the course
            else:
                is_valid_course_path = False           # If invalid course is found, course path is invalid
                print(f'Invalid course {prereq} has been found.')
                break

    
    # Check to see if the created DAG has cycles; return result
    is_valid_course_path = is_valid_course_path and nx.is_directed_acyclic_graph(G)
    for edge in G.edges:
        print(edge)
    return is_valid_course_path
