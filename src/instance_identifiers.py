# Thomas Merino
# 4/24/2023
# CPSC 4176 Project

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Any
    from course_info_container import CourseInfoContainer
    from requirement_container import RequirementsContainer
    from requirement_tree import RequirementsTree
    

from general_utilities import *
from requirement_parser import RequirementsParser

DEFAULT_COURSE_CREDIT_HOURS: int = 3

# The name to give to a course identifier if no descriptions are found
DEFAULT_COURSE_PRINTABLE_NAME: str = 'Course'


class CourseIdentifier:

    def __init__(self, course_number: Optional[str], name: Optional[str] = None, is_stub: Optional[bool] = None):
        self.course_number: Optional[str] = course_number
        self.name: Optional[str] = name
        self._is_stub: bool = is_stub if is_stub is not None else course_number is None

    def __eq__(self, rhs: Any):
        result: bool = False
        if isinstance(rhs, CourseIdentifier):
            rhs: CourseIdentifier
            result = self.course_number == rhs.course_number and not self.is_stub()
        elif isinstance(rhs, Schedulable):
            rhs: Schedulable
            result = self == rhs.course_identifier
        return result

    def __str__(self) -> str:
        return self.course_number or self.name or 'Course'

    def is_stub(self) -> bool:
        return self._is_stub



class LegacyCourseIdentifier:

    def __init__(self, course_number: Optional[str] = None, course_name: Optional[str] = None, is_concrete: bool = True, \
            can_exist_multiple_times: bool = False) -> None:
        self._course_number: Optional[str] = course_number
        self._course_name: Optional[str] = course_name
        self._is_concrete: bool = is_concrete and course_number is not None
        self._can_exist_multiple_times: bool = can_exist_multiple_times
        
        self._stub_credits: Optional[int] = None
        self._stub_prequisite_tree: Optional[RequirementsContainer] = None
        self._stub_corequisite_tree: Optional[RequirementsContainer] = None
    
    def __str__(self) -> str:
        return self.get_printable_name()

    def get_printable_name(self) -> str:

        result: str = ''

        if self._is_concrete:
            result = str(self._course_number)
            if self._course_name is not None:
                result +=  f' - {self._course_name}'
        else:
            result = self._course_name or DEFAULT_COURSE_PRINTABLE_NAME
        
        return result


    def get_unique_id(self) -> Optional[str]:
        return self._course_number
    
    def get_name(self) -> Optional[str]:
        return self._course_name or self._course_number

    def is_concrete(self) -> bool:
        return self._is_concrete

    def can_exist_multiple_times(self) -> bool:
        return self._can_exist_multiple_times

    def get_credit_hours(self, course_info_container: CourseInfoContainer) -> int:

        result: int = DEFAULT_COURSE_CREDIT_HOURS

        if self._is_concrete:
            # TODO: add the actual function call here:
            #course_info_container.get_credits(self._course_number)
            pass
        elif result is None and self._stub_credits is not None:
            result = self._stub_credits
        
        return result

    def get_prequisites(self, course_info_container) -> Optional[RequirementsContainer]:
        
        result: Optional[RequirementsContainer] = self._stub_prequisite_tree

        if self._is_concrete:
            # TODO: add the actual function call here:
            course_info_container.get_credits(self._course_number)
        elif result is None:
            result = None # TODO: ADD DEFAULT TREE
        
        return result
        


class Schedulable:

    @staticmethod
    def create_schedulables(course_identifiers: list[CourseIdentifier],
            course_info_container: CourseInfoContainer) -> list[Schedulable]:
        
        result: list[Schedulable] = []

        identifier: CourseIdentifier
        for identifier in course_identifiers:
            if identifier.is_stub():
                raise NotImplementedError
            else:
                # TODO: IMP NEW -> 

                # TODO: REMOVE THIS - it is to support old interfaces (course info protocol)
                FUNC_identifier = identifier if isinstance(course_info_container, CourseInfoContainer) else identifier.course_number
                FUNC_availabilities = course_info_container.get_availability(FUNC_identifier)
                if isinstance(FUNC_availabilities, list):
                    FUNC_availabilities = set(map(lambda x: {'Fa':FALL, 'Sp':SPRING, 'Su':SUMMER, '--':None}[x], FUNC_availabilities))

                result.append(
                    Schedulable(
                        identifier,
                        course_info_container.get_prereqs(FUNC_identifier) or " ",
                        course_info_container.get_coreqs(FUNC_identifier) or " ",
                        course_info_container.get_hours(FUNC_identifier),
                        FUNC_availabilities,
                        course_info_container.get_recommended(FUNC_identifier)
                    )
                )
                
        return result


    def __init__(self, course_identifier: CourseIdentifier, prerequisite_string: str = '', corequisite_string: str = '',
            hours: int = 3, availability: set[SemesterType] = [],
            recommended: set[str] = []):
        self.course_identifier: CourseIdentifier = course_identifier
        self._prequisite_tree_string: str = prerequisite_string
        self._corequisite_tree_string: str = corequisite_string
        self.hours: int = hours
        self.availability: set[SemesterType] = availability
        self.recommended: set[str] = recommended

        self._prequisite_tree: Optional[RequirementsTree] = None
        self._corequisite_tree: Optional[RequirementsTree] = None
        
    
    def __eq__(self, rhs: Any):
        result: bool = False
        if isinstance(rhs, CourseIdentifier):
            rhs: CourseIdentifier
            result = self.course_identifier == rhs
        elif isinstance(rhs, Schedulable):
            rhs: Schedulable
            result = self.course_identifier == rhs.course_identifier
        return result

    def __str__(self):
        return str(self.course_identifier)
    
    def get_printable_name(self):
        return str(self)

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
    
    def sync_course_taken(self, course_identifier: CourseIdentifier) -> None:
        course_number: Optional[str] = course_identifier.course_number
        if course_number:
            corequisites: RequirementsTree = self.get_corequisite_tree()
            corequisites.sync_deep_deselection(course_number)

            prequisites: RequirementsTree = self.get_prequisite_tree()
            prequisites.sync_deep_selection(course_number)

    def sync_course_taking(self, course_identifier: CourseIdentifier) -> None:
        course_number: Optional[str] = course_identifier.course_number
        if course_number:
            corequisites: RequirementsTree = self.get_corequisite_tree()
            corequisites.sync_deep_selection(course_number)

            prequisites: RequirementsTree = self.get_prequisite_tree()
            prequisites.sync_deep_deselection(course_number)
            prequisites.sync_deep_concurrent_selection(course_number)

    def sync_course_not_taken(self, course_identifier: CourseIdentifier) -> None:
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
        if self._corequisite_tree is not None:
            corequisites: RequirementsTree = self.get_corequisite_tree()
            corequisites.reset_deep_selection()

    def reset_corerequisites_selection(self) -> None:
        if self._prequisite_tree is not None:
            corequisites: RequirementsTree = self.get_corequisite_tree()
            corequisites.reset_deep_selection()

    def reset_all_selection(self) -> None:
        self.reset_prerequisites_selection()
        self.reset_corerequisites_selection()


    def create_stateless_copy(self) -> Schedulable:
        
        result: Schedulable =  Schedulable(
            self.course_identifier,
            self._prequisite_tree_string,
            self._corequisite_tree_string,
            self.hours,
            self.availability,
            self.recommended
        )
        return result


class StudentIdentifier:

    def __init__(self, student_number: Optional[str] = None, student_name: Optional[str] = None) -> None:
        self.student_number: Optional[str] = student_number
        self.student_name: Optional[str] = student_name

    def is_concrete(self) -> bool:
        return self.student_number is not None or self.student_name is not None

    def __str__(self) -> str:
        description: str = 'Student'

        if self.student_name is not None:
            description = self.student_name

            if self.student_number is not None:
                description += f' ({self.student_number})'

        elif self.student_number is not None:
             description = str(self.student_number)

        return description
