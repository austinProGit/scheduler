# Max Lewis and Thomas Merino 02/19/23
# CPSC 4176 Project

import pickle
from general_utilities import *
from instance_identifiers import StudentIdentifier

class SemesterDescription:
    
    def __init__(self, year, semester_type, courses):
        self.year = year
        self.semester_type = semester_type
        self.courses = courses

    def __str__(self):
        header = f'{self.year}, {SEMESTER_DESCRIPTION_MAPPING[self.semester_type]}: '
        return header + ', '.join(self.courses)

    def course_count(self):
        return sum(self.courses)


DEFAULT_DEGREE_DESCRIPTION = 'Degree Plan'

class ScheduleInfoContainer:
    
    # cf = confidence factor
    def __init__(self, semesters, student_identifier=None, degree_description=DEFAULT_DEGREE_DESCRIPTION, confidence_level=None):
        self._semesters = semesters
        self._student_identifier = student_identifier if student_identifier is not None else StudentIdentifier()
        self._degree_description = degree_description
        self._confidence_level = confidence_level

    # This method pickles ScheduleInfoContainer class object so data can be saved
    def pickle(self):
        pickled_data = pickle.dumps(self)
        return pickled_data

    def __str__(self):
        return '\n'.join(self._semesters)

    def get_schedule(self):
        return self._schedule

    def get_confidence_level(self):
        return self._confidence_level

    def semester_count(self):
        return len(self._semesters)

    def course_count(self):
        return sum(semester.course_count() for semester in self._semesters)



# class ScheduleInfoContainer:
    
#     # cf = confidence factor
#     def __init__(self, schedule, cf):
#         self._schedule = schedule
#         self._cf = cf

#     # This method pickles ScheduleInfoContainer class object so data can be saved
#     def pickle(self):
#         pickled_data = pickle.dumps(self)
#         return pickled_data

#     def display_container(self):
#         print(self._schedule)
#         print(self._cf)

#     def display_schedule(self):
#         print(self._schedule)

#     def display_cf(self):
#         print(self._cf)

#     def get_container(self):
#         return self._schedule, self._cf

#     def get_schedule(self):
#         return self._schedule

#     def get_cf(self):
#         return self._cf

#     def semester_count(self):
#         return len(self._schedule)

#     def course_count(self):
#         count = 0
#         for semester in self._schedule:
#             for course in semester:
#                 count = count + 1
#         return count

#lst = [['c'], ['d'], ['p'], [], ['m', 'h', 'e'], ['r', 't', 'f']]
#cf = 0.87

#container = ScheduleInfoContainer(lst, cf)
#pickled_data = container.pickle()
#print(pickled_data)
#reconstucted_data = pickle.loads(pickled_data)
#print(container)
#print(reconstucted_data)
#container.display_container()
#reconstucted_data.display_container()
#print(container.semester_count())
#print(container.course_count())

