# Max Lewis and Thomas Merino 03/5/23
# CPSC 4176 Project

# TODO: dataframes may not be suitable for construction given the result will not be rectanglular.
# We will need to set the maximum before hand, and the empty slots will be filled with nulls.

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Iterator
    from pandas.core.series import Series as pdSeries
    


import pickle
from general_utilities import *
from instance_identifiers import StudentIdentifier, CourseIdentifier



class SemesterDescription:
    '''The description of a given semester.'''
    
    def __init__(self, year: int, semester_type: SemesterType, courses: Optional[list[CourseIdentifier]] = None) -> None:
        self.year: int = year
        self.semester_type: SemesterType = semester_type
        self.courses: list[CourseIdentifier] = courses if courses is not None else []

    def __str__(self) -> str:
        header: str = f'{self.year}, {SEMESTER_DESCRIPTION_MAPPING[self.semester_type]}: '
        return header + ', '.join(self.courses)

    def __getitem__(self, index) -> str:
        # TODO: this is used to support legacy formatters
        return self.courses[index].get_printable_name()

    def __len__(self) -> int:
        return len(self.courses)


DEFAULT_DEGREE_DESCRIPTION: str = 'Degree Plan'

# TODO: remove this!
DEBUG_YEAR: int = 2023

class ScheduleInfoContainer:

    @staticmethod
    def make_from_string_list(raw_list: list[list[str]], confidence_level: float = None, year: int = DEBUG_YEAR) -> ScheduleInfoContainer:

        semesters: list[SemesterDescription] = []
        running_year: int = year
        running_semester: SemesterType = FALL

        semester_list: list[str]
        for semester_list in raw_list:

            course_identifiers: list[CourseIdentifier] = []

            course_number: str
            for course_number in semester_list:
                course_identifiers.append(CourseIdentifier(course_number))

            semesters.append(SemesterDescription(running_year, running_semester, course_identifiers))

            running_semester = SEMESTER_TYPE_SUCCESSOR[running_semester]
            if running_semester == FALL:
                running_year += 1

        result: ScheduleInfoContainer = ScheduleInfoContainer(semesters=semesters, confidence_level=confidence_level)
        return result

    # cf = confidence factor
    def __init__(self, semesters: Optional[list[SemesterDescription]] = None, student_identifier: Optional[StudentIdentifier] = None, \
            degree_description: str = DEFAULT_DEGREE_DESCRIPTION, confidence_level: Optional[float] = None):
        self._semesters: list[SemesterDescription] = semesters if semesters is not None else []
        
        self._student_identifier: StudentIdentifier = student_identifier if student_identifier is not None \
            else StudentIdentifier()
        self._degree_description: str = degree_description
        self._confidence_level: Optional[float] = confidence_level

    def __str__(self) -> str:
        return str(self._semesters)

    def __iter__(self) -> Iterator[SemesterDescription]:
        return self._semesters.__iter__()

    # This method pickles ScheduleInfoContainer class object so data can be saved
    def pickle(self) -> bytes:
        pickled_data: bytes = pickle.dumps(self)
        return pickled_data

    def debug_display_container(self) -> None:
        print(self._semesters)
        print(self._confidence_level)

    def get_schedule(self) -> list[SemesterDescription]:
        return self._semesters

    def get_confidence_level(self) -> Optional[float]:
        return self._confidence_level

    def semester_count(self) -> int:
        return len(self._semesters)

    def max_semester_course_count(self) -> int:
        return max(len(semester) for semester in self._semesters)

    def course_count(self) -> int:
        return sum(len(semester) for semester in self._semesters)
    



# -------------------------------------- Dataframe version -------------------------------------- #

# # The following are imported for type annotations
# from __future__ import annotations
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from typing import Any, Tuple, Optional
#     import pandas as pd
#     from pandas.core.series import Series as pdSeries


# from math import nan

# def course_is_null(course_string) -> bool:
#     return course_string == nan or course_string.strip() == '' or course_string is None

# class SemesterDescription:
#     '''The description of a given semester (other than courses/schedulables).'''
    
#     def __init__(self, year: int, semester_type: SemesterType) -> None:
#         self.year: int = year
#         self.semester_type: SemesterType = semester_type

#     def __str__(self) -> str:
#         header: str = f'{self.year}, {SEMESTER_DESCRIPTION_MAPPING[self.semester_type]}: '
#         return header # + ', '.join(self.courses)


# DEFAULT_DEGREE_DESCRIPTION: str = 'Degree Plan'

# class ScheduleInfoContainer:

#     # cf = confidence factor
#     def __init__(self, semesters: Optional[pd.DataFrame] = None, student_identifier: Optional[StudentIdentifier] = None, \
#             degree_description: str = DEFAULT_DEGREE_DESCRIPTION, confidence_level: float = None):
#         # The dataframe for semsters will have str objects for columns and entries and will have int entires
#         # for the rows.
#         self._semesters: pd.DataFrame = semesters if semesters is not None else pd.DataFrame()
#         # The following is used to query the description of the semester by using the same key as the 
#         # dataframe.
#         self._semester_descriptions: dict[Any, SemesterDescription]
#         self._student_identifier: StudentIdentifier = student_identifier if student_identifier is not None \
#             else StudentIdentifier()
#         self._degree_description: str = degree_description
#         self._confidence_level: float = confidence_level

#     def __str__(self) -> str:
#         return f'{self._semesters}\n{self._semester_descriptions}'

#     def __iter__(self) -> SemesterIterator:
#         dataframe_iterator = self._semesters.__iter__()
#         return ScheduleInfoContainer.SemesterIterator(dataframe_iterator, self._semester_descriptions, self.max_semester_course_count())

#     # This method pickles ScheduleInfoContainer class object so data can be saved
#     def pickle(self) -> bytes:
#         pickled_data: bytes = pickle.dumps(self)
#         return pickled_data

#     def debug_display_container(self) -> None:
#         print(self._semester)
#         print(self._confidence_level)

#     def get_schedule(self) -> pd.DataFrame:
#         return self._semester

#     def get_confidence_level(self) -> float:
#         return self._confidence_level

#     def semester_count(self) -> int:
#         return len(self._semesters.columns)

#     def max_semester_course_count(self) -> int:
#         return len(self._semesters)

#     def course_count(self) -> int:
#         count: int = 0
#         semester_column: str
#         for semester_column in self._semesters:
#             semester: pdSeries = self._semesters[semester_column]
#             course: str
#             for course in semester:
#                 if not course_is_null(course):
#                     count += 1
#         return count
    
#     class SemesterIterator:

#         def __init__(self, dataframe_series: map, semester_descriptions: dict[Any, SemesterDescription], max_index: int) -> None:
#             self.dataframe_series: map = dataframe_series
#             self.semester_descriptions: dict[Any, SemesterDescription] = semester_descriptions
#             self._max_index: int = max_index

#         def __next__(self) -> Tuple[ScheduleInfoContainer.SemesterElement, SemesterDescription]:
#             next_column: Any = self.dataframe_series.__next__()
#             series: pdSeries = self.dataframe_series[next_column]
#             return ScheduleInfoContainer.SemesterElement(series, self._max_index), self.semester_descriptions[next_column]

#     class SemesterElement:
#         def __init__(self, series: pdSeries, max_index: int) -> None:
#             self.series: pdSeries = series
#             self._max_index: int = max_index

#         def __iter__(self) -> ScheduleInfoContainer.SemesterElement.CourseIterator:
#             return ScheduleInfoContainer.SemesterElement.CourseIterator(self.series, self._max_index)

#         class CourseIterator:
#             def __init__(self, series: pdSeries, max_index: int) -> None:
#                 self.series: pdSeries = series
#                 self._working_index = 0
#                 self._max_index = max_index

#             def __next__(self) -> str:
#                 if (self._working_index >= self._max_index):
#                     raise StopIteration
#                 result = self.series[self._working_index]
#                 if not course_is_null(result):
#                     raise StopIteration
#                 self._working_index += 1
#                 return result







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

