#creates a Case object that contains filename, gpa, course list, and type of case (source or target)
#input files and case base files are both made into Case objects


class Case():

    def __init__(self, file_name, gpa, course_list, type):
        self.file_name = file_name
        self.gpa = gpa
        self.course_list = course_list
        self.type = type #type values are either "input" or "case_base"

    def set_file_name(self, file_name):
        self.file_name = file_name

    def set_gpa(self, gpa):
        self.gpa = gpa

    def set_course_list(self, course_list):
        self.course_list = course_list

    def set_type(self, type):
        self.type = type

    def get_file_name(self):
        return self.file_name

    def get_gpa(self):
        return self.gpa

    def get_course_list(self):
        return self.course_list

    def get_type(self):
        return self.type


