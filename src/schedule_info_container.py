# Max Lewis and Thomas Merino 04/24/23
# CPSC 4176 Project

# TODO: dataframes may not be suitable for construction given the result will not be rectanglular.
# We will need to set the maximum before hand, and the empty slots will be filled with nulls.

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Iterator, Any
    from pandas.core.series import Series as pdSeries
    from requirement_tree import RequirementsTree
    from course_info_container import CourseInfoContainer

import pickle
from general_utilities import *
from instance_identifiers import StudentIdentifier, CourseIdentifier, Schedulable


DEFAULT_DEGREE_DESCRIPTION: str = 'Degree Plan'
DEFAULT_STARTING_YEAR: int = ESTIMATED_NEXT_YEAR


class SemesterDescription:
    '''The description of a given semester.'''
    
    def __init__(self, year: int, semester_type: SemesterType, courses: Optional[list[Schedulable]] = None) -> None:
        self.year: int = year
        self.semester_type: SemesterType = semester_type
        self.courses: list[Schedulable] = courses if courses is not None else []

    def __str__(self) -> str:
        header: str = f'{self.year}, {SEMESTER_DESCRIPTION_MAPPING[self.semester_type]}: '
        return header + ', '.join(self.str_iterator())

    def __iter__(self) -> Iterator[Schedulable]:
        return self.courses.__iter__()
    
    def __getitem__(self, index) -> str:
        # TODO: this is used to support legacy formatters
        return self.courses[index].get_printable_name()

    def __len__(self) -> int:
        return len(self.courses)

    def __contains__(self, element: Any):
        return any(element == course for course in self.courses)

    def str_iterator(self) -> Iterator[str]:
        return [str(course) for course in self.courses].__iter__()



class ScheduleInfoContainer:

    @staticmethod
    def make_from_string_list(raw_list: list[list[str]], course_info: ScheduleInfoContainer,
            starting_semester: SemesterType = FALL, starting_year: int = DEFAULT_STARTING_YEAR,
            confidence_level: Optional[float] = None) -> ScheduleInfoContainer:

        semesters: list[SemesterDescription] = []
        running_year: int = starting_year
        running_semester: SemesterType = starting_semester

        semester_list: list[str]
        for semester_list in raw_list:

            course_identifiers: list[CourseIdentifier] = \
                [CourseIdentifier(course_number) for course_number in semester_list]

            # course_number: str
            # for course_number in semester_list:
            #     course_identifiers.append(CourseIdentifier(course_number))

            schedulables: list[Schedulable] = Schedulable.create_schedulables(course_identifiers, course_info)

            semesters.append(SemesterDescription(running_year, running_semester, schedulables))

            running_semester = SEMESTER_TYPE_SUCCESSOR[running_semester]
            if running_semester == SPRING:
                running_year += 1
        
        return ScheduleInfoContainer(semesters=semesters, confidence_level=confidence_level)

    # TODO: this is redundant (combine this and the above code)
    @staticmethod
    def make_from_schedulables_list(raw_list: list[list[Schedulable]],
            starting_semester: SemesterType = ESTIMATED_NEXT_SEMESTER, starting_year: int = ESTIMATED_NEXT_YEAR,
            confidence_level: Optional[float] = None) -> ScheduleInfoContainer:

        semesters: list[SemesterDescription] = []
        running_year: int = starting_year
        running_semester: SemesterType = starting_semester

        schedulables_list: list[CourseIdentifier]
        for schedulables_list in raw_list:
            semesters.append(SemesterDescription(running_year, running_semester, schedulables_list))

            running_semester = SEMESTER_TYPE_SUCCESSOR[running_semester]
            if running_semester == SPRING:
                running_year += 1
        while not semesters[-1]:
            semesters.pop()
            
        
        return ScheduleInfoContainer(semesters=semesters, confidence_level=confidence_level)


    def __init__(self, semesters: Optional[list[SemesterDescription]] = None,
            confidence_level: Optional[float] = None,
            student_identifier: Optional[StudentIdentifier] = None,
            degree_description: str = DEFAULT_DEGREE_DESCRIPTION):
        self._semesters: list[SemesterDescription] = semesters if semesters is not None else []
        self._confidence_level: Optional[float] = confidence_level
        
        self._student_identifier: StudentIdentifier = student_identifier if student_identifier is not None \
            else StudentIdentifier()
        self._degree_description: str = degree_description

    def __str__(self) -> str:
        return "\n".join([str(semester) for semester in self._semesters]) if len(self._semesters) != 0 else '*Empty Path*'

    def __iter__(self) -> Iterator[SemesterDescription]:
        return self._semesters.__iter__()

    # This method pickles ScheduleInfoContainer class object so data can be saved
    def pickle(self) -> bytes:
        pickled_data: bytes = pickle.dumps(self)
        return pickled_data

    def debug_display_container(self) -> None:
        print(str(self))
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

    def to_list_of_lists(self) -> list[list[Schedulable]]:
        return list(list(course for course in semester) for semester in self)
    


