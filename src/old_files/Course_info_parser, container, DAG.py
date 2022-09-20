# Max Lewis 09/14/22
# CPSC 4175 Project

import pandas as pd
import networkx as nx

class Course_info_dataframe_container:
    
    def __init__(self, df):
        self._df = df

    def display(self):
        print(self._df)

    def get_name(self, courseid):       
        name = self.get_data('courseName', courseid)
        return name

    def get_coreqs(self, courseid):
        coreqs_list = self.get_comma_split_list(self.get_data('co-requisites', courseid))
        return coreqs_list

    def get_recommended(self, courseid):
        recommended_list = self.get_comma_split_list(self.get_data('recommended', courseid))       
        return recommended_list

    def get_courseIDs(self):
        courseID_list = self._df['courseID'].tolist()
        return courseID_list

    def get_availability(self, courseid):
        availability_list = self.get_space_split_list(self.get_data('availability', courseid))
        return availability_list  

    def get_prereqs(self, courseid):
        prereqs_list = self.get_comma_split_list(self.get_data('prerequisites', courseid))
        return prereqs_list

    # ............helper methods............................helper methods...........................helper methods

    def get_data(self, columnHeader, courseid): # helper method to access contents of df
        index = self._df[self._df['courseID'] == courseid].index[0]
        data = self._df.at[index, columnHeader]
        return data

    def get_comma_split_list(self, data): # helper method to separate data by commas
        data_list = [contents.strip() for contents in data.split(',')]
        if data_list[0] == 'none' or data_list[0] == '??':
            data_list = []
        return data_list

    def get_space_split_list(self, data): # helper method to separate data by space
        data_list = data.split()
        if data_list[0] == 'none' or data_list[0] == '??':
            data_list = []
        return data_list

# ------END OF CLASS---------END OF CLASS-----------END OF CLASS----------END OF CLASS---------------------------

# ******beginning of DAG_validator for df containers**********beginning of DAG_validator for dfs containers******

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

# ******ending of DAG_validator for df containers**********ending of DAG_validator for df containers*************

# ******beginning of course_info_parser**********beginning of course_info_parser*********************************

def load_course_info(file_name):
    df = pd.read_excel('src/input_files/' + file_name, sheet_name='Sheet1')
    return df

# ******ending of course_info_parser**********ending of course_info_parser***************************************

# Testing...

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
print('Course ID List: ', container1.get_courseIDs())
print()
print('DAG success check: ', validate_course_path(container1))

