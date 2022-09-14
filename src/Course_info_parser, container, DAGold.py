# Max Lewis 09/10/22
# CPSC 4175 Project

import pandas as pd
import networkx as nx

class Course_info_dataframe_container:
    
    def __init__(self, df):
        self._df = df

    def display(self):
        print(self._df)

    def get_name(self, courseid):       
        index = self._df[self._df['courseID'] == courseid].index[0]
        name = self._df.at[index, 'courseName']
        return name
   
    def get_availability(self, courseid):
        index = self._df[self._df['courseID'] == courseid].index[0]
        availability = self._df.at[index, 'availability']
        return availability

    def get_prereqs(self, courseid):
        index = self._df[self._df['courseID'] == courseid].index[0]
        prereqs = self._df.at[index, 'prerequisites']
        return prereqs

    def get_coreqs(self, courseid):
        index = self._df[self._df['courseID'] == courseid].index[0]
        coreqs = self._df.at[index, 'co-requisites']
        return coreqs

    def get_recommended(self, courseid):
        index = self._df[self._df['courseID'] == courseid].index[0]
        recommended = self._df.at[index, 'recommended']
        return recommended

    def get_courseID_list(self):
        list_of_courseIDs = self._df['courseID'].tolist()
        return list_of_courseIDs

    def get_availability_list(self, courseid):
        index = self._df[self._df['courseID'] == courseid].index[0]
        availability = self._df.at[index, 'availability']
        availability_list = availability.split()
        return availability_list

    # This method is heavily dependent on how we orient our ClassInfo.xlsx.  To make our outputs cleaner I suggest deleting
    # all columns and rows from notes and past it.  This method is build specific to our excel and validate_course_path(con).  

    def get_prereqs_list(self, courseid):
        index = self._df[self._df['courseID'] == courseid].index[0]
        prereqs = self._df.at[index, 'prerequisites']
        prereqs_list = [word.strip() for word in prereqs.split(',')]
        if prereqs_list[0] == 'none' or prereqs_list[0] == '??':
            prereqs_list = []
        return prereqs_list

        

# ------END OF CLASS---------END OF CLASS-----------END OF CLASS----------END OF CLASS---------------------------

# ******beginning of DAG_validator for df containers**********beginning of DAG_validator for dfs containers******

# Returns a boolean of whether or not path is valid.
def validate_course_path(container):
    # Assume that the course path will be valid
    is_valid_course_path = True

    # Instantiate a new directed graph
    G = nx.DiGraph()

    # Get all the courseIDs as a list of IDs
    courseids = container.get_courseID_list()

    for course in courseids:                           # Iterate through the list of course IDs
        if not is_valid_course_path:                   # Check if an invalid course has been found
            break
        prereqs = container.get_prereqs_list(course)  # Get the prereqs for each course ID
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

# ******ending of DAG_validator for df containers**********ending of DAG_validator for df containers*************

# ******beginning of course_info_parser**********beginning of course_info_parser*********************************

# Vince crushed this; made my life easy!!!
def load_course_info(file_name):
    """ inputs file_name, reads excel file (specifically Sheet1),
        returns pandas dataframe """
    df = pd.read_excel('src/input_files/' + file_name, sheet_name='Sheet1')
    return df

# ******ending of course_info_parser**********ending of course_info_parser***************************************

# We call get_course_info(filename) as the parameter for the "constuctor" of our container object assigned to a variable.
# Again some sanity checks to keep us happy.  Note in ClassInfo.xlsx availability is spelled wrong; just correct that
# in your excel file.  We can separate these modules and classes if preferred.  Smooth like butter...

container1 = Course_info_dataframe_container(load_course_info('ClassInfo.xlsx'))
container1.display()
course1 = 'CPSC 5157'
course2 = 'CPSC 3125'
print()
print('Name: ', container1.get_name(course1))
print('Availability: ', container1.get_availability(course1))
print('Pre-requisites: ', container1.get_prereqs(course1))
print('Co-requisites: ', container1.get_coreqs(course1))
print('Recommendations: ', container1.get_recommended(course1))
print()
print('Name: ',container1.get_name(course2))
print('Availability: ',container1.get_availability(course2))
print('Pre-requisites: ', container1.get_prereqs(course2))
print('Co-requisites: ', container1.get_coreqs(course2))
print('Recommendations: ',container1.get_recommended(course2))
print()
print('Course ID List: ', container1.get_courseID_list())
print('Availability List: ',container1.get_availability_list(course1))
print('Availability List: ',container1.get_availability_list(course2))
print()
print('Prerequisite List: ',container1.get_prereqs_list(course1))
print('Prerequisite List: ',container1.get_prereqs_list(course2))
print()
print(validate_course_path(container1))
