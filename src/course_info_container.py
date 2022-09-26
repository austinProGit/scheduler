# Max Lewis 09/20/22
# CPSC 4175 Project

import pandas as pd
import re
from dag_validator import validate_course_path

class CourseInfoContainer:
    
    def __init__(self, df):
        self._df = df

    def display(self):
        print(self._df)

    def get_name(self, courseid): 
        name = self.get_data('courseName', courseid)
        return name


    def get_hours(self, courseid): 
        hours = self.get_data('hours', courseid)
        hours_refined = self.get_imbedded_hours(hours)
        return hours_refined


    def get_courseIDs(self):
        courseID_list = []
        if self.validate_header('courseID'):
            courseID_list = self._df['courseID'].tolist()
        return courseID_list

    def get_availability(self, courseid):
        availability_list = self.get_space_split_list(self.get_data('availability', courseid))
        # MERINO: We may want to send an error (notification pattern or error raise) when list is empty or use something like "availability_list if availability_list else ['Fa', 'Sp', 'Su']" to default to always available. This is necessary to prevent infinite loops on the scheduler when a unrecognized course is entered.
        return availability_list

    def get_prereqs(self, courseid):
        prereqs_list = self.get_comma_split_list(self.get_data('prerequisites', courseid))
        return prereqs_list

    def get_coreqs(self, courseid):
        coreqs_list = self.get_comma_split_list(self.get_data('co-requisites', courseid))
        return coreqs_list

    def get_recommended(self, courseid):
        recommended_list = self.get_comma_split_list(self.get_data('recommended', courseid))       
        return recommended_list

    def get_isElective(self, courseid):
        success = False
        isElective = self.get_data('isElective', courseid)   
        if isElective == 1: success = True
        return success

    def get_electives(self):
        courses = self.get_courseIDs()
        electives = []
        for course in courses:
            if self.get_isElective(course):
                electives.append(course)
        return electives

    def get_restrictions(self, courseid):
        restrictions_list = self.get_comma_split_list(self.get_data('restrictions', courseid))       
        return restrictions_list

    def get_note(self, courseid):   
        note = self.get_data('note', courseid)
        return note

    # Need get electives list

    # ............helper methods............................helper methods...........................helper methods
    # methods now account for None, 'none', or '??' values, and still return lists

    def get_data(self, columnHeader, courseid): # helper method to access contents of df
        data = None
        index = None
        if(self.validate_header(columnHeader) and self.validate_course(courseid)):
            index = self._df[self._df['courseID'] == courseid].index[0]
            data = self._df.at[index, columnHeader]
            if self._df.isnull().at[index, columnHeader] or data == 'none' or data == '??':
                data = None
        return data

    def get_comma_split_list(self, data): # helper method to separate data by commas
        if data == None or data == 'none' or data == '??':
            return []
        else:
            data_list = [contents.strip() for contents in data.split(',')]
            return data_list

    def get_space_split_list(self, data): # helper method to separate data by space
        if data == None or data == 'none' or data == '??':
            return []
        else:
            data_list = data.split()
            return data_list

    def get_imbedded_hours(self, data): # this method covers cases where hours are imbedded pulled jargon or stand alone
        if data == None or data == 'none' or data == '??':
            return 0
        if (len(str(data)) == 1):
            return int(data)
        else:
            data = list(map(int, re.findall(r'\d+', data)))
        return data[-1]

    def validate_course(self, course):
        lst = self.get_courseIDs()
        return course in lst

    def validate_header(self, column_names):
        lst = self._df.columns
        return column_names in lst


# ------END OF CLASS---------END OF CLASS-----------END OF CLASS----------END OF CLASS---------------------------

# ******beginning of course_info_parser**********beginning of course_info_parser*********************************

# MERINO: probably should give Vincent credit here (I believe this is his)
def load_course_info(file_name):
    # MERINO: changed name to "Sheet1"
    df = pd.read_excel(file_name, sheet_name='Sheet1') # !!! insert this sheet name or ClassInfo if using ClassInfo.xlsx!!!
    return df

# ******ending of course_info_parser**********ending of course_info_parser***************************************
# Line below will be deleted when we merge all files
# MERINO: commented this out
#container = CourseInfoContainer(load_course_info('src/input_files/course_info.xlsx'))
#print(validate_course_path(container))
