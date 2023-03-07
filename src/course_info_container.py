# Max Lewis 09/20/22
# CPSC 4175 Project

import pandas as pd
import re
import pickle
from dataframe_io import *
from driver_fs_functions import *
#from courses_needed_container import *
#from program_generated_evaluator import evaluate_container

class CourseInfoContainer:
    
    def __init__(self, df_dict):
        self._df_dict = df_dict

    def get_df_dict(self):
        return self._df_dict

    def set_df_dict(self, df_dict):
        self._df_dict = df_dict

    def df_exists(self, dept):
        success = False
        if dept in self._df_dict.keys():
            success = True
        return success

    def get_df(self, dept):
        if self.df_exists(dept):
            df = self._df_dict[dept]
            return df
        return None

    def get_df_courseIDs(self, dept):
        if self.df_exists(dept):
            df = self._df_dict[dept]
            lst = df['courseID'].tolist()
            return lst
        return None

    def set_df(self, dept, df):
        self._df_dict[dept] = df

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

    def display_df_dict(self):
        print(self._df_dict)

    def display_df(self, dept):
        if self.df_exists(dept):
            print(self.get_df(dept))
        else: print("Dataframe for department not in dataframe dictionary.")

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
        df_dept_lst = list(self._df_dict.keys())
        for dept in df_dept_lst:
            df = self._df_dict[dept]
            lst = df['courseID'].tolist()
            for course in lst:        
                courseID_list.append(course)
        return courseID_list

    def get_availability(self, courseid):
        availability_list = self.get_space_split_list(self.get_data('availability', courseid))
        if availability_list == []: # If list is empty we default to below availability
            availability_list = ['Fa', 'Sp', '--']
        return availability_list

    def get_prereqs(self, courseid):
        prereqs_list = self.get_data('prerequisites', courseid)
        return prereqs_list

    def get_coreqs(self, courseid):
        coreqs_list = self.get_data('co-requisites', courseid)
        return coreqs_list

    def get_recommended(self, courseid):
        recommended_list = self.get_data('recommended', courseid)     
        return recommended_list

    def get_restrictions(self, courseid):
        restrictions = self.get_data('restrictions', courseid)     
        return restrictions

    def get_note(self, courseid):   
        note = self.get_data('note', courseid)
        return note

    def get_importance(self, courseid):
        importance = self.get_data('importance', courseid)
        if importance == None:
            return 60
        return importance

    # This method pickles CourseInfoContainer class so data can be saved
    def pickle(self):
        pickled_data = pickle.dumps(self)
        return pickled_data

    # Combines parameter container dfs with this container dfs; the container with the most updated data needs to be first 
    # when listing frames.  Dataframes with sheet name matches will be added to each other, then duplicates will be deleted.
    # Sheets without matches will be added.  Use this method to update this container with the most current data.
    def update_container_keeping_external_duplicates(self, container):
        df_names_a = list(self._df_dict.keys())
        df_names_b = list(container.get_df_dict().keys())
        for name_a in df_names_a:
            for name_b in df_names_b:
                if name_b == name_a:
                    self_df = self.get_df(name_a)
                    df = container.get_df(name_b)
                    frames = [df, self_df]
                    result = pd.concat(frames)
                    result = result[~result.index.duplicated(keep='first')]
                    self._df_dict[name_a] = result
                if name_b != name_a:
                    df = container.get_df(name_b)
                    self._df_dict[name_b] = df
        return self._df_dict

    def write_df_dict_xlsx(self, filename):
        dataframe_xlsx_writes(filename, self._df_dict)

    # ............helper methods............................helper methods...........................helper methods
    # methods account for None, 'none', or '??' values, and still return lists

    def get_data(self, columnHeader, courseid): # helper method to access contents of df
        if courseid == None: return
        data = None
        department = re.findall(r"^\w+", courseid)
        department = department[0]
        df = self.get_df(department)
        if(self.df_exists(department) and self.validate_course(courseid)):
            index = df[df['courseID'] == courseid].index[0]
            data = df.at[index, columnHeader]
            if df.isnull().at[index, columnHeader] or data == 'none' or data == None or data == '??' or data == '' or data == ' ' or data == '  ':
                data = None
        return data

    def get_comma_split_list(self, data): # helper method to separate data by commas
        if data == None:
            return []
        else:
            data_list = [contents.strip() for contents in data.split(',')]
            return data_list

    def get_space_split_list(self, data): # helper method to separate data by space
        if data == None:
            return []
        else:
            data_list = data.split()
            return data_list

    # Covers cases where hours are imbedded in CSU's website format or stand alone
    def get_imbedded_hours(self, data):
        if data == None:
            return 0
        elif (len(str(data)) == 1):
            return int(data)
        else:
            data = list(map(int, re.findall(r'\d+', data)))
            return data[-1]

    def validate_course(self, course):
        lst = self.get_courseIDs()
        return course in lst

# ..........end of helper methods.......................end of helper methods......................helper methods
# ------END OF CLASS---------END OF CLASS-----------END OF CLASS----------END OF CLASS---------------------------

# Combining two containers dataframes where the left parameter container keeps duplicates and deletes one from
# the right container dataframe
@staticmethod
def combine_container_keeping_right_duplicates(container_a, container_b):
    df_dict_a = container_a.get_df_dict()
    df_dict_b = container_b.get_df_dict()
    df_names_a = list(df_dict_a.keys())
    df_names_b = list(df_dict_b.keys())
    for name_a in df_names_a:
        for name_b in df_names_b:
            if name_b == name_a:
                left_df = container_a.get_df(name_a)
                right_df = container_b.get_df(name_b)
                frames = [right_df, left_df]
                result = pd.concat(frames)
                result = result[~result.index.duplicated(keep='first')]
                container_a.set_df(name_b, result)
            if name_b != name_a:
                right_df = container_b.get_df(name_b)
                container_a.set_df(name_b, right_df)
    return container_a.get_df_dict()

@staticmethod
def write_df_dict_xlsx(container, filename):
    dataframe_xlsx_writes(filename, container.get_df_dict())

# ******beginning of course_info_parser**********beginning of course_info_parser*********************************

# Author: Vincent Miller
# Contributer: Max Lewis
def load_course_info(file_name):
    df_dict = dataframe_xlsx_read(file_name, sheet=None)
    return df_dict

# ******ending of course_info_parser**********ending of course_info_parser***************************************

# quick test below
#file0 = get_source_path()
#file0 = get_source_relative_path(file0, 'input_files/Course Info.xlsx')
#dfdict = load_course_info(file0)
#container = CourseInfoContainer(dfdict)
#write_df_dict_xlsx(container, file0)
#print(container.update_container_keeping_external_duplicates(container1))
#print(combine_container_keeping_right_duplicates(container, container1))
