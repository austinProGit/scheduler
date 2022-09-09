# Max Lewis 09/01/22
# CPSC 4175 Project

import pandas as pd

# These methods are self explanatory.  You may have to check out how dataframes operate and their internal methods.  
# The point of this easy version is to show the interaction at a very low scale.  I understand we want to keep things
# modular or generic to where we dont have to change a lot of code if structures change.  I have implemented type 
# checking at level that is easily understood.  Switch structures depend on Python version so I will avoid those for now.  
# I'm thinking maybe incorporating generics to determine type or even dict or whatever.  This is not finished just 
# a rough draft.  I know there is much redudancy here.  

class Course_info_container:
    
    def __init__(self, structure):
        self._structure = structure

    def display(self):
        print(self._structure)

    def get_name(self, courseid):
        _structure_type = type(self._structure)
        example_df_type = type(pd.DataFrame())
        name = ''
        if _structure_type == example_df_type:
            index = self._structure[self._structure['course ID'] == courseid].index[0]
            name = self._structure.at[index, 'course name']
        return name
   
    def get_availability(self, courseid):
        _structure_type = type(self._structure)
        example_df_type = type(pd.DataFrame())
        is_available = ''
        if _structure_type == example_df_type:
            index = self._structure[self._structure['course ID'] == courseid].index[0]
            is_available = self._structure.at[index, 'availability']
        return is_available

    def get_prereqs(self, courseid):
        _structure_type = type(self._structure)
        example_df_type = type(pd.DataFrame())
        prereqs = ''
        if _structure_type == example_df_type:
            index = self._structure[self._structure['course ID'] == courseid].index[0]
            prereqs = self._structure.at[index, 'pre-requisites']
        return prereqs

    def get_coreqs(self, courseid):
        _structure_type = type(self._structure)
        example_df_type = type(pd.DataFrame())
        coreqs = ''
        if _structure_type == example_df_type:
            index = self._structure[self._structure['course ID'] == courseid].index[0]
            coreqs = self._structure.at[index, 'co-requisites']
        return coreqs

    def get_recommended(self, courseid):
        _structure_type = type(self._structure)
        example_df_type = type(pd.DataFrame())
        recommended = ''
        if _structure_type == example_df_type:
            index = self._structure[self._structure['course ID'] == courseid].index[0]
            recommended = self._structure.at[index, 'recommended']
        return recommended

# ------END OF CLASS---------END OF CLASS-----------END OF CLASS----------END OF CLASS---------------------------

# ******beginning of course_info_parser**********beginning of course_info_parser*********************************

# Only for demonstration of the interaction between course_info_parser and Course_info_wrapper
# 2D array filled with data from our class_info excel sheet.  Maybe this has too much info, but
# this is for demonstration purposes only.

data = [['MATH 1113', 'Pre-Calculus', 'Fa Sp Su', 'none', 'none', 'none'], 
        ['CPSC 2108', 'Data Structures', 'Fa Sp Su', 'CPSC 1302', 'MATH 5125', 'MATH 2125']]

# As we all know by now this creates dataframes; I am trying to mimic the ideal dataframe that would
# be produced from the real course_info_parser minus most of the rows from the class info excel sheet.
# My next version uploaded will actually include structures derived from Vince's work, which he has
# already given me but I want every body to check this out and critique it before I move on.    

courses_info_df = pd.DataFrame(data, columns=['course ID', 'course name', 'availability',
                                               'pre-requisites', 'co-requisites', 'recommended'])

# container1 is now a class wrapped around a dataframe with methods as one object that Scheduler can import
# below are sanity checks

container1 = Course_info_container(courses_info_df)
container1.display()
course1 = 'CPSC 2108'
course2 = 'MATH 1113'
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