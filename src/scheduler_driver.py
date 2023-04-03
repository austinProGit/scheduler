# Thomas Merino
# 4/2/2023
# CPSC 4176 Project


# TODO: recommend to Lew caching the queried course from the info container (many requests utilizing the same
# course identifier)


# TODO: schedule evaluator needs to be added (dummied) with the new coreq and concurr prereqs approach taken into account

# TODO: (IMPORTANT) at the moment, coreq.s in constructive scheduler do not work fully:
#               We just look for "simple coreq.s", which means 1 coreq in which every dependant course's other requirements are ignored.
#               It is assumed the requirements for the course and it's coreq. are the same

from __future__ import annotations
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from typing import Optional, Any
    from requirement_tree import RequirementsTree, SchedulableParameters
    from scheduling_parameters_container import ConstructiveSchedulingParametersContainers
    from course_info_container import CourseInfoContainer
    from courses_needed_container import CoursesNeededContainer
    from pathlib import Path
    from end_reports import ValidationReportResult
from end_reports import VALIDATION_REPORT_PARSED, VALIDATION_REPORT_ERRORS, VALIDATION_REPORT_NO_FILE
from requirement_parser import RequirementsParser
from general_utilities import *

# TODO: This is not importing correctly from end_reports.py (FIX!)
VALIDATION_REPORT_WORKING = 0x03

# TODO: THIS IS A TEST IMPORT (REMOVE)!!
from degree_extraction_container import DegreeExtractionContainer

# TODO: TEMP
from scheduling_parameters_container import SchedulerParameterContainer 
from pathlib import Path 

from expert_system_module import ExpertSystem, DynamicKnowledge
from schedule_info_container import *
from general_utilities import *
from requirement_parser import RequirementsParser

from bisect import insort
from math import inf
from random import choice, randint, shuffle, random
from time import perf_counter


"""

============== Here are the types ==============

CourseIdentifier:
    This represents a single course or a unique pattern for a course.
    If the identifier is concrete/not a stub, then identifiers with the same course number/id are considered equivalent.
    If the identifier is not (the above), then no other identifier is consider equivalent.

Schedulable:
    This represents individual entities/entries that are entered into a schedule.
    A schedulable contains a CourseIdentifier to classify it.

NOTE: to differentiate between CourseIdentifiers and Schedulables, identifiers can be passed around/shared, duplicated,
recreated, etc., and each will work as expected. They serve as keys to identify courses or classes of courses.
Schedulables, on the other hand, represent entries in a schedule. Each schedulable should appear in a path only once--
a identifier may appear in multiple schedulables.


SemesterDescription:
    This stores a list of schedulables, representing a single scheduled semester
    
ScheduleInfoContainer:


PathValidationReport:
PathValidationReport.Error:
CourseInfoContainer:
ConstructiveScheduler:
GeneticScheduler:


============== Here are the methods ==============

rigorous_validate_schedule:
validate_user_submitted_schedule:




============== Here is the structure of the following ==============




"""

class DummyCourseIdentifier:

    def __init__(self, course_number: Optional[str], name: Optional[str] = None, is_stub: Optional[bool] = None):
        self.course_number: Optional[str] = course_number
        self.name: Optional[str] = name
        self._is_stub: bool = is_stub if is_stub is not None else course_number is None

    def __eq__(self, rhs: Any):
        result: bool = False
        if isinstance(rhs, DummyCourseIdentifier):
            rhs: DummyCourseIdentifier
            result = self.course_number == rhs.course_number and not self.is_stub()
        elif isinstance(rhs, DummySchedulable):
            rhs: DummySchedulable
            result = self == rhs.course_identifier
        return result

    def __str__(self) -> str:
        return self.course_number or self.name or 'Course'

    def is_stub(self) -> bool:
        return self._is_stub


class DummySchedulable:

    @staticmethod
    def create_schedulables(course_identifiers: list[DummyCourseIdentifier],
            course_info_container: DummyCourseInfoContainer) -> list[DummySchedulable]:
        
        result: list[DummySchedulable] = []

        identifier: DummyCourseIdentifier
        for identifier in course_identifiers:
            if identifier.is_stub():
                raise NotImplementedError
            else:
                result.append(
                    DummySchedulable(
                        identifier,
                        course_info_container.get_prereqs(identifier),
                        course_info_container.get_coreqs(identifier),
                        course_info_container.get_hours(identifier),
                        course_info_container.get_availability(identifier),
                        course_info_container.get_recommended(identifier)
                    )
                )
                
        return result


    def __init__(self, course_identifier: DummyCourseIdentifier, prerequisite_string: str = '', corequisite_string: str = '',
            hours: int = 3, availability: set[SemesterType] = [],
            recommended: set[str] = []):
        self.course_identifier: DummyCourseIdentifier = course_identifier
        self._prequisite_tree_string: str = prerequisite_string
        self._corequisite_tree_string: str = corequisite_string
        self.hours: int = hours
        self.availability: set[SemesterType] = availability
        self.recommended: set[str] = recommended

        self._prequisite_tree: Optional[RequirementsTree] = None
        self._corequisite_tree: Optional[RequirementsTree] = None
        
    
    def __eq__(self, rhs: Any):
        result: bool = False
        if isinstance(rhs, DummyCourseIdentifier):
            rhs: DummyCourseIdentifier
            result = self.course_identifier == rhs
        elif isinstance(rhs, DummySchedulable):
            rhs: DummySchedulable
            result = self.course_identifier == rhs.course_identifier
        return result

    def __str__(self):
        return str(self.course_identifier)
    
    def get_prequisite_tree(self) -> RequirementsTree:

        tree: Optional[RequirementsTree] = self._prequisite_tree
        if tree is None:
            tree = RequirementsParser.make_unified_from_course_selection_logic_string(self._prequisite_tree_string,
                artificial_exhaustive=True)
            self._prequisite_tree = tree

        return tree

    
    def get_corequisite_tree(self) -> RequirementsTree:

        tree: Optional[RequirementsTree] = self._corequisite_tree
        if tree is None:
            tree = RequirementsParser.make_unified_from_course_selection_logic_string(self._corequisite_tree_string,
                artificial_exhaustive=True)
            self._corequisite_tree = tree

        return tree
    
    def sync_course_taken(self, course_identifier: DummyCourseIdentifier) -> None:
        course_number: Optional[str] = course_identifier.course_number
        if course_number:
            corequisites: RequirementsTree = self.get_corequisite_tree()
            corequisites.sync_deep_deselection(course_number)

            prequisites: RequirementsTree = self.get_prequisite_tree()
            prequisites.sync_deep_selection(course_number)

    def sync_course_taking(self, course_identifier: DummyCourseIdentifier) -> None:
        course_number: Optional[str] = course_identifier.course_number
        if course_number:
            corequisites: RequirementsTree = self.get_corequisite_tree()
            corequisites.sync_deep_selection(course_number)

            prequisites: RequirementsTree = self.get_prequisite_tree()
            prequisites.sync_deep_deselection(course_number)
            prequisites.sync_deep_concurrent_selection(course_number)

    def sync_course_not_taken(self, course_identifier: DummyCourseIdentifier) -> None:
        # TODO: check if this is even a useful method
        # NOTE: this will set all courses matching the identifier as not taken (not undo one instance in the case of multiple instances to satisfy)
        course_number: Optional[str] = course_identifier.course_number
        if course_number:
            corequisites: RequirementsTree = self.get_corequisite_tree()
            corequisites.sync_deep_deselection(course_number)

            prequisites: RequirementsTree = self.get_prequisite_tree()
            prequisites.sync_deep_deselection(course_number)
            

    def can_be_taken_for_prequisites(self) -> bool:
        # TODO: use flag to check if the trees have been modified since the last check (to avoid deep_select_all_satified_children recalls)
        prequisites: RequirementsTree = self.get_prequisite_tree()
        prequisites.deep_select_all_satified_children() # Make all parents who can be satisfied selected
        return prequisites.is_deep_resolved()

    def can_be_taken_for_corequisites(self) -> bool:
        # TODO: use flag to check if the trees have been modified since the last check (to avoid deep_select_all_satified_children recalls)
        corequisites: RequirementsTree = self.get_corequisite_tree()
        corequisites.deep_select_all_satified_children() # Make all parents who can be satisfied selected
        return corequisites.is_deep_resolved()

    def can_be_taken(self) -> bool:
        return self.can_be_taken_for_prequisites() and self.can_be_taken_for_corequisites()

    def reset_prerequisites_selection(self) -> None:
        corequisites: RequirementsTree = self.get_corequisite_tree()
        corequisites.reset_deep_selection()

    def reset_corerequisites_selection(self) -> None:
        corequisites: RequirementsTree = self.get_corequisite_tree()
        corequisites.reset_deep_selection()

    def reset_all_selection(self) -> None:
        self.reset_prerequisites_selection()
        self.reset_corerequisites_selection()




class DummySemesterDescription:
    '''The description of a given semester.'''
    
    def __init__(self, year: int, semester_type: SemesterType, courses: Optional[list[DummySchedulable]] = None) -> None:
        self.year: int = year
        self.semester_type: SemesterType = semester_type
        self.courses: list[DummySchedulable] = courses if courses is not None else []

    def __str__(self) -> str:
        header: str = f'{self.year}, {SEMESTER_DESCRIPTION_MAPPING[self.semester_type]}: '
        return header + ', '.join(self.str_iterator())

    def __iter__(self) -> Iterator[DummySchedulable]:
        return self.courses.__iter__()
    
    # def __getitem__(self, index) -> str:
        # TODO: this is used to support legacy formatters
        # return self.courses[index].get_printable_name()

    def __len__(self) -> int:
        return len(self.courses)

    def __contains__(self, element: Any):
        return any(element == course for course in self.courses)

    def str_iterator(self) -> Iterator[str]:
        return [str(course) for course in self.courses].__iter__()



class DummyScheduleInfoContainer:

    @staticmethod
    def make_from_string_list(raw_list: list[list[str]], course_info: DummyScheduleInfoContainer,
            starting_semester: SemesterType = FALL, starting_year: int = 2023,
            confidence_level: Optional[float] = None) -> DummyScheduleInfoContainer:

        semesters: list[DummySemesterDescription] = []
        running_year: int = starting_year
        running_semester: SemesterType = starting_semester

        semester_list: list[str]
        for semester_list in raw_list:

            course_identifiers: list[DummyCourseIdentifier] = \
                [DummyCourseIdentifier(course_number) for course_number in semester_list]

            # course_number: str
            # for course_number in semester_list:
            #     course_identifiers.append(DummyCourseIdentifier(course_number))

            schedulables: list[DummySchedulable] = DummySchedulable.create_schedulables(course_identifiers, course_info)

            semesters.append(DummySemesterDescription(running_year, running_semester, schedulables))

            running_semester = SEMESTER_TYPE_SUCCESSOR[running_semester]
            if running_semester == SPRING:
                running_year += 1
        
        return DummyScheduleInfoContainer(semesters=semesters, confidence_level=confidence_level)

    # TODO: this is redundant (combine this and the above code)
    @staticmethod
    def make_from_schedulables_list(raw_list: list[list[DummySchedulable]],
            starting_semester: SemesterType = FALL, starting_year: int = 2023,
            confidence_level: Optional[float] = None) -> DummyScheduleInfoContainer:

        semesters: list[DummySemesterDescription] = []
        running_year: int = starting_year
        running_semester: SemesterType = starting_semester

        schedulables_list: list[CourseIdentifier]
        for schedulables_list in raw_list:
            semesters.append(DummySemesterDescription(running_year, running_semester, schedulables_list))

            running_semester = SEMESTER_TYPE_SUCCESSOR[running_semester]
            if running_semester == SPRING:
                running_year += 1
        
        return DummyScheduleInfoContainer(semesters=semesters, confidence_level=confidence_level)

    def __init__(self, semesters: Optional[list[DummySemesterDescription]] = None,
            confidence_level: Optional[float] = None):
        self._semesters: list[DummySemesterDescription] = semesters if semesters is not None else []
        self._confidence_level: Optional[float] = confidence_level

    def __str__(self) -> str:
        return "\n".join([str(semester) for semester in self._semesters]) if len(self._semesters) != 0 else '*Empty Path*'

    def __iter__(self) -> Iterator[DummySemesterDescription]:
        return self._semesters.__iter__()

    def get_schedule(self) -> list[DummySemesterDescription]:
        return self._semesters

    def get_confidence_level(self) -> Optional[float]:
        return self._confidence_level

    def semester_count(self) -> int:
        return len(self._semesters)

    def max_semester_course_count(self) -> int:
        return max(len(semester) for semester in self._semesters)

    def course_count(self) -> int:
        return sum(len(semester) for semester in self._semesters)
    


class DummyPathValidationReport:
    
    class Error:
        def __init__(self, description: str) -> None:
            self.description = description

        def __str__(self) -> str:
            return self.description

    def __init__(self, error_list: Optional[list[DummyPathValidationReport.Error]] = None,
                 resultType: ValidationReportResult = VALIDATION_REPORT_WORKING,
                 file_description: Optional[Path] = None, confidence_factor: Optional[float] = None) -> None:
        self.file_description: Optional[Path] = file_description
        self.confidence_factor: Optional[float] = confidence_factor
        self.error_list: list[DummyPathValidationReport.Error] = error_list if error_list is not None else []
        self.resultType: ValidationReportResult = resultType

    def __str__(self):
        return 'Valid' if self.is_valid() else 'Invalid'
    
    def is_valid(self) -> bool:
        '''Returns the validity (boolean) of the student's path.'''
        return self.error_list == [] and (self.resultType == VALIDATION_REPORT_PARSED or 
            self.resultType == VALIDATION_REPORT_WORKING)

    def get_errors_printable(self) -> str:
        return '\n'.join([str(error) for error in self.error_list]) if len(self.error_list) != 0 else '*No Errors*'

    

    

def dummy_rigorous_validate_schedule(schedule: DummyScheduleInfoContainer,
        taken_courses: list[DummyCourseIdentifier] = [],
        prequisite_ignored_courses: list[DummyCourseIdentifier] = []) -> DummyPathValidationReport:

    # TODO: implement checking for courses not appearing in course info container (unless signed off on)

    # TODO:
    # NOTE: there is a lot of longer than needed searches in this method.
    # It might be a good move to create a sometimes-hashed map for searching. There are 2 parts:
    # 1. hashed map for searching, 2. a shorter list for linear searching or no searching at all.

    running_taken_courses: list[DummyCourseIdentifier] = taken_courses[:]
    error_list: list[DummyPathValidationReport.Error] = []

    semester: DummySemesterDescription
    for semester in schedule:

        # Get the year and semester information
        working_year: int = semester.year
        working_semester: SemesterType = semester.semester_type

        # Create a list of schedulables to check (requirements)--the identifiers will be added to running_taken_courses
        currently_taking_courses: list[DummySchedulable] = []
        
        course: DummySchedulable

        # Check for repeating course within a semester and update the coreq.s
        for course in semester:

            # Clear all the selections (this is the first time encountering the course)
            course.reset_all_selection()

            # Check for repeating course within a semester
            if course not in currently_taking_courses:
                
                # Check if the course was taken in another semester
                if course in running_taken_courses:
                    # Repeating course found in different semester (append an error report)
                    error_description: str = f'Taking {course} again in {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                    error_list.append(DummyPathValidationReport.Error(error_description))

                # Make each course recognize the coreq. relationship (bidirectional)
                taking_course: DummySchedulable
                for taking_course in currently_taking_courses:
                    course.sync_course_taking(taking_course.course_identifier)
                    taking_course.sync_course_taking(course.course_identifier)
                
                # Make each course recognize the prereq.s
                taken_course_identifier: DummyCourseIdentifier
                for taken_course_identifier in running_taken_courses:
                    course.sync_course_taken(taken_course_identifier)

                # Append the course the to the list of currentlyt taking courses
                currently_taking_courses.append(course)

            else:
                # Repeating course found in the same semester (append an error report)
                error_description: str = f'Taking {course} multiple times in {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                error_list.append(DummyPathValidationReport.Error(error_description))


        # Check for prereq.s/coreq.s and availability
        for course in currently_taking_courses:

            # Check prereq.s/coreq.s
            if not course.can_be_taken() and course not in prequisite_ignored_courses:
                # TODO: add a logic requiremnt print out to the report (prereq.s and coreq.s)
                # Inadequate fulfillment of requirements (append an error report)
                error_description: str = f'Not all requirements satisfied before taking {course} in {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                error_list.append(DummyPathValidationReport.Error(error_description))

            # Check availability
            if working_semester not in course.availability:
                # Inadequate fulfillment of requirements (append an error report)
                error_description: str = f'Availability for {course} not present in {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                error_list.append(DummyPathValidationReport.Error(error_description))
        
        # Add the semester's courses to the list of courses taken
        for course in currently_taking_courses:
            running_taken_courses.append(course.course_identifier)
        
    return DummyPathValidationReport(error_list, VALIDATION_REPORT_PARSED)

    # processed_list = []
    # err_list = []
    # err_str = ''
    # current_semester = 'Su'
    
    # for semester in reversed(schedule):

    #     for course in semester:
    #         if current_semester not in container.get_availability(course):
    #             err_str = (f'{course} taken during the {USER_READABLE_SEMESTER_DESCRIPTION[current_semester]} term (not available).')
    #             err_list.append(err_str)

    #         #course_coreqs = container.get_coreqs(course)

    #         # TODO: this was added before presentation for demonstration
    #         requirements = container.get_coreqs(course) or ''
    #         tree = RequirementsParser.make_from_course_selection_logic_string(requirements)
    #         course_coreqs = []#[i.course_number for i in tree.decision_tree.get_all_aggragate()]

    #         for coreq in course_coreqs:
    #             if coreq in processed_list:
    #                 err_str = (f'{course} taken before {coreq}.')
    #                 err_list.append(err_str)

    #     for course in semester:
    #         processed_list.append(course)
    #     for course in semester:
    #         # Check if the course is being scheduled multiple times
    #         if processed_list.count(course) > 1:
    #             err_str = (f'{course} scheduled multiple times.')
    #             if err_str not in err_list and 'XXX' not in course:
    #                 err_list.append(err_str)

    #         #course_prereqs = container.get_prereqs(course)
            
    #         # TODO: this was added before presentation for demonstration
    #         requirements = container.get_prereqs(course) or ''
    #         tree = RequirementsParser.make_from_course_selection_logic_string(requirements)
    #         course_prereqs = [i.course_number for i in tree.decision_tree.get_all_aggragate()]
            
    #         for prereq in course_prereqs:
    #             if prereq in processed_list:
    #                 err_str = (f'{course} taken before/during {prereq}.')
    #                 err_list.append(err_str)

    #     # Update the semester term
    #     current_semester = SEMESTER_TYPE_PREDECESSOR[current_semester]

    # return err_list

    # throw the semester's courses in big list
    # check to see if any of the prereqs for the courses 
    # for the semester you are 
    # on are in the big list. If the are, append to string.
    # If no problems return none

    # New comment to test branch




# The following is surely going to be removed:

class DummyCourseInfoContainer:

    def __init__(self):
        # "CPSC 1301": ("Computer Science", 3, set(FALL, SPRING, SUMMER), set(),
        #     "[s <n=Prerequsites, c=1>[d <n=MATH 1234>][d <n=MATH 4321>]]",
        #     ""),
        # "CPSC 1301": ("Computer Science", 3, set(FALL, SPRING, SUMMER), set(),
        #     "[s <n=Prerequsites, c=1>[d <n=MATH 1234>][d <n=MATH 4321>]]",
        #     ""),
        """[e <n=Requires All:>
	[d <n=CPSC 1301K>]
	[d <n=MATH 1113>]
]
"""
        self.dataset = {
            "CPSC 1105": ("Introduction to Computing Principles and Technology", 3, set([FALL, SPRING, SUMMER]), set(), "", ""),
            "CPSC 1301K": ("Computer Science I", 3, set([FALL, SPRING, SUMMER]), set(), "", ""),
            "CPSC 1302": ("Computer Science II", 3, set([FALL, SPRING, SUMMER]), set(), """(CPSC 1301K, MATH 1113)""", ""),
            "CPSC 1555": ("Selected Topics in Computer Science", 3, set([]), set(), "", ""),
            "CPSC 2105": ("Computer Organization", 3, set([FALL, SPRING]), set(), """[e <n=Requires All:>
	[s <c=1, n=Requires 1:>
		[d <n=CSCI 1301>]
		[d <n=CPSC 1301K>]
	]
	[d <n=MATH 2125>]
]
""", ""),
            "CPSC 2108": ("Data Structures", 3, set([FALL, SPRING, SUMMER]), set(), """[s <c=1, n=Requires 1:>
	[e <n=Requires All:>
		[d <n=CPSC 1302>]
		[d <n=MATH 2125>]
	]
	[d <n=MATH 2125>]
]
""", ""),
            "CPSC 2115": ("Information Technology Fundamentals", 3, set([]), set(), "", ""),
            "CPSC 2125": ("Internet Programming", 3, set([FALL]), set(), """[d <n=CPSC 1301K>]
""", ""),
            "CPSC 2555": ("Selected Topics in Computer Science", 3, set([]), set(), """[d <n=CPSC 1302>]
""", ""),
            "CPSC 3105": ("Digital Multimedia Development", 3, set([SPRING]), set(), """[d <n=CPSC 2125>]
""", ""),
            "CPSC 3111": ("COBOL Programming", 3, set([FALL]), set(), """[d <n=CPSC 1302>]
""", ""),
            "CPSC 3116": ("z/OS and JCL", 3, set([FALL]), set(), """[d <n=CPSC 1302>]
""", ""),
            "CPSC 3118": ("Graphical User Interface Development", 3, set([SPRING]), set(), """[d <n=CPSC 1302>]
""", ""),
            "CPSC 3121": ("Assembly Language Programming I", 3, set([SPRING]), set(), """[e <n=Requires All:>
	[d <n=CPSC 2105>]
	[d <n=CPSC 1302>]
]
""", ""),
            "CPSC 3125": ("Operating Systems", 3, set([FALL, SPRING]), set(), """[s <c=1, n=Requires 1:>
	[e <n=Requires All:>
		[d <n=CPSC 2105>]
		[d <n=CPSC 2108>]
	]
	[d <n=CPSC 2108>]
]
""", ""),
            "CPSC 3131": (" Database Systems I", 3, set([FALL, SPRING]), set(), """[d <n=CPSC 1302>]
""", ""),
            "CPSC 3137": ("Natural Language Processing and Text Mining", 3, set([]), set(), """[d <n=CPSC 1301K>]
""", ""),
            "CPSC 3156": ("Transaction Processing", 3, set ([SPRING]), set(), """[d <n=CPSC 3111>]
""", ""),
            "CPSC 3165": ("Professionalism in Computing", 3, set([FALL, SPRING, SUMMER]), set(), "", ""),
            "CPSC 3175": ("Object-Oriented Design", 3, set([FALL, SPRING]), set(), """[d <n=CPSC 2108>]
""", ""),
            "CPSC 3415": ("Information Technology (IT) Practicum", 3, set([FALL, SPRING, SUMMER]), set(), "", ""),
            "CPSC 3555": ("Selected Topics in Computer Science", 3, set([FALL, SPRING, SUMMER]), set(), """[d <n=CPSC 2108>]
""", ""),
            "CPSC 4000": ("Baccalaureate Survey", 3, set([FALL, SPRING, SUMMER]), set(), "", ""),
            "CPSC 4111": ("Game Programming I", 3, set([FALL]), set(), """[e <n=Requires All:>
	[d <n=CPSC 3118>]
	[d <n=CPSC 3175>]
]
""", ""),
            "CPSC 4112": ("Game Programming II", 3, set([SPRING]), set(), """[e <n=Requires All:>
	[d <n=CPSC 4111>]
	[d <n=CPSC 4113>]
]
""", ""),
            "CPSC 4113": ("Game Jam", 3, set([SPRING]), set(), """[e <n=Requires All:>
	[d <n=CPSC 4111>]
	[d <n=CPSC 4112>]
]
""", ""),
            "CPSC 4115": ("Algorithms", 3, set([FALL]), set(), """[e <n=Requires All:>
	[d <n=CPSC 2108>]
	[d <n=MATH 5125U>]
]
""", ""),
            "CPSC 4121": ("Robotics Programming I", 3, set([FALL]), set(), """[d <n=CPSC 1302>]
""", ""),
            "CPSC 4122": ("Robotics Programming II", 3, set([]), set(), """[d <n=CPSC 4121>]
""", ""),
            "CPSC 4125": ("Server-Side Web Development", 3, set([FALL]), set(), """[e <n=Requires All:>
	[d <n=CPSC 2125>]
	[d <n=CPSC 3131>]
]
""", ""),
            "CPSC 4126": ("Web Development Projects", 3, set([SPRING]), set(), """[d <n=CPSC 4125>]
""", ""),
            "CPSC 4127": ("Computer and Network Security", 3, set([]), set(), """[e <n=Requires All:>
	[d <n=CYBR 2160>]
	[s <c=1, n=Requires 1:>
		[d <n=CYBR 2159>]
		[d <n=MISM 3145>]
	]
]
""", ""),
            "CPSC 4130": ("Mobile Computing", 3, set([]), set(), """[d <n=CPSC 3175>]
""", ""),
            "CPSC 4135": ("Programming Languages", 3, set([SPRING]), set(), """[d <n=CPSC 3175>]
""", ""),
            "CPSC 4138": ("Advanced Database Systems", 3, set([]), set(), """[d <n=CPSC 3131>]
""", ""),
            "CPSC 4145": ("Computer Graphics", 3, set([FALL]), set(), """[d <n=CPSC 2108>]
""", ""),
            "CPSC 4148": ("Theory of Computation", 3, set([SPRING]), set(), """[d <n=CPSC 4115>]
""", ""),
            "CPSC 4155": ("Computer Architecture", 3, set([FALL]), set(), """[d <n=CPSC 3121>]
""", ""),
            "CPSC 4157": ("Computer Networks", 3, set([FALL, SUMMER]), set(), """[d <n=CPSC 2108>]
""", ""),
            "CPSC 4175": ("Software Engineering", 3, set([FALL]), set(), """[d <n=CPSC 3175>]
""", ""),
            "CPSC 4176": ("Senior Software Engineering Project", 3, set([SPRING]), set(), """[d <n=CPSC 4175>]
""", ""),
            "CPSC 4185": ("Artificial Intelligence and Machine Learning", 3, set([SPRING]), set(), """[d <n=CPSC 2108>]
""", ""),
            "CPSC 4205": ("IT Senior Capstone", 3, set([FALL, SPRING, SUMMER]), set(), "", ""),
            "CPSC 4505": ("Undergraduate Research", 3, set([FALL, SPRING]), set(), """[d <n=CPSC 2108>]
""", ""),
            "CPSC 4555": ("Selected Topics in Computer Science", 3, set([]), set(), "", ""),
            "CPSC 4698": ("Internship", 3, set([SPRING]), set(), "", ""),
            "CPSC 4899": ("Independent Study", 3, set([SPRING]), set(), "", ""),
            "CPSC 6000": ("Graduate Exit Examination", 3, set([FALL, SPRING, SUMMER]), set(), "", ""),
            "CPSC 6103": ("Computer Science Principles for Teachers", 3, set([SPRING]), set(), "", ""),
            "CPSC 6105": ("Fundamental Principles of Computer Science", 3, set([FALL, SPRING]), set(), "", ""),
            "CPSC 6106": ("Fundamentals of Computer Programming and Data Structures", 3, set([FALL, SPRING, SUMMER]), set(), "", ""),
            "CPSC 6107": ("Survey of Modeling and Simulation", 3, set([SPRING]), set(), "", ""),
            "CPSC 6109": ("Algorithms Analysis and Design", 3, set([SPRING]), set(), "", ""),
            "CPSC 6114": ("Fundamentals of Machine Learning", 3, set([FALL]), set(), "", ""),
            "CPSC 6118": ("Human-Computer Interface Development", 3, set([]), set(), """[d <n=CPSC 6114>]
""", ""),
            "CPSC 6119": ("Object-Oriented Development", 3, set([FALL, SPRING]), set(), "", ""),
            "CPSC 6124": ("Advanced Machine Learning", 3, set([SPRING]), set(), """[d <n=CPSC 6114>]
""", ""),
            "CPSC 6125": ("Operating Systems Design and Implementation", 3, set([FALL]), set(), "", ""),
            "CPSC 6126": ("Introduction to Cybersecurity", 3, set([SPRING, SUMMER]), set(), "", ""),
            "CPSC 6127": ("Contemporary Issues in Database Management Systems", 3, set([SPRING]), set(), "", ""),
            "CPSC 6128": ("Network Security", 3, set([SPRING]), set(), """[d <n=CPSC 6126>]
""", ""),
            "CPSC 6129": ("Computer Language Design and Interpretation", 3, set([]), set(), "", ""),
            "CPSC 6136": ("Human Aspects of Cybersecurity", 3, set([SUMMER]), set(), """[d <n=CPSC 6126>]
""", ""),
            "CPSC 6138": ("Mobile Systems and Applications", 3, set([SUMMER]), set(), """[d <n=CPSC 6119>]
""", ""),
            "CPSC 6147": ("Data Visualization and Presentation", 3, set([SPRING]), set(), "", ""),
            "CPSC 6155": ("Advanced Computer Architecture", 3, set([]), set(), "", ""),
            "CPSC 6157": ("Network and Cloud Management", 3, set([FALL]), set(), "", ""),
            "CPSC 6159": ("Digital Forensics", 3, set([FALL]), set(), """[d <n=CPSC 6126>]
""", ""),
            "CPSC 6167": ("Cybersecurity Risk Management", 3, set([SPRING]), set(), """[d <n=CPSC 6126>]
""", ""),
            "CPSC 6175": ("Web Engineering and Technologies", 3, set([SPRING]), set(), "", ""),
            "CPSC 6177": ("Software Design and Development", 3, set([]), set(), "", ""),
            "CPSC 6178": ("Software Testing and Quality Assurance", 3, set([]), set(), "", ""),
            "CPSC 6179": ("Software Project Planning and Management", 3, set([FALL]), set(), "", ""),
            "CPSC 6180": ("Software Estimation and Measurement", 3, set([]), set(), "", ""),
            "CPSC 6185": ("Intelligent Systems", 3, set([SPRING]), set(), "", ""),
            "CPSC 6190": ("Applied Cryptography", 3, set([]), set(), """[d <n=CPSC 6106>]
""", ""),
            "CPSC 6555": ("Selected Topics in Computer Science", 3, set([SUMMER]), set(), "", ""),
            "CPSC 6698": ("Graduate Internship in Computer Science", 3, set([]), set(), "", ""),
            "CPSC 6899": ("Independent Study", 3, set([FALL, SPRING]), set(), "", ""),
            "CPSC 6985": ("Research and Thesis", 3, set([SPRING]), set(), "", ""),
            "CPSC 6986": ("Thesis Defense", 3, set([SPRING]), set(), "", ""),
        }

    # TODO: add dynamic to this in real info container
    def validate_course(self, courseid: str) -> bool:
        return courseid in self.dataset
    
    def get_name(self, courseid: DummyCourseIdentifier):
        if courseid.course_number in self.dataset:
            return self.dataset[courseid.course_number][0]
        else:
            raise KeyError(courseid.course_number + " is not found!")
    
    def get_hours(self, courseid): 
        if courseid.course_number in self.dataset:
            return self.dataset[courseid.course_number][1]
        else:
            raise KeyError(courseid.course_number + " is not found!")
    
    def get_availability(self, courseid):
        if courseid.course_number in self.dataset:
            result = self.dataset[courseid.course_number][2]
            return result if len(result) != 0 else set([FALL, SPRING])
        else:
            raise KeyError(courseid.course_number + " is not found!")

    def get_prereqs(self, courseid):
        if courseid.course_number in self.dataset:
            return self.dataset[courseid.course_number][4]
        else:
            raise KeyError(courseid.course_number + " is not found!")

    def get_coreqs(self, courseid):
        if courseid.course_number in self.dataset:
            return self.dataset[courseid.course_number][5]
        else:
            raise KeyError(courseid.course_number + " is not found!")

    def get_recommended(self, courseid):
        if courseid.course_number in self.dataset:
            return self.dataset[courseid.course_number][3]
        else:
            raise KeyError(courseid.course_number + " is not found!")

    def get_importance(self, courseid):
        return 1


# Approach:
# Keep a list of courses for each semester in itself a list
# each list stores a list of course indices
# each evaluation only schedules those that can be scheduled (every other will not be pushed)
# if a schedule misses scheduling a course (not being scheduled at all), it is dead/zero fitness (strong rule)

# hyper parameter will be strong rule: how many extra course indices in a given semester allowed (either kill entire schedule (strong) or truncate (weak))


# Caching will become very important:
# this will be used to speed up determining which courses can be taken

# TODO: there needs to be fitness influence from the number of semesters taken

# Approach:
# Steps to initialization:
#   create a blank object
#   load the provided list of list of courses
#   for each semester, create a new gene semester
#       for each course, add it into the gene semester and register all schedulables with each other (taking)
#   



# Steps to judge a semester (fitness)



# Steps to mutate a course:



ScheduleFitenessFunction = Callable[[ScheduleInfoContainer, DummyCourseInfoContainer], float]

class DummyGeneticOptimizer:

    class Gene:

        # The process of "executing" genes will consist of pulling courses from the list of possibilities.
        # This will involve taking courses from a running list of courses based on availability.
        # The actual judging will be done seperately.

        # There are two reasons to check whether a course can be taken:
        #   1. to construct a one-dimensional list of courses to pull from as per the gene encoding.
        #       This is a dynamic schema that ensures better quality results.
        #   2. to find the validatity of the produced schedule.


        def __init__(self, cloned: Optional[DummyGeneticOptimizer.Gene]):
            self.selections: list[int] = [] if cloned is None else cloned.selections[:]

        def __str__(self) -> str:
            return str(self.selections)

        def make_schedule_info_container(self, optimizer: DummyGeneticOptimizer) -> DummyScheduleInfoContainer:
            raw_list: list[list[DummySchedulable]] = []

            #return DummyScheduleInfoContainer.make_from_schedulables_list(raw_list, starting_semester = optimizer.semester_start, starting_year =, confidence_level: float | None = None))

    def __init__(self, domain: list[DummySchedulable], course_info_container: DummyCourseInfoContainer,
            parameters_container: SchedulerParameterContainer, fiteness_function: ScheduleFitenessFunction,
            semester_start: SemesterType, year: int) -> None:
        
        self.course_info_container: DummyCourseInfoContainer = course_info_container

        self.semester_start: SemesterType = semester_start
        self.year_start: int = year

        # The following will vary by student
        self.parameters_container: SchedulerParameterContainer = parameters_container

        # The following are derived from a degree extraction container
        self._courses_needed_container: Optional[CoursesNeededContainer] = None
        self.taken_course: list[DummyCourseIdentifier] = []
        self.schedulables: list[DummySchedulable] = []

        # The fitness function for evolving the gene sequences
        self._fiteness_function = fiteness_function

        # Setup genetic algorithm variables
        self.setup_genetics(population_size=1, course_count=0, mutation_rate=0.25)


    
    def setup_genetics(self, population_size: int, course_count: int, mutation_rate: float = 0.25,\
            fitness_function: Optional[ScheduleFitenessFunction] = None) -> None:
        '''Setup the gene algorithm relevant instance variables.'''
        
        # ------------------------ Populations Properties ------------------------ #

        # The number of gene sequences in the population
        self._population_size: int = population_size

        # The list of population gene sequences in no particular order
        self._population_gene_sequences: list[DummyGeneticOptimizer.Gene] = []

        # The number of courses to schedule
        self._course_count: int = course_count

        # The chance (0 to 1) that a mutation will occur on a single bit for a new gene sequence
        self._mutation_rate: float = mutation_rate
        
        # ------------------------ Training Properties ------------------------ #

        # The hard/maximum number of iterations left for training
        self._training_iterations_left: int = 0

        # The threshold for the fitness that when met terminates training
        self._fitness_threshold: Optional[float] = None
        
        # ------------------------ Cache Properties ------------------------ #

        # A simple cache queue that is used to determine which cached fitness values should be removed from the cache (does not sort by access, only by addition)
        self._fitness_cache_queue: list[str] = []

        # A cache of fitness values given a gene sequence (cleared when the fitness function is updated)
        self._fitness_cache: dict[str, float] = {}

        # The active size of the fitness value cache
        self._cache_size: int = 0

        # The maximum size of the fitness value cache
        self._max_cache_size: int = CACHE_SIZE

        # ------------------------ Fitness Function ------------------------ #

        if fitness_function is not None:
            self._fitness_function: FitenessFunction = fitness_function
            


    # ------------------------ Fitness Function Property ------------------------ #

    def _get_fitness_function(self) -> FitenessFunction:
        '''Getter for fitness function.'''
        return self._fitness_function
    
    def _set_fitness_function(self, value: FitenessFunction):
        '''Setter for fitness function.'''
        self._fitness_function = value
        self._fitness_cache_queue = []
        self._fitness_cache = {}
        self._cache_size = 0
    
    _fitness_function = property(_get_fitness_function, _set_fitness_function)

    # ------------------------ Setup/configuration ------------------------ #

    '''Fill the remaining space in the population with random gene sequences.'''
    def fill_population_with_model(self, possible_gene_sequence: list[DummyGeneticOptimizer.Gene]) -> None:

        while len(self._population_gene_sequences) < self._population_size:
            new_gene_sequence: DummyGeneticOptimizer.Gene = DummyGeneticOptimizer.Gene(choice(possible_gene_sequence))
            self._population_gene_sequences.append(new_gene_sequence)


    def set_to_track_session(self, maximum_iterations: int, fitness_threshold: Optional[float] = None) -> None:
        '''Set up the trainer to start performing evolution.'''
        self._training_iterations_left = maximum_iterations
        self._fitness_threshold = fitness_threshold
    
    # ------------------------ Gene Sequence Evaluation ------------------------ #

    def evaluate_gene_sequence_fitness(self, gene_sequence: DummyGeneticOptimizer.Gene) -> float:
        '''Calculate the passed gene sequence's fitness.'''
        
        memo: str = str(gene_sequence)
        fitness: float = -inf
        
        # Check if the memo (gene) is already cached
        if memo not in self._fitness_cache:

            # The sequence is not cached
            schedule: DummyScheduleInfoContainer = gene_sequence.make_schedule_info_container(self)
            fitness: float = self._fitness_function(schedule)

            # Memoization management
            self._fitness_cache_queue.append(memo)
            self._fitness_cache[memo] = fitness
            self._cache_size += 1

            if self._cache_size > self._max_cache_size:
                cachedEntityToRemove = self._fitness_cache_queue.pop(0)
                del self._fitness_cache[cachedEntityToRemove]
                self._cache_size -= 1
        else:
            # The sequence is cached
            fitness = self._fitness_cache[memo]
            
        return fitness


    def best_genes(self, count: int) -> list[DummyGeneticOptimizer.Gene]:
        '''Get a list of the (count)-many best gene sequences in order (using the current fitness function).'''

        best_genes: list[(float, DummyGeneticOptimizer.Gene)] = []

        gene: DummyGeneticOptimizer.Gene
        for gene in self._population_gene_sequences:
            fitness: float = self.evaluate_gene_sequence_fitness(gene)
            best_genes.append((fitness, gene))
        
        best_genes.sort(key=lambda tuple: tuple[0], reverse=True)

        return [entry for _, entry in best_genes[:count]]

    # ------------------------ Breeding ------------------------ #

    def crossover_gene_sequences(self, gene1: str, gene2: str) -> str:
        '''Get a single child from the passed parents, crossing over the genes randomly.
        The order of the parents does not matter.'''

        crossIndex: int = randint(0, self.bitLength)
        firstGene: str
        secondGene: str
        firstGene, secondGene = (gene1, gene2) if randint(0, 1) else (gene2, gene1)
        return firstGene[:crossIndex] + secondGene[crossIndex:]

    def mutate_genes(self, gene: str) -> str:
        '''Get a mutated version of the passed gene sequence. This applies one bit flips
        for a random bit.'''

        # Mutate has different parts:
        #   by shuffling courses within a semester (so some are taken over others)
        #   by changing completely a single class
        #   by swapping the positions of course bewteen semesters

        # TODO: Implement!!

        flippedIndex: int = randint(0, self.bitLength - 1)
        newBit: str = '1' if gene[flippedIndex] == '0' else '0'
        newGene: str = gene[:flippedIndex] + newBit + gene[flippedIndex+1:]
        return newGene

    def make_child_from(self, geneSequence1: str, geneSequence2: str) -> str:
        '''Get a child (gene sequence) from two parent (oder does not matter). This applies
        crossover and may flip any number of bits (less likely to be more).'''
        child = self.crossover_gene_sequences(geneSequence1, geneSequence2)
        should_mutate: bool = random() <= self._mutation_rate
        while should_mutate:
            child = self.mutate_genes(child)
            should_mutate = random() <= self._mutation_rate
        return child

    # ------------------------ Iteration training/evolution ------------------------ #

    def _reached_threshold(self, bestGeneSequences: list[str]) -> bool:
        '''Helper method for iteration method that updates the iteration count and determines if 
        any threshold has been met.'''

        self._training_iterations_left -= 1
        isFinishedTraining: bool = self._training_iterations_left <= 0
        
        # Check fitness
        if self._fitness_threshold is not None and \
                self.evaluate_gene_sequence_fitness(bestGeneSequences[0]) >= self._fitness_threshold:
            isFinishedTraining = True

        return isFinishedTraining


    def run_iteration(self, reduction_size: int, best_performer_maintain: int = 0) -> bool:
        '''Perform a single iteration/evolution over'''
        best_gene_sequences: list[DummyGeneticOptimizer.Gene] = self.best_genes(reduction_size)

        if self._reached_threshold(best_gene_sequences):
            return True
        
        number_of_parent_pairs: int = reduction_size//2
        new_population: list[DummyGeneticOptimizer.Gene] = []

        for index in range(min(best_performer_maintain, self._population_size)):
            new_population.append(best_gene_sequences[index])

        children_per_pair: int = (self._population_size - len(new_population))//number_of_parent_pairs
        shuffle(best_gene_sequences)

        for index in range(number_of_parent_pairs):
            gene_sequence_1 = best_gene_sequences[2 * index]
            gene_sequence_2 = best_gene_sequences[2 * index + 1]

            for _ in range(children_per_pair):
                new_population.append(self.make_child_from(gene_sequence_1, gene_sequence_2))
        
        for index in range(self._population_size - len(new_population)):
            gene_sequence_1 = best_gene_sequences[2 * index]
            gene_sequence_2 = best_gene_sequences[2 * index + 1]
            new_population.append(self.make_child_from(gene_sequence_1, gene_sequence_2))

        self._population_gene_sequences = new_population

        return False
    


    # TODO: make the schedulers interface uniform (maybe remove this)
    def prepare_schedulables(self) -> bool:
        pass

    def configure_hours_per_semester(self, number_of_hours) -> None:
        # self.hours_per_semester = number_of_hours
        # TODO: this is hard set on using the Fall (update to use any given semester or take into account tbe parameter
        # container and its interface) 
        self._parameters_container.set_hours(FALL, number_of_hours)
    
    def generate_schedule(self, prequisite_ignored_courses: list[DummyCourseIdentifier]) -> DummyScheduleInfoContainer:
        pass


DEFAULT_HOURS_PER_SEMESTER: int= 15

LOW_FITNESS: float = 1
MID_FITNESS: float = 5.5
HIGH_FITNESS: float = 10


NUMBER_COORDINATION: dict[str, float] = {
    "1": HIGH_FITNESS,
    "2": (HIGH_FITNESS + MID_FITNESS) / 2.0,
    "3": MID_FITNESS,
    "4": (MID_FITNESS + LOW_FITNESS) / 2.0
}

# TODO: implement this!
lower_number_rule: DummyConstuctiveScheduler.Rule
def lower_number_rule(course: DummyConstuctiveScheduler.Schedulable,
        courses_needed: list[DummyConstuctiveScheduler.Schedulable],
        course_info_container: DummyCourseInfoContainer) -> float:
    course_number: str = course.schedulable.course_identifier.course_number or ' \0'
    first_number: str = course_number[course_number.find(' ') + 1]
    return NUMBER_COORDINATION[first_number] if first_number in NUMBER_COORDINATION else LOW_FITNESS



# TODO: This needs to go!
TEST_GATEWAY_HARDSET_DICT: dict[str, float] = {
    "CPSC 1302": HIGH_FITNESS,
    "CPSC 1555": LOW_FITNESS
}

local_gatekeeper_rule: DummyConstuctiveScheduler.Rule
def local_gatekeeper_rule(course: DummyConstuctiveScheduler.Schedulable,
        courses_needed: list[DummyConstuctiveScheduler.Schedulable],
        course_info_container: DummyCourseInfoContainer) -> float:
    # TODO: this was commented out for the demonstration
    # weight = course_info_container.get_weight(courseID)
    # if weight is None:
    #     weight = LOW_FITNESS
    # fitness = HIGH_FITNESS - (HIGH_FITNESS - LOW_FITNESS) / (weight + 1)
    # return fitness
    # TODO: this is a test!
    return MID_FITNESS if course.schedulable.course_identifier.course_number not in TEST_GATEWAY_HARDSET_DICT \
        else TEST_GATEWAY_HARDSET_DICT[course.schedulable.course_identifier.course_number]
    course_id: str = course.schedulable.course_identifier.course_number
    count = 5
    other_course: DummyConstuctiveScheduler
    for other_course in courses_needed:
        pass
    return course.schedulable.get_prequisite_tree().has_deep_child_by_course_id()
    

FITNESS_LISTING: list[float] = [HIGH_FITNESS, MID_FITNESS, LOW_FITNESS]

availability_rule: DummyConstuctiveScheduler.Rule
def availability_rule(course: DummyConstuctiveScheduler.Schedulable,
        courses_needed: list[DummyConstuctiveScheduler.Schedulable],
        course_info_container: DummyCourseInfoContainer) -> float:
    return FITNESS_LISTING[max(len(course.schedulable.availability) - 1, 2)]
    

class DummyConstructiveSchedulingParametersContainers(SchedulerParameterContainer):
    
    def set_hours(self, semester_type: SemesterType, hours: int) -> None:
        '''Get the acceptability range for hours for a given semester type and year.'''
        if semester_type != SUMMER:
            self._fall_spring_hours = hours
        else:
            self._summer_hours = hours



class DummyConstuctiveScheduler:

    HARD_SEMESTER_LIMIT = 50
    
    class Schedulable:

        def __init__(self, schedulable: DummySchedulable) -> None:
            self.schedulable: DummySchedulable = schedulable
            self.first_take_fitness: Optional[float] = None

        def __str__(self) -> str:
            return str(self.schedulable)

        def __ge__(self, rhs: DummyConstuctiveScheduler.Schedulable) -> bool:
            return self.first_take_fitness <= rhs.first_take_fitness
        
        def __gt__(self, rhs: DummyConstuctiveScheduler.Schedulable) -> bool:
            return self.first_take_fitness < rhs.first_take_fitness
        
        def __le__(self, rhs: DummyConstuctiveScheduler.Schedulable) -> bool:
            return self.first_take_fitness >= rhs.first_take_fitness

        def __lt__(self, rhs: DummyConstuctiveScheduler.Schedulable) -> bool:
            return self.first_take_fitness > rhs.first_take_fitness
    
    class SortingDict:

        def __init__(self) -> None:
            self._keys: list[int] = [] # ordered low to high
            self._data: dict[int, list[DummyConstuctiveScheduler.Schedulable]] = {}
            self._set: set[DummyConstuctiveScheduler.Schedulable] = set()
        
        def has_course(self) -> bool:
            return len(self._keys) != 0

        def all(self) -> Iterator[DummyConstuctiveScheduler.Schedulable]:
            return self._set.__iter__()

        def get_top_key(self) -> Optional[int]:
            return self._keys[-1] if self._keys else None

        def get_next_key(self, key: int) -> Optional[int]:
            # NOTE: this is linear because of the domain
            next_key_index: int = len(self._keys) - 1
            while next_key_index >= 0 and self._keys[next_key_index] >= key:
                next_key_index -= 1
            return self._keys[next_key_index] if next_key_index >= 0 else None

        def get_schedulable(self, key: int, index: int) -> Optional[DummyConstuctiveScheduler.Schedulable]:
            result: Optional[DummyConstuctiveScheduler.Schedulable] = None
            if key in self._data:
                listing: list[DummyConstuctiveScheduler.Schedulable] = self._data[key]
                if index < len(listing):
                    result = listing[index]
            return result

        def add(self, schedulable: DummyConstuctiveScheduler.Schedulable) -> None:
            hours: int = schedulable.schedulable.hours
            if hours not in self._data:
                insort(self._keys, hours)
                self._data[hours] = []
            # Insert by Schedulable's "<", "<=", ">", and ">=" operator definitions
            insort(self._data[hours], schedulable)
            self._set.add(schedulable)
        
        def remove(self, key: int, index: int) -> None:
            if key in self._data:
                listing: list[DummyConstuctiveScheduler.Schedulable] = self._data[key]
                if index < len(listing):
                    self._set.remove(listing.pop(index)) # remove from both list and set
                # self._data[key] = listing[:index] + listing[index+1:]
                if not listing:
                    self._keys.remove(key)
                    del self._data[key]

        def remove_schedulable(self, schedulable: DummyConstuctiveScheduler.Schedulable) -> None:
            key: int = schedulable.schedulable.hours
            if key in self._data:
                listing: list[DummyConstuctiveScheduler.Schedulable] = self._data[key]
                if schedulable in listing:
                    listing.remove(schedulable)
                    if not listing:
                        self._keys.remove(key)
                        del self._data[key]

    

    Rule = Callable[[Schedulable, "list[Schedulable]", DummyCourseInfoContainer], float]
    
    def __init__(self, course_info_container: Optional[DummyCourseInfoContainer],
            parameters_container: SchedulerParameterContainer,
            semester_start: Optional[SemesterType] = None, year: Optional[int] = None) -> None:
        
        # TODO: implement some sort of time detection or pick up from the university website
        self.semester_start: SemesterType = semester_start if semester_start is not None else SPRING
        self.year_start: int = year if year is not None else 2023

        self._course_info_container: Optional[DummyCourseInfoContainer] = course_info_container
        self.schedule_evaluator: ExpertSystem = ExpertSystem()
        
        # The following will vary by student
        self._parameters_container: Optional[SchedulerParameterContainer] = parameters_container
        self._degree_extraction: Optional[DegreeExtractionContainer] = None

        # The following are derived from a degree extraction container
        self._courses_needed_container: Optional[CoursesNeededContainer] = None
        self._taken_course: list[DummyCourseIdentifier] = []
        self._schedulables: list[DummyConstuctiveScheduler.Schedulable] = []

        self._fitness_functions: list[DummyConstuctiveScheduler.Rule] = [
            lower_number_rule,
            local_gatekeeper_rule,
            availability_rule
        ]
    
    def get_schedulables(self) -> list[Schedulable]:
        return self._schedulables

    def get_parameter_container(self) -> Optional[SchedulerParameterContainer]:
        return self._parameters_container

    def get_course_info(self) -> Optional[CourseInfoContainer]:
        return self._course_info_container
        
    def get_schedule_evaluator(self) -> Optional[ExpertSystem]:
        return self.schedule_evaluator
        
    def get_courses_needed_container(self) -> Optional[DummyCourseInfoContainer]:
        return self._courses_needed_container
    
    def get_hours_per_semester(self, semesterType: SemesterType = FALL) -> int:
        # TODO: this uses just hours for the Fall (fix)
        return self._parameters_container.get_hours_for(semesterType)
    
    def configure_parameters(self, parameters_containter: SchedulerParameterContainer) -> None:
        self._parameters_container = parameters_containter

    def configure_degree_extraction(self, degree_extraction: DegreeExtractionContainer) -> None:
        self._degree_extraction = degree_extraction
        self._courses_needed_container = degree_extraction.make_courses_needed_container()
        self._taken_course = []
        taken_course_string: str
        for taken_course_string in degree_extraction.make_taken_courses_list():
            # TODO: verify the name and number are checked
            self._taken_course.append(DummyCourseIdentifier(taken_course_string))
    
    def configure_course_info(self, container: DummyCourseInfoContainer) -> None:
        self._course_info_container = container
        
    def prepare_schedulables(self) -> bool:

        courses_needed_root: RequirementsTree = self._courses_needed_container.get_decision_tree()

        if not courses_needed_root.is_deep_resolved():
            return False
        
        self._schedulables = []

        schedulable_parameters: list[SchedulableParameters] = courses_needed_root.get_aggregate()

        schedulable_parameters_item: SchedulableParameters
        for schedulable_parameters_item in schedulable_parameters:

            if not schedulable_parameters_item.is_stub:

                course_number: str = schedulable_parameters_item.course_number

                if course_number is None and course_info_container.validate_course(schedulable_parameters_item.course_name):
                    course_number = schedulable_parameters_item.course_name

                course_identifier: DummyCourseIdentifier = \
                    DummyCourseIdentifier(course_number, schedulable_parameters_item.course_name)
                schedulable: DummySchedulable = DummySchedulable(
                    course_identifier = course_identifier,
                    prerequisite_string = self._course_info_container.get_prereqs(course_identifier),
                    corequisite_string = self._course_info_container.get_coreqs(course_identifier),
                    hours = self._course_info_container.get_hours(course_identifier),
                    availability = self._course_info_container.get_availability(course_identifier),
                    recommended = self._course_info_container.get_recommended(course_identifier)
                )
                self._schedulables.append(DummyConstuctiveScheduler.Schedulable(schedulable))

            else:
                schedulable: DummySchedulable = DummySchedulable(
                    course_identifier = DummyCourseIdentifier(None, schedulable_parameters_item.course_name),
                    prerequisite_string = schedulable_parameters_item.stub_prereqs_logic_string,
                    corequisite_string = schedulable_parameters_item.stub_coreqs_logic_string,
                    hours = schedulable_parameters_item.stub_hours,
                    availability = schedulable_parameters_item.stub_availability,
                    recommended = schedulable_parameters_item.stub_availability
                )
                self._schedulables.append(DummyConstuctiveScheduler.Schedulable(schedulable))

        return True
        

    def configure_hours_per_semester(self, number_of_hours) -> None:
        # self.hours_per_semester = number_of_hours
        # TODO: this is hard set on using the Fall (update to use any given semester or take into account tbe parameter
        # container and its interface) 
        self._parameters_container.set_hours(FALL, number_of_hours)
    

    def _create_weighted_schedulables(self, prequisite_ignored_courses: list[DummyCourseIdentifier]) -> DummyConstuctiveScheduler.SortingDict:

        courses_needed: list[DummyConstuctiveScheduler.Schedulable] = self._schedulables
        taken_courses: list[DummyCourseIdentifier] = self._taken_course + prequisite_ignored_courses
        # print('Whats going into the scheduler:', [str(s) for s in courses_needed])

        course_info = self._course_info_container # Get the course info container

        schedulables_dictionary: DummyConstuctiveScheduler.SortingDict = DummyConstuctiveScheduler.SortingDict()

        schedulable: DummyConstuctiveScheduler.Schedulable
        for schedulable in courses_needed:

            new_fitness: float = 0
            fitness_function: DummyConstuctiveScheduler.Rule
            for fitness_function in self._fitness_functions:
                new_fitness += fitness_function(schedulable, courses_needed, course_info)
            schedulable.first_take_fitness = new_fitness

            schedulables_dictionary.add(schedulable)

            # Register all taken courses with the current schedule
            taken_course: DummyCourseIdentifier
            for taken_course in taken_courses:
                schedulable.schedulable.sync_course_taken(taken_course)
            
        # TODO: this is debugging
        for schedulable_class_hours, schedulable_class in schedulables_dictionary._data.items():
            print(schedulable_class_hours, ":")
            for schedulable in schedulable_class:
                print(schedulable, schedulable.first_take_fitness)

        return schedulables_dictionary

    def _generate_simple_corequisite_pairs(self) -> dict[str, DummyConstuctiveScheduler.Schedulable]:

        result: dict[str, DummyConstuctiveScheduler.Schedulable] = {}
        courses_needed: list[DummyConstuctiveScheduler.Schedulable] = self._schedulables

        schedulable: DummyConstuctiveScheduler.Schedulable
        for schedulable in courses_needed:
            corequisite_tree: RequirementsTree = schedulable.schedulable.get_corequisite_tree()
            if corequisite_tree.get_all_deep_count() == 1:
                delivable: SchedulableParameters = corequisite_tree.get_all_aggragate()[0]
                if delivable.course_number:
                    result[delivable.course_number] = schedulable

        print('Here is it, boss...', result) # TODO: remove this print
        return result
    
    def _constructive_schedule_as_list(self, schedulables_dictionary: DummyConstuctiveScheduler.SortingDict,
            simple_corequisite_pairs: dict[str, DummyConstuctiveScheduler.Schedulable]) -> list[list[DummySchedulable]]:
        '''Create a path/schedule as a list of list of schedulables. NOTE: the passes schedulables collection will be mutated.'''

        # This scheduling method work constructively, adding new courses to a working semester.
        # When the semester is full or no courses can be taken, the semester is appended to the path.
        # As soon as no courses remain or the hard limit is met, the path is returned as a list of list.
        # Course will be scheduled first by the larger credit hours (for a given semester).
        # Tie breaking will be performed by the precalculated fitness scores for the class.

        # Create list of lists (each sublist is a semester and in each sublist are the schedulables)
        result_list: list[list[DummySchedulable]] = []

        # Create variables to track the working the semester type (Spring, Fall, Summer) and year (such as 2023)
        working_semester_type: SemesterType = self.semester_start
        working_year: int = self.year_start

        # The hours available for the current semester
        hours_available = self.get_parameter_container().get_hours_for(working_semester_type, working_year).stop

        # The hard limit of semesters for the schedule (this will be decremented as scheduling continues)
        hard_iteration_limit: int = DummyConstuctiveScheduler.HARD_SEMESTER_LIMIT

        # The current number of hours to try to use for scheduling (this is part of the dictionary key for schedulable look up)
        hours_key: int = schedulables_dictionary.get_top_key()


        course_index: int = 0
        working_semester_list: list[DummyConstuctiveScheduler.Schedulable] = []
        
        # While course are still left to be scheduled
        while schedulables_dictionary.has_course():
            if hours_available >= hours_key:
                course: Optional[DummyConstuctiveScheduler.Schedulable] = \
                    schedulables_dictionary.get_schedulable(hours_key, course_index)
                if course is not None:
                    
                    if working_semester_type in course.schedulable.availability:
                        if course.schedulable.can_be_taken():
                            working_semester_list.append(course)
                            hours_available -= hours_key
                            schedulables_dictionary.remove(hours_key, course_index)
                            remaining_course: DummyConstuctiveScheduler.Schedulable
                            for remaining_course in schedulables_dictionary.all():
                                remaining_course.schedulable.sync_course_taking(course.schedulable.course_identifier)
                        else:
                            course_number: str = course.schedulable.course_identifier.course_number
                            if course_number in simple_corequisite_pairs:
                                # There is an associated simple coreq. (see if it will work)
                                additional_schedulable: DummyConstuctiveScheduler.Schedulable = simple_corequisite_pairs[course_number]
                                if working_semester_type in additional_schedulable.schedulable.availability and \
                                        hours_available >= hours_key + additional_schedulable.schedulable.hours:
                                    working_semester_list.append(course)
                                    working_semester_list.append(additional_schedulable)
                                    hours_available -= hours_key + additional_schedulable.schedulable.hours
                                    schedulables_dictionary.remove(hours_key, course_index)
                                    schedulables_dictionary.remove_schedulable(additional_schedulable)
                                    remaining_course: DummyConstuctiveScheduler.Schedulable
                                    for remaining_course in schedulables_dictionary.all():
                                        remaining_course.schedulable.sync_course_taking(course.schedulable.course_identifier)
                                        remaining_course.schedulable.sync_course_taking(additional_schedulable.schedulable.course_identifier)
                                else:
                                    course_index += 1
                            else:
                                course_index += 1
                    else:
                        course_index += 1
                else:
                    hours_key = schedulables_dictionary.get_next_key(hours_key)
                    course_index = 0
            else:
                hours_key = schedulables_dictionary.get_next_key(hours_key)
                course_index = 0

            if hours_key is None:

                # Rotate all courses to recognize the course as "taken" instead of "taking"
                working_course: DummyConstuctiveScheduler.Schedulable
                for working_course in working_semester_list:
                    remaining_course: DummyConstuctiveScheduler.Schedulable
                    for remaining_course in schedulables_dictionary.all():
                        remaining_course.schedulable.sync_course_taken(working_course.schedulable.course_identifier) 

                result_list.append([schedulable.schedulable for schedulable in working_semester_list])
                working_semester_list = []

                hours_key = schedulables_dictionary.get_top_key()
                course_index = 0

                working_semester_type = SEMESTER_TYPE_SUCCESSOR[working_semester_type]
                if working_semester_type == SPRING:
                    working_year += 1
                
                hours_available = self.get_parameter_container().get_hours_for(working_semester_type, working_year).stop

                hard_iteration_limit -= 1
                if hard_iteration_limit <= 0:
                    raise RuntimeError("Semester generating limit met")
            
        if working_semester_list:
            result_list.append([schedulable.schedulable for schedulable in working_semester_list])
        
        return result_list

        

    def generate_schedule(self, prequisite_ignored_courses: list[DummyCourseIdentifier], optimizer: Optional[DummyGeneticOptimizer] = None) -> DummyScheduleInfoContainer:
        """Primary method to schedule a path to graduation
           Inputs: None, but requires course_info and courses_needed setup prior to running
           Returns: list of lists, inner list is one semester of courses, outer list is full schedule"""

        # Create a dictionary that indexed by a composite of the credits hours and the fitness index (0 is the most fit, 1 the second most fit, etc.)
        schedulables_dictionary: DummyConstuctiveScheduler.SortingDict = self._create_weighted_schedulables(prequisite_ignored_courses)
        
        simple_corequisite_pairs: dict[str, DummyConstuctiveScheduler.Schedulable] = self._generate_simple_corequisite_pairs()

        # Create a list of lists using the above schedulables
        result_list = self._constructive_schedule_as_list(schedulables_dictionary, simple_corequisite_pairs)

        # Perform optimizations here (if an optimizer was passes in)
        if optimizer is not None:

            optimizer
        
        # Calculate the confidence factor for the new schedule
        dynamic_knowledge = DynamicKnowledge()
        dynamic_knowledge.set_schedule([[l.course_identifier.course_number or l.course_identifier.name for l in r] for r in result_list])
        confidence_factor = self.schedule_evaluator.calculate_confidence(dynamic_knowledge, self._course_info_container)

        return DummyScheduleInfoContainer.make_from_schedulables_list(
            raw_list = result_list,
            starting_semester = self.semester_start,
            starting_year = self.year_start,
            confidence_level = confidence_factor
        )
    


if __name__ == '__main__':
        print('Test starting')
        print(80*'=')
        print(80*'=')

        course_info_container: DummyCourseInfoContainer = DummyCourseInfoContainer()

        course_set_a: list[set] = [
            'CPSC 1301K',
            'CPSC 1302',
            'CPSC 2105',
            'CPSC 2108',
            'CPSC 3111',
            'CPSC 3121',
            'CPSC 3125',
            'CPSC 3131',
            'CPSC 3165',
            'CPSC 3165',
            'CPSC 3175',
            'CPSC 4115',
            'CPSC 4127',
            'CPSC 4135',
        ]
        
        identifiers = {id : DummyCourseIdentifier(id) for id in course_set_a}

        schedulables = DummySchedulable.create_schedulables(list(identifiers.values()), course_info_container)
        
        # for s in schedulables:
        #     print(40*'-')
        #     s.sync_prerequisites_taking(identifiers['CPSC 1301K'])
        #     s.sync_prerequisites_taking(DummyCourseIdentifier('MATH 2125'))
        #     s.sync_prerequisites_taking(DummyCourseIdentifier('MATH 1113'))
        #     s.sync_prerequisites_taking(DummyCourseIdentifier('CPSC 3175'))
        #     s.sync_prerequisites_taking(DummyCourseIdentifier('CYBR 2160'))
        #     s.sync_prerequisites_taking(DummyCourseIdentifier('MISM 3145'))
        #     # s.reset_all_selection()
        #     print(s.can_be_taken())
        #     print(s.course_identifier.course_number)
        #     print(s.get_prequisite_tree().get_deep_description())

        test_path_a: DummyScheduleInfoContainer = DummyScheduleInfoContainer.make_from_string_list([
            ['CPSC 1301K'],
            ['CPSC 1302', 'CPSC 1555'],
            ['CPSC 2108'],
            [],
            ['CPSC 2555'],
        ], course_info_container, starting_semester=FALL, starting_year=2023)
        
        print(test_path_a)



        report: DummyPathValidationReport = dummy_rigorous_validate_schedule(
            test_path_a,
            taken_courses=[DummyCourseIdentifier('MATH 2125'), DummyCourseIdentifier('MATH 1113')],
            prequisite_ignored_courses=[]
        )
        print('Errors:')
        print(report.get_errors_printable())


        ##################################################################
        ##################################################################



        dcspc: DummyConstructiveSchedulingParametersContainers\
            = DummyConstructiveSchedulingParametersContainers(Path.home(), [],
            fall_spring_hours=15, summer_hours=6)
        scheduler: DummyConstuctiveScheduler = DummyConstuctiveScheduler(course_info_container, dcspc)


#         degree_extraction: DegreeExtractionContainer = DegreeExtractionContainer(taken_courses=['MATH 2125', 'MATH 1113'],\
#             courses_needed_constuction_string='''
# [e <n=The Things>[d <n=CPSC 1301K>][d <n=CPSC 1302>][d <n=CPSC 1555>][d <n=CPSC 2108>][d <n=CPSC 2555>]
#             ''')

        degree_extraction: DegreeExtractionContainer = DegreeExtractionContainer(taken_courses=['MATH 2125'],\
            courses_needed_constuction_string='''
(CPSC 1105, CPSC 2105, CPSC 2115, CPSC 2125, CPSC 3105, CPSC 3111)[e <n=The Things>[d <n=CPSC 1301K>][d <n=CPSC 1302>][d <n=CPSC 1555>][s <n=Take, c=1>[d <n=CPSC 2108>][d <n=CPSC 2555>]]]
            ''')

        prequisite_ignored_courses: list[DummyCourseIdentifier] = [
            DummyCourseIdentifier('MATH 1113')
        ]
            
        print('SCHED')
        scheduler.configure_degree_extraction(degree_extraction)
        scheduler.get_courses_needed_container().stub_all_unresolved_nodes()
        scheduler.prepare_schedulables()
        print(scheduler.generate_schedule(prequisite_ignored_courses=prequisite_ignored_courses))

        



# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------------------------------------------------------------------------------------------------ #

# REFERNCE FROM OTHER ASSIGNMENT (aided by Ryan Zimmerman):

# Two Guys and a Duck (Thomas Merino and Ryan Zimmerman)
# 3/11/23
# Assignment 4 - CPSC 4185 - R. Abid - Spring, 2023


# ---------------------------------- Fitness Functions ---------------------------------- #


FitenessFunction = Callable[[ScheduleInfoContainer], float]

ratioOfSums: ScheduleFitenessFunction
def ratioOfSums(valuables: list[DummySchedulable]) -> float:
    '''The ratio between the some of the values and the sum of the weights (0 is empty list passed).'''
    if valuables:
        weightsSum: float = sum(valuable.weight for valuable in valuables)
        valuesSum: float = sum(valuable.value for valuable in valuables)
        return valuesSum / weightsSum
    else:
        return 0 

sumOfRatios: FitenessFunction
def sumOfRatios(valuables: set[Valuable]) -> float:
    '''The sum of the ratios between the values and the weights (0 is empty list passed).'''
    result = 0
    for valuable in valuables:
        result += valuable.value / valuable.weight
    return result


sumsDifference: FitenessFunction
def sumsDifference(valuables: set[Valuable]) -> float:
    '''The sum of the values minus the sum of the weights (0 is empty list passed).'''
    if valuables:
        return sum(valuable.value - valuable.weight for valuable in valuables)
    else:
        return 0

# The sum of the values (0 is empty list passed).
justValue: FitenessFunction = lambda valuables: \
    sum(valuable.value for valuable in valuables) if valuables else 0

# ---------------------------------- Trainer ---------------------------------- #

CACHE_SIZE: int = 1000
'''The max size of the cache for caching calculated fitness values'''

class Trainer:
    
    '''A trainer that manages a population (gene sequence strings) and the evolution of that population.'''
    def __init__(self, populationSize: int, maximumWeight: float, store: list[Valuable] = [], \
            mutationRate: float = 0.25, fitnessFunction: FitenessFunction = sumsDifference) -> None:
        
        # ------------------------ Populations Properties ------------------------ #

        self.populationSize: int = populationSize
        '''The number of gene sequences in the population.'''

        self.populationGeneSequences: list[str] = []
        '''The list of population gene sequences in no particular order.'''

        self.maximumWeight: float = maximumWeight
        '''The maximum weight a knapsack can hold.'''

        self.store: list[Valuable] = store
        '''The list of Valuable objects in the problem (order matters).'''

        self.bitLength: int = len(store)
        '''The size of the bit strings that make up each gene sequence. This should be the same
        as the length store.'''

        self.mutationRate: float = mutationRate
        '''The chance (0 to 1) that a mutation will occur on a single bit for a new gene sequence.'''
        
        # ------------------------ Training Properties ------------------------ #

        self.trainingIterationsLeft: int = 0
        '''the hard/maximum number of iterations left for training.'''

        self.valueThreshold: Optional[float] = None
        '''The threshold for the value that when met terminates training.'''

        self.valueCheckingSetSize: Optional[float] = None 
        '''The number of top n-many genes (when sorting the genes by fitness) to check
        when applying the valueThreshold check.'''

        self.fitnessThreshold: Optional[float] = None
        '''The threshold for the fitness that when met terminates training.'''
        
        # ------------------------ Cache Properties ------------------------ #
        
        self.fitnessCacheQueue: list[str] = []
        '''A simple cache queue that is used to determine which cached fitness values
        should be removed from the cache (does not sort by access, only by addition).'''

        self.fitnessCache: dict[str, float] = {}
        '''A cache of fitness values given a gene sequence (cleared when the fitness
        function is updated).'''

        self.cacheSize: int = 0
        '''The active size of the fitness value cache.'''

        self.maxCacheSize: int = CACHE_SIZE
        '''The maximum size of the fitness value cache.'''

        # ------------------------ Fitness Function ------------------------ #

        self._fitnessFunction: FitenessFunction = fitnessFunction
        '''The fitness function for evolving the gene sequences.'''


    # ------------------------ Fitness Function Property ------------------------ #

    def _get_fitnessFunction(self) -> FitenessFunction:
        '''Getter for fitness function.'''
        return self._fitnessFunction
    
    def _set_fitnessFunction(self, value: FitenessFunction):
        '''Setter for fitness function.'''
        self._fitnessFunction = value
        self.fitnessCacheQueue = []
        self.fitnessCache = {}
        self.cacheSize = 0
    
    fitnessFunction = property(_get_fitnessFunction, _set_fitnessFunction)

    # ------------------------ Setup/configuration ------------------------ #

    def setUpRandomPopulation(self) -> None:
        '''Set up the population using random gene sequences.'''
        self.populationGeneSequences = []
        self.fillRandomPopulation()

    def fillRandomPopulation(self) -> None:
        '''Fill the remaining space in the population with random gene sequences.'''
        choices: list[str] = ['0', '1']
        while len(self.populationGeneSequences) < self.populationSize:
            newGeneSequence: str = ''.join(choice(choices) for _ in range(self.bitLength))
            self.populationGeneSequences.append(newGeneSequence)

    def setUpSchemaPopulation(self, fillCap: Optional[int] = None) -> None:
        '''Set up the population using schema-based gene sequences. If fillCap is passed,
        only fillCap-many genes will be schema-based and the rest will be random.'''
        
        self.populationGeneSequences = []
        prototype: str = self.generatePrototype()
        prototypeCount = self.populationSize

        if fillCap is not None and fillCap < self.populationSize:
            prototypeCount = fillCap

        for _ in range(prototypeCount):
            self.populationGeneSequences.append(prototype)

        # Fill the rest with random
        self.fillRandomPopulation()
            

    def setToTrackSession(self, maximumIterations: int, valueThreshold: Union[float, None, str] = None, \
            fitnessThreshold: Optional[float] = None, valueCheckSize: Optional[int] = None) -> None:
        '''Set up the trainer to start performing evolution.'''

        self.trainingIterationsLeft = maximumIterations

        # Calculate or set the value threshold
        if isinstance(valueThreshold, str):
            if valueThreshold == 'guess':
                self.valueThreshold = self.generateValueApproximateThreshold()
            else:
                raise ValueError('Illegal value threshold calculation method.')
        else:
            self.valueThreshold = valueThreshold
        
        self.fitnessThreshold = fitnessThreshold
        self.valueCheckingSetSize = valueCheckSize
    

    # ------------------------ Heuristics ------------------------ #

    def generatePrototype(self) -> str:
        '''Generate a prototype by including 1s in all available places (don't exceed max weight),
        filling in order of best bang-for-buck (best value-to-weight ratio).'''

        # Create a list of store item indices ranked from best bang-for-buck to worst
        sortingLambda = lambda bitIndex: self.fitnessFunction({self.store[bitIndex]})
        itemIndicesRanking: list[int] = list(range(self.bitLength))
        itemIndicesRanking.sort(key=sortingLambda, reverse=True)
        
        resultBitSet: set[int] = set()
        workingResultWeight: float = 0
        for itemIndex in itemIndicesRanking:
            candidateItem: Valuable = self.store[itemIndex]
            
            if candidateItem.weight + workingResultWeight <= self.maximumWeight:
                resultBitSet.add(itemIndex)
                workingResultWeight += candidateItem.weight
        
        result: str = ''.join('1' if index in resultBitSet else '0' for index in range(self.bitLength))
        return result

    def generateValueApproximateThreshold(self) -> float:
        '''Calculate the threshold value by generating a prototype and adding to its value sum
        the smallest possible amount (0 if the prototype's remaining weight is 0).'''
        
        prototype: str = self.generatePrototype()
        prototypeValue: float = self.evaluateGeneSequenceValue(prototype)
        prototypeWeight: float = self.evaluateGeneSequenceWeight(prototype)
        
        # Check if the prototype's remaining weight is 0
        if self.maximumWeight - prototypeWeight == 0:
            return prototypeValue
        
        workingSmallestDifference = inf

        for lhsIndex in range(self.bitLength - 1):
            for rhsIndex in range(lhsIndex + 1, self.bitLength):
                difference: float = abs(self.store[lhsIndex].value - self.store[rhsIndex].value)
                if difference != 0 and difference < workingSmallestDifference:
                    workingSmallestDifference = difference

        return prototypeValue + workingSmallestDifference / 2.0

    
    # ------------------------ Gene Sequence Evaluation ------------------------ #

    def evaluateGeneSequenceWeight(self, geneSequence: str) -> float:
        '''Calculate the passed gene sequence's weight.'''
        weightSum: float = 0
        for bitIndex, bitValue in enumerate(geneSequence):
            if bitValue != '0':
                valuable: Valuable = self.store[bitIndex]
                weightSum += valuable.weight
        return weightSum

    def evaluateGeneSequenceValue(self, geneSequence: str) -> float:
        '''Calculate the passed gene sequence's value.'''
        valueSum: float = 0
        for bitIndex, bitValue in enumerate(geneSequence):
            if bitValue != '0':
                valuable: Valuable = self.store[bitIndex]
                valueSum += valuable.value
        return valueSum
    
    def evaluateGeneSequenceFitness(self, geneSequence: str) -> float:
        '''Calculate the passed gene sequence's fitness.'''
        
        memo: str = geneSequence
        fitness: float = -inf
        
        # Check if the memo (gene) is already cached
        if memo not in self.fitnessCache:
            # The sequence is not cached

            valuables: set[Valuable] = set()
            weightSum: float = 0

            for bitIndex, bitValue in enumerate(geneSequence):
                if bitValue != '0':
                    valuable: Valuable = self.store[bitIndex]
                    valuables.add(valuable)
                    weightSum += valuable.weight

                    if weightSum > self.maximumWeight:
                        break

            if weightSum <= self.maximumWeight:
                fitness = self.fitnessFunction(valuables)
            
            # Memoization management
            
            self.fitnessCacheQueue.append(memo)
            self.fitnessCache[memo] = fitness
            self.cacheSize += 1

            if self.cacheSize > self.maxCacheSize:
                cachedEntityToRemove = self.fitnessCacheQueue.pop(0)
                del self.fitnessCache[cachedEntityToRemove]
                self.cacheSize -= 1
        else:
            # The sequence is cached
            fitness = self.fitnessCache[memo]
            
        return fitness


    def bestGenes(self, count: int, silencePrint: bool = False) -> list[str]:
        '''Get a list of the (count)-many best gene sequences in order (using the
        current fitness function).'''

        bestGenes: list[(float, str)] = []
        highestFitness: float = -inf
        fitnessSum: float = 0

        gene: str
        for gene in self.populationGeneSequences:
            fitness: float = self.evaluateGeneSequenceFitness(gene)
            bestGenes.append((fitness, gene))
            highestFitness = max(highestFitness, fitness)
            if fitness != -inf:
                fitnessSum += fitness
        
        bestGenes.sort(key=lambda tuple: tuple[0], reverse=True)

        if SHOULD_PRINT_FITNESS and not silencePrint:
            print(f'Highest: {highestFitness:.2f},    Average: {fitnessSum/self.populationSize:.2f}')

        return [entry for _, entry in bestGenes[:count]]

    # ------------------------ Breeding ------------------------ #

    def crossoverGeneSequences(self, gene1: str, gene2: str) -> str:
        '''Get a single child from the passed parents, crossing over the genes randomly.
        The order of the parents does not matter.'''

        crossIndex: int = randint(0, self.bitLength)
        firstGene: str
        secondGene: str
        firstGene, secondGene = (gene1, gene2) if randint(0, 1) else (gene2, gene1)
        return firstGene[:crossIndex] + secondGene[crossIndex:]

    def mutateGenes(self, gene: str) -> str:
        '''Get a mutated version of the passed gene sequence. This applies one bit flips
        for a random bit.'''

        flippedIndex: int = randint(0, self.bitLength - 1)
        newBit: str = '1' if gene[flippedIndex] == '0' else '0'
        newGene: str = gene[:flippedIndex] + newBit + gene[flippedIndex+1:]
        return newGene

    def makeChildFrom(self, geneSequence1: str, geneSequence2: str) -> str:
        '''Get a child (gene sequence) from two parent (oder does not matter). This applies
        crossover and may flip any number of bits (less likely to be more).'''
        child = self.crossoverGeneSequences(geneSequence1, geneSequence2)
        should_mutate: bool = random() <= self.mutationRate
        while should_mutate:
            child = self.mutateGenes(child)
            should_mutate = random() <= self.mutationRate
        return child

    # ------------------------ Iteration training/evolution ------------------------ #

    def _reachedThreshold(self, bestGeneSequences: list[str]) -> bool:
        '''Helper method for iteration method that updates the iteration count and determines if 
        any threshold has been met.'''

        self.trainingIterationsLeft -= 1
        isFinishedTraining: bool = self.trainingIterationsLeft <= 0

        # Make the set/list of genes to perform a value check over 
        valueCheckingSet: list[str] = bestGeneSequences if self.valueCheckingSetSize is None \
            else bestGeneSequences[:self.valueCheckingSetSize]

        # Check value
        if self.valueThreshold is not None and \
                any(self.evaluateGeneSequenceValue(geneSequence) >= self.valueThreshold \
                for geneSequence in valueCheckingSet \
                if self.evaluateGeneSequenceWeight(geneSequence) <= self.maximumWeight):
            isFinishedTraining = True
            if SHOULD_PRINT_THRESHOLD_MEET:
                print('Reached the value threshold')
        
        # Check fitness
        if self.fitnessThreshold is not None and \
                self.evaluateGeneSequenceFitness(bestGeneSequences[0]) >= self.fitnessThreshold:
            isFinishedTraining = True
            if SHOULD_PRINT_THRESHOLD_MEET:
                print('Reached the fitness threshold')

        return isFinishedTraining


    def runIteration(self, reductionSize: int, bestPerformerMaintain: int = 0) -> bool:
        '''Perform a single iteration/evolution over'''
        bestGeneSequences: list[str] = self.bestGenes(reductionSize)

        if self._reachedThreshold(bestGeneSequences):
            return True
        
        numberOfParentPairs: int = reductionSize//2
        newPopulation: list[str] = []

        for index in range(min(bestPerformerMaintain, self.populationSize)):
            newPopulation.append(bestGeneSequences[index])

        childrenPerPair: int = (self.populationSize - len(newPopulation))//numberOfParentPairs
        shuffle(bestGeneSequences)

        for index in range(numberOfParentPairs):
            geneSequence1 = bestGeneSequences[2 * index]
            geneSequence2 = bestGeneSequences[2 * index + 1]

            for _ in range(childrenPerPair):
                newPopulation.append(self.makeChildFrom(geneSequence1, geneSequence2))
        
        for index in range(self.populationSize - len(newPopulation)):
            geneSequence1 = bestGeneSequences[2 * index]
            geneSequence2 = bestGeneSequences[2 * index + 1]
            newPopulation.append(self.makeChildFrom(geneSequence1, geneSequence2))

        self.populationGeneSequences = newPopulation

        return False
        

# ---------------------------------- Analysis ---------------------------------- #

def performanceTest(maximumWeight: float, store: list[Valuable]) -> None:

    # *ADJUST THIS TO ADJUST THE BEHAVIOR OF WHAT APPEARS IN MAIN*
    # More test parameters:
    populationSize: int = 100
    mutationRate: float = 0.25
    fitnessFunction: fitnessFunction = justValue
    initialSchemaPopulationFillCap: int = 0
    maximumIterations: int = 10
    # Use 'guess' to approximate the value threshold (just beyond what the schema gives)
    valueThrehold: Union[str, None, int] = None
    fitnessThreshold: Optional[float] = None
    reductionSize: int = populationSize//2
    bestPerformerMaintain: Optional[int] = 10

    # Testing:
    startTime = perf_counter()

    trainer = Trainer(populationSize=populationSize, maximumWeight=maximumWeight,\
        mutationRate=mutationRate, store=store, fitnessFunction=fitnessFunction)
    trainer.setUpSchemaPopulation(fillCap=initialSchemaPopulationFillCap)
    trainer.setToTrackSession(maximumIterations, valueThreshold=valueThrehold, \
        fitnessThreshold=fitnessThreshold)
    
    while not trainer.runIteration(reductionSize=reductionSize, \
        bestPerformerMaintain=bestPerformerMaintain): pass

    endTime = perf_counter()
    trainingTimeDelta = endTime - startTime

    # Return the trainer and the time to train
    return trainer, trainingTimeDelta


# ---------------------------------- Main ---------------------------------- #

if __name__ == '__main__' and False:

    # Get the arguments passed in via the terminal
    commandArguments = sys.argv[1:]

    if len(commandArguments) > 0 and commandArguments[0] == 'test':
        # trainer, trainingTime = performanceTest(10, assignmentStore1)
        # trainer, trainingTime = performanceTest(165, assignmentStore2)
        trainer, trainingTime = performanceTest(750, assignmentStore3)

        trainer.fitnessFunction = justValue
        geneSequences = trainer.bestGenes(10, silencePrint=True)
        print('Top 10 value-gene pairings:', [(trainer.evaluateGeneSequenceFitness(gene), gene) for gene in geneSequences])
        print(f'Training time: {trainingTime:.4f}')

    else:

        # Attempt to open a file and read the contents (for input)
        fileInputs: list[str] = []
        if len(commandArguments) > 0 and commandArguments[0] != '-t':
            with open(commandArguments[0], 'r') as f:
                fileInputs = f.readlines()

        # Get the input from the file (if available) or from the user
        def pullInput() -> str:
            result = None
            if fileInputs:
                result = fileInputs.pop(0)
            else:
                result = input()
            return result

        # Get the user-entered max weight and number of valuables
        userParmeters: list[str] = pullInput().split(' ')
        filter(lambda entry: entry != '', userParmeters)
        maxWeight: float = int(userParmeters[0])
        numberOfValuables: float = int(userParmeters[1])

        # Creata a list of the user-configured valuables
        usersStore: list[Valuable] = []

        for _ in range(numberOfValuables):
            # Add a valuable
            valuableParmeters: list[str] = pullInput().split(' ')
            filter(lambda entry: entry != '', valuableParmeters)
            usersStore.append(Valuable(value=int(valuableParmeters[1]), weight=int(valuableParmeters[0])))

        # Perform the training
        trainer, trainingTime = performanceTest(maxWeight, usersStore)

        # Get and print the best results by total value (new fitness function)
        trainer.fitnessFunction = justValue
        bestGeneSequence: str = trainer.bestGenes(1, silencePrint=True)[0]
        print(' '.join(bestGeneSequence))
        print(trainer.evaluateGeneSequenceFitness(bestGeneSequence), \
            trainer.evaluateGeneSequenceWeight(bestGeneSequence))
        print(f'Training time: {trainingTime:.4f}')





