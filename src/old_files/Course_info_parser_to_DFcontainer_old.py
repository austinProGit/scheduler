# Max Lewis 09/10/22
# CPSC 4175 Project

import pandas as pd

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
        prereqs = ''
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

# ------END OF CLASS---------END OF CLASS-----------END OF CLASS----------END OF CLASS---------------------------

# ******beginning of course_info_parser**********beginning of course_info_parser*********************************

# Vince crushed this; made my life easy!!!
def get_course_info(file_name):
    """ inputs file_name, reads excel file (specifically Sheet1),
        returns pandas dataframe """
    df = pd.read_excel('src/input_files/' + file_name, sheet_name='Sheet1')
    return df

# We call get_course_info(filename) as the parameter for the "constuctor" of our container object assigned to a variable.
# Again some sanity checks to keep us happy.  Note in ClassInfo.xlsx availability is spelled wrong; just correct that
# in your excel file.  We can separate these modules and classes if preferred.  Smooth like butter...

container1 = Course_info_dataframe_container(get_course_info('ClassInfo.xlsx'))
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
print()
print('Course ID List: ', container1.get_courseID_list())
print('Availability List: ',container1.get_availability_list(course1))
print('Availability List: ',container1.get_availability_list(course2))