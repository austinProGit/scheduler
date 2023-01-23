# Max Lewis 09/20/22
# CPSC 4175 Project

import pandas as pd
import re
import pickle

class CourseInfoContainer:
    
    def __init__(self, df, excused_prereqs):
        self._df = df
        self._excused_prereqs = excused_prereqs

    # This method pickles CourseInfoContainer class so data can be saved
    def pickle(self):
        pickled_data = pickle.dumps(self)
        return pickled_data

    # This method should only be used to load Report after construction of respective container and graph
    def load_report(self, report):
        self._report = report

    # Used after load_report(self, report) to get number of descendants of each course
    def get_weight(self, courseid):
        weight = None
        if courseid in self._report.course_descendants:
            weight = self._report.course_descendants[courseid]
        return weight

    # This returns boolean if course is in dictionary of report.  Note we already have a method to do this without report
    # called validate_course(courseid).  Can only use this method after report is loaded.
    def is_course_in_report(self, courseid):
        return courseid in self._report.course_descendants

    def get_excused_prereqs(self):
        return self._excused_prereqs

    def display_df(self):
        print(self._df)

    def display_weights(self):
        print(self._report.course_descendants)

    def display_graph(self):
        print(self._report.graph)

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
        if availability_list == []: # If list is empty we default to below availability
            availability_list = ['Fa', 'Sp', '--']
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

    def get_importance(self, courseid):
        importance = self.get_data('importance', courseid)
        return importance

    # ............helper methods............................helper methods...........................helper methods
    # methods account for None, 'none', or '??' values, and still return lists

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

    # Covers cases where hours are imbedded in CSU's website format or stand alone
    def get_imbedded_hours(self, data):
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

# Author: Vincent Miller
def load_course_info(file_name):
    df = pd.read_excel(file_name, sheet_name='CPSC')
    return df

def load_course_info_excused_prereqs(file_name):
    df = pd.read_excel(file_name, sheet_name='ExcusedPrereqs')
    return df.courseID.values.tolist()

# ******ending of course_info_parser**********ending of course_info_parser***************************************

# quick test below
#from program_generated_evaluator import evaluate_container # imported for self testing purposes
#df = load_course_info('src/input_files/Course Info.xlsx')
#lst = load_course_info_excused_prereqs('src/input_files/Course Info.xlsx')
#container = CourseInfoContainer(df, lst)
#report = evaluate_container(container)
#container.load_report(report)
#print(container.get_importance('CPSC 1301'))
